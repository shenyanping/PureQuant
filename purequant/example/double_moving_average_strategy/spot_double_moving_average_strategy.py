"""
双均线策略
此策略适用于OKEX的现货
如需用于其他类型合约或现货，可自行修改
Author: Gary-Hertel
Date:   2020/09/01
email: interstella.ranger2020@gmail.com
"""

import time
from purequant.indicators import INDICATORS
from purequant.trade import OKEXSPOT
from purequant.position import POSITION
from purequant.market import MARKET
from purequant.logger import LOGGER
from purequant.push import push
from purequant.storage import storage
from purequant.time import get_localtime, utctime_str_to_ts, ts_to_datetime_str
from purequant.config import config

class Strategy:

    def __init__(self, instrument_id, time_frame, fast_length, slow_length, long_stop, short_stop, start_asset, precision):
        try:
            print("{} {} 双均线多空策略已启动！".format(get_localtime(), instrument_id))   # 程序启动时打印提示信息
            config.loads('config.json')  # 载入配置文件
            self.instrument_id = instrument_id  # 合约ID
            self.time_frame = time_frame  # k线周期
            self.precision = precision  # 精度，即币对的最小交易数量
            self.exchange = OKEXSPOT(config.access_key, config.secret_key, config.passphrase, self.instrument_id)  # 初始化交易所
            self.position = POSITION(self.exchange, self.instrument_id, self.time_frame)  # 初始化potion
            self.market = MARKET(self.exchange, self.instrument_id, self.time_frame)  # 初始化market
            self.indicators = INDICATORS(self.exchange, self.instrument_id, self.time_frame)    # 初始化indicators
            self.logger = LOGGER('config.json')     # 初始化logger
            # 在第一次运行程序时，将初始资金数据保存至数据库中
            self.database = "回测"    # 回测时必须为"回测"
            self.datasheet = self.instrument_id.split("-")[0].lower() + "_" + time_frame
            if config.first_run == "true":
                storage.mysql_save_strategy_run_info(self.database, self.datasheet, get_localtime(),
                                                "none", 0, 0, 0, 0, "none", 0, 0, 0, start_asset)
            # 读取数据库中保存的总资金数据
            self.total_asset = storage.read_mysql_datas(0, self.database, self.datasheet, "总资金", ">")[-1][-1]
            self.total_profit = storage.read_mysql_datas(0, self.database, self.datasheet, "总资金", ">")[-1][-2]  # 策略总盈亏
            self.counter = 0  # 计数器
            self.fast_length = fast_length  # 短周期均线长度
            self.slow_length = slow_length  # 长周期均线长度
            self.long_stop = long_stop   # 多单止损幅度
            self.short_stop = short_stop    # 空单止损幅度
            self.hold_price = 0     # 注意：okex的现货没有获取持仓均价的接口，故需实盘时需要手动记录入场价格。此种写法对于不同的交易所是通用的。
                                    # 此种写法，若策略重启，持仓价格会回归0
        except Exception as msg:
            self.logger.warning(msg)

    def begin_trade(self, kline=None):
        try:
            if self.indicators.CurrentBar(kline=kline) < self.slow_length:  # 如果k线数据不够长就返回
                return
            timestamp = ts_to_datetime_str(utctime_str_to_ts(kline[-1][0])) if kline else get_localtime()    # 非回测模式下时间戳就是当前本地时间
            # 计算策略信号
            ma = self.indicators.MA(self.fast_length, self.slow_length, kline=kline)
            fast_ma = ma[0]
            slow_ma = ma[1]
            cross_over = fast_ma[-2] >= slow_ma[-2] and fast_ma[-3] < slow_ma[-3]   # 不用当根k线上的ma来计算信号，防止信号闪烁
            cross_below = slow_ma[-2] >= fast_ma[-2] and slow_ma[-3] < fast_ma[-3]
            if self.indicators.BarUpdate(kline=kline):     # 如果k线更新，计数器归零
                self.counter = 0
            if self.counter < 1:
                # 按照策略信号开平仓
                if cross_over and round(self.position.amount()) < self.precision:     # 金叉时，若当前无持仓，则买入开多并推送下单结果。0.1这个数值根据每个币对的最小交易数量决定
                    price = float(self.market.open(-1, kline=kline))  # 下单价格=此根k线开盘价
                    self.hold_price = price  # 记录开仓价格
                    amount = float(self.total_asset / price)  # 数量=总资金/价格
                    info = self.exchange.buy(price, amount)
                    push(info)
                    storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp, "买入开多",
                                                    price, amount, amount * price, price, "long", amount,
                                                    0, self.total_profit, self.total_asset)     # 将信息保存至数据库
                if cross_below and round(self.position.amount(), 1) >= self.precision:     # 死叉时，如果当前持多就卖出平多。当前持仓数量根据币对的最小交易数量取小数
                    price = float(self.market.open(-1, kline=kline))
                    amount = float(self.position.amount())
                    profit = (price - self.hold_price) * amount  # 计算逻辑盈亏
                    self.total_profit += profit
                    self.total_asset += profit
                    info = self.exchange.sell(price, amount)
                    push(info)
                    self.hold_price = 0  # 平多后记录持仓价格为0
                    storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp, "卖出平多",
                                                price, amount, amount * price, 0, "none", 0,
                                                profit, self.total_profit, self.total_asset)
                # 如果当前持多且最低价小于等于持仓均价*止损幅度，触发止损，卖出平多止损
                if round(self.position.amount(), 1) >= self.precision and self.market.low(-1, kline=kline) <= self.hold_price * self.long_stop:
                    price = float(self.hold_price * self.long_stop)
                    amount = float(self.position.amount())
                    profit = (price - self.hold_price) * amount  # 计算逻辑盈亏
                    self.total_profit += profit
                    self.total_asset += profit
                    info = self.exchange.sell(price, amount)
                    push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                    self.hold_price = 0  # 平多后记录持仓价格为0
                    storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp,
                                                    "卖出止损", price, amount, amount * price, 0, "none", 0,
                                                    profit, self.total_profit, self.total_asset)
                    self.counter += 1   # 计数器加1，控制此根k线上不再下单
        except Exception as e:
            self.logger.info(e)   # 输出异常日志信息，当前路径下需建立logger文件夹

if __name__ == "__main__":

    # 实例化策略类
    instrument_id = "EOS-USDT"
    time_frame = "1m"
    strategy = Strategy(instrument_id=instrument_id, time_frame=time_frame,
                        fast_length=5, slow_length=10, long_stop=0.98, short_stop=1.02,
                        start_asset=4, precision=0.1)

    if config.backtest == "enabled":    # 回测模式
        print("正在回测，可能需要一段时间，请稍后...")
        start_time = time.time()
        records = []
        data = storage.read_purequant_server_datas(instrument_id.split("-")[0].lower() + "_" + time_frame)
        for k in data:
            records.append(k)
            strategy.begin_trade(kline=records)
        cost_time = time.time() - start_time
        print("回测用时{}秒，结果已保存至mysql数据库！".format(cost_time))
    else:   # 实盘模式
        while True:     # 循环运行begin_trade函数
            strategy.begin_trade()
            time.sleep(3)  # 休眠几秒 ，防止请求频率超限