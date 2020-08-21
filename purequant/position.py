# -*- coding:utf-8 -*-

"""
持仓信息模块

Author: Gary-Hertel
Date:   2020/07/09
email: interstella.ranger2020@gmail.com
"""
from purequant.market import MARKET

class POSITION:

    def __init__(self, platform, instrument_id, time_frame):
        self.__platform = platform
        self.__instrument_id = instrument_id
        self.__time_frame = time_frame
        self.__market = MARKET(self.__platform, self.__instrument_id, self.__time_frame)

    def direction(self):
        """获取当前持仓方向"""
        result = self.__platform.get_position()['direction']
        return result

    def amount(self):
        """获取当前持仓数量"""
        result = self.__platform.get_position()['amount']
        return result

    def price(self):
        """获取当前的持仓价格"""
        result = self.__platform.get_position()['price']
        return result

    def coverlong_profit(self):
        """计算平多的单笔交易利润"""
        self.__value = self.__market.contract_value() # 合约面值
        result = (self.__market.last() - self.price()) * (self.amount() * self.__value)
        return result

    def covershort_profit(self):
        """计算平空的单笔交易利润"""
        self.__value = self.__market.contract_value() # 合约面值
        result = (self.price() - self.__market.last()) * (self.amount() * self.__value)
        return result