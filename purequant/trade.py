# -*- coding:utf-8 -*-

"""
交易模块

Author: Gary-Hertel
Date:   2020/07/09
email: interstella.ranger2020@gmail.com
"""
import time
from purequant.exchange.okex import spot_api as okexspot
from purequant.exchange.okex import futures_api as okexfutures
from purequant.exchange.okex import swap_api as okexswap
from purequant.exchange.huobi import huobi_futures as huobifutures
from purequant.exchange.huobi import huobi_swap as huobiswap
from purequant.time import ts_to_utc_str
from purequant.exchange.huobi import huobi_spot as huobispot
from purequant.config import config
from purequant.exceptions import *
from purequant.storage import storage

class OKEXFUTURES:
    """okex交割合约操作  https://www.okex.com/docs/zh/#futures-README"""
    def __init__(self, access_key, secret_key, passphrase, instrument_id):
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__passphrase = passphrase
        self.__instrument_id = instrument_id
        self.__okex_futures = okexfutures.FutureAPI(self.__access_key, self.__secret_key, self.__passphrase)

    def buy(self, price, size, order_type=None):
        if config.backtest != "enabled":   # 实盘模式
            order_type = order_type or 0    # 如果不填order_type,则默认为普通委托
            result = self.__okex_futures.take_order(self.__instrument_id, 1, price, size, order_type=order_type) # 下订单
            order_info = self.get_order_info(order_id=result['order_id'])   # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ": # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true": # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "等待成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true": # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['order_id'])
                if order_info["订单状态"] == "等待成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['order_id'])
                state = self.get_order_info(order_id=result['order_id'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:   # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:   # 回测模式
            return "回测模拟下单成功！"

    def sell(self, price, size, order_type=None):
        if config.backtest != "enabled":    # 实盘模式
            order_type = order_type or 0
            result = self.__okex_futures.take_order(self.__instrument_id, 3, price, size, order_type=order_type)
            order_info = self.get_order_info(order_id=result['order_id'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "等待成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['order_id'])
                if order_info["订单状态"] == "等待成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['order_id'])
                state = self.get_order_info(order_id=result['order_id'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:   # 回测模式
            return "回测模拟下单成功！"


    def sellshort(self, price, size, order_type=None):
        if config.backtest != "enabled":   # 实盘模式
            order_type = order_type or 0
            result = self.__okex_futures.take_order(self.__instrument_id, 2, price, size, order_type=order_type)
            order_info = self.get_order_info(order_id=result['order_id'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "等待成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['order_id'])
                if order_info["订单状态"] == "等待成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['order_id'])
                state = self.get_order_info(order_id=result['order_id'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:   # 回测模式
            return "回测模拟下单成功！"

    def buytocover(self, price, size, order_type=None):
        if config.backtest != "enabled":    # 实盘模式
            order_type = order_type or 0
            result = self.__okex_futures.take_order(self.__instrument_id, 4, price, size, order_type=order_type)
            order_info = self.get_order_info(order_id=result['order_id'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "等待成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['order_id'])
                if order_info["订单状态"] == "等待成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['order_id'])
                state = self.get_order_info(order_id=result['order_id'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:   # 回测模式
            return "回测模拟下单成功！"

    def BUY(self, cover_short_price, cover_short_size, open_long_price, open_long_size, order_type=None):
        if config.backtest != "enabled":    # 实盘模式
            order_type = order_type or 0
            result1 = self.buytocover(cover_short_price, cover_short_size, order_type)
            if "完全成交" in result1:
                result2 = self.buy(open_long_price, open_long_size, order_type)
                return result1 + result2
            else:
                return result1
        else:   # 回测模式
            return "回测模拟下单成功！"

    def SELL(self, cover_long_price, cover_long_size, open_short_price, open_short_size, order_type=None):
        if config.backtest != "enabled":    # 实盘模式
            order_type = order_type or 0
            result1 = self.sell(cover_long_price, cover_long_size, order_type)
            if "完全成交" in result1:
                result2 = self.sellshort(open_short_price, open_short_size, order_type)
                return result1 + result2
            else:
                return result1
        else:   # 回测模式
            return "回测模拟下单成功！"

    def get_order_list(self, state, limit):
        receipt = self.__okex_futures.get_order_list(self.__instrument_id, state=state, limit=limit)
        return receipt

    def revoke_order(self, order_id):
        receipt = self.__okex_futures.revoke_order(self.__instrument_id, order_id)
        if receipt['error_code'] == "0":
            return '【交易提醒】撤单成功'
        else:
            return '【交易提醒】撤单失败' + receipt['error_message']

    def get_order_info(self, order_id):
        result = self.__okex_futures.get_order_info(self.__instrument_id, order_id)
        instrument_id = result['instrument_id']
        action = None
        if result['type'] == '1':
            action = "买入开多"
        elif result['type'] == '2':
            action = "卖出开空"
        if result['type'] == '3':
            action = "卖出平多"
        if result['type'] == '4':
            action = "买入平空"
        if int(result['state']) == 2:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "完全成交", "成交均价": result['price_avg'],
                    "数量": result['filled_qty'],
                    "成交金额": round(int(result['contract_val']) * int(result['filled_qty']) * float(result['price_avg']),
                                  2)}
            return dict
        elif int(result['state']) == -2:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "失败"}
            return dict
        elif int(result['state']) == -1:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "撤单成功"}
            return dict
        elif int(result['state']) == 0:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "等待成交"}
            return dict
        elif int(result['state']) == 1:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "部分成交", "成交均价": result['price_avg'],
                    "已成交数量": result['filled_qty'], "成交金额": round(
                    int(result['contract_val']) * int(result['filled_qty']) * float(result['price_avg']), 2)}
            return dict
        elif int(result['state']) == 3:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "下单中"}
            return dict
        elif int(result['state']) == 4:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "撤单中"}
            return dict


    def get_kline(self, time_frame):
        if time_frame == "1m" or time_frame == "1M":
            granularity = '60'
        elif time_frame == '3m' or time_frame == "3M":
            granularity = '180'
        elif time_frame == '5m' or time_frame == "5M":
            granularity = '300'
        elif time_frame == '15m' or time_frame == "15M":
            granularity = '900'
        elif time_frame == '30m' or time_frame == "30M":
            granularity = '1800'
        elif time_frame == '1h' or time_frame == "1H":
            granularity = '3600'
        elif time_frame == '2h' or time_frame == "2H":
            granularity = '7200'
        elif time_frame == '4h' or time_frame == "4H":
            granularity = '14400'
        elif time_frame == '6h' or time_frame == "6H":
            granularity = '21600'
        elif time_frame == '12h' or time_frame == "12H":
            granularity = '43200'
        elif time_frame == '1d' or time_frame == "1D":
            granularity = '86400'
        else:
            raise KlineError
        receipt = self.__okex_futures.get_kline(self.__instrument_id, granularity=granularity)
        return receipt

    def get_position(self):
        result = self.__okex_futures.get_specific_position(instrument_id=self.__instrument_id)
        if int(result['holding'][0]['long_qty']) > 0:
            dict = {'direction': 'long', 'amount': int(result['holding'][0]['long_qty']),
                    'price': float(result['holding'][0]['long_avg_cost'])}
            return dict
        elif int(result['holding'][0]['short_qty']) > 0:
            dict = {'direction': 'short', 'amount': int(result['holding'][0]['short_qty']),
                    'price': float(result['holding'][0]['short_avg_cost'])}
            return dict
        else:
            dict = {'direction': 'none', 'amount': 0, 'price': 0.0}
            return dict

    def get_ticker(self):
        receipt = self.__okex_futures.get_specific_ticker(instrument_id=self.__instrument_id)
        return receipt

    def get_contract_value(self):
        receipt = self.__okex_futures.get_products()
        t = 0
        result = {}
        for item in receipt:
            result[item['instrument_id']] = item['contract_val']
            t += 1
        return result

class OKEXSPOT:
    """okex现货操作  https://www.okex.com/docs/zh/#spot-README"""
    def __init__(self, access_key, secret_key, passphrase, instrument_id):
        """

        :param access_key:
        :param secret_key:
        :param passphrase:
        :param instrument_id: e.g. etc-usdt
        """
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__passphrase = passphrase
        self.__instrument_id = instrument_id
        self.__okex_spot = okexspot.SpotAPI(self.__access_key, self.__secret_key, self.__passphrase)

    def buy(self, price, size, order_type=None, type=None, notional=""):
        """
        okex现货买入
        :param price:价格
        :param size:数量
        :param order_type:参数填数字
        0：普通委托（order type不填或填0都是普通委托）
        1：只做Maker（Post only）
        2：全部成交或立即取消（FOK）
        3：立即成交并取消剩余（IOC）
        :param type:limit或market（默认是limit）。当以market（市价）下单，order_type只能选择0（普通委托）
        :param notional:买入金额，市价买入时必填notional
        :return:
        """
        if config.backtest != "enabled":    # 实盘模式
            order_type = order_type or 0
            type=type or "limit"
            result = self.__okex_spot.take_order(instrument_id=self.__instrument_id, side="buy", type=type, size=size, price=price, order_type=order_type, notional=notional)
            order_info = self.get_order_info(order_id=result['order_id'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "等待成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":    # 部分成交时撤单然后重发委托，下单数量为原下单数量减去已成交数量
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['order_id'])
                if order_info["订单状态"] == "等待成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":    # 部分成交时撤单然后重发委托，下单数量为原下单数量减去已成交数量
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['order_id'])
                state = self.get_order_info(order_id=result['order_id'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:   # 回测模式
            return "回测模拟下单成功！"

    def sell(self, price, size, order_type=None, type=None):
        """
        okex现货卖出
        :param price: 价格
        :param size:卖出数量，市价卖出时必填size
        :param order_type:参数填数字
        0：普通委托（order type不填或填0都是普通委托）
        1：只做Maker（Post only）
        2：全部成交或立即取消（FOK）
        3：立即成交并取消剩余（IOC）
        :param type:limit或market（默认是limit）。当以market（市价）下单，order_type只能选择0（普通委托）
        :return:
        """
        if config.backtest != "enabled":    # 实盘模式
            order_type = order_type or 0
            type = type or "limit"
            result = self.__okex_spot.take_order(instrument_id=self.__instrument_id, side="sell", type=type, size=size, price=price, order_type=order_type)
            order_info = self.get_order_info(order_id=result['order_id'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "等待成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":    # 部分成交时撤单然后重发委托，下单数量为原下单数量减去已成交数量
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['order_id'])
                if order_info["订单状态"] == "等待成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":    # 部分成交时撤单然后重发委托，下单数量为原下单数量减去已成交数量
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['order_id'])
                state = self.get_order_info(order_id=result['order_id'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:   # 回测模式
            return "回测模拟下单成功！"

    def get_order_list(self, state, limit):
        receipt = self.__okex_spot.get_orders_list(self.__instrument_id, state=state, limit=limit)
        return receipt

    def revoke_order(self, order_id):
        receipt = self.__okex_spot.revoke_order(self.__instrument_id, order_id)
        if receipt['error_code'] == "0":
            return '【交易提醒】撤单成功'
        else:
            return '【交易提醒】撤单失败' + receipt['error_message']

    def get_order_info(self, order_id):
        result = self.__okex_spot.get_order_info(self.__instrument_id, order_id)
        instrument_id = result['instrument_id']
        action = None
        if result['side'] == 'buy':
            action = "买入开多"
        if result['side'] == 'sell':
            action = "卖出平多"
        if int(result['state']) == 2:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "完全成交", "成交均价": result['price_avg'],
                    "数量": result['filled_size'], "成交金额": result['filled_notional']}
            return dict
        elif int(result['state']) == -2:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "失败"}
            return dict
        elif int(result['state']) == -1:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "撤单成功"}
            return dict
        elif int(result['state']) == 0:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "等待成交"}
            return dict
        elif int(result['state']) == 1:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "部分成交", "成交均价": result['price_avg'],
                    "已成交数量": result['filled_size'], "已成交金额": result['filled_notional']}
            return dict
        elif int(result['state']) == 3:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "下单中"}
            return dict
        elif int(result['state']) == 4:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "撤单中"}
            return dict

    def get_kline(self, time_frame):
        if time_frame == "1m" or time_frame == "1M":
            granularity = '60'
        elif time_frame == '3m' or time_frame == "3M":
            granularity = '180'
        elif time_frame == '5m' or time_frame == "5M":
            granularity = '300'
        elif time_frame == '15m' or time_frame == "15M":
            granularity = '900'
        elif time_frame == '30m' or time_frame == "30M":
            granularity = '1800'
        elif time_frame == '1h' or time_frame == "1H":
            granularity = '3600'
        elif time_frame == '2h' or time_frame == "2H":
            granularity = '7200'
        elif time_frame == '4h' or time_frame == "4H":
            granularity = '14400'
        elif time_frame == '6h' or time_frame == "6H":
            granularity = '21600'
        elif time_frame == '12h' or time_frame == "12H":
            granularity = '43200'
        elif time_frame == '1d' or time_frame == "1D":
            granularity = '86400'
        else:
            raise KlineError
        receipt = self.__okex_spot.get_kline(self.__instrument_id, granularity=granularity)
        return receipt

    def get_position(self):
        """OKEX现货，如交易对为'ETC-USDT', 则获取的是ETC的可用余额"""
        currency = self.__instrument_id.split('-')[0]
        receipt = self.__okex_spot.get_coin_account_info(currency=currency)
        direction = 'long'
        amount = receipt['balance']
        price = None
        result = {'direction': direction, 'amount': amount, 'price': price}
        return result

    def get_ticker(self):
        receipt = self.__okex_spot.get_specific_ticker(instrument_id=self.__instrument_id)
        return receipt


class OKEXSWAP:
    """okex永续合约操作 https://www.okex.com/docs/zh/#swap-README"""
    def __init__(self, access_key, secret_key, passphrase, instrument_id):
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__passphrase = passphrase
        self.__instrument_id = instrument_id
        self.__okex_swap = okexswap.SwapAPI(self.__access_key, self.__secret_key, self.__passphrase)

    def buy(self, price, size, order_type=None):
        if config.backtest != "enabled":    # 实盘模式
            order_type = order_type or 0  # 如果不填order_type,则默认为普通委托
            result = self.__okex_swap.take_order(self.__instrument_id, 1, price, size, order_type=order_type)
            order_info = self.get_order_info(order_id=result['order_id'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "等待成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['order_id'])
                if order_info["订单状态"] == "等待成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['order_id'])
                state = self.get_order_info(order_id=result['order_id'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:   # 回测模式
            return "回测模拟下单成功！"

    def sell(self, price, size, order_type=None):
        if config.backtest != "enabled":
            order_type = order_type or 0
            result = self.__okex_swap.take_order(self.__instrument_id, 3, price, size, order_type=order_type)
            order_info = self.get_order_info(order_id=result['order_id'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "等待成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['order_id'])
                if order_info["订单状态"] == "等待成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['order_id'])
                state = self.get_order_info(order_id=result['order_id'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:   # 回测模式
            return "回测模拟下单成功！"

    def sellshort(self, price, size, order_type=None):
        if config.backtest != "enabled":
            order_type = order_type or 0
            result = self.__okex_swap.take_order(self.__instrument_id, 2, price, size, order_type=order_type)
            order_info = self.get_order_info(order_id=result['order_id'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "等待成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['order_id'])
                if order_info["订单状态"] == "等待成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['order_id'])
                state = self.get_order_info(order_id=result['order_id'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:   # 回测模式
            return "回测模拟下单成功！"

    def buytocover(self, price, size, order_type=None):
        if config.backtest != "enabled":
            order_type = order_type or 0
            result = self.__okex_swap.take_order(self.__instrument_id, 4, price, size, order_type=order_type)
            order_info = self.get_order_info(order_id=result['order_id'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "等待成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['order_id'])
                        state = self.get_order_info(order_id=result['order_id'])
                        if state['订单状态'] == "撤单成功":
                            return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['order_id'])
                if order_info["订单状态"] == "等待成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['order_id'])
                    state = self.get_order_info(order_id=result['order_id'])
                    if state['订单状态'] == "撤单成功":
                        return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['order_id'])
                state = self.get_order_info(order_id=result['order_id'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:   # 回测模式
            return "回测模拟下单成功！"

    def BUY(self, cover_short_price, cover_short_size, open_long_price, open_long_size, order_type=None):
        if config.backtest != "enabled":
            order_type = order_type or 0
            result1 = self.buytocover(cover_short_price, cover_short_size, order_type)
            if "完全成交" in result1:
                result2 = self.buy(open_long_price, open_long_size, order_type)
                return result1 + result2
            else:
                return result1
        else:   # 回测模式
            return "回测模拟下单成功！"

    def SELL(self, cover_long_price, cover_long_size, open_short_price, open_short_size, order_type=None):
        if config.backtest != "enabled":
            order_type = order_type or 0
            result1 = self.sell(cover_long_price, cover_long_size, order_type)
            if "完全成交" in result1:
                result2 = self.sellshort(open_short_price, open_short_size, order_type)
                return result1 + result2
            else:
                return result1
        else:  # 回测模式
            return "回测模拟下单成功！"

    def get_order_list(self, state, limit):
        receipt = self.__okex_swap.get_order_list(self.__instrument_id, state=state, limit=limit)
        return receipt

    def revoke_order(self, order_id):
        receipt = self.__okex_swap.revoke_order(self.__instrument_id, order_id)
        if receipt['error_code'] == "0":
            return '【交易提醒】撤单成功'
        else:
            return '【交易提醒】撤单失败' + receipt['error_message']

    def get_order_info(self, order_id):
        result = self.__okex_swap.get_order_info(self.__instrument_id, order_id)
        instrument_id = result['instrument_id']
        action = None
        if result['type'] == '1':
            action = "买入开多"
        elif result['type'] == '2':
            action = "卖出开空"
        if result['type'] == '3':
            action = "卖出平多"
        if result['type'] == '4':
            action = "买入平空"
        if int(result['state']) == 2:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "完全成交", "成交均价": result['price_avg'],
                    "数量": result['filled_qty'], "成交金额": round(
                    int(result['contract_val']) * int(result['filled_qty']) * float(result['price_avg']), 2)}
            return dict
        elif int(result['state']) == -2:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "失败"}
            return dict
        elif int(result['state']) == -1:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "撤单成功"}
            return dict
        elif int(result['state']) == 0:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "等待成交"}
            return dict
        elif int(result['state']) == 1:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "部分成交", "成交均价": result['price_avg'],
                    "已成交数量": result['filled_qty'], "成交金额": round(
                    int(result['contract_val']) * int(result['filled_qty']) * float(result['price_avg']), 2)}
            return dict
        elif int(result['state']) == 3:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "下单中"}
            return dict
        elif int(result['state']) == 4:
            dict = {"交易所": "Okex", "合约ID": instrument_id, "方向": action, "订单状态": "撤单中"}
            return dict

    def get_kline(self, time_frame):
        if time_frame == "1m" or time_frame == "1M":
            granularity = '60'
        elif time_frame == '3m' or time_frame == "3M":
            granularity = '180'
        elif time_frame == '5m' or time_frame == "5M":
            granularity = '300'
        elif time_frame == '15m' or time_frame == "15M":
            granularity = '900'
        elif time_frame == '30m' or time_frame == "30M":
            granularity = '1800'
        elif time_frame == '1h' or time_frame == "1H":
            granularity = '3600'
        elif time_frame == '2h' or time_frame == "2H":
            granularity = '7200'
        elif time_frame == '4h' or time_frame == "4H":
            granularity = '14400'
        elif time_frame == '6h' or time_frame == "6H":
            granularity = '21600'
        elif time_frame == '12h' or time_frame == "12H":
            granularity = '43200'
        elif time_frame == '1d' or time_frame == "1D":
            granularity = '86400'
        else:
            raise KlineError
        receipt = self.__okex_swap.get_kline(self.__instrument_id, granularity=granularity)
        return receipt

    def get_position(self):
        receipt = self.__okex_swap.get_specific_position(self.__instrument_id)
        direction = receipt['holding'][0]['side']
        amount = int(receipt['holding'][0]['position'])
        price = float(receipt['holding'][0]['avg_cost'])
        if amount == 0:
            direction = "none"
        result = {'direction': direction, 'amount': amount, 'price': price}
        return result

    def get_contract_value(self):
        receipt = self.__okex_swap.get_instruments()
        t = 0
        result = {}
        for item in receipt:
            result[item['instrument_id']]=item['contract_val']
            t += 1
        return result

    def get_ticker(self):
        receipt = self.__okex_swap.get_specific_ticker(instrument_id=self.__instrument_id)
        return receipt

class HUOBIFUTURES:
    """火币合约 https://huobiapi.github.io/docs/dm/v1/cn/#5ea2e0cde2"""
    def __init__(self, access_key, secret_key, instrument_id):
        """

        :param access_key:
        :param secret_key:
        :param instrument_id: 'BTC-201225'
        """
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__instrument_id = instrument_id
        self.__huobi_futures = huobifutures.HuobiFutures(self.__access_key, self.__secret_key)
        self.__symbol = self.__instrument_id[0:3]
        self.__contract_code = self.__instrument_id[0:3] + self.__instrument_id[4:10]

        if self.__instrument_id[6:8] == '03' or self.__instrument_id[6:8] == '09':
            self.__contract_type = "quarter"
        elif self.__instrument_id[6:8] == '06' or self.__instrument_id[6:8] == '12':
            self.__contract_type = "next_quarter"
        else:
            self.__contract_type = None
            raise SymbolError("交易所: Huobi 合约ID错误，只支持当季与次季合约！")

    def buy(self, price, size, order_type=None, lever_rate=None):
        """
        火币交割合约下单买入开多，只支持季度和次季合约，杠杆倍数如不填杠杆倍数则默认20倍杠杆
        :param self.__instrument_id: 合约ID 例如：'BTC-201225'
        :param price:   下单价格
        :param size:    下单数量
        :param order_type:  0：限价单
                            1：只做Maker（Post only）
                            2：全部成交或立即取消（FOK）
                            3：立即成交并取消剩余（IOC）
                            4：对手价下单
        :return:
        """
        if config.backtest != "enabled":
            lever_rate=20 or lever_rate
            order_type = order_type or 0
            if order_type == 0:
                order_price_type = 'limit'
            elif order_type == 1:
                order_price_type = "post_only"
            elif order_type == 2:
                order_price_type = "fok"
            elif order_type == 3:
                order_price_type = "ioc"
            elif order_type == 4:
                order_price_type = "opponent"
            else:
                return "【交易提醒】交易所：Huobi 订单报价类型错误！"
            result = self.__huobi_futures.send_contract_order(symbol=self.__symbol, contract_type=self.__contract_type, contract_code=self.__contract_code,
                            client_order_id='', price=price, volume=size, direction='buy',
                            offset='open', lever_rate=20, order_price_type=order_price_type)
            order_info = self.get_order_info(order_id = result['data']['order_id_str'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id = result['data']['order_id_str'])
                        state = self.get_order_info(order_id = result['data']['order_id_str'])
                        if state['订单状态'] == "撤单成功":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id = result['data']['order_id_str'])
                        state = self.get_order_info(order_id = result['data']['order_id_str'])
                        if state['订单状态'] == "部分成交撤销":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id = result['data']['order_id_str'])
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    self.revoke_order(order_id = result['data']['order_id_str'])
                    state = self.get_order_info(order_id = result['data']['order_id_str'])
                    if state['订单状态'] == "撤单成功":
                        return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id = result['data']['order_id_str'])
                    state = self.get_order_info(order_id = result['data']['order_id_str'])
                    if state['订单状态'] == "部分成交撤销":
                        return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id = result['data']['order_id_str'])
                state = self.get_order_info(order_id = result['data']['order_id_str'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:
            return "回测模拟下单成功！"


    def sell(self, price, size, order_type=None, lever_rate=None):
        """
        火币交割合约下单卖出平多，只支持季度和次季合约，杠杆倍数如不填杠杆倍数则默认20倍杠杆
        :param self.__instrument_id: 合约ID 例如：'BTC-201225'
        :param price:   下单价格
        :param size:    下单数量
        :param order_type:  0：限价单
                            1：只做Maker（Post only）
                            2：全部成交或立即取消（FOK）
                            3：立即成交并取消剩余（IOC）
                            4：对手价下单
        :return:
        """
        if config.backtest != "enabled":
            lever_rate=20 or lever_rate
            order_type = order_type or 0
            if order_type == 0:
                order_price_type = 'limit'
            elif order_type == 1:
                order_price_type = "post_only"
            elif order_type == 2:
                order_price_type = "fok"
            elif order_type == 3:
                order_price_type = "ioc"
            elif order_type == 4:
                order_price_type = "opponent"
            else:
                return "【交易提醒】交易所: Huobi 订单报价类型错误！"
            result = self.__huobi_futures.send_contract_order(symbol=self.__symbol, contract_type=self.__contract_type, contract_code=self.__contract_code,
                            client_order_id='', price=price, volume=size, direction='sell',
                            offset='close', lever_rate=20, order_price_type=order_price_type)
            order_info = self.get_order_info(order_id=result['data']['order_id_str'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "撤单成功":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "部分成交撤销":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['data']['order_id_str'])
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "撤单成功":
                        return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "部分成交撤销":
                        return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['data']['order_id_str'])
                state = self.get_order_info(order_id=result['data']['order_id_str'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:
            return "回测模拟下单成功！"

    def buytocover(self, price, size, order_type=None, lever_rate=None):
        """
        火币交割合约下单买入平空，只支持季度和次季合约，杠杆倍数如不填杠杆倍数则默认20倍杠杆
        :param self.__instrument_id: 合约ID 例如：'BTC-201225'
        :param price:   下单价格
        :param size:    下单数量
        :param order_type:  0：限价单
                            1：只做Maker（Post only）
                            2：全部成交或立即取消（FOK）
                            3：立即成交并取消剩余（IOC）
                            4：对手价下单
        :return:
        """
        if config.backtest != "enabled":
            lever_rate=20 or lever_rate
            order_type = order_type or 0
            if order_type == 0:
                order_price_type = 'limit'
            elif order_type == 1:
                order_price_type = "post_only"
            elif order_type == 2:
                order_price_type = "fok"
            elif order_type == 3:
                order_price_type = "ioc"
            elif order_type == 4:
                order_price_type = "opponent"
            else:
                return "【交易提醒】交易所: Huobi订单报价类型错误！"
            result = self.__huobi_futures.send_contract_order(symbol=self.__symbol, contract_type=self.__contract_type, contract_code=self.__contract_code,
                            client_order_id='', price=price, volume=size, direction='buy',
                            offset='close', lever_rate=20, order_price_type=order_price_type)
            order_info = self.get_order_info(order_id=result['data']['order_id_str'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "撤单成功":
                            return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "部分成交撤销":
                            return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['data']['order_id_str'])
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "撤单成功":
                        return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "部分成交撤销":
                        return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['data']['order_id_str'])
                state = self.get_order_info(order_id=result['data']['order_id_str'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:
            return "回测模拟下单成功！"

    def sellshort(self, price, size, order_type=None, lever_rate=None):
        """
        火币交割合约下单卖出开空，只支持季度和次季合约，杠杆倍数如不填杠杆倍数则默认20倍杠杆
        :param self.__instrument_id: 合约ID 例如：'BTC-201225'
        :param price:   下单价格
        :param size:    下单数量
        :param order_type:  0：限价单
                            1：只做Maker（Post only）
                            2：全部成交或立即取消（FOK）
                            3：立即成交并取消剩余（IOC）
                            4：对手价下单
        :return:
        """
        if config.backtest != "enabled":
            lever_rate=20 or lever_rate
            order_type = order_type or 0
            if order_type == 0:
                order_price_type = 'limit'
            elif order_type == 1:
                order_price_type = "post_only"
            elif order_type == 2:
                order_price_type = "fok"
            elif order_type == 3:
                order_price_type = "ioc"
            elif order_type == 4:
                order_price_type = "opponent"
            else:
                return "【交易提醒】交易所: Huobi 订单报价类型错误！"
            result = self.__huobi_futures.send_contract_order(symbol=self.__symbol, contract_type=self.__contract_type, contract_code=self.__contract_code,
                            client_order_id='', price=price, volume=size, direction='sell',
                            offset='open', lever_rate=20, order_price_type=order_price_type)
            order_info = self.get_order_info(order_id=result['data']['order_id_str'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "撤单成功":
                            return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "部分成交撤销":
                            return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['data']['order_id_str'])
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "撤单成功":
                        return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "部分成交撤销":
                        return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['data']['order_id_str'])
                state = self.get_order_info(order_id=result['data']['order_id_str'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:
            return "回测模拟下单成功！"

    def BUY(self, cover_short_price, cover_short_size, open_long_price, open_long_size, order_type=None):
        """火币交割合约平空开多"""
        if config.backtest != "enabled":
            order_type = order_type or 0
            receipt1 = self.buytocover(cover_short_price, cover_short_size, order_type)
            if "完全成交" in receipt1:
                receipt2 = self.buy(open_long_price, open_long_size, order_type)
                return receipt1 + receipt2
            else:
                return receipt1
        else:
            return "回测模拟下单成功！"

    def SELL(self, cover_long_price, cover_long_size, open_short_price, open_short_size, order_type=None):
        """火币交割合约平多开空"""
        if config.backtest != "enabled":
            order_type = order_type or 0
            receipt1 = self.sell(cover_long_price, cover_long_size, order_type)
            if "完全成交" in receipt1:
                receipt2 = self.sellshort(open_short_price, open_short_size, order_type)
                return receipt1 + receipt2
            else:
                return receipt1
        else:
            return "回测模拟下单成功！"

    def revoke_order(self, order_id):
        receipt = self.__huobi_futures.cancel_contract_order(self.__symbol, order_id)
        if receipt['status'] == "ok":
            return '【交易提醒】交易所: Huobi 撤单成功'
        else:
            return '【交易提醒】交易所: Huobi 撤单失败' + receipt['data']['errors'][0]['err_msg']

    def get_order_info(self, order_id):
        result = self.__huobi_futures.get_contract_order_info(self.__symbol, order_id)
        instrument_id = result['data'][0]['contract_code']
        state = int(result['data'][0]['status'])
        avg_price = result['data'][0]['trade_avg_price']
        amount = result['data'][0]['trade_volume']
        turnover = result['data'][0]['trade_turnover']
        if result['data'][0]['direction'] == "buy" and result['data'][0]['offset'] == "open":
            action = "买入开多"
        elif result['data'][0]['direction'] == "buy" and result['data'][0]['offset'] == "close":
            action = "买入平空"
        elif result['data'][0]['direction'] == "sell" and result['data'][0]['offset'] == "open":
            action = "卖出开空"
        elif result['data'][0]['direction'] == "sell" and result['data'][0]['offset'] == "close":
            action = "卖出平多"
        else:
            action = "交易方向错误！"
        if state == 6:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "完全成交", "成交均价": avg_price,
                    "数量": amount,
                    "成交金额": turnover}
            return dict
        elif state == 1:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "准备提交"}
            return dict
        elif state == 7:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "撤单成功"}
            return dict
        elif state == 2:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "准备提交"}
            return dict
        elif state == 4:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "部分成交", "成交均价": avg_price,
                    "已成交数量": amount, "成交金额": turnover}
            return dict
        elif state == 3:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "已提交"}
            return dict
        elif state == 11:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "撤单中"}
            return dict
        elif state == 5:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "部分成交撤销", "成交均价": avg_price,
                    "数量": amount, "成交金额": turnover}
            return dict

    def get_kline(self, time_frame):
        if self.__instrument_id[6:8] == "03" or self.__instrument_id[6:8] == "09":
            symbol = self.__symbol + "_" + 'CQ'
        elif self.__instrument_id[6:8] == "06" or self.__instrument_id[6:8] == "12":
            symbol = self.__symbol + "_" + 'NQ'
        else:
            symbol = None
            raise SymbolError
        if time_frame == '1m' or time_frame == '1M':
            period = '1min'
        elif time_frame == '5m' or time_frame == '5M':
            period = '5min'
        elif time_frame == '15m' or time_frame == '15M':
            period = '15min'
        elif time_frame == '30m' or time_frame == '30M':
            period = '30min'
        elif time_frame == '1h' or time_frame == '1H':
            period = '60min'
        elif time_frame == '4h' or time_frame == '4H':
            period = '4hour'
        elif time_frame == '1d' or time_frame == '1D':
            period = '1day'
        else:
            raise KlineError("k线周期错误，k线周期只能是【1m, 5m, 15m, 30m, 1h, 4h, 1d】!")
        records = self.__huobi_futures.get_contract_kline(symbol=symbol, period=period)['data']
        length = len(records)
        j = 1
        list = []
        while j < length:
            for item in records:
                item = [ts_to_utc_str(item['id']), item['open'], item['high'], item['low'], item['close'], item['vol'], round(item['amount'], 2)]
                list.append(item)
                j+=1
        list.reverse()
        return list

    def get_position(self):
        receipt = self.__huobi_futures.get_contract_position_info(self.__symbol)
        if receipt['data'] != []:
            direction = receipt['data'][0]['direction']
            amount = receipt['data'][0]['volume']
            price = receipt['data'][0]['cost_hold']
            if amount > 0 and direction == "buy":
                dict = {'direction': 'long', 'amount': amount, 'price': price}
                return dict
            elif amount > 0 and direction == "sell":
                dict = {'direction': 'short', 'amount': amount, 'price': price}
                return dict
        else:
            dict = {'direction': 'none', 'amount': 0, 'price': 0.0}
        return dict

    def get_ticker(self):
        if self.__instrument_id[6:8] == "03" or self.__instrument_id[6:8]=="09":
            symbol = self.__symbol + "_" + 'CQ'
        elif self.__instrument_id[6:8] == "06" or self.__instrument_id[6:8] == "12":
            symbol = self.__symbol + "_" + 'NQ'
        else:
            symbol = None
            raise SymbolError("交易所: Huobi 合约ID错误，只支持当季与次季合约！")
        receipt = self.__huobi_futures.get_contract_market_merged(symbol)
        last = receipt['tick']['close']
        return {"last": last}

    def get_contract_value(self):
        receipt = self.__huobi_futures.get_contract_info()
        t = 0
        result = {}
        for item in receipt['data']:
            result[self.__symbol + "-" + item['contract_code'][-6:]] = item['contract_size']
            t += 1
        return result

class HUOBISWAP:
    """火币永续合约 https://docs.huobigroup.com/docs/coin_margined_swap/v1/cn/#5ea2e0cde2"""

    def __init__(self, access_key, secret_key, instrument_id):
        """
        :param access_key:
        :param secret_key:
        :param instrument_id: 'BTC-USD'
        """
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__instrument_id = instrument_id
        self.__huobi_swap = huobiswap.HuobiSwap(self.__access_key, self.__secret_key)

    def buy(self, price, size, order_type=None, lever_rate=None):
        """
        火币永续合约下单买入开多，如不填杠杆倍数则默认20倍杠杆
        :param self.__instrument_id: 合约ID 例如：'BTC-USD'
        :param price:   下单价格
        :param size:    下单数量
        :param order_type:  0：限价单
                            1：只做Maker（Post only）
                            2：全部成交或立即取消（FOK）
                            3：立即成交并取消剩余（IOC）
                            4：对手价下单
        :return:
        """
        if config.backtest != "enabled":
            lever_rate=20 or lever_rate
            order_type = order_type or 0
            if order_type == 0:
                order_price_type = 'limit'
            elif order_type == 1:
                order_price_type = "post_only"
            elif order_type == 2:
                order_price_type = "fok"
            elif order_type == 3:
                order_price_type = "ioc"
            elif order_type == 4:
                order_price_type = "opponent"
            else:
                return "【交易提醒】交易所: Huobi 订单报价类型错误！"
            result = self.__huobi_swap.send_contract_order(contract_code=self.__instrument_id,
                            client_order_id='', price=price, volume=size, direction='buy',
                            offset='open', lever_rate=lever_rate, order_price_type=order_price_type)
            order_info = self.get_order_info(order_id=result['data']['order_id_str'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "撤单成功":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "部分成交撤销":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['data']['order_id_str'])
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "撤单成功":
                        return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "部分成交撤销":
                        return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['data']['order_id_str'])
                state = self.get_order_info(order_id=result['data']['order_id_str'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:
            return "回测模拟下单成功！"

    def sell(self, price, size, order_type=None, lever_rate=None):
        """
        火币永续合约下单卖出平多，如不填杠杆倍数则默认20倍杠杆
        :param self.__instrument_id: 合约ID 例如：'BTC-USD'
        :param price:   下单价格
        :param size:    下单数量
        :param order_type:  0：限价单
                            1：只做Maker（Post only）
                            2：全部成交或立即取消（FOK）
                            3：立即成交并取消剩余（IOC）
                            4：对手价下单
        :return:
        """
        if config.backtest != "enabled":
            lever_rate=20 or lever_rate
            order_type = order_type or 0
            if order_type == 0:
                order_price_type = 'limit'
            elif order_type == 1:
                order_price_type = "post_only"
            elif order_type == 2:
                order_price_type = "fok"
            elif order_type == 3:
                order_price_type = "ioc"
            elif order_type == 4:
                order_price_type = "opponent"
            else:
                return "【交易提醒】交易所: Huobi 订单报价类型错误！"
            result = self.__huobi_swap.send_contract_order(contract_code=self.__instrument_id,
                            client_order_id='', price=price, volume=size, direction='sell',
                            offset='close', lever_rate=lever_rate, order_price_type=order_price_type)
            order_info = self.get_order_info(order_id=result['data']['order_id_str'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "撤单成功":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "部分成交撤销":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['data']['order_id_str'])
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "撤单成功":
                        return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "部分成交撤销":
                        return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['data']['order_id_str'])
                state = self.get_order_info(order_id=result['data']['order_id_str'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:
            return "回测模拟下单成功！"

    def buytocover(self, price, size, order_type=None, lever_rate=None):
        """
        火币永续合约下单买入平空,如不填杠杆倍数则默认20倍杠杆
        :param self.__instrument_id: 合约ID 例如：'BTC-USD'
        :param price:   下单价格
        :param size:    下单数量
        :param order_type:  0：限价单
                            1：只做Maker（Post only）
                            2：全部成交或立即取消（FOK）
                            3：立即成交并取消剩余（IOC）
                            4：对手价下单
        :return:
        """
        if config.backtest != "enabled":
            lever_rate=20 or lever_rate
            order_type = order_type or 0
            if order_type == 0:
                order_price_type = 'limit'
            elif order_type == 1:
                order_price_type = "post_only"
            elif order_type == 2:
                order_price_type = "fok"
            elif order_type == 3:
                order_price_type = "ioc"
            elif order_type == 4:
                order_price_type = "opponent"
            else:
                return "【交易提醒】交易所: Huobi 订单报价类型错误！"
            result = self.__huobi_swap.send_contract_order(contract_code=self.__instrument_id,
                            client_order_id='', price=price, volume=size, direction='buy',
                            offset='close', lever_rate=lever_rate, order_price_type=order_price_type)
            order_info = self.get_order_info(order_id=result['data']['order_id_str'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "撤单成功":
                            return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "部分成交撤销":
                            return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['data']['order_id_str'])
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "撤单成功":
                        return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "部分成交撤销":
                        return self.buytocover(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['data']['order_id_str'])
                state = self.get_order_info(order_id=result['data']['order_id_str'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:
            return "回测模拟下单成功！"

    def sellshort(self, price, size, order_type=None, lever_rate=None):
        """
        火币永续合约下单卖出开空，如不填杠杆倍数则默认20倍杠杆
        :param self.__instrument_id: 合约ID 例如：'BTC-USD'
        :param price:   下单价格
        :param size:    下单数量
        :param order_type:  0：限价单
                            1：只做Maker（Post only）
                            2：全部成交或立即取消（FOK）
                            3：立即成交并取消剩余（IOC）
                            4：对手价下单
        :return:
        """
        if config.backtest != "enabled":
            lever_rate=20 or lever_rate
            order_type = order_type or 0
            if order_type == 0:
                order_price_type = 'limit'
            elif order_type == 1:
                order_price_type = "post_only"
            elif order_type == 2:
                order_price_type = "fok"
            elif order_type == 3:
                order_price_type = "ioc"
            elif order_type == 4:
                order_price_type = "opponent"
            else:
                return "【交易提醒】交易所: Huobi 订单报价类型错误！"
            result = self.__huobi_swap.send_contract_order(contract_code=self.__instrument_id,
                            client_order_id='', price=price, volume=size, direction='sell',
                            offset='open', lever_rate=lever_rate, order_price_type=order_price_type)
            order_info = self.get_order_info(order_id=result['data']['order_id_str'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "撤单成功":
                            return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "部分成交撤销":
                            return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['data']['order_id_str'])
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "撤单成功":
                        return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "部分成交撤销":
                        return self.sellshort(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['data']['order_id_str'])
                state = self.get_order_info(order_id=result['data']['order_id_str'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:
            return "回测模拟下单成功！"

    def BUY(self, cover_short_price, cover_short_size, open_long_price, open_long_size, order_type=None):
        """火币交割合约平空开多"""
        if config.backtest != "enabled":
            order_type = order_type or 0
            receipt1 = self.buytocover(cover_short_price, cover_short_size, order_type)
            if "完全成交" in receipt1:
                receipt2 = self.buy(open_long_price, open_long_size, order_type)
                return receipt1 + receipt2
            else:
                return receipt1
        else:
            return "回测模拟下单成功！"

    def SELL(self, cover_long_price, cover_long_size, open_short_price, open_short_size, order_type=None):
        """火币交割合约平多开空"""
        if config.backtest != "enabled":
            order_type = order_type or 0
            receipt1 = self.sell(cover_long_price, cover_long_size, order_type)
            if "完全成交" in receipt1:
                receipt2 = self.sellshort(open_short_price, open_short_size, order_type)
                return receipt1 + receipt2
            else:
                return receipt1
        else:
            return "回测模拟下单成功！"

    def revoke_order(self, order_id):
        receipt = self.__huobi_swap.cancel_contract_order(self.__instrument_id, order_id)
        if receipt['status'] == "ok":
            return '【交易提醒】交易所: Huobi 撤单成功'
        else:
            return '【交易提醒】交易所: Huobi 撤单失败' + receipt['data']['errors'][0]['err_msg']

    def get_order_info(self, order_id):
        result = self.__huobi_swap.get_contract_order_info(self.__instrument_id, order_id)
        instrument_id = self.__instrument_id
        state = int(result['data'][0]['status'])
        avg_price = result['data'][0]['trade_avg_price']
        amount = result['data'][0]['trade_volume']
        turnover = result['data'][0]['trade_turnover']
        if result['data'][0]['direction'] == "buy" and result['data'][0]['offset'] == "open":
            action = "买入开多"
        elif result['data'][0]['direction'] == "buy" and result['data'][0]['offset'] == "close":
            action = "买入平空"
        elif result['data'][0]['direction'] == "sell" and result['data'][0]['offset'] == "open":
            action = "卖出开空"
        elif result['data'][0]['direction'] == "sell" and result['data'][0]['offset'] == "close":
            action = "卖出平多"
        else:
            action = "交易方向错误！"
        if state == 6:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "完全成交", "成交均价": avg_price,
                    "数量": amount,
                    "成交金额": turnover}
            return dict
        elif state == 1:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "准备提交"}
            return dict
        elif state == 7:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "撤单成功"}
            return dict
        elif state == 2:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "准备提交"}
            return dict
        elif state == 4:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "部分成交", "成交均价": avg_price,
                    "已成交数量": amount, "成交金额": turnover}
            return dict
        elif state == 3:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "已提交"}
            return dict
        elif state == 11:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "撤单中"}
            return dict
        elif state == 5:
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "部分成交撤销", "成交均价": avg_price,
                    "数量": amount, "成交金额": turnover}
            return dict

    def get_kline(self, time_frame):
        if time_frame == '1m' or time_frame == '1M':
            period = '1min'
        elif time_frame == '5m' or time_frame == '5M':
            period = '5min'
        elif time_frame == '15m' or time_frame == '15M':
            period = '15min'
        elif time_frame == '30m' or time_frame == '30M':
            period = '30min'
        elif time_frame == '1h' or time_frame == '1H':
            period = '60min'
        elif time_frame == '4h' or time_frame == '4H':
            period = '4hour'
        elif time_frame == '1d' or time_frame == '1D':
            period = '1day'
        else:
            raise KlineError("交易所: Huobi k线周期错误，k线周期只能是【1m, 5m, 15m, 30m, 1h, 4h, 1d】!")
        records = self.__huobi_swap.get_contract_kline(self.__instrument_id, period=period)['data']
        length = len(records)
        j = 1
        list = []
        while j < length:
            for item in records:
                item = [ts_to_utc_str(item['id']), item['open'], item['high'], item['low'], item['close'], item['vol'], round(item['amount'], 2)]
                list.append(item)
                j+=1
        list.reverse()
        return list

    def get_position(self):
        receipt = self.__huobi_swap.get_contract_position_info(self.__instrument_id)
        if receipt['data'] != []:
            direction = receipt['data'][0]['direction']
            amount = receipt['data'][0]['volume']
            price = receipt['data'][0]['cost_hold']
            if amount > 0 and direction == "buy":
                dict = {'direction': 'long', 'amount': amount, 'price': price}
                return dict
            elif amount > 0 and direction == "sell":
                dict = {'direction': 'short', 'amount': amount, 'price': price}
                return dict
        else:
            dict = {'direction': 'none', 'amount': 0, 'price': 0.0}
        return dict

    def get_ticker(self):
        receipt = self.__huobi_swap.get_contract_market_merged(self.__instrument_id)
        last = receipt['tick']['close']
        return {"last": last}

    def get_contract_value(self):
        receipt = self.__huobi_swap.get_contract_info()
        t = 0
        result = {}
        for item in receipt['data']:
            result[self.__instrument_id] = item['contract_size']
            t += 1
        return result

class HUOBISPOT:
    """火币现货"""

    def __init__(self, access_key, secret_key, instrument_id):
        """

        :param access_key:
        :param secret_key:
        :param instrument_id: e.g. 'ETC-USDT'
        """
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__instrument_id = (instrument_id.split('-')[0] + instrument_id.split('-')[1]).lower()
        self.__huobi_spot = huobispot.HuobiSVC(self.__access_key, self.__secret_key)
        self.__currency = (instrument_id.split('-')[0]).lower()
        self.__account_id = self.__huobi_spot.get_accounts()['data'][0]['id']
        self.__symbol = (instrument_id).lower()  # 获取合约面值的函数中所用到的交易对未处理前的格式

    def buy(self, price, size, order_type=None):
        """
        火币现货买入开多
        :param price: 价格
        :param size: 数量
        :param order_type: 填 0或者不填都是限价单，
                            1：只做Maker（Post only）
                            2：全部成交或立即取消（FOK）
                            3：立即成交并取消剩余（IOC）
                            4.市价买入
        :return:
        """
        if config.backtest != "enabled":
            order_type=order_type or 'buy-limit'
            if order_type == 0:
                order_type = 'buy-limit'
            elif order_type == 1:
                order_type = 'buy-limit-maker'
            elif order_type == 2:
                order_type = 'buy-limit-fok'
            elif order_type == 3:
                order_type = 'buy-ioc'
            elif order_type == 4:
                order_type = 'buy-market'
            result = self.__huobi_spot.send_order(self.__account_id, size, 'spot-api', self.__instrument_id, _type=order_type, price=price)
            order_info = self.get_order_info(order_id=result['data']['order_id_str'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "撤单成功":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "部分成交撤销":
                            return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['data']['order_id_str'])
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "撤单成功":
                        return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "部分成交撤销":
                        return self.buy(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['data']['order_id_str'])
                state = self.get_order_info(order_id=result['data']['order_id_str'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:
            return "回测模拟下单成功！"

    def sell(self, price, size, order_type=None):
        """
        火币现货卖出平多
        :param price: 价格
        :param size: 数量
        :param order_type: 填 0或者不填都是限价单，
                            1：只做Maker（Post only）
                            2：全部成交或立即取消（FOK）
                            3：立即成交并取消剩余（IOC）
                            4.市价卖出
        :return:
        """
        if config.backtest != "enabled":
            order_type=order_type or 'sell-limit'
            if order_type == 0:
                order_type = 'sell-limit'
            elif order_type == 1:
                order_type = 'sell-limit-maker'
            elif order_type == 2:
                order_type = 'sell-limit-fok'
            elif order_type == 3:
                order_type = 'sell-ioc'
            elif order_type == 4:
                order_type = 'sell-market'
            result = self.__huobi_spot.send_order(self.__account_id, size, 'spot-api', self.__instrument_id, _type=order_type, price=price)
            order_info = self.get_order_info(order_id=result['data']['order_id_str'])  # 下单后查询一次订单状态
            if order_info["订单状态"] == "完全成交" or order_info["订单状态"] == "失败 ":  # 如果订单状态为"完全成交"或者"失败"，返回结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
            # 如果订单状态不是"完全成交"或者"失败"
            if config.price_cancellation == "true":  # 选择了价格撤单时，如果最新价超过委托价一定幅度，撤单重发，返回下单结果
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "撤单成功":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    if float(self.get_ticker()['last']) >= price * (1 + config.price_cancellation_amplitude):
                        self.revoke_order(order_id=result['data']['order_id_str'])
                        state = self.get_order_info(order_id=result['data']['order_id_str'])
                        if state['订单状态'] == "部分成交撤销":
                            return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.time_cancellation == "true":  # 选择了时间撤单时，如果委托单发出多少秒后不成交，撤单重发，直至完全成交，返回成交结果
                time.sleep(config.time_cancellation_seconds)
                order_info = self.get_order_info(order_id=result['data']['order_id_str'])
                if order_info["订单状态"] == "准备提交" or order_info["订单状态"] == "已提交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "撤单成功":
                        return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size)
                if order_info["订单状态"] == "部分成交":
                    self.revoke_order(order_id=result['data']['order_id_str'])
                    state = self.get_order_info(order_id=result['data']['order_id_str'])
                    if state['订单状态'] == "部分成交撤销":
                        return self.sell(float(self.get_ticker()['last']) * (1 + config.reissue_order), size - state["已成交数量"])
            if config.automatic_cancellation == "true":
                # 如果订单未完全成交，且未设置价格撤单和时间撤单，且设置了自动撤单，就自动撤单并返回下单结果与撤单结果
                self.revoke_order(order_id=result['data']['order_id_str'])
                state = self.get_order_info(order_id=result['data']['order_id_str'])
                return '【交易提醒】' + "下单结果：{}".format(state)
            else:  # 未启用交易助手时，下单并查询订单状态后直接返回下单结果
                return '【交易提醒】' + "下单结果：{}".format(order_info)
        else:
            return "回测模拟下单成功！"

    def get_order_info(self, order_id):
        result = self.__huobi_spot.order_info(order_id)
        instrument_id = result['data']['symbol']
        action = None
        if "buy" in result['data']['type']:
            action = "买入开多"
        if  "sell" in result['data']['type']:
            action = "卖出平多"

        if result["data"]['state'] == 'filled':
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "完全成交", "成交均价": result['data']['price'],
                    "数量": result["data"]["amount"], "成交金额": result['data']["field-cash-amount"]}
            return dict
        elif result["data"]['state'] == 'canceled':
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "撤单成功"}
            return dict
        elif result["data"]['state'] == 'partial-filled':
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "部分成交", "成交均价": result['data']['price'],
                    "已成交数量": result["data"]["field-amount"], "成交金额": result['data']["field-cash-amount"]}
            return dict
        elif result["data"]['state'] == 'partial-canceled':
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "部分成交撤销"}
            return dict
        elif result["data"]['state'] == 'submitted':
            dict = {"交易所": "Huobi", "合约ID": instrument_id, "方向": action, "订单状态": "已提交"}
            return dict

    def revoke_order(self, order_id):
        receipt = self.__huobi_spot.cancel_order(order_id)
        if receipt['status'] == "ok":
            return '【交易提醒】交易所: Huobi 撤单成功'
        else:
            return '【交易提醒】交易所: Huobi 撤单失败' + receipt['data']['errors'][0]['err_msg']

    def get_kline(self, time_frame):
        if time_frame == '1m' or time_frame == '1M':
            period = '1min'
        elif time_frame == '5m' or time_frame == '5M':
            period = '5min'
        elif time_frame == '15m' or time_frame == '15M':
            period = '15min'
        elif time_frame == '30m' or time_frame == '30M':
            period = '30min'
        elif time_frame == '1h' or time_frame == '1H':
            period = '60min'
        elif time_frame == '4h' or time_frame == '4H':
            period = '4hour'
        elif time_frame == '1d' or time_frame == '1D':
            period = '1day'
        else:
            raise KlineError("交易所: Huobi k线周期错误，k线周期只能是【1m, 5m, 15m, 30m, 1h, 4h, 1d】!")
        records = self.__huobi_spot.get_kline(self.__instrument_id, period=period)['data']
        length = len(records)
        j = 1
        list = []
        while j < length:
            for item in records:
                item = [ts_to_utc_str(item['id']), item['open'], item['high'], item['low'], item['close'], item['vol'],
                        round(item['amount'], 2)]
                list.append(item)
                j += 1
        return list

    def get_position(self):
        """获取当前交易对的计价货币的可用余额，如当前交易对为etc-usdt, 则获取的是etc的可用余额"""
        receipt = self.__huobi_spot.get_balance_currency(self.__account_id, self.__currency)
        direction = 'long'
        amount = receipt[self.__currency]
        price = None
        result = {'direction': direction, 'amount': amount, 'price': price}
        return result

    def get_ticker(self):
        receipt = self.__huobi_spot.get_ticker(self.__instrument_id)
        last = receipt['tick']['close']
        return {"last": last}