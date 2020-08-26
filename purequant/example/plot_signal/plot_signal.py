from purequant.signalize import SIGNALIZE
from purequant.trade import OKEXFUTURES, OKEXSPOT, OKEXSWAP, HUOBISPOT, HUOBIFUTURES, HUOBISWAP
from purequant.const import *
from purequant.config import config

config.loads('config.json')
symbol = "ETC-USDT-201225"
time_frame = "1d"
okex = OKEXFUTURES("", "", "", symbol)
# huobi = HUOBIFUTURES("", "", symbol)    # 火币需填入api

signalize = SIGNALIZE(okex, symbol, time_frame)     # 实例化
signalize.plot_last(color=GOLDEN)
signalize.plot_ma(60, color=PINK)
signalize.plot_ma(90, color=SKYBLUE)
# signalize.plot_atr(14)
# signalize.plot_boll(14)
# signalize.plot_highest(30)
# signalize.plot_macd(12, 26, 9)
# signalize.plot_ema(20)
# signalize.plot_kama(10, color=PINK)
# signalize.plot_kdj(9, 3, 3)
# signalize.plot_lowest(30)
# signalize.plot_obv()
# signalize.plot_rsi(20)
# signalize.plot_roc(20)
# signalize.plot_stochrsi(14, 14, 3)
# signalize.plot_sar()
# signalize.plot_stddev(20)
# signalize.plot_trix(20)
# signalize.plot_volume()

signalize.show()