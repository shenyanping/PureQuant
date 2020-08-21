from purequant.position import POSITION
from purequant.storage import storage
from purequant.time import get_localtime
from purequant.market import MARKET
from purequant.config import config
from purequant.exceptions import *

class SYNCHRONIZE:
    """持仓同步"""

    def __init__(self, databank, database, data_sheet, exchange, instrument_id, time_frame):
        print("{} {} 持仓同步功能已启动！".format(get_localtime(), instrument_id))
        self.__databank = databank
        self.__database = database
        self.__datasheet = data_sheet
        self.__exchange = exchange
        self.__instrument_id = instrument_id
        self.__time_frame = time_frame
        self.__position = POSITION(self.__exchange, self.__instrument_id, self.__time_frame)
        self.__market = MARKET(self.__exchange, self.__instrument_id, self.__time_frame)
        self.__overprice_range = config.overprice_range

    def save_strategy_position(self, strategy_direction, strategy_amount):
        """下单后将仓位信息保存至数据库."""
        if self.__databank == "mysql":
            storage.mysql_save_strategy_position(self.__database, self.__datasheet, strategy_direction,
                                           strategy_amount)
        elif self.__databank == "mongodb":
            storage.mongodb_save(data={"时间": get_localtime(), "strategy_direction": strategy_direction, "strategy_amount": strategy_amount}, database=self.__database, collection=self.__datasheet)
        else:
            raise DataBankError

    def match(self):
        # 获取当前账户持仓信息
        account_direction = self.__position.direction()
        account_amount = self.__position.amount()

        # 获取当前策略应持仓位信息
        if self.__databank == "mysql":
            strategy_direction = storage.read_mysql_datas(0, self.__database, self.__datasheet, "amount", ">=")[-1][-2]
            strategy_amount = storage.read_mysql_datas(0, self.__database, self.__datasheet, "amount", ">=")[-1][-1]
        elif self.__databank == "mongodb":
            strategy_direction = storage.mongodb_read_data(self.__database, self.__datasheet)[-1][0]["strategy_direction"]
            strategy_amount = int(storage.mongodb_read_data(self.__database, self.__datasheet)[-1][0]["strategy_amount"])
        else:
            strategy_direction = None
            strategy_amount = None
            raise DataBankError

        # 比较账户持仓与策略持仓，如不匹配则同步之
        if strategy_direction == "long" and account_direction == "long":
            if account_amount < strategy_amount:
                receipt = self.__exchange.buy(self.__market.last() * (1 + self.__overprice_range), strategy_amount - account_amount, 0)
                return "当前持多，当前实际持仓小于策略应持仓位数量，自动同步结果：{}".format(receipt)
            elif account_amount > strategy_amount:
                receipt = self.__exchange.sell(self.__market.last() * (1 - self.__overprice_range), account_amount - strategy_amount, 0)
                return "当前持多，当前实际持仓大于策略应持仓位数量，自动同步结果：{}".format(receipt)
        if strategy_direction == "short" and account_direction == "short": # 策略与账户均持空时
            if account_amount < strategy_amount:
                receipt = self.__exchange.sellshort(self.__market.last() * (1 - self.__overprice_range), strategy_amount - account_amount, 0)
                return "当前持空，当前实际持仓小于策略应持仓位数量，自动同步结果：{}".format(receipt)
            elif account_amount > strategy_amount:
                receipt = self.__exchange.buytocover(self.__market.last() * (1 + self.__overprice_range), account_amount - strategy_amount, 0)
                return "当前持空，当前实际持仓大于策略应持仓位数量，自动同步结果：{}".format(receipt)
        if strategy_direction == "long" and account_direction == "short": # 策略持多，账户却持空时
            receipt1 = self.__exchange.buytocover(self.__market.last() * (1 + self.__overprice_range), account_amount, 0)
            if "完全成交" not in receipt1:
                return "策略应持多，当前实际持空，自动同步结果：{}".format(receipt1)
            else:
                receipt2 = self.__exchange.buy(self.__market.last() * (1 + self.__overprice_range), strategy_amount, 0)
                return "策略应持多，当前实际持空，自动同步结果：{}".format(receipt1 + receipt2)
        if strategy_direction == "short" and account_direction == "long": # 策略持空，账户却持多时
            receipt1 = self.__exchange.sell(self.__market.last() * (1 - self.__overprice_range), account_amount, 0)
            if "完全成交" not in receipt1:
                return "策略应持空，当前实际持多，自动同步结果：{}".format(receipt1)
            else:
                receipt2 = self.__exchange.sellshort(self.__market.last() * (1 - self.__overprice_range), strategy_amount, 0)
                return "策略应持空，当前实际持多，自动同步结果：{}".format(receipt1 + receipt2)
        if strategy_direction == "none" and account_direction == "long":    # 策略无持仓，账户却持多时
            receipt = self.__exchange.sell(self.__market.last() * (1 - self.__overprice_range), account_amount, 0)
            return "策略应无持仓，当前实际持多，自动同步结果：{}".format(receipt)
        if strategy_direction == "none" and account_direction == "short":     # 策略无持仓，账户却持空时
            receipt = self.__exchange.buytocover(self.__market.last() * (1 + self.__overprice_range), account_amount, 0)
            return "策略应无持仓，当前实际持空，自动同步结果：{}".format(receipt)
        if account_direction == "none" and strategy_direction == "long":     # 账户无持仓，策略却应持多时
            receipt = self.__exchange.buy(self.__market.last() * (1 + self.__overprice_range), strategy_amount, 0)
            return "策略应持多仓，当前实际无持仓，自动同步结果：{}".format(receipt)
        if account_direction == "none" and strategy_direction == "short":     # 账户无持仓，策略却应持空
            receipt = self.__exchange.sellshort(self.__market.last() * (1 - self.__overprice_range), strategy_amount, 0)
            return "策略应持空仓，当前实际无持仓，自动同步结果：{}".format(receipt)
        if account_amount == strategy_amount and account_direction == strategy_direction:
            dict = {"策略持仓方向": strategy_direction, "策略持仓数量": strategy_amount, "账户实际持仓方向": account_direction,
                    "账户实际持仓数量": account_amount}
            return "策略持仓与账户持仓匹配！ {}".format(dict)
        else:
            raise MatchError

