"""
双均线策略
此策略适用于OKEX的USDT合约
如需用于其他类型合约或现货，可自行修改
Author: Gary-Hertel
Date:   2020/08/21
email: interstella.ranger2020@gmail.com
"""

import time
from purequant.indicators import INDICATORS
from purequant.trade import OKEXFUTURES
from purequant.position import POSITION
from purequant.market import MARKET
from purequant.push import push
from purequant.storage import storage
from purequant.time import get_localtime, utctime_str_to_ts, ts_to_datetime_str
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
        # 在第一次运行程序时，将初始资金数据保存至数据库中
        self.database = "回测"    # 回测时必须为"回测"
        self.datasheet = self.instrument_id.split("-")[0].lower() + "_" + time_frame
        if config.first_run == "true":
            storage.mysql_save_strategy_run_info(self.database, self.datasheet, get_localtime(),
                                            "none", 0, 0, 0, 0, "none", 0, 0, 0, start_asset)
        # 读取数据库中保存的总资金数据
        self.total_asset = storage.read_mysql_datas(0, self.database, self.datasheet, "总资金", ">")[-1][-1]
        self.overprice_range = config.reissue_order     # 超价下单幅度
        self.counter = 0  # 计数器
        self.fast_length = fast_length  # 短周期均线长度
        self.slow_length = slow_length  # 长周期均线长度
        self.long_stop = long_stop   # 多单止损幅度
        self.short_stop = short_stop    # 空单止损幅度
        self.total_profit = 0
        self.contract_value = self.market.contract_value()  # 合约面值，每次获取需发起网络请求，故于此处声明变量，优化性能

    def begin_trade(self, kline=None):
        try:
            timestamp = ts_to_datetime_str(utctime_str_to_ts(kline[-1][0])) if kline else get_localtime()    # 非回测模式下时间戳就是当前本地时间
            # 计算策略信号
            if self.indicators.CurrentBar(kline=kline) < self.slow_length:  # 如果k线数据不够长就返回
                return
            ma = self.indicators.MA(self.fast_length, self.slow_length, kline=kline)
            fast_ma = ma[0]
            slow_ma = ma[1]
            cross_over = fast_ma[-2] >= slow_ma[-2] and fast_ma[-3] < slow_ma[-3]   # 不用当根k线上的ma来计算信号，防止信号闪烁
            cross_below = slow_ma[-2] >= fast_ma[-2] and slow_ma[-3] < fast_ma[-3]
            if self.indicators.BarUpdate(kline=kline):     # 如果k线更新，计数器归零
                self.counter = 0
            if self.counter < 1:
                # 按照策略信号开平仓
                if cross_over:     # 金叉时
                    if self.position.amount() == 0:     # 若当前无持仓，则买入开多并推送下单结果
                        price = self.market.open(-1, kline=kline) * (1 + self.overprice_range)  # 下单价格=此根k线收盘价*超价幅度
                        amount = round(self.total_asset / price / self.contract_value)   # 数量=总资金/价格/合约面值
                        info = self.exchange.buy(price, amount)
                        push(info)
                        storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp, "买入开多",
                                                        price, amount, amount*price*self.contract_value, price,
                                                        "long", amount, 0, self.total_profit, self.total_asset)     # 将信息保存至数据库
                    if self.position.direction() == 'short':    # 若当前持空头，先平空再开多
                        profit = self.position.covershort_profit(last=self.market.close(-1, kline=kline))  # 在平空前先计算逻辑盈亏，当前最新成交价为收盘价close
                        self.total_profit += profit
                        self.total_asset += profit  # 计算此次盈亏后的总资金
                        cover_short_price = self.market.close(-1, kline=kline) * (1 - self.overprice_range)
                        cover_short_amount = self.position.amount()
                        open_long_price = self.market.close(-1, kline=kline) * (1 + self.overprice_range)
                        open_long_amount = round(self.total_asset / self.market.close(-1, kline=kline) / self.contract_value)
                        info = self.exchange.BUY(cover_short_price, cover_short_amount, open_long_price, open_long_amount)
                        push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                        storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp, "平空开多",
                                                        open_long_price, open_long_amount, open_long_amount * open_long_price * self.contract_value,
                                                        open_long_price, "long", open_long_amount, profit, self.total_profit, self.total_asset)
                if cross_below:     # 死叉时
                    if self.position.amount() == 0:
                        price = self.market.close(-1, kline=kline) * (1 - self.overprice_range)
                        amount = round(self.total_asset / price / self.contract_value)
                        info = self.exchange.sellshort(price, amount)
                        push(info)
                        storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp, "卖出开空",
                                                    price, amount, amount * price * self.contract_value, price,
                                                    "short", amount, 0, self.total_profit, self.total_asset)
                    if self.position.direction() == 'long':
                        profit = self.position.coverlong_profit(last=self.market.close(-1, kline=kline))     # 在平多前先计算逻辑盈亏，当前最新成交价为收盘价close
                        self.total_profit += profit
                        self.total_asset += profit
                        cover_long_price = self.market.close(-1, kline=kline) * (1 + self.overprice_range)
                        cover_long_amount = self.position.amount()
                        open_short_price = self.market.close(-1, kline=kline) * (1 - self.overprice_range)
                        open_short_amount = round(self.total_asset / self.market.close(-1, kline=kline) / self.contract_value)
                        info = self.exchange.SELL(cover_long_price,
                                                  cover_long_amount,
                                                  open_short_price,
                                                  open_short_amount)
                        push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                        storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp, "平多开空",
                                                        open_short_price, open_short_amount,
                                                        open_short_price * open_short_amount * self.contract_value,
                                                        open_short_price, "short", open_short_amount, profit, self.total_profit,
                                                        self.total_asset)
                # 止损
                if self.position.amount() > 0:
                    if self.position.direction() == 'long' and self.market.low(-1, kline=kline) <= self.position.price() * self.long_stop:    # 多单止损
                        profit = self.position.coverlong_profit(last=self.position.price() * self.long_stop)    # 在平多前先计算逻辑盈亏，当前最新成交价为止损价
                        self.total_profit += profit
                        self.total_asset += profit
                        price = self.position.price() * self.long_stop * (1 - self.overprice_range)
                        amount = self.position.amount()
                        info = self.exchange.sell(price, amount)
                        push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                        storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp,
                                                        "卖出止损", price, amount,
                                                        amount * price * self.contract_value,
                                                        0, "none", 0, profit, self.total_profit,
                                                        self.total_asset)
                        self.counter += 1   # 计数器加1，控制此根k线上不再下单

                    if self.position.direction() == 'short' and self.market.high(-1, kline=kline) >= self.position.price() * self.short_stop:  # 空头止损
                        profit = self.position.covershort_profit(last=self.position.price() * self.short_stop)
                        self.total_profit += profit
                        self.total_asset += profit
                        price = self.position.price() * self.short_stop * (1 + self.overprice_range)
                        amount = self.position.amount()
                        info = self.exchange.buytocover(price, amount)
                        push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                        storage.mysql_save_strategy_run_info(self.database, self.datasheet, timestamp,
                                                        "买入止损", price, amount,
                                                        amount * price * self.contract_value,
                                                        0, "none", 0, profit, self.total_profit,
                                                        self.total_asset)
                        self.counter += 1
        except Exception as e:
            print(e)   # 输出异常日志信息

if __name__ == "__main__":

    # 实例化策略类
    instrument_id = "ETH-USDT-201225"
    time_frame = "1d"
    strategy = Strategy(instrument_id=instrument_id, time_frame=time_frame, fast_length=60, slow_length=90, long_stop=0.9, short_stop=1.1, start_asset=1000)

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