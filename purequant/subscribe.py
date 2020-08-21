from purequant.config import config
from purequant.exchange.huobi.websocket import subscribe, handle_ws_data
from purequant.exchange.okex.websocket import subscribe_without_login
from purequant.exceptions import *
import asyncio, uuid

def markets_update():
    print("行情服务器已启动，数据正获取并保存至MongoDB数据库中！")
    if config.markets_server_platform == "okex":
        try:
            url = 'wss://real.okex.com:8443/ws/v3'
            channels_list = config.markets_channels_list
            task_list = []
            for item in channels_list:
                task_list.append(subscribe_without_login(url, item))
            asyncio.run(asyncio.wait(task_list))
        except Exception as e:
            print(e)
    if config.markets_server_platform == "huobi_futures":
        try:
            market_url = 'wss://www.hbdm.vn/ws'
            access_key = ""
            secret_key = ""
            channels_list = config.markets_channels_list
            market_subs = []
            for item in channels_list:
                market_subs.append({"sub": item[0], "id": str(uuid.uuid1())})
            asyncio.run(subscribe(market_url, access_key, secret_key, market_subs, handle_ws_data, auth=False))
        except Exception as e:
            print(e)
    if config.markets_server_platform == "huobi_swap":
        try:
            market_url = 'wss://api.hbdm.vn/swap-ws'
            access_key = ""
            secret_key = ""
            channels_list = config.markets_channels_list
            market_subs = []
            for item in channels_list:
                market_subs.append({"sub": item[0], "id": str(uuid.uuid1())})
            asyncio.run(subscribe(market_url, access_key, secret_key, market_subs, handle_ws_data, auth=False))
        except Exception as e:
            print(e)
    else:
        raise ExchangeError("配置文件中markets sever的platform设置错误！")