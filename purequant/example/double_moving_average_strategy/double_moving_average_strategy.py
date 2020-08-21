"""
双均线策略
此策略适用于OKEX的USDT合约
如需用于其他类型合约或现货，可自行修改

Author: Gary-Hertel
Date:   2020/08/21
email: interstella.ranger2020@gmail.com
"""


from purequant.indicators import INDICATORS
from purequant.trade import OKEXFUTURES
from purequant.position import POSITION
from purequant.market import MARKET
from purequant.logger import LOGGER
from purequant.push import push
from purequant.storage import storage
from purequant.time import get_localtime
from purequant.config import config


class Strategy:

    def __init__(self, instrument_id, time_frame, fast_length, slow_length, long_stop, short_stop, start_asset):
        print("{} {} 双均线多空策略已启动！".format(get_localtime(), instrument_id))   # 程序启动时打印提示信息
        config.loads('config.json')  # 载入配置文件
        self.instrument_id = instrument_id  # 合约ID
        self.time_frame = time_frame  # k线周期
        self.exchange = OKEXFUTURES(config.access_key, config.secret_key, config.passphrase, self.instrument_id)  # 初始化交易所
        self.position = POSITION(self.exchange, self.instrument_id, self.time_frame)  # 初始化potion
        self.market = MARKET(self.exchange, self.instrument_id, self.time_frame)  # 初始化market
        self.indicators = INDICATORS(self.exchange, self.instrument_id, self.time_frame)    # 初始化indicators
        self.logger = LOGGER('config.json')     # 初始化logger，如将日志保存至文件，当前路径下需建立logger文件夹
        # 在第一次运行程序时，将初始资金数据保存至数据库中，数据库可选mysql或者mongodb
        if config.first_run == "true":
            storage.save_asset_and_profit("asset", (self.instrument_id[0:3]).lower(), 0, start_asset)
            # storage.mongodb_save({"时间": get_localtime(), "profit": 0, "asset": start_asset}, 'asset', self.instrument_id[0:3])
        # 读取数据库中保存的总资金数据
        self.total_asset = storage.read_mysql_datas(0, "asset", (self.instrument_id[0:3]).lower(), "asset", ">")[-1][-1]
        # self.total_asset = storage.mongodb_read_data('asset', self.instrument_id[0:3])[-1][0]['asset']
        self.overprice_range = config.reissue_order     # 超价下单幅度
        self.counter = 0  # 计数器
        self.fast_length = fast_length  # 短周期均线长度
        self.slow_length = slow_length  # 长周期均线长度
        self.long_stop = long_stop   # 多单止损幅度
        self.short_stop = short_stop    # 空单止损幅度


    def begin_trade(self):
        try:
            # 计算策略信号
            ma = self.indicators.MA(self.fast_length, self.slow_length)
            fast_ma = ma[0]
            slow_ma = ma[1]
            cross_over = fast_ma[-2] >= slow_ma[-2] and fast_ma[-3] < slow_ma[-3]
            cross_below = slow_ma[-2] >= fast_ma[-2] and slow_ma[-3] < fast_ma[-3]
            if self.indicators.BarUpdate():     # 如果k线更新，计数器归零
                self.counter = 0
            if self.counter < 1:
                # 按照策略信号开平仓
                if cross_over:     # 金叉时
                    if self.position.amount() == 0:     # 若当前无持仓，则买入开多并推送下单结果
                        info = self.exchange.buy(self.market.last() * (1 + self.overprice_range), round(
                            self.total_asset / self.market.last() / self.market.contract_value()))
                        push(info)
                    if self.position.direction() == 'short':    # 若当前持空头，先平空再开多
                        profit = self.position.covershort_profit()  # 在平空前先计算逻辑盈亏
                        self.total_asset += profit  # 计算此次盈亏后的总资金
                        # 将此次盈亏及变化后的总资金信息存入mysql或者mongodb数据库中
                        storage.save_asset_and_profit("asset", (self.instrument_id[0:3]).lower(), profit, self.total_asset)
                        # storage.mongodb_save({"时间": get_localtime(), "profit": profit, "asset": self.total_asset}, 'asset', self.instrument_id[0:3])
                        info = self.exchange.BUY(self.market.last() * (1 - self.overprice_range),
                                                 self.position.amount(),
                                                 self.market.last() * (1 + self.overprice_range), round(
                                self.total_asset / self.market.last() / self.market.contract_value()))
                        push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                if cross_below:     # 死叉时
                    if self.position.amount() == 0:
                        info = self.exchange.sellshort(self.market.last() * (1 - self.overprice_range), round(
                            self.total_asset / self.market.last() / self.market.contract_value()))
                        push(info)
                    if self.position.direction() == 'long':
                        profit = self.position.coverlong_profit()
                        self.total_asset += profit
                        storage.save_asset_and_profit("asset", (self.instrument_id[0:3]).lower(), profit, self.total_asset)
                        # storage.mongodb_save({"时间": get_localtime(), "profit": profit, "asset": self.total_asset}, 'asset', self.instrument_id[0:3])
                        info = self.exchange.SELL(self.market.last() * (1 + self.overprice_range),
                                                  self.position.amount(),
                                                  self.market.last() * (1 - self.overprice_range), round(
                                self.total_asset / self.market.last() / self.market.contract_value()))
                        push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                # 止损
                if self.position.amount() > 0:
                    if self.position.direction() == 'long' and self.market.last() <= self.position.price() * self.long_stop:    # 多单止损
                        profit = self.position.coverlong_profit()
                        self.total_asset += profit
                        storage.save_asset_and_profit("asset", (self.instrument_id[0:3]).lower(), profit, self.total_asset)
                        # storage.mongodb_save({"时间": get_localtime(), "profit": profit, "asset": self.total_asset}, 'asset', self.instrument_id[0:3])
                        info = self.exchange.sell(self.market.last() * (1 - self.overprice_range),
                                                  self.position.amount())
                        push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                        storage.mongodb_save({"strategy_direction": "none", "strategy_amount": 0},
                                             "position", self.instrument_id[0:3])
                        self.counter += 1   # 计数器加1，控制此根k线上不再下单

                    if self.position.direction() == 'short' and self.market.last() >= self.position.price() * self.short_stop:  # 空头止损
                        profit = self.position.covershort_profit()
                        self.total_asset += profit
                        storage.save_asset_and_profit("asset", (self.instrument_id[0:3]).lower(), profit, self.total_asset)
                        # storage.mongodb_save({"时间": get_localtime(), "profit": profit, "asset": self.total_asset}, 'asset', self.instrument_id[0:3])
                        info = self.exchange.buytocover(self.market.last() * (1 + self.overprice_range),
                                                        self.position.amount())
                        push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                        self.counter += 1
        except Exception as e:
            self.logger.debug(str(e))   # 输出异常日志信息


if __name__ == "__main__":
    strategy = Strategy("TRX-USDT-201225", time_frame="1m", fast_length=5, slow_length=10, long_stop=0.98, short_stop=1.02, start_asset=20)   # 实例化策略类
    while True:     # 循环运行begin_trade函数
        strategy.begin_trade()