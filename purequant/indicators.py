import numpy as np
import talib
from purequant import time
from purequant.config import config

class INDICATORS:

    def __init__(self, platform, instrument_id, time_frame):
        self.__platform = platform
        self.__instrument_id = instrument_id
        self.__time_frame = time_frame
        self.__last_time_stamp = 0

    def ATR(self,length, kline=None):
        """
        指数移动平均线
        :param length: 长度参数，如14获取的是14周期上的ATR值
        :param kline:回测时传入指定k线数据
        :return:返回一个一维数组
        """
        if config.backtest == "enabled":    # 如果是回测模式传入了指定的k线数据
            records = kline
        else:   # 实盘模式下从交易所获取k线数据
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()   # 将k线数据倒序排列
        kline_length = len(records)     # 计算k线数据的长度
        high_array = np.zeros(kline_length)     # 创建为零的数组
        low_array = np.zeros(kline_length)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            high_array[t] = item[2]
            low_array[t] = item[3]
            close_array[t] = item[4]
            t += 1
        result = talib.ATR(high_array, low_array, close_array, timeperiod=length)
        return result


    def BOLL(self, length, kline=None):
        """
        布林指标
        :param length:长度参数
        :param kline:回测时传入指定k线数据
        :return: 返回一个字典 {"upperband": 上轨数组， "middleband": 中轨数组， "lowerband": 下轨数组}
        """
        if config.backtest == "enabled":    # 如果是回测模式传入了指定的k线数据
            records = kline
        else:  # 实盘模式下从交易所获取k线数据
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            close_array[t] = item[4]
            t += 1
        result = (talib.BBANDS(close_array, timeperiod=length, nbdevup=2, nbdevdn=2, matype=0))
        upperband = result[0]
        middleband = result[1]
        lowerband = result[2]
        dict = {"upperband": upperband, "middleband": middleband, "lowerband": lowerband}
        return dict

    def BarUpdate(self, kline=None):
        """
        判断K线是否更新
        :param kline: 回测时传入指定k线数据
        :return: k线更新，返回True；否则返回False
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
        kline_length = len(records)
        current_timestamp = time.utctime_str_to_ts(records[kline_length - 1][0])
        if current_timestamp != self.__last_time_stamp:  # 如果当前时间戳不等于lastTime，说明k线更新
            if current_timestamp < self.__last_time_stamp:
                return
            else:
                self.__last_time_stamp = current_timestamp
                return True
        else:
            return False

    def CurrentBar(self, kline=None):
        """
        获取k线数据的长度
        :param kline: 回测时传入指定k线数据
        :return: 返回一个整型数字
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
        kline_length = len(records)
        return kline_length

    def HIGHEST(self, length, kline=None):
        """
        周期最高价
        :param length: 长度参数
        :param kline: 回测时传入指定k线数据
        :return:返回一个一维数组
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        high_array = np.zeros(kline_length)
        t = 0
        for item in records:
            high_array[t] = item[2]
            t += 1
        result = (talib.MAX(high_array, length))
        return result

    def MA(self, length, *args, kline=None):
        """
        移动平均线(简单移动平均)
        :param length:长度参数，如20获取的是20周期的移动平均
        :param args:不定长参数，可传入多个值计算
        :param kline:回测时传入指定k线数据
        :return:返回一个一维数组
        """
        if config.backtest == "enabled":    # 如果是回测模式传入了指定的k线数据
            records = kline
        else:   # 实盘模式下从交易所获取k线数据
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            close_array[t] = item[4]
            t += 1
        if len(args) < 1:  # 如果无别的参数
            result = talib.SMA(close_array, length)
        else:   # 如果传入多个参数
            result = [talib.SMA(close_array, length)]
            for x in args:
                result.append(talib.SMA(close_array, x))
        return result

    def MACD(self, fastperiod, slowperiod, signalperiod, kline=None):
        """
        计算MACD
        :param fastperiod: 参数1
        :param slowperiod: 参数2
        :param signalperiod: 参数3
        :param kline: 回测时传入指定k线数据
        :return: 返回一个字典 {'DIF': DIF数组, 'DEA': DEA数组, 'MACD': MACD数组}
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            close_array[t] = item[4]
            t += 1
        result = (talib.MACD(close_array, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod))
        DIF = result[0]
        DEA = result[1]
        MACD = result[2] * 2
        dict = {'DIF': DIF, 'DEA': DEA, 'MACD': MACD}
        return dict

    def EMA(self, length, *args, kline=None):
        """
        指数移动平均线
        :param length: 长度参数
        :param args: 不定长参数，可传入多个值计算
        :param kline: 回测时传入指定k线数据
        :return: 返回一个一维数组
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            close_array[t] = item[4]
            t += 1
        if len(args) < 1:  # 如果无别的参数
            result = talib.EMA(close_array, length)
        else:
            result = [talib.EMA(close_array, length)]
            for x in args:
                result.append(talib.EMA(close_array, x))
        return result

    def KAMA(self, length, *args, kline=None):
        """
        适应性移动平均线
        :param length: 长度参数
        :param args: 不定长参数，可传入多个值计算
        :param kline: 回测时传入指定k线数据
        :return: 返回一个一维数组
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            close_array[t] = item[4]
            t += 1
        if len(args) < 1:  # 如果无别的参数
            result = talib.KAMA(close_array, length)
        else:
            result = [talib.KAMA(close_array, length)]
            for x in args:
                result.append(talib.KAMA(close_array, x))
        return result

    def KDJ(self, fastk_period, slowk_period, slowd_period, kline=None):
        """
        计算k值和d值
        :param fastk_period: 参数1
        :param slowk_period: 参数2
        :param slowd_period: 参数3
        :param kline: 回测时传入指定k线数据
        :return: 返回一个字典，{'k': k值数组， 'd': d值数组}
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        high_array = np.zeros(kline_length)
        low_array = np.zeros(kline_length)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            high_array[t1] = item[2]
            low_array[t2] = item[3]
            close_array[t3] = item[4]
            t += 1
        result = (talib.STOCH(high_array, low_array, close_array, fastk_period=fastk_period,
                                                                slowk_period=slowk_period,
                                                                slowk_matype=0,
                                                                slowd_period=slowd_period,
                                                                slowd_matype=0))
        slowk = result[0]
        slowd = result[1]
        dict = {'k': slowk, 'd': slowd}
        return dict

    def LOWEST(self, length, kline=None):
        """
        周期最低价
        :param length: 长度参数
        :param kline: 回测时传入指定k线数据
        :return: 返回一个一维数组
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        low_array = np.zeros(kline_length)
        t = 0
        for item in records:
            low_array[t] = item[3]
            t += 1
        result = (talib.MIN(low_array, length))
        return result

    def OBV(self, kline=None):
        """
        OBV
        :param kline: 回测时传入指定k线数据
        :return: 返回一个一维数组
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            close_array[t] = item[4]
            t += 1
        result = (talib.OBV(close_array, self.VOLUME()))
        return result

    def RSI(self, length, kline=None):
        """
        RSI
        :param length: 长度参数
        :param kline: 回测时传入指定k线数据
        :return:返回一个一维数组
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            close_array[t] = item[4]
            t += 1
        result = (talib.RSI(close_array, timeperiod=length))
        return result

    def ROC(self, length, kline=None):
        """
        变动率指标
        :param length:长度参数
        :param kline:回测时传入指定k线数据
        :return:返回一个一维数组
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            close_array[t] = item[4]
            t += 1
        result = (talib.ROC(close_array, timeperiod=length))
        return result

    def STOCHRSI(self, timeperiod, fastk_period, fastd_period, kline=None):
        """
        计算STOCHRSI
        :param timeperiod: 参数1
        :param fastk_period:参数2
        :param fastd_period:参数3
        :param kline:回测时传入指定k线数据
        :return: 返回一个字典  {'STOCHRSI': STOCHRSI数组, 'fastk': fastk数组}
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            close_array[t] = item[4]
            t += 1
        result = (talib.STOCHRSI(close_array, timeperiod=timeperiod, fastk_period=fastk_period, fastd_period=fastd_period, fastd_matype=0))
        STOCHRSI = result[1]
        fastk = talib.MA(STOCHRSI, 3)
        dict = {'stochrsi': STOCHRSI, 'fastk': fastk}
        return dict

    def SAR(self, kline=None):
        """
        抛物线指标
        :param kline:回测时传入指定k线数据
        :return:返回一个一维数组
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        high_array = np.zeros(kline_length)
        low_array = np.zeros(kline_length)
        t = 0
        for item in records:
            high_array[t1] = item[2]
            low_array[t2] = item[3]
            t += 1
        result = (talib.SAR(high_array, low_array, acceleration=0.02, maximum=0.2))
        return result

    def STDDEV(self, length, nbdev=None, kline=None):
        """
        求标准差
        :param length:周期参数
        :param nbdev:求估计方差的类型，1 – 求总体方差，2 – 求样本方差
        :param kline:回测时传入指定k线数据
        :return:返回一个一维数组
        """
        nbdev=1 or nbdev
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            close_array[t] = item[4]
            t += 1
        result = (talib.STDDEV(close_array, timeperiod=length, nbdev=1))
        return result


    def TRIX(self, length, kline=None):
        """
        三重指数平滑平均线
        :param length:长度参数
        :param kline:回测时传入指定k线数据
        :return:返回一个一维数组
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
            records.reverse()
        kline_length = len(records)
        close_array = np.zeros(kline_length)
        t = 0
        for item in records:
            close_array[t] = item[4]
            t += 1
        result = (talib.TRIX(close_array, timeperiod=length))
        return result

    def VOLUME(self, kline=None):
        """
        成交量
        :param kline: 回测时传入指定k线数据
        :return: 返回一个一维数组
        """
        if config.backtest == "enabled":
            records = kline
        else:
            records = self.__platform.get_kline(self.__time_frame)
        length = len(records)
        records.reverse()
        t = 0
        volume_array = np.zeros(length)
        for item in records:
            volume_array[t] = item[5]
            t += 1
        return volume_array




