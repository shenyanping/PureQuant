from purequant.exchange.okex.websocket import subscribe as okex_subscribe
from purequant.exchange.huobi.websocket import subscribe as huobi_subscribe
from purequant.exchange.huobi.websocket import huobi_swap_position_subscribe
import asyncio, uuid
from purequant.config import config
from purequant.exchange.huobi.websocket import handle_ws_data
from purequant.exceptions import *


def okex_futures_usd():
    print("Okex币本位交割合约持仓状态监控中...")
    url = 'wss://real.okex.com:8443/ws/v3'
    access_key = config.access_key
    secret_key = config.secret_key
    passphrase = config.passphrase
    delivery_date = config.delivery_date
    task1 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:BTC-USD-{}".format(delivery_date)])
    task2 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:BCH-USD-{}".format(delivery_date)])
    task3 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:BSV-USD-{}".format(delivery_date)])
    task4 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:ETH-USD-{}".format(delivery_date)])
    task5 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:ETC-USD-{}".format(delivery_date)])
    task6 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:EOS-USD-{}".format(delivery_date)])
    task7 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:LTC-USD-{}".format(delivery_date)])
    task8 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:TRX-USD-{}".format(delivery_date)])
    task9 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:XRP-USD-{}".format(delivery_date)])
    task_list = [task1, task2, task3, task4, task5, task6, task7, task8, task9]
    asyncio.run(asyncio.wait(task_list))

def okex_futures_usdt():
    print("Okex USDT本位交割合约持仓状态监控中...")
    url = 'wss://real.okex.com:8443/ws/v3'
    access_key = config.access_key
    secret_key = config.secret_key
    passphrase = config.passphrase
    delivery_date = config.delivery_date
    task1 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:BTC-USDT-{}".format(delivery_date)])
    task2 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:BCH-USDT-{}".format(delivery_date)])
    task3 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:BSV-USDT-{}".format(delivery_date)])
    task4 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:ETH-USDT-{}".format(delivery_date)])
    task5 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:ETC-USDT-{}".format(delivery_date)])
    task6 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:EOS-USDT-{}".format(delivery_date)])
    task7 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:LTC-USDT-{}".format(delivery_date)])
    task8 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:TRX-USDT-{}".format(delivery_date)])
    task9 = okex_subscribe(url, access_key, passphrase, secret_key, ["futures/position:XRP-USDT-{}".format(delivery_date)])
    task_list = [task1, task2, task3, task4, task5, task6, task7, task8, task9]
    asyncio.run(asyncio.wait(task_list))

def okex_swap_usd():
    print("Okex 永续合约持仓状态监控中...")
    url = 'wss://real.okex.com:8443/ws/v3'
    access_key = config.access_key
    secret_key = config.secret_key
    passphrase = config.passphrase
    task_list = []
    symbol_list = ['BTC-USD-SWAP', 'lTC-USD-SWAP', 'ETH-USD-SWAP', 'ETC-USD-SWAP', 'XRP-USD-SWAP',
                   'EOS-USD-SWAP', 'BCH-USD-SWAP', 'BSV-USD-SWAP', 'TRX-USD-SWAP', ]
    for item in symbol_list:
        task_list.append(okex_subscribe(url, access_key, passphrase, secret_key, ["swap/position:{}".format(item)]))
    asyncio.run(asyncio.wait(task_list))

def okex_swap_usdt():
    print("Okex 永续合约持仓状态监控中...")
    url = 'wss://real.okex.com:8443/ws/v3'
    access_key = config.access_key
    secret_key = config.secret_key
    passphrase = config.passphrase
    task_list = []
    symbol_list = ['BTC-USDT-SWAP', 'lTC-USDT-SWAP', 'ETH-USDT-SWAP', 'ETC-USDT-SWAP', 'XRP-USDT-SWAP',
                   'EOS-USDT-SWAP', 'BCH-USDT-SWAP', 'BSV-USDT-SWAP', 'TRX-USDT-SWAP', ]
    for item in symbol_list:
        task_list.append(okex_subscribe(url, access_key, passphrase, secret_key, ["swap/position:{}".format(item)]))
    asyncio.run(asyncio.wait(task_list))

def okex_spot():
    print("Okex 币币账户状态监控中...")
    url = 'wss://real.okex.com:8443/ws/v3'
    access_key = config.access_key
    secret_key = config.secret_key
    passphrase = config.passphrase
    task_list = []
    symbol_list = ['BTC', 'lTC', 'ETH', 'ETC', 'XRP',
                   'EOS', 'BCH', 'BSV', 'TRX', 'USDT']
    for item in symbol_list:
        task_list.append(okex_subscribe(url, access_key, passphrase, secret_key, ["spot/account:{}".format(item)]))
    asyncio.run(asyncio.wait(task_list))

def okex_margin():
    print("Okex 币币杠杆账户状态监控中...")
    url = 'wss://real.okex.com:8443/ws/v3'
    access_key = config.access_key
    secret_key = config.secret_key
    passphrase = config.passphrase
    task_list = []
    symbol_list = ['BTC-USDT', 'lTC-USDT', 'ETH-USDT', 'ETC-USDT', 'XRP-USDT',
                   'EOS-USDT', 'BCH-USDT', 'BSV-USDT', 'TRX-USDT']
    for item in symbol_list:
        task_list.append(okex_subscribe(url, access_key, passphrase, secret_key, ["spot/margin_account:{}".format(item)]))
    asyncio.run(asyncio.wait(task_list))

def huobi_futures():
    print("Huobi币本位交割合约持仓状态监控中...")
    url = 'wss://api.hbdm.vn/notification'
    access_key = config.access_key
    secret_key = config.secret_key
    position_subs = [
        {
            "op": "sub",
            "cid": str(uuid.uuid1()),
            "topic": "positions.*"
        }
    ]
    asyncio.run(huobi_subscribe(url, access_key, secret_key, position_subs, handle_ws_data, auth=True))

def huobi_swap():
    print("Huobi币本位永续合约持仓状态监控中...")
    url = 'wss://api.hbdm.vn/swap-notification'
    access_key = config.access_key
    secret_key = config.secret_key
    position_subs = [
        {
            "op": "sub",
            "cid": str(uuid.uuid1()),
            "topic": "positions.*"
        }
    ]
    asyncio.run(huobi_swap_position_subscribe(url, access_key, secret_key, position_subs, handle_ws_data, auth=True))


def position_update():
    """持仓状态更新自动推送"""
    if config.position_server_platform == "okex":
        if config.okex_futures_usd == "true":
            okex_futures_usd()
        if config.okex_futures_usdt == "true":
            okex_futures_usdt()
        if config.okex_swap_usd == "true":
            okex_swap_usd()
        if config.okex_swap_usdt == "true":
            okex_swap_usdt()
        if config.okex_spot == "true":
            okex_spot()
        if config.okex_margin == "true":
            okex_margin()
    if config.position_server_platform == "huobi":
        if config.huobi_futures == "true":
            huobi_futures()
        if config.huobi_swap == "true":
            huobi_swap()
    else:
        raise ExchangeError("配置文件中position sever的platform设置错误！")
