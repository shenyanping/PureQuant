# -*- coding:utf-8 -*-

"""
持仓信息模块

Author: Gary-Hertel
Date:   2020/07/09
email: interstella.ranger2020@gmail.com
"""
from purequant.market import MARKET
from purequant.config import config
from purequant.storage import storage

class POSITION:

    def __init__(self, platform, instrument_id, time_frame):
        self.__platform = platform
        self.__instrument_id = instrument_id
        self.__time_frame = time_frame
        self.__market = MARKET(self.__platform, self.__instrument_id, self.__time_frame)

    def direction(self):
        """获取当前持仓方向"""
        if config.backtest != "enabled":    # 实盘模式下实时获取账户实际持仓方向
            result = self.__platform.get_position()['direction']
            return result
        else:   # 回测模式下从数据库中读取持仓方向
            result = storage.read_mysql_datas(0, "回测", self.__instrument_id.split("-")[0].lower() + "_" + self.__time_frame, "总资金", ">")[-1][6]
            return result

    def amount(self):
        """获取当前持仓数量"""
        if config.backtest != "enabled":    # 实盘模式下实时获取账户实际持仓数量
            result = self.__platform.get_position()['amount']
            return result
        else:   # 回测模式下从数据库中读取持仓数量
            result = storage.read_mysql_datas(0, "回测", self.__instrument_id.split("-")[0].lower() + "_" + self.__time_frame, "总资金", ">")[-1][7]
            return result

    def price(self):
        """获取当前的持仓价格"""
        if config.backtest != "enabled":    # 实盘模式下实时获取账户实际持仓价格
            result = self.__platform.get_position()['price']
            return result
        else:   # 回测模式下从数据库中读取持仓价格
            result = storage.read_mysql_datas(0, "回测", self.__instrument_id.split("-")[0].lower() + "_" + self.__time_frame, "总资金", ">")[-1][5]
            return result


    def coverlong_profit(self, market_type=None, last=None):
        """
        计算平多的单笔交易利润
        :param market_type: 默认是USDT合约，可填"usd_contract"（币本位合约）或者"spot"(现货)
        :param last: 回测模式可以传入最新成交价
        :return: 返回计算出的利润结果
        """
        if market_type == "usd_contract":    # 如果是币本位合约
            self.__value = self.__market.contract_value()  # 合约面值
            if config.backtest == "enabled" and last is not None:    # 如果是回测模式且传入了last最新成交价
                result = (last - self.price()) * ((self.amount() * self.__value) / self.price())    # 利润=价差*（合约张数*面值）/持仓价格
            else:   # 如果是实盘模式
                result = (self.__market.last() - self.price()) * ((self.amount() * self.__value) / self.price())  # 利润=价差*（合约张数*面值）/持仓价格

        elif market_type == "spot":    # 如果是现货
            if config.backtest == "enabled" and last is not None:    # 如果是回测模式且传入了last最新成交价
                result = (last - self.price()) * self.amount()    # 利润=价差*持仓数量
            else:   # 如果是实盘模式
                result = (self.__market.last() - self.price()) * self.amount()

        else:   # 默认是usdt合约
            self.__value = self.__market.contract_value()  # 合约面值
            if config.backtest == "enabled" and last is not None:    # 如果是回测模式且传入了last最新成交价
                result = (last - self.price()) * (self.amount() * self.__value) # 利润=价差*（持仓数量*面值）
            else:   # 如果是实盘模式
                result = (self.__market.last() - self.price()) * (self.amount() * self.__value)
        return result

    def covershort_profit(self, market_type=None, last=None):
        """
        计算平空的单笔交易利润
        :param market_type: 默认是USDT合约，可填"usd_contract"（币本位合约）或者"spot"(现货)
        :param last: 回测模式可以传入最新成交价
        :return: 返回计算出的利润结果
        """
        if market_type == "usd_contract":  # 如果是币本位合约
            self.__value = self.__market.contract_value()  # 合约面值
            if config.backtest == "enabled" and last is not None:    # 如果是回测模式且传入了last最新成交价
                result = (self.price() - last) * ((self.amount() * self.__value) / self.price())  # 利润=价差*（合约张数*面值）/持仓价格
            else:  # 如果是实盘模式
                result = (self.price() - self.__market.last()) * (
                            (self.amount() * self.__value) / self.price())  # 利润=价差*（合约张数*面值）/持仓价格

        elif market_type == "spot":  # 如果是现货
            if config.backtest == "enabled" and last is not None:    # 如果是回测模式且传入了last最新成交价
                result = (self.price() - last) * self.amount()  # 利润=价差*持仓数量
            else: # 如果是实盘模式
                result = (self.price() - self.__market.last()) * self.amount()

        else:  # 默认是usdt合约
            self.__value = self.__market.contract_value()  # 合约面值
            if config.backtest == "enabled" and last is not None:    # 如果是回测模式且传入了last最新成交价
                result = (self.price() - last) * (self.amount() * self.__value)  # 利润=价差*（持仓数量*面值）
            else: # 如果是实盘模式
                result = (self.price() - self.__market.last()) * (self.amount() * self.__value)
        return result

