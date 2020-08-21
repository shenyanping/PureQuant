# -*- coding:utf-8 -*-

"""
策略信号可视化

Author: Gary-Hertel
Date:   2020/08/17
email: interstella.ranger2020@gmail.com
"""


import finplot as fplt
import pandas as pd
import numpy as np
from purequant.indicators import INDICATORS
from purequant.market import MARKET

class SIGNALIZE:

    def __init__(self, platform, symbol, time_frame):

        self.__platform = platform
        self.__symbol = symbol
        self.__time_frame = time_frame
        self.__market = MARKET(self.__platform, self.__symbol, self.__time_frame)

        # pull some data
        self.__indicators = INDICATORS(self.__platform, self.__symbol, self.__time_frame)
        self.__kline = platform.get_kline(self.__time_frame)
        self.__kline.reverse()

        # format it in pandas
        try:    # dataframe有7列的情况
            self.__df = pd.DataFrame(self.__kline, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'currency_volume'])
            self.__df = self.__df.astype({'time': 'datetime64[ns]', 'open': 'float64', 'close': 'float64',
                                          'high': 'float64', 'low': 'float64', 'volume': 'float64',
                                          'currency_volume': 'float64'})
        except:   # dataframe只有6列的情况，如okex的现货k线数据
            self.__df = pd.DataFrame(self.__kline,
                                     columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            self.__df = self.__df.astype({'time': 'datetime64[ns]', 'open': 'float64', 'close': 'float64',
                                          'high': 'float64', 'low': 'float64', 'volume': 'float64'})

        # create three plot 创建三层图纸，第一层画k线，第二层画成交量，第三层画一些适宜于副图显示的指标
        fplt.foreground = '#FFFFFF'     # 前景色
        fplt.background = '#333333'     # 背景色
        fplt.odd_plot_background = '#333333'    # 第二层图纸的背景色
        fplt.cross_hair_color = "#FFFFFF"   # 准星的颜色
        self.__ax, self.__ax2, self.__ax3 = fplt.create_plot(symbol, rows=3)

        # plot candle sticks
        candles = self.__df[['time', 'open', 'close', 'high', 'low']]
        fplt.candlestick_ochl(candles, ax=self.__ax)

        # overlay volume on the plot
        volumes = self.__df[['time', 'open', 'close', 'volume']]
        fplt.volume_ocv(volumes, ax=self.__ax2)
        fplt.add_legend("VOLUME", self.__ax2)   # 增加"VOLUME"图例


    """
    plot indicators
    """
    def show(self):
        """最后必须调用此函数以显示图像"""
        fplt.show()

    def plot_last(self, color=None):
        """在图上画出最新成交价这根横线，便于观察"""
        last = self.__market.last()
        array = np.empty(len(self.__kline))
        array.fill(last)
        color = color if color is not None else "#CD7F32"  # 默认设置为红色
        fplt.plot(self.__df['time'], array, color=color, ax=self.__ax, legend="LAST {}".format(last))


    def plot_array(self, array, ax, legend, color=None):
        """
        绘制任意的数组成线性
        :param array: 传入一个数组
        :param ax: 加载在第几行的图上
        :param legend: 图例名称
        :param color: 颜色
        :return:
        """
        if ax == 1:
            ax = self.__ax
        elif ax == 2:
            ax = self.__ax2
        elif ax ==3:
            ax = self.__ax3
        color = color if color is not None else "#FF0000"   # 默认设置为红色
        fplt.plot(self.__df['time'], array, color=color, ax=ax, legend=legend)


    def plot_atr(self, length, color=None):
        """
        在图上画出ATR
        :param length: ATR指标参数
        :param color: 线的颜色
        :return:
        """
        color = color if color is not None else "#FF0000"   # 默认设置为红色
        fplt.plot(self.__df['time'], self.__indicators.ATR(length), color=color, ax=self.__ax3, legend='ATR({})'.format(length))

    def plot_boll(self, length, color1=None, color2=None, color3=None):
        """
        在图上画出布林通道的上轨、中轨、下轨
        :param length: BOLL指标参数
        :param upperband_color: 上轨颜色
        :param middleband_color: 中轨颜色
        :param lowerband_color: 下轨颜色
        :return:
        """
        color1 = color1 if color1 is not None else "#FF0000"  # 默认设置为红色
        color2 = color2 if color2 is not None else "#00FF00"  # 默认设置为绿色
        color3 = color3 if color3 is not None else "#0000FF"  # 默认设置为蓝色
        upperband_array = self.__indicators.BOLL(length)['upperband']
        middleband_array = self.__indicators.BOLL(length)["middleband"]
        lowerband_array = self.__indicators.BOLL(length)["lowerband"]
        fplt.plot(self.__df['time'], upperband_array, color=color1, ax=self.__ax, legend='BOLL({})-UPPERBAND'.format(length))
        fplt.plot(self.__df['time'], middleband_array, color=color2, ax=self.__ax, legend='BOLL({})-MIDDLEBAND'.format(length))
        fplt.plot(self.__df['time'], lowerband_array, color=color3, ax=self.__ax, legend='BOLL({})-LOWERBAND'.format(length))
        # 副图上也加载
        fplt.plot(self.__df['time'], upperband_array, color=color1, ax=self.__ax3, legend='BOLL({})-UPPERBAND'.format(length))
        fplt.plot(self.__df['time'], middleband_array, color=color2, ax=self.__ax3, legend='BOLL({})-MIDDLEBAND'.format(length))
        fplt.plot(self.__df['time'], lowerband_array, color=color3, ax=self.__ax3, legend='BOLL({})-LOWERBAND'.format(length))

    def plot_highest(self, length, color=None):
        """
        在图上画出最高价
        :param length: HIGHEST指标参数
        :param color: 线的颜色
        :return:
        """
        color = color if color is not None else "#FF0000"  # 默认设置红黑色
        fplt.plot(self.__df['time'], self.__indicators.HIGHEST(length), color=color, ax=self.__ax,
                  legend='HIGHEST({})'.format(length))
        # 副图也加载
        fplt.plot(self.__df['time'], self.__indicators.HIGHEST(length), color=color, ax=self.__ax3,
                  legend='HIGHEST({})'.format(length))

    def plot_ma(self, length, color=None):
        """
        在图上画出移动平均线
        :param length: 简单移动平均线参数
        :param color: 线的颜色
        :return:
        """
        color = color if color is not None else "#FF0000"   # 默认设置为红色
        # 主图与副图加载指标
        fplt.plot(self.__df['time'], self.__indicators.MA(length), color=color, ax=self.__ax, legend='MA({})'.format(length))
        fplt.plot(self.__df['time'], self.__indicators.MA(length), color=color, ax=self.__ax3, legend='MA({})'.format(length))

    def plot_macd(self, fastperiod, slowperiod, signalperiod, color1=None, color2=None, color3=None):
        """
        在图上画出MACD指标
        :param fastperiod:
        :param slowperiod:
        :param signalperiod:
        :param color1:
        :param color2:
        :param color3:
        :return:
        """
        color1 = color1 if color1 is not None else "#FF0000"  # 默认设置为红色
        color2 = color2 if color2 is not None else "#00FF00"  # 默认设置为绿色
        color3 = color3 if color3 is not None else "#0000FF"  # 默认设置为蓝色
        dif = self.__indicators.MACD(fastperiod, slowperiod, signalperiod)['DIF']
        dea = self.__indicators.MACD(fastperiod, slowperiod, signalperiod)["DEA"]
        macd = self.__indicators.MACD(fastperiod, slowperiod, signalperiod)["MACD"]
        fplt.plot(self.__df['time'], dif, color=color1, ax=self.__ax3,
                  legend='MACD({}, {}, {})-DIF'.format(fastperiod, slowperiod, signalperiod))
        fplt.plot(self.__df['time'], dea, color=color2, ax=self.__ax3,
                  legend='MACD({}, {}, {})-DEA'.format(fastperiod, slowperiod, signalperiod))
        fplt.plot(self.__df['time'], macd, color=color3, ax=self.__ax3,
                  legend='MACD({}, {}, {})-MACD'.format(fastperiod, slowperiod, signalperiod))

    def plot_ema(self, length, color=None):
        """
        在图上画出EMA指标
        :param length:
        :param color:
        :return:
        """
        color = color if color is not None else "#FF0000"  # 默认设置为红色
        fplt.plot(self.__df['time'], self.__indicators.EMA(length), color=color, ax=self.__ax,
                  legend='EMA({})'.format(length))
        # 副图也加载
        fplt.plot(self.__df['time'], self.__indicators.EMA(length), color=color, ax=self.__ax3,
                  legend='EMA({})'.format(length))

    def plot_kama(self, length, color=None):
        """在图上画出KAMA指标"""
        color = color if color is not None else "#FF0000"  # 默认设置为红色
        fplt.plot(self.__df['time'], self.__indicators.KAMA(length), color=color, ax=self.__ax,
                  legend='KAMA({})'.format(length))
        # 副图也加载
        fplt.plot(self.__df['time'], self.__indicators.KAMA(length), color=color, ax=self.__ax3,
                  legend='KAMA({})'.format(length))

    def plot_kdj(self, fastk_period, slowk_period, slowd_period, color1=None, color2=None):
        """
        在图上画出KDJ指标
        :param fastk_period:
        :param slowk_period:
        :param slowd_period:
        :param color1:
        :param color2:
        :param color3:
        :return:
        """
        color1 = color1 if color1 is not None else "#FF0000"  # 默认设置为红色
        color2 = color2 if color2 is not None else "#00FF00"  # 默认设置为绿色
        k = self.__indicators.KDJ(fastk_period, slowk_period, slowd_period)['k']
        d = self.__indicators.KDJ(fastk_period, slowk_period, slowd_period)["d"]
        # 仅副图加载
        fplt.plot(self.__df['time'], k, color=color1, ax=self.__ax3,
                  legend='KDJ({}, {}, {})-K'.format(fastk_period, slowk_period, slowd_period))
        fplt.plot(self.__df['time'], d, color=color2, ax=self.__ax3,
                  legend='KDJ({}, {}, {})-D'.format(fastk_period, slowk_period, slowd_period))

    def plot_lowest(self, length, color=None):
        """LOWEST"""
        color = color if color is not None else "#FF0000"  # 默认设置红黑色
        fplt.plot(self.__df['time'], self.__indicators.LOWEST(length), color=color, ax=self.__ax,
                  legend='LOWEST({})'.format(length))
        # 副图也加载
        fplt.plot(self.__df['time'], self.__indicators.LOWEST(length), color=color, ax=self.__ax3,
                  legend='LOWEST({})'.format(length))

    def plot_obv(self, color=None):
        """OBV"""
        color = color if color is not None else "#FF0000"  # 默认设置红黑色
        # 仅副图加载
        fplt.plot(self.__df['time'], self.__indicators.OBV(), color=color, ax=self.__ax3,
                  legend='OBV')

    def plot_rsi(self, length, color=None):
        """RSI"""
        color = color if color is not None else "#FF0000"  # 默认设置为红色
        # 仅副图加载
        fplt.plot(self.__df['time'], self.__indicators.RSI(length), color=color, ax=self.__ax3,
                  legend='RSI({})'.format(length))

    def plot_roc(self, length, color=None):
        """ROC"""
        color = color if color is not None else "#FF0000"  # 默认设置为红色
        # 仅副图加载
        fplt.plot(self.__df['time'], self.__indicators.ROC(length), color=color, ax=self.__ax3,
                  legend='ROC({})'.format(length))

    def plot_stochrsi(self, timeperiod, fastk_period, fastd_period, color1=None, color2=None):
        """STOCHRSI"""
        color1 = color1 if color1 is not None else "#FF0000"  # 默认设置为红色
        color2 = color2 if color2 is not None else "#00FF00"  # 默认设置为绿色
        stochrsi = self.__indicators.STOCHRSI(timeperiod, fastk_period, fastd_period)['stochrsi']
        fastk = self.__indicators.STOCHRSI(timeperiod, fastk_period, fastd_period)["fastk"]
        # 仅副图加载
        fplt.plot(self.__df['time'], stochrsi, color=color1, ax=self.__ax3,
                  legend='STOCHRSI({}, {}, {})-STOCHRSI'.format(timeperiod, fastk_period, fastd_period))
        fplt.plot(self.__df['time'], fastk , color=color2, ax=self.__ax3,
                  legend='STOCHRSI({}, {}, {})-FASTK'.format(timeperiod, fastk_period, fastd_period))

    def plot_sar(self, color=None):
        """
        在图上画出SAR
        :param length: SAR指标参数
        :param color: 线的颜色
        :return:
        """
        color = color if color is not None else "#FF0000"  # 默认设置为红色
        # 主副图均加载
        fplt.plot(self.__df['time'], self.__indicators.SAR(), color=color, ax=self.__ax,
                  legend='SAR')
        fplt.plot(self.__df['time'], self.__indicators.SAR(), color=color, ax=self.__ax3,
                  legend='SAR')

    def plot_stddev(self, length, color=None):
        """STDDEV"""
        color = color if color is not None else "#FF0000"  # 默认设置为红色
        # 仅副图加载
        fplt.plot(self.__df['time'], self.__indicators.STDDEV(length), color=color, ax=self.__ax3,
                  legend='STDDEV({})'.format(length))

    def plot_trix(self, length, color=None):
        """STDDEV"""
        color = color if color is not None else "#FF0000"  # 默认设置为红色
        # 仅副图加载
        fplt.plot(self.__df['time'], self.__indicators.TRIX(length), color=color, ax=self.__ax3,
                  legend='TRIX({})'.format(length))

    def plot_volume(self, color=None):
        """VOLUME"""
        color = color if color is not None else "#FF0000"  # 默认设置为红色
        # 仅副图均加载
        fplt.plot(self.__df['time'], self.__indicators.VOLUME(), color=color, ax=self.__ax3,
                  legend='VOLUME')