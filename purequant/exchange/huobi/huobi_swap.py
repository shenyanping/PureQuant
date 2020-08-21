# -*- coding:utf-8 -*-

"""
火币永续合约
"""


from purequant.exchange.huobi.util import http_get_request, api_key_post


class HuobiSwap:

    def __init__(self, access_key, secret_key):
        self.__url = 'https://api.hbdm.com'
        self.__access_key = access_key
        self.__secret_key = secret_key

    '''
    ======================
    Market data API
    ======================
    '''

    # 获取合约信息
    def get_contract_info(self, contract_code=''):
        """
        获取合约信息
        :param contract_code: string 大小写均支持，"BTC-USD",不填查询所有合约
        :return:
        """
        params = {'contract_code': contract_code}
        url = self.__url + '/swap-api/v1/swap_contract_info'
        return http_get_request(url, params)

    # 获取合约指数信息
    def get_contract_index(self, contract_code=''):
        """
        获取合约指数信息
        :param contract_code: string   支持大小写，"BTC-USD","ETH-USD"...
        :return:
        """
        params = {'contract_code': contract_code}
        url = self.__url + '/swap-api/v1/swap_index'
        return http_get_request(url, params)

    # 获取合约最高限价和最低限价
    def get_contract_price_limit(self, contract_code=''):
        """
        获取合约最高限价和最低限价
        :param contract_code: string	合约代码，支持大小写，BTC-USD
        :return:
        """
        params = {'contract_code': contract_code}
        url = self.__url + '/swap-api/v1/swap_price_limit'
        return http_get_request(url, params)

    # 获取当前可用合约总持仓量
    def get_contract_open_interest(self, contract_code=''):
        """
        获取当前可用合约总持仓量
        :param contract_code: string	支持大小写，"BTC-USD",不填查询所有合约
        :return:
        """
        params = {'contract_code': contract_code}
        url = self.__url + '/swap-api/v1/swap_open_interest'
        return http_get_request(url, params)

    # 获取行情深度
    def get_contract_depth(self, contract_code, type):
        """
        获取行情深度
        :param contract_code: string	支持大小写, "BTC-USD" ...
        :param type: string	(150档数据) step0, step1, step2, step3, step4, step5（合并深度1-5）；step0时，不合并深度, (20档数据) step6, step7, step8, step9, step10, step11（合并深度7-11）；step6时，不合并深度
        :return:
        """
        params = {'contract_code': contract_code,
                  'type': type}
        url = self.__url + '/swap-ex/market/depth'
        return http_get_request(url, params)

    # 获取KLine
    def get_contract_kline(self, contract_code, period, size=150):
        """
        获取KLine
        :param contract_code: 仅支持大写， "BTC-USD" ...
        :param period: K线类型		1min, 5min, 15min, 30min, 60min,4hour,1day, 1mon
        :param size: 获取数量	150	[1,2000]
        :return:
        """
        params = {'contract_code': contract_code,
                  'period': period}
        if size:
            params['size'] = size
        url = self.__url + '/swap-ex/market/history/kline'
        return http_get_request(url, params)

    # 获取聚合行情
    def get_contract_market_merged(self, contract_code):
        """
        获取聚合行情
        :param contract_code: 合约代码	仅支持大写， "BTC-USD" ...
        :return:
        """
        params = {'contract_code': contract_code}
        url = self.__url + '/swap-ex/market/detail/merged'
        return http_get_request(url, params)

    # 获取市场最近成交记录
    def get_contract_trade(self, contract_code):
        """
        获取市场最近成交记录
        :param contract_code: 合约代码,支持大小写	"BTC-USD" ...
        :return:
        """
        params = {'contract_code': contract_code}
        url = self.__url + '/swap-ex/market/trade'
        return http_get_request(url, params)

    # 批量获取最近的交易记录
    def get_contract_batch_trade(self, contract_code, size=1):
        """
        批量获取最近的交易记录
        :param contract_code: 合约代码,支持大小写	"BTC-USD" ...
        :param size: 获取交易记录的数量	1	[1, 2000]
        :return:
        """
        params = {'contract_code': contract_code,
                  'size': size}
        url = self.__url + '/swap-ex/market/history/trade'
        return http_get_request(url, params)

    '''
    ======================
    Trade/Account API
    ======================
    '''

    # 获取用户账户信息
    def get_contract_account_info(self, contract_code=''):
        """
        获取用户账户信息
        :param contract_code: 支持大小写, "BTC-USD"... ,如果缺省，默认返回所有合约
        :return:
        """
        params = {}
        if contract_code:
            params["contract_code"] = contract_code
        request_path = '/swap-api/v1/swap_account_info'
        return api_key_post(self.__url, request_path, params, self.__access_key, self.__secret_key)

    # 获取用户持仓信息
    def get_contract_position_info(self, contract_code=''):
        """
        获取用户持仓信息
        :param contract_code: 合约代码		支持大小写，"BTC-USD"... ,如果缺省，默认返回所有合约
        :return:
        """
        params = {}
        if contract_code:
            params["contract_code"] = contract_code
        request_path = '/swap-api/v1/swap_position_info'
        return api_key_post(self.__url, request_path, params, self.__access_key, self.__secret_key)

    # 合约下单
    def send_contract_order(self, contract_code,
                            client_order_id, price, volume, direction, offset,
                            lever_rate, order_price_type):
        """
        合约下单
        :param contract_code: 合约代码,支持大小写,"BTC-USD"
        :param client_order_id: 客户自己填写和维护，必须为数字, 请注意必须小于等于9223372036854775807
        :param price: 价格
        :param volume: 委托数量(张)
        :param direction: "buy":买 "sell":卖
        :param offset: "open":开 "close":平
        :param lever_rate: 杠杆倍数[“开仓”若有10倍多单，就不能再下20倍多单;首次使用高倍杠杆(>20倍)，请使用主账号登录web端同意高倍杠杆协议后，才能使用接口下高倍杠杆(>20倍)]
        :param order_price_type: 订单报价类型 "limit":限价
                                            "opponent":对手价
                                            "post_only":只做maker单, post only下单只受用户持仓数量限制,
                                            optimal_5：最优5档、optimal_10：最优10档、optimal_20：最优20档，
                                            "fok":FOK订单，
                                            "ioc":IOC订单,
                                            opponent_ioc"： 对手价-IOC下单，
                                            "optimal_5_ioc"：最优5档-IOC下单，
                                            "optimal_10_ioc"：最优10档-IOC下单，
                                            "optimal_20_ioc"：最优20档-IOC下单,
                                            "opponent_fok"： 对手价-FOK下单，
                                            "optimal_5_fok"：最优5档-FOK下单，
                                            "optimal_10_fok"：最优10档-FOK下单，
                                            "optimal_20_fok"：最优20档-FOK下单
        :return:
        """
        params = {"price": price,
                  "volume": volume,
                  "direction": direction,
                  "offset": offset,
                  "lever_rate": lever_rate,
                  "order_price_type": order_price_type}
        if contract_code:
            params['contract_code'] = contract_code
        if client_order_id:
            params['client_order_id'] = client_order_id

        request_path = '/swap-api/v1/swap_order'
        return api_key_post(self.__url, request_path, params, self.__access_key, self.__secret_key)

    # 合约批量下单
    def send_contract_batchorder(self, orders_data):
        """
        合约批量下单
        :param orders_data: 详见https://docs.huobigroup.com/docs/coin_margined_swap/v1/cn/#33123f0c09
        :return:
        """
        params = orders_data
        request_path = '/swap-api/v1/swap_batchorder'
        return api_key_post(self.__url, request_path, params, self.__access_key, self.__secret_key)

    # 撤销订单
    def cancel_contract_order(self, contract_code, order_id='', client_order_id=''):
        """
        撤销订单
        :param contract_code: 合约代码,支持大小写,"BTC-USD"
        :param order_id: 订单ID(多个订单ID中间以","分隔,一次最多允许撤消10个订单)
        :param client_order_id: 客户订单ID(多个订单ID中间以","分隔,一次最多允许撤消10个订单)
        :return:
        """
        params = {"contract_code": contract_code}
        if order_id:
            params["order_id"] = order_id
        if client_order_id:
            params["client_order_id"] = client_order_id

        request_path = '/swap-api/v1/swap_cancel'
        return api_key_post(self.__url, request_path, params, self.__access_key, self.__secret_key)

    # 全部撤单
    def cancel_all_contract_order(self, contract_code):
        """
        全部撤单
        :param contract_code: 合约代码,支持大小写，"BTC-USD"
        :return:
        """
        params = {"contract_code": contract_code}
        request_path = '/swap-api/v1/swap_cancelall'
        return api_key_post(self.__url, request_path, params, self.__access_key, self.__secret_key)

    # 获取合约订单信息
    def get_contract_order_info(self, contract_code, order_id='', client_order_id=''):
        """
        获取合约订单信息
        :param contract_code: 合约代码,支持大小写,"BTC-USD"
        :param order_id: 订单ID(多个订单ID中间以","分隔,一次最多允许查询50个订单)
        :param client_order_id: 客户订单ID(多个订单ID中间以","分隔,一次最多允许查询50个订单)
        :return:
        """
        params = {"contract_code": contract_code}
        if order_id:
            params["order_id"] = order_id
        if client_order_id:
            params["client_order_id"] = client_order_id

        request_path = '/swap-api/v1/swap_order_info'
        return api_key_post(self.__url, request_path, params, self.__access_key, self.__secret_key)

    # 获取合约订单明细信息
    def get_contract_order_detail(self, contract_code, order_id, order_type, created_at, page_index=None, page_size=None):
        """
        获取合约订单明细信息
        :param contract_code: 合约代码,支持大小写,"BTC-USD"
        :param order_id: 订单id
        :param order_type: 订单类型，1:报单 、 2:撤单 、 3:强平、4:交割
        :param created_at: 下单时间戳
        :param page_index: 第几页,不填第一页
        :param page_size: 不填默认20，不得多于50
        :return:
        """
        params = {"contract_code": contract_code,
                  "order_id": order_id,
                  "order_type": order_type,
                  "created_at": created_at}
        if page_index:
            params["page_index"] = page_index
        if page_size:
            params["page_size"] = page_size

        request_path = '/swap-api/v1/swap_order_detail'
        return api_key_post(self.__url, request_path, params, self.__access_key, self.__secret_key)

    # 获取合约当前未成交委托
    def get_contract_open_orders(self, contract_code=None, page_index=None, page_size=None):
        """
        获取合约当前未成交委托
        :param contract_code: 合约代码	支持大小写,"BTC-USD" ...
        :param page_index: 页码，不填默认第1页
        :param page_size: 不填默认20，不得多于50
        :return:
        """
        params = {}
        if contract_code:
            params["contract_code"] = contract_code
        if page_index:
            params["page_index"] = page_index
        if page_size:
            params["page_size"] = page_size

        request_path = '/swap-api/v1/swap_openorders'
        return api_key_post(self.__url, request_path, params, self.__access_key, self.__secret_key)

    # 获取合约历史委托
    def get_contract_history_orders(self, contract_code, trade_type, type, status, create_date,
                                    page_index=None, page_size=None):
        """
        获取合约历史委托
        :param contract_code: 支持大小写,"BTC-USD" ...
        :param trade_type: 0:全部,1:买入开多,2: 卖出开空,3: 买入平空,4: 卖出平多,5: 卖出强平,6: 买入强平,7:交割平多,8: 交割平空, 11:减仓平多，12:减仓平空
        :param type: 1:所有订单,2:结束状态的订单
        :param status: 可查询多个状态，"3,4,5" , 0:全部,3:未成交, 4: 部分成交,5: 部分成交已撤单,6: 全部成交,7:已撤单
        :param create_date: 可随意输入正整数，如果参数超过90则默认查询90天的数据
        :param page_index: 页码，不填默认第1页
        :param page_size: 每页条数，不填默认20
        :return:
        """
        params = {"contract_code": contract_code,
                  "trade_type": trade_type,
                  "type": type,
                  "status": status,
                  "create_date": create_date}
        if page_index:
            params["page_index"] = page_index
        if page_size:
            params["page_size"] = page_size

        request_path = '/swap-api/v1/swap_hisorders'
        return api_key_post(self.__url, request_path, params, self.__access_key, self.__secret_key)



