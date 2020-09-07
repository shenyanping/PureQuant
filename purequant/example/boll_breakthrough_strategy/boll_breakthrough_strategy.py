"""
布林强盗突破策略    策略规则详见：https://zhuanlan.zhihu.com/p/64238996
此策略适用于OKEX的USDT合约
如需用于其他类型合约或现货，可自行修改
Author: Gary-Hertel
Date:   2020/08/31
email: interstella.ranger2020@gmail.com

鉴于回测模式与实盘模式策略运行机制的不同，故此策略的设置是当根k线开仓后当根k线不平仓
"""

from purequant.trade import OKEXFUTURES
from purequant.market import MARKET
from purequant.position import POSITION
from purequant.indicators import INDICATORS
from purequant.logger import logger
from purequant.config import config
from purequant.time import *
from purequant.storage import storage
from purequant.push import push

class Strategy:
    """布林强盗策略"""

    def __init__(self, instrument_id, time_frame, bollinger_lengths, filter_length, start_asset):
        try:
            # 策略启动时控制台输出提示信息
            print("{} {} 布林强盗突破策略已启动！".format(get_localtime(), instrument_id))   # 程序启动时打印提示信息
            config.loads("config.json")  # 载入配置文件
            # 初始化
            self.instrument_id = instrument_id  # 合约ID
            self.time_frame = time_frame    # k线周期
            self.exchange = OKEXFUTURES(config.access_key, config.secret_key, config.passphrase, self.instrument_id)  # 交易所
            self.market = MARKET(self.exchange, self.instrument_id, self.time_frame)    # 行情
            self.position = POSITION(self.exchange, self.instrument_id, self.time_frame)   # 持仓
            self.indicators = INDICATORS(self.exchange, self.instrument_id, self.time_frame)    # 指标
            # 在第一次运行程序时，将初始资金、总盈亏等数据保存至数据库中
            self.database = "回测"  # 数据库，回测时必须为"回测"
            self.datasheet = self.instrument_id.split("-")[0].lower() + "_" + time_frame    # 数据表
            if config.first_run == "true":
                storage.mysql_save_strategy_run_info(self.database, self.datasheet, get_localtime(),
                                                     "none", 0, 0, 0, 0, "none", 0, 0, 0, start_asset)
            # 读取数据库中保存的总资金数据
            self.total_asset = storage.read_mysql_datas(0, self.database, self.datasheet, "总资金", ">")[-1][-1]
            self.total_profit = storage.read_mysql_datas(0, self.database, self.datasheet, "总资金", ">")[-1][-2]  # 策略总盈亏
            # 策略参数
            self.contract_value = self.market.contract_value()  # 合约面值
            self.counter = 0  # 计数器
            self.bollinger_lengths = bollinger_lengths  # 布林通道参数
            self.filter_length = filter_length  # 过滤器参数
            self.out_day = self.bollinger_lengths + 1  # 自适应出场ma的初始值,设为51，因为策略启动时k线更新函数会起作用，其值会减去1
        except:
            logger.warning()

    def begin_trade(self, kline=None):
        try:    # 异常处理
            if self.indicators.CurrentBar(kline=kline) < self.bollinger_lengths:  # 如果k线数据不够长就返回
                return

            timestamp = ts_to_datetime_str(utctime_str_to_ts(kline[-1][0])) if kline else get_localtime()  # 非回测模式下时间戳就是当前本地时间

            if self.indicators.BarUpdate(kline=kline):
                self.counter = 0    # k线更新时还原计数器
                if self.out_day > 10:   # 计算MA的天数最小递减到10。如果达到10，则不再递减。
                    self.out_day -= 1   # 自适应出场ma的长度参数根据持仓周期递减，持有头寸的时间每多一天，计算MA的天数减1

            deviation = float(self.indicators.STDDEV(self.bollinger_lengths, nbdev=2, kline=kline)[-1])   # 标准差
            middleband = float(self.indicators.BOLL(self.bollinger_lengths, kline=kline)['middleband'][-1])  # 布林通道中轨
            upperband = float(middleband + deviation)  # 布林通道上轨
            lowerband = float(middleband - deviation)  # 布林通道下轨
            filter = float(self.market.close(-1, kline=kline) - self.market.close((self.filter_length * -1) - 1, kline=kline))  # 过滤器：当日收盘价减去30日前的收盘价
            ma = float(self.indicators.MA(self.out_day, kline=kline)[-1])     # 自适应移动出场平均线

            # 策略主体
            # 若k线数据足够长，且满足过滤条件，且当根k线最高价大于等于布林通道上轨，买入开多。
            # 开仓处也设置计数器过滤，是为了防止没有启用交易助手的情况下挂单未成交，仓位为零时当根k线一直满足开仓条件，会重复挂单。
            if self.indicators.CurrentBar(kline=kline) >= self.bollinger_lengths and filter > 0 and self.market.high(-1, kline=kline) > upperband  and self.counter < 1:
                if self.position.amount() == 0:     # 若当前无持仓
                    price = upperband   # 开多价格为布林通道上轨的值
                    amount = round(self.total_asset/upperband/self.contract_value)  # 合约张数取整
                    info = self.exchange.buy(price, amount)     # 买入开多，并将返回的信息赋值给变量info
                    push(info)  # 推送信息
                    storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp, "买入开多",
                                                         price, amount, amount * price * self.contract_value, price,
                                                         "long", amount, 0, self.total_profit,
                                                         self.total_asset)  # 将信息保存至数据库
                    self.counter += 1   # 此策略是在盘中开仓，而在回测时，每根bar只会运行一次，每根bar上的价格不分时间先后，故此处开仓后计数器加1，也就是当根k线不平仓
                                        # 因为实盘时每个ticker进来策略就会运行一次。注意回测和实盘策略运行机制的不同。
            # 开空
            if self.indicators.CurrentBar(kline=kline) >= self.bollinger_lengths and filter < 0 and self.market.low(-1, kline=kline) < lowerband and self.counter < 1:
                if self.position.amount() == 0:
                    price = lowerband
                    amount = round(self.total_asset/upperband/self.contract_value)
                    info = self.exchange.sellshort(price, amount)
                    push(info)
                    storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp, "卖出开空",
                                                         price, amount, amount * price * self.contract_value, price,
                                                         "short", amount, 0, self.total_profit, self.total_asset)
                    self.counter += 1
            # 如果当前持多，且当根k线最低价小于等于中轨值，触发保护性止损，就平多止损
                # 因为回测是一根k线上运行整个策略一次，所以要实现当根k线开仓后当根k线不平仓，需要将self.counter < 1的条件加在平仓的地方
            if self.position.direction() == "long" and self.market.low(-1, kline=kline) < middleband and self.counter < 1:
                profit = self.position.coverlong_profit(last=middleband)    # 此处计算平多利润时，传入最新价last为中轨值，也就是触发止损价格的那个值。
                self.total_profit += profit     # 计算经过本次盈亏后的总利润
                self.total_asset += profit      # 计算经过本次盈亏后的总资金
                price = middleband  # 平多价格为中轨值
                amount = self.position.amount()     # 平仓数量为当前持仓数量
                info = self.exchange.sell(price, amount)
                push(info)
                self.counter += 1
                storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp, "卖出止损",
                                                     price, amount, price * amount * self.contract_value,
                                                     0, "none", 0, profit, self.total_profit, self.total_asset)
            if self.position.direction() == "short" and self.market.high(-1, kline=kline) > middleband and self.counter < 1:
                profit = self.position.covershort_profit(last=middleband)
                self.total_profit += profit
                self.total_asset += profit
                price = middleband
                amount = self.position.amount()
                info = self.exchange.buytocover(price, amount)
                push(info)
                self.counter += 1
                storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp,
                                                     "买入止损", price, amount, amount * price * self.contract_value,
                                                     0, "none", 0, profit, self.total_profit, self.total_asset)
            # 平多
            if self.position.direction() == "long" and upperband > ma > self.market.low(-1, kline=kline) and self.counter < 1:
                profit = self.position.coverlong_profit(last=ma)
                self.total_profit += profit
                self.total_asset += profit
                price = ma  # 平仓价格为自适应出场均线的值
                amount = self.position.amount()
                info = self.exchange.sell(price, amount)
                push(info)
                self.counter += 1
                storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp, "卖出平多",
                                                     price, amount, price * amount * self.contract_value,
                                                     0, "none", 0, profit, self.total_profit, self.total_asset)
            # 平空
            if self.position.direction() == "short" and lowerband < ma < self.market.high(-1, kline=kline) and self.counter < 1:
                profit = self.position.covershort_profit(last=ma)
                self.total_profit += profit
                self.total_asset += profit
                price = ma
                amount = self.position.amount()
                info = self.exchange.buytocover(price, amount)
                push(info)
                self.counter += 1
                storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp,
                                                     "买入平空", price, amount, amount * price * self.contract_value,
                                                     0, "none", 0, profit, self.total_profit, self.total_asset)
        except:
            logger.error()

if __name__ == "__main__":

    instrument_id = "ETH-USDT-201225"
    time_frame = "1d"
    strategy = Strategy(instrument_id=instrument_id, time_frame=time_frame, bollinger_lengths=50, filter_length=30, start_asset=1000)   # 实例化策略类

    if config.backtest == "enabled":  # 回测模式
        print("正在回测，可能需要一段时间，请稍后...")
        start_time = get_cur_timestamp()
        records = []
        data = storage.read_purequant_server_datas(instrument_id.split("-")[0].lower() + "_" + time_frame)
        for k in data:
            records.append(k)
            strategy.begin_trade(kline=records)
        cost_time = get_cur_timestamp() - start_time
        print("回测用时{}秒，结果已保存至mysql数据库！".format(cost_time))
    else:  # 实盘模式
        while True:  # 循环运行begin_trade函数
            strategy.begin_trade()
