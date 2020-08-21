# PureQuant

------

PureQuant是一套使用Python语言开发的数字货币程序化交易框架，致力于为数字货币行业的投资者提供一个快速、简便地编写自己的交易系统的工具，希望使用者能够通过使用系统，建立并优化自己的交易思想，形成自己的交易策略。感谢您选择PureQuant，希望您能够通过使用该框架找到乐趣，并能创造更多价值。

## 框架依赖

+ **运行环境**

  建议安装python3.7版本

+ **MySQL数据库(可选)**，**MongoDB数据库(可选)**

  数据存储
  
+ **依赖python三方包**

  pip install purequant 时会自动安装依赖三方包，请确保提前安装了setuptools，可以 pip install setuptools

## 安装

+ 使用 `pip` 可以简单方便安装:

```python
pip install purequant
```

## 项目结构

+ 推荐创建如下结构的文件及文件夹

```python
ProjectName
    |----- config.json
    |----- strategy1.py
    |----- strategy2.py
    |----- ...
    |----- logger
  
```

## 有任何问题，欢迎联系

+ 在Github上提交issue

+ 联系微信：caa-essay

## 赞赏与支持

+ 微信

  [https://github.com/eternalranger/pictures/blob/master/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20200819173133.jpg]: 

+ 支付宝

  [https://github.com/eternalranger/pictures/blob/master/%E6%94%AF%E4%BB%98%E5%AE%9D.jpg]: 

  

感谢您的赞赏与支持！


------



## 下单交易

```python
from purequant.trade import OKEXSPOT  # 从trade模块中导入交易所
from purequant.config import config  # 导入配置模块

config.loads(config_file) 	# 载入配置文件
exchange = OKEXSPOT(config.access_key, config.secret_key, config.passphrase, instrument_id) # 实例化交易所
```

### 买入开多

```python
exchange.buy(price, amount)  
```

### 卖出平多

```python
exchange.sell(price, amount)  
```

### 卖出开空

```python
exchange.sellshort(price, amount)  
```

### 买入平空

```python
exchange.buytocover(price, amount)  
```

### 平多开空

```python
exchange.SELL(平多价格，平多数量，开空价格，开空数量)
```

### 平空开多

```python
exchange.BUY(平空价格，平空数量，开多价格，开多数量)
```

下单后无论是否完全成交，返回下单结果。

```python
【交易提醒】下单结果：{'合约ID': 'TRX-USDT-SWAP', '方向': '卖出平多', '订单状态': '完全成交', '成交均价': '0.01784', '数量': '1', '成交金额': 17.84} 
```

------



## 交易助手

使用交易助手可以实现自动撤单以及撤单后重发委托直至完全成交的功能。

```json
{
"ASSISTANT": {
        "automatic_cancellation": "false",
        "reissue_order": "0.0%",
        "price_cancellation": "false",
        "amplitude": "1%",
        "time_cancellation": "false",
        "seconds": 10
    }
}
```

### 自动撤单

将配置文件中的"automatic_cancellation"设置为"true"，即可实现下单后如订单未完全成交就自动撤单。

### 价格撤单

将配置文件中的"price_cancellation"设置为 "true",当最新价超过委托价一定百分比（"amplitude"），则自动撤单，并以最新价（可以使用超价下单，设置"reissue_order"即可）重发委托。

### 时间撤单

将配置文件中的"time_cancellation"设置为 "true",若超时未成交（"seconds"），则自动撤单，并以最新价（可以使用超价下单，设置"reissue_order"即可）重发委托直至完全成交。

### 交易助手使用说明

1.若未启用交易助手，则下单后自动查询订单状态然后返回订单结果。

2.若只启用了自动撤单功能，下单后如果订单未完全成交，则自动撤单，返回下单结果。

3.价格撤单功能只会在最新价超过委托价一定百分比时去自动撤单然后以最新价下单，不能实现达到完全成交的作用。

4.时间撤单功能可以一直重发委托直至完全成交。

5.建议启用交易助手的三个功能，参数可以按需自行设置。

------



## 智能渠道推送

调用时需先导入push模块中的函数名称：

```python
from purequant.push import push
```

还需导入config模块并载入配置文件

```python
from purequant.config import config 

config.loads(filename)
```

配置文件是一个名为config.json的文件，只需将其中参数修改为自己的即可

```json
{
    "PUSH": {
        "sendmail": "true",
        "dingtalk": "false",
        "twilio": "false"
    },
    "DINGTALK": {
        "ding_talk_api": "https://oapi.dingtalk.com/robot/send?access_token=d3a368908a7db882cd3f6afcccca302e51a1c9"
    },
    "TWILIO": {
        "accountSID" : "AC97a11fcc5ede559cd39061ad140f",
        "authToken" : "3616b6ced8e250232ca2fa4aa559",
        "myNumber" : "+8613712345678",
        "twilio_Number" : "+12058946789"
    },
    "SENDMAIL": {
        "from_addr" : "123456789@qq.com",
        "password" : "xqkwtrsfqwcjgjjgh",
        "to_addr" : "abc@icloud.com",
        "smtp_server" : "smtp.qq.com",
        "port":587
    }
}
```

### 集成推送信息

```python
push("要推送的信息内容")
```

在配置文件中，"PUSH"中的对应参数若设置为"true"，使用push()时则会推送消息至相应智能渠道。

twilio所能推送的短信字节过短，因此只能用来发送简短信息，在交易时建议将此项设为"false"。

钉钉推送时会自动@群里的所有人，并且会在当前策略文件目录下自动创建一个名为'dingtalk.text'的文件，其中记录了钉钉消息的发送时间、状态以及具体的发送内容。

------



## 获取持仓信息

```python
from purequant.position import POSITION		# 导入持仓模块

position = POSITION(exchange, instrument_id, time_frame)	# 实例化POSITION
```

### 当前持仓方向

```python
direction = position.direction()
# 若当前无持仓，返回"none"
# 若当前持多头，返回"long"
# 若当前持空头，返回"short"
```

### 当前持仓数量

```python
amount = position.amount()
# 返回整型数字
```

### 当前持仓均价

```python
price = position.price()
# 返回浮点数
```

------



## 获取行情信息

调用时需先导入MARKET模块并创建market对象， 返回浮点数

```python
from purequant.market import MARKET

market = MARKET(exchange, instrument_id, time_frame)
```

### 最新成交价

```python
last = market.last()
```

### 开盘价

```python
open = market.open()

market.open(-1)  # 获取当根bar上的开盘价
market.open(-2)  # 获取上根bar上的开盘价
market.open(0)  # 获取最远一根bar上的开盘价
```

### 最高价

```python
high = market.high()

market.high(-1)  # 获取当根bar上的最高价
market.high(-2)  # 获取上根bar上的最高价
market.high(0)  # 获取最远一根bar上的最高价
```

### 最低价

```python
low = market.low()

market.low(-1)  # 获取当根bar上的最低价
market.low(-2)  # 获取上根bar上的最低价
market.low(0)  # 获取最远一根bar上的最低价
```

### 收盘价

```python
close = market.close()

market.close(-1)  # 获取当根bar上的收盘价
market.close(-2)  # 获取上根bar上的收盘价
market.close(0)  # 获取最远一根bar上的收盘价
```

### 合约面值

```python
# 获取合约面值，返回结果为计价货币数量，数据类型为整型数字。
# 如一张币本位BTC合约面值为100美元，一张USDT本位BTC合约面值为0.01个BTC
contract_value = market.contract_value()
```

------



## 持仓同步

调用时需先导入SYNCHRONIZE模块并初始化：

```python
from purequant.synchronize import SYNCHRONIZE

synchronize = SYNCHRONIZE("mongodb", "trade", "position", exchange, instrument_id, time_frame)
# 数据库可选MySQL或MongoDB，都不用手动创建数据库与集合（数据表）
```

在策略中，在下单代码之后加上如下代码以保存策略应持仓位信息至数据库：

```python
synchronize.save_strategy_position(strategy_direction, strategy_amount)
```

循环运行持仓自动匹配函数：

```python
while True:
    synchronize.match()
```

测试时也可输出其运行信息至控制台以观察：

```python
info = synchronize.match()
print(info)
```

在配置文件中可以设置是否超价下单：

```json
{
"SYNCHRONIZE": {
        "overprice": {
            "range": "0.1%"
        }
    }
}
```

注意："0.1 %"是一个由双引号包裹的字符串。

------



## 持仓监控

调用时需先导入monitor模块：

```python
from purequant.monitor import position_update
```

使用此功能还需载入配置文件：

```python
from purequant.config import config

config.loads(config_file)  # 载入配置文件
position_update()	# 运行持仓更新自动提醒服务
```

在配置文件中可以设置要订阅的持仓频道：

+ OKEX

```json
{	
    "POSITION_SERVER": {
        "futures_usd": "false",      # 币本位交割合约
        "futures_usdt": "false",	# U本位交割合约
        "delivery_date": "201225",	# 交割合约需要设置交割日期
        "swap_usd": "false",	# 币本位永续合约
        "swap_usdt": "false",	# U本位永续合约
        "spot": "false",	# 现货账户
        "margin": "false"	# 杠杆账户
    }
}
```

+ HUOBI

```python
{
    "POSITION_SERVER": {
            "platform": {
                "huobi": {
                        "futures": "true",
                        "swap": "false"
                }
            }
        }
}
```

如将对应频道设置为"true"，则会订阅此频道的持仓更新自动推送，推送渠道可在配置文件的"PUSH"中设置。

OKEX交割合约的币本位与U本位皆可订阅全部九大品种。OKEX现货、杠杆、永续合约都只支持 BTC BCH BSV ETH ETC EOS LTC TRX XRP 九个主流币种。暂不支持期权合约。

支持火币交割合约与永续合约，同时只能订阅一个频道，火币默认是订阅所有品种的持仓更新数据。

因交易所对多个频道有总字节限制，所以此处我们设限为只能订阅一个频道。

推送的信息内容如下：

```python
# USDT交割合约
【交易提醒】交割合约持仓更新！合约ID:ETC-USDT-201225 多头仓位：0 持多均价：0 空头仓位：0 持空均价：6.457 最新成交价：6.176 杠杆倍数：20  # 变动前
【交易提醒】交割合约持仓更新！合约ID:ETC-USDT-201225 多头仓位：1 持多均价：6.177 空头仓位：0 持空均价：6.457 最新成交价：6.176 杠杆倍数：20	# 变动后
```

```python
# USD交割合约
【交易提醒】交割合约持仓更新！合约ID:ETC-USD-201225 多头仓位：1 持多均价：6.172 空头仓位：0 持空均价：6.168 最新成交价：6.171 杠杆倍数：10	# 变动前
【交易提醒】交割合约持仓更新！合约ID:ETC-USD-201225 多头仓位：0 持多均价：6.172 空头仓位：0 持空均价：6.168 最新成交价：6.171 杠杆倍数：10	# 变动后
```

```python
# 现货账户
【交易提醒】币币账户更新！币种:USDT 余额：6.8401564534263976 冻结：0 可用：6.8401564534263976 # 转入USDT
【交易提醒】币币账户更新！币种:USDT 余额：6.8401564534263976 冻结：0.30575 可用：6.5344064534263976 # 下单未成交冻结中的USDT
【交易提醒】币币账户更新！币种:ETC 余额：0.049023605 冻结：0 可用：0.049023605  # 买入ETC
【交易提醒】币币账户更新！币种:ETC 余额：0.000003605 冻结：0 可用：0.000003605  # 卖出ETC
```

```python
# 杠杆账户
【交易提醒】币币杠杆账户更新！交易对:EOS-USDT 强平价：-0.996 计价币：【currency:USDT 余额：3.0000208 可用：3.0000208 冻结:0 已借未还：0】 交易币：【currency:EOS 余额：3.0146712 可用：0.0000712 冻结:3.0146 已借未还：0】 # 卖出前
【交易提醒】币币杠杆账户更新！交易对:EOS-USDT 强平价：-151842.325 计价币：【currency:USDT 余额：10.8111734695 可用：10.8111734695 冻结:0 已借未还：0】 交易币：【currency:EOS 余额：0.0000712 可用：0.0000712 冻结:0 已借未还：0】 # 卖出后
```

```python
# USD永续合约
【交易提醒】永续合约持仓更新！合约ID:EOS-USD-SWAP 多头方向：long 持多均价：0.000 持多数量：0 空头方向：short 持空均价：0.000 持空数量：0 最新成交价：2.590 杠杆倍数：10.00	# 开多前
【交易提醒】永续合约持仓更新！合约ID:EOS-USD-SWAP 多头方向：long 持多均价：2.590 持多数量：1 空头方向：short 持空均价：0.000 持空数量：0 最新成交价：2.590 杠杆倍数：10.00	# 开多后
    
【交易提醒】永续合约持仓更新！合约ID:EOS-USD-SWAP 多头方向：long 持多均价：2.590 持多数量：1 空头方向：short 持空均价：0.000 持空数量：0 最新成交价：2.588 杠杆倍数：10.00	# 平多前
【交易提醒】永续合约持仓更新！合约ID:EOS-USD-SWAP 多头方向：long 持多均价：0.000 持多数量：0 空头方向：short 持空均价：0.000 持空数量：0 最新成交价：2.588 杠杆倍数：10.00	# 平多后
    
【交易提醒】永续合约持仓更新！合约ID:EOS-USD-SWAP 多头方向：long 持多均价：0.000 持多数量：0 空头方向：short 持空均价：0.000 持空数量：0 最新成交价：2.588 杠杆倍数：10.00	# 开空前
【交易提醒】永续合约持仓更新！合约ID:EOS-USD-SWAP 多头方向：long 持多均价：0.000 持多数量：0 空头方向：short 持空均价：2.587 持空数量：1 最新成交价：2.588 杠杆倍数：10.00	# 开空后
    
【交易提醒】永续合约持仓更新！合约ID:EOS-USD-SWAP 多头方向：long 持多均价：0.000 持多数量：0 空头方向：short 持空均价：2.587 持空数量：1 最新成交价：2.586 杠杆倍数：10.00	# 平空前
【交易提醒】永续合约持仓更新！合约ID:EOS-USD-SWAP 多头方向：long 持多均价：0.000 持多数量：0 空头方向：short 持空均价：0.000 持空数量：0 最新成交价：2.586 杠杆倍数：10.00	# 平空后
```

------



## 行情服务

subscribe行情服务是专用于获取通过交易所websocket接口订阅的公共行情数据，并将返回的数据内容保存至MongoDB数据库中，保存的数据需要自行进行清洗。

### 存储数据

```python
from purequant.subscribe import markets_update	# 导入行情服务器模块
from purequant.config import config	# 导入配置模块

config.loads("config.json")	# 载入配置文件
markets_update()	# 运行行情服务器
```

运行结果示例：

```python
行情服务器已启动，数据已保存至MongoDB数据库！
2020-07-21T07:28:35.107Z{"event":"subscribe","channel":"futures/depth5:BTC-USD-201225"}
2020-07-21T07:28:35.123Z{"table":"futures/depth5","data":[{"asks":[["9362.1","23","0","3"],["9362.93","1","0","1"],["9363.03","4","0","1"],["9363.18","93","0","1"],["9363.57","109","0","1"]],"bids":[["9362.09","1615","0","9"],["9361.99","20","0","1"],["9361.91","106","0","1"],["9361.61","1","0","1"],["9361.5","111","0","1"]],"instrument_id":"BTC-USD-201225","timestamp":"2020-07-20T23:28:35.433Z"}]}
2020-07-21T07:28:35.183Z{"table":"futures/depth5","data":[{"asks":[["9362.1","23","0","3"],["9362.93","1","0","1"],["9363.03","4","0","1"],["9363.18","93","0","1"],["9363.57","109","0","1"]],"bids":[["9362.09","1615","0","9"],["9361.99","20","0","1"],["9361.91","106","0","1"],["9361.61","1","0","1"],["9361.5","111","0","1"]],"instrument_id":"BTC-USD-201225","timestamp":"2020-07-20T23:28:35.535Z"}]}
```

MongoDB数据库中保存的数据：

```python
> db.depth5.find()
{ "_id" : ObjectId("5f1628974f26375cad944749"), "data" : "{\"event\":\"subscribe
\",\"channel\":\"futures/depth5:BTC-USD-201225\"}" }
{ "_id" : ObjectId("5f1628984f26375cad94474b"), "data" : "{\"table\":\"futures/d
epth5\",\"data\":[{\"asks\":[[\"9362.1\",\"23\",\"0\",\"3\"],[\"9362.93\",\"1\",
\"0\",\"1\"],[\"9363.18\",\"93\",\"0\",\"1\"],[\"9363.57\",\"109\",\"0\",\"1\"],
[\"9363.58\",\"197\",\"0\",\"1\"]],\"bids\":[[\"9362.09\",\"1655\",\"0\",\"10\"]
,[\"9361.99\",\"20\",\"0\",\"1\"],[\"9361.91\",\"106\",\"0\",\"1\"],[\"9361.61\"
,\"1\",\"0\",\"1\"],[\"9361.5\",\"111\",\"0\",\"1\"]],\"instrument_id\":\"BTC-US
D-201225\",\"timestamp\":\"2020-07-20T23:28:24.263Z\"}]}" }
{ "_id" : ObjectId("5f1628984f26375cad94474d"), "data" : "{\"table\":\"futures/d
epth5\",\"data\":[{\"asks\":[[\"9362.1\",\"23\",\"0\",\"3\"],[\"9362.93\",\"1\",
\"0\",\"1\"],[\"9363.18\",\"93\",\"0\",\"1\"],[\"9363.57\",\"109\",\"0\",\"1\"],
[\"9363.58\",\"197\",\"0\",\"1\"]],\"bids\":[[\"9362.09\",\"1655\",\"0\",\"10\"]
,[\"9361.99\",\"20\",\"0\",\"1\"],[\"9361.91\",\"106\",\"0\",\"1\"],[\"9361.61\"
,\"1\",\"0\",\"1\"],[\"9361.5\",\"111\",\"0\",\"1\"]],\"instrument_id\":\"BTC-US
D-201225\",\"timestamp\":\"2020-07-20T23:28:24.366Z\"}]}" }
```

可以通过修改配置文件来进行设置：

+ 行情服务器okex平台配置示例

```json
{
    "MARKETS_SERVER": {
        "platform": {
            "okex": {
            "console": "true",	# 是否输出订阅的数据至控制台
            "database": "trade",	# 将数据保存至MongoDB的"trade"数据库
            "collection": "depth5",		# 将数据保存至"trade"数据库的"depth5"集合中
            "channels": [
                ["futures/depth5:BTC-USD-201225"], ["futures/candle60s:BTC-USD-201225"]	# 订阅的频道，可订阅多个频道，但数据会存储至同一个数据库的集合中，需自行处理数据
        ]
    }
}
```

+ 行情服务器火币平台配置示例

```json
{
    "MARKETS_SERVER": {
        "platform": {
            "huobi_futures": {			# huobi_futures 或 huobi_swap
                "console": "false",
                "database": "trade",
                "collection": "hbdata",
                "channels": [
                ["market.BTC_NW.depth.step6"], ["market.BTC_CQ.kline.1min"]
                ]
            }
        }
    }
}
```

支持OKEX现货、交割合约、永续合约，支持火币交割合约与永续合约。

### 导出数据

```python
from purequant.storage import storage	# 导入数据存储与读取模块

storage.export_mongodb_to_csv("trade", "depth5", "depth5.csv") # 将MongoDB "trade"数据库中"depth5"集合的数据导出至当前目录下的"depth5.csv"文件
```

```python
# 运行结果
MongoDB【trade】数据库中【depth5】集合的数据已导出至【depth5.csv】文件！

Process finished with exit code 0
```

------



## 交易指标

调用时需先导入indicators模块：

```python
from purequant.indicators import INDICATORS
```

要传入的参数中都有platform、instrument_id、time_frame，所以需要声明这几个变量，并且初始化indicators

```python
from purequant.trade import OKEXFUTURES
# k线是公共数据，api传入空的字符串即可
instrument_id = "BTC-USDT-201225"
time_frame = "1d"
exchange = OKEXFUTURES("", "", "", instrument_id)


indicators = INDICATORS(exchange, instrument_id, time_frame)
```

### ATR，平均真实波幅

返回一个一维数组

```python
indicators.ATR(14)
```

```python
# 获取最新一根bar上的atr
atr = indicators.ATR(14)[-1]
```

ATR已检验，计算出的值与huobi交易所k线图上所显示的一致。

### BarUpdate，判断k线是否更新

如果更新，返回值为True，否则为False

```python
indicators.BarUpdate()
```

```python
# 调用方式
if indicators.BarUpdate():
    print("k线更新")
```

BarUpdate已检验，k线更新时，其值会变成True。

### BOLL，布林线指标

返回一个字典 {"upperband": 上轨数组， "middleband": 中轨数组， "lowerband": 下轨数组}

```python
indicators.BOLL(20)
```

```python
# 获取最新一根bar上的上、中、下轨值
upperband = indicators.BOLL(20)['upperband'][-1]
middleband = indicators.BOLL(20)['middleband'][-1]
lowerband = indicators.BOLL(20)['lowerband'][-1]
```

BOLL已检验，与okex及huobi上k线图上所显示一致。

### CurrentBar，获取bar的长度

返回一个整型数字

```python
indicators.CurrentBar()
```

```python
# 获取交易所返回k线数据的长度
kline_length = indicators.CurrentBar()
```

CurrentBar已检验，与FMZ量化所计算出的值一致。

### HIGHEST，周期最高价

返回一个一维数组

```python
indicators.HIGHEST(30)
```

```python
# 获取最新一根bar上的最高价
highest = indicators.HIGHEST(30)[-1]
```

HIGHEST已检验，与FMZ量化所计算出的值一致。

### MA，移动平均线

返回一个一维数组

```python
indicators.MA(15)
```

```python
# 获取最新一根bar上的ma
ma15 = indicators.MA(15)[-1]
```

MA已检验，与okex交易所k线图上所显示一致。

### MACD，指数平滑异同平均线

返回一个字典  {'DIF': DIF数组, 'DEA': DEA数组, 'MACD': MACD数组}

```python
indicators.MACD(12, 26, 9)
```

```python
# 获取最新一根bar上的DIF、DEA、MACD
DIF = indicators.MACD(12, 26, 9)['DIF'][-1]
DEA = indicators.MACD(12, 26, 9)['DEA'][-1]
MACD = indicators.MACD(12, 26, 9)['MACD'][-1]
```

MACD已检验，与okex交易所k线图上所显示一致。

### EMA，指数平均数

返回一个一维数组

```python
indicators.EMA(9)
```

```python
# 获取最新一根bar上的ema
ema = indicators.EMA(9)[-1]
```

EMA已检验，与okex交易所k线图上所显示一致。

### KAMA ，考夫曼自适应移动平均线

返回一个一维数组

```python
indicators.EMA(30)
```

```python
# 获取最新一根bar上的kama
kama = indicators.KAMA(30)[-1]
```

KAMA已检验，与turtle quant程序化交易软件所计算出的值一致。

### KDJ，随机指标

返回一个字典，{'k': k值数组， 'd': d值数组}

```python
indicators.KDJ(9 ,3, 3)
```

```python
# 获取最新一根bar上的k和d
k = indicators.KDJ(9 ,3, 3)['k'][-1]
d = indicators.KDJ(9 ,3, 3)['d'][-1]
```

KDJ值与交易所及FMZ量化均不一致，与turtle quant软件所显示的值 略有差异，有待以后再次验证。

### LOWEST，周期最低价

返回一个一维数组

```python
indicators.LOWEST(30)
```

```python
# 获取最新一根bar上的最低价
indicators.LOWEST(30)[-1]
```

LOWEST已检验，与FMZ量化所计算出的值一致。

### OBV，能量潮

返回一个一维数组

```python
indicators.OBV()
```

```python
# 获取最新一根bar上的obv
obv = indicators.OBV()[-1]
```

计算出的obv值与交易所k线图上显示的数据不一致，但与发明者量化上计算出的obv值一致：

```python
# PureQuant计算obv：
okex = OkexFutures("", "", "", "BTC-USD-201225")
time_frame = "1d"
indicators = Indicators(okex, "BTC-USD-201225", time_frame)
print(indicators.OBV()[-2])

# 输出结果
38773276.0


# FMZ量化计算obv，标的为Okex交割合约币本位BTC:
exchange.SetContractType("next_quarter") //设置合约类型为次季合约
function main(){
    var records = exchange.GetRecords(PERIOD_D1)
    var obv = TA.OBV(records)
    Log(obv[obv.length - 2])
}
# 输出结果
信息	38773276
```

因此可以放心使用。

### RSI，强弱指标

返回一个一维数组

```python
indicators.RSI(14)
```

```python
# 获取最新一根bar上的rsi
rsi = indicators.RSI(14)[-1]
```

RSI已检验，计算出的值与okex交易所k线图上所显示的一致。

### ROC，变动率指标

返回一个一维数组

```python
indicators.ROC(12)
```

```python
# 获取最新一根bar上的roc
roc = indicators.ROC(12)[-1]
```

ROC已检验，计算出的值与okex交易所k线图上所显示的一致。

### STOCHRSI，随机相对强弱指数

返回一个字典  {'stochrsi': stochrsi数组, 'fastk': fastk数组}

```python
indicators.STOCHRSI(14, 14, 3)
```

```python
# 获取最新一根bar上的stochrsi、fastk
stochrsi = indicators.STOCHRSI(14, 14, 3)['stochrsi'][-1]
fastk = indicators.STOCHRSI(14, 14, 3)['fastk'][-1]
```

STOCHRSI已验证，与okex、huobi交易所k线图上所显示的一致。

### SAR，抛物线指标

返回一个一维数组

```python
indicators.SAR()
```

```python
# 获取最新一根bar上的sar
sar = indicators.SAR()[-1]
```

SAR与okex、huobi交易所k线图上所显示均不一致，但与turtlequant一致，应是算法略有不同的缘故。

### STDDEV， 标准方差

返回一个一维数组

```python
indicators.STDDEV()
```

```python
# 获取最新一根bar上的stddev
stddev = indicators.STDDEV(20)-1
```

STDDEV（StandardDev）已验证，与turtlequant所计算的值一致。

### TRIX，三重指数平滑平均线

返回一个一维数组

```python
indicators.TRIX(12)
```

```python
# 获取最新一根bar上的trix
trix = indicators.TRIX(12)[-1]
```

TRIX已验证，与okex交易所k线图上所显示的一致。

### VOLUME，成交量

返回一个一维数组

```python
indicators.VOLUME()

# 获取最新一根bar上的volume
volume = indicators.VOLUME()[-1]
```

VOLUME已验证，与okex交易所k线图上所显示的一致。



indicators模块中的MA、EMA、KAMA函数，可以传入多个参数进行计算，求多个参数计算出的指标数值。

当传入多个参数时，返回的结果是一个列表。

用法示例：

```python
from purequant.indicators import INDICATORS
from purequant.trade import OKEXFUTURES

instrument_id = "ETC-USDT-201225"
time_frame = "1d"
exchange = OKEXFUTURES("", "", "", instrument_id)   # 实例化一个交易所对象
indicators = INDICATORS(exchange, instrument_id, time_frame)    # 实例化指标对象
ma = indicators.MA(60, 90)  # 传入两个参数
ma60 = ma[0]   # MA60, 一个一维数组
ma90 = ma[1]   # MA90, 一个一维数组
print(ma60[-1])     # 打印出当前k线上的ma60的值
print(ma90[-1])     # 打印出当前k线上的ma90的值
```



------



## 日志输出

调用时需先导入LOGGER模块，并在当前目录下创建名为"logger"的文件夹用以存放日志输出文件

```python
from purequant.logger import LOGGER

logger = LOGGER(config_file)
```

在配置文件中，可以直接修改日志输出的等级来控制日志输出级别：

+ 将"level"设置成"critical"，则只输出"CRITICAL"级别的日志

+ "handler"中可以指明日志的输出方式

+ "file"是以文件输出的方式存储日志到当前目录下的"logger"文件夹，按照文件大小1M进行分割，保留最近10个文件

+ "time"也是文件输出，但是以按照一天的时间间隔来分割文件，保留最近10个文件

+ "stream"或者不填或者填入其他字符，都是输出到控制台，不会存储到文件

```json
{
    "LOG": {
        "level": "critical",
        "handler": "file"
    }
}
```

### debug

一般用来打印一些调试信息，级别最低

```python
logger.debug("要输出的调试信息")
```

### info

一般用来打印一些正常的操作信息

```python
logger.info("要输出的操作信息")
```

### warning

一般用来打印警告信息

```python
logger.info("要输出的警告信息")
```

### error

一般用来打印一些错误信息

```python
logger.info("要输出的错误信息")
```

### critical

一般用来打印一些致命的错误信息，等级最高

```python
logger.critical("要输出的致命的错误信息")
```

------



## 获取时间信息

调用前需先导入time_tools模块中的函数

```python
from purequant.time import *
```

### 获取本地时间

```python
localtime = get_localtime()
```

### 获取当前utc时间

```python
utc_time = get_utc_time()
```

### 获取当前时间戳（秒）

```python
cur_timestamp = get_cur_timestamp()
```

### 获取当前时间戳（毫秒）

```python
cur_timestamp_ms = get_cur_timestamp_ms()
```

------



## 示例策略

### 双均线多空策略

```python
from purequant.indicators import INDICATORS
from purequant.trade import OKEXFUTURES
from purequant.position import POSITION
from purequant.market import MARKET
from purequant.synchronize import SYNCHRONIZE
from purequant.push import push
from purequant.storage import storage
from purequant.time import get_localtime
from purequant.config import config

class Strategy:

    def __init__(self, instrument_id, time_frame, fast_length, slow_length, long_stop, short_stop, start_asset, initial_position_direction, initial_position_amount):
        """双均线策略"""
        try:
            print("{} {} 双均线多空策略已启动！".format(get_localtime(), instrument_id))
            config.loads('config.json')  # 载入配置文件

            self.instrument_id = instrument_id  # 合约ID
            self.time_frame = time_frame  # k线周期
            self.initial_position_direction = initial_position_direction  # 初始持仓方向
            self.initial_position_amount = initial_position_amount   # 初始持仓数量
            self.exchange = OKEXFUTURES(config.access_key, config.secret_key, config.passphrase, self.instrument_id)  # 初始化交易所
            self.position = POSITION(self.exchange, self.instrument_id, self.time_frame)  # 初始化potion
            self.market = MARKET(self.exchange, self.instrument_id, self.time_frame)  # 初始化market
            self.indicators = INDICATORS(self.exchange, self.instrument_id, self.time_frame)
            self.synchronize = SYNCHRONIZE("mongodb", "position", self.instrument_id[0:3], self.exchange, self.instrument_id, self.time_frame)
            # 在第一次运行程序时，将初始资金数据、初始无持仓信息保存至mongodb数据库中
            if config.first_run == "true":
                storage.mongodb_save({"时间": get_localtime(), "profit": 0, "asset": start_asset}, 'asset', self.instrument_id[0:3])
                self.synchronize.save_strategy_position(self.initial_position_direction, self.initial_position_amount)
            # 读取数据库中保存的总资金数据
            self.total_asset = storage.mongodb_read_data('asset', self.instrument_id[0:3])[-1][0]['asset']
            self.overprice_range = config.overprice_range # 超价下单幅度
            self.counter = 0  # 计数器
            self.fast_length = fast_length  # 短周期均线长度
            self.slow_length = slow_length  # 长周期均线长度
            self.long_stop = long_stop   # 多单止损幅度
            self.short_stop = short_stop    # 空单止损幅度
        except Exception as msg:
            storage.mongodb_save({"warning! 时间": get_localtime(), "error message": str(msg)}, 'logger', self.instrument_id[0:3])  # 将异常信息保存至mongodb数据库

    def begin_trade(self):
        try:
            synchronize_info = self.synchronize.match()     # 运行持仓同步功能，并返回持仓同步信息
            if "匹配" in synchronize_info:    # 如果策略持仓与账户持仓不匹配，保存持仓同步信息至mongodb数据库
                pass
            else:
                storage.mongodb_save({"时间": get_localtime(), "持仓同步信息": synchronize_info}, 'synchronize', self.instrument_id[0:3])    # 运行持仓同步
            # 计算策略信号
            fast_ma = self.indicators.MA(self.fast_length)
            slow_ma = self.indicators.MA(self.slow_length)
            cross_over = fast_ma[-2] >= slow_ma[-2] and fast_ma[-3] < slow_ma[-3]
            cross_below = slow_ma[-2] >= fast_ma[-2] and slow_ma[-3] < fast_ma[-3]
            if self.indicators.BarUpdate():
                self.counter = 0

            if self.counter < 2:
                # 按照策略信号开平仓
                if cross_over and self.counter < 1:     # 金叉时
                    if self.position.amount() == 0:
                        info = self.exchange.buy(self.market.last() * (1 + self.overprice_range), round(self.total_asset/self.market.last()/self.market.contract_value()))
                        push(info)
                        self.synchronize.save_strategy_position("long", round(self.total_asset/self.market.last()/self.market.contract_value()))
                        self.counter += 1
                    if self.position.direction() == 'short':
                        profit = self.position.covershort_profit()
                        self.total_asset += profit
                        storage.mongodb_save({"时间": get_localtime(), "profit": profit, "asset": self.total_asset}, 'asset', self.instrument_id[0:3])
                        info = self.exchange.BUY(self.market.last() * (1 - self.overprice_range), self.position.amount(), self.market.last() * (1 + self.overprice_range), round(self.total_asset/self.market.last()/self.market.contract_value()))
                        push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                        self.synchronize.save_strategy_position("long", round(self.total_asset / self.market.last() / self.market.contract_value()))
                        self.counter += 1
                if cross_below and self.counter < 1:     # 死叉时
                    if self.position.amount() == 0:
                        info = self.exchange.sellshort(self.market.last() * (1 - self.overprice_range), round(self.total_asset/self.market.last()/self.market.contract_value()))
                        push(info)
                        self.synchronize.save_strategy_position("short", round(self.total_asset / self.market.last() / self.market.contract_value()))
                        self.counter += 1
                    if self.position.direction() == 'long':
                        profit = self.position.coverlong_profit()
                        self.total_asset += profit
                        storage.mongodb_save({"时间": get_localtime(), "profit": profit, "asset": self.total_asset}, 'asset', self.instrument_id[0:3])
                        info = self.exchange.SELL(self.market.last() * (1 + self.overprice_range), self.position.amount(), self.market.last() * (1 - self.overprice_range), round(self.total_asset/self.market.last()/self.market.contract_value()))
                        push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                        self.synchronize.save_strategy_position("short", round(self.total_asset / self.market.last() / self.market.contract_value()))
                        self.counter += 1
                # 止损
                if self.position.amount() > 0:
                    if self.position.direction() == 'long' and self.market.last() <= self.position.price() * self.long_stop:
                        profit = self.position.coverlong_profit()
                        self.total_asset += profit
                        storage.mongodb_save({"时间": get_localtime(), "profit": profit, "asset": self.total_asset}, 'asset', self.instrument_id[0:3])
                        info = self.exchange.sell(self.market.last() * (1 - self.overprice_range), self.position.amount())
                        push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                        self.synchronize.save_strategy_position("none", 0)
                        self.counter += 2
                    if self.position.direction() == 'short' and self.market.last() >= self.position.price() * self.short_stop:
                        profit = self.position.covershort_profit()
                        self.total_asset += profit
                        storage.mongodb_save({"时间": get_localtime(), "profit": profit, "asset": self.total_asset}, 'asset', self.instrument_id[0:3])
                        info = self.exchange.buytocover(self.market.last() * (1 + self.overprice_range), self.position.amount())
                        push("此次盈亏：{} 当前总资金：{}".format(profit, self.total_asset) + info)
                        self.synchronize.save_strategy_position("none", 0)
                        self.counter += 2

            storage.mongodb_save({"error! 时间": get_localtime(), "error message": str(msg)}, 'logger', self.instrument_id[0:3])  # 将异常信息保存至mongodb数据库

if __name__ == "__main__":
    strategy = Strategy("TRX-USDT-201225", "3m", 5, 10, 0.98, 1.02, 20, "none", 0)
    while True:
        strategy.begin_trade()
```



+ 更多示例策略敬请期待！