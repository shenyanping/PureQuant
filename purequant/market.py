# -*- coding:utf-8 -*-

"""
市场行情模块

Author: Gary-Hertel
Date:   2020/07/11
email: interstella.ranger2020@gmail.com
"""

from purequant.config import config

class MARKET:

    def __init__(self, platform, instrument_id, time_frame):
        self.__platform = platform
        self.__instrument_id = instrument_id
        self.__time_frame = time_frame

    def last(self):
        """获取交易对的最新成交价"""
        result = float(self.__platform.get_ticker()['last'])
        return result

    def open(self, param, kline=None):
        """
        获取交易对当前k线上的开盘价
        :param param: 参数，如-1是获取当根k线上的开盘价，-2是上一根k线上的开盘价
        :param kline: 回测时传入指定k线数据
        :return:
        """
        if config.backtest == "enabled":    # 回测模式
            return float(kline[param][1])
        else:   # 实盘模式
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
            result = float((records)[param][1])
            return result

    def high(self, param, kline=None):
        """
        获取交易对当前k线上的最高价
        :param param: 参数，如-1是获取当根k线上的最高价，-2是上一根k线上的最高价
        :param kline: 回测时传入指定k线数据
        :return:
        """
        if config.backtest == "enabled":
            return float(kline[param][2])
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
            result = float((records)[param][2])
            return result

    def low(self, param, kline=None):
        """
        获取交易对当前k线上的最低价
        :param param: 参数，如-1是获取当根k线上的最低价，-2是上一根k线上的最低价
        :param kline: 回测时传入指定k线数据
        :return:
        """
        if config.backtest == "enabled":
            return float(kline[param][3])
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
            result = float((records)[param][3])
            return result

    def close(self, param, kline=None):
        """
        获取交易对当前k线上的收盘价
        :param param: 参数，如-1是获取当根k线上的收盘价，-2是上一根k线上的收盘价
        :param kline: 回测时传入指定k线数据
        :return:
        """
        if config.backtest == "enabled":
            return float(kline[param][4])
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
            result = float((records)[param][4])
            return result

    def contract_value(self):
        """获取合约面值"""
        contract_value = float(self.__platform.get_contract_value()['{}'.format(self.__instrument_id)])
        return contract_value