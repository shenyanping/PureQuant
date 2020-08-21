import base64
import datetime
import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import requests
import pandas as pd

# In general, the domain api-aws.huobi.pro is optimized for AWS client, the latency will be lower.
MARKET_URL = "https://api.huobi.pro"
TRADE_URL = "https://api.huobi.pro"
AWS_MARKET_URL = "https://api-aws.huobi.pro"
AWS_TRADE_URL = "https://api-aws.huobi.pro"

class HuobiSVC:
    def __init__(self, access_key, secret_key, url_type='normal'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.market_url = AWS_MARKET_URL if url_type == 'aws' else MARKET_URL
        self.trade_url = AWS_TRADE_URL if url_type == 'aws' else TRADE_URL

    # get KLine
    def get_kline(self, symbol, period, size=150):
        """
        :param symbol: btcusdt, ethbtc, ...
        :param period: 可选值：{1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
        :param size: 可选值： [1,2000]
        :return:
        """
        params = {'symbol': symbol,
                  'period': period,
                  'size': size}

        url = self.market_url + '/market/history/kline'
        return self.http_get_request(url, params)

    # get market prices
    def get_kline_df(self, symbol, period, size):
        res = self.get_kline(symbol, period, size)
        if res['status'] == 'ok':
            kline_df = pd.DataFrame(res['data'])
            return kline_df
        else:
            raise Exception('Query failed with status: {}'.format(res))

    # get market depth
    def get_depth(self, symbol, type):
        """
        :param symbol
        :param type: 可选值：{ percent10, step0, step1, step2, step3, step4, step5 }
        :return:
        """
        params = {'symbol': symbol,
                  'type': type}

        url = self.market_url + '/market/depth'
        return self.http_get_request(url, params)

    # get trade detail
    def get_trade(self, symbol):
        """
        :param symbol
        :return:
        """
        params = {'symbol': symbol}

        url = self.market_url + '/market/trade'
        return self.http_get_request(url, params)

    # Tickers detail
    def get_tickers(self):
        """
        :return:
        """
        params = {}
        url = self.market_url + '/market/tickers'
        return self.http_get_request(url, params)

    # get merge ticker
    def get_ticker(self, symbol):
        """
        :param symbol:
        :return:
        """
        params = {'symbol': symbol}

        url = self.market_url + '/market/detail/merged'
        return self.http_get_request(url, params)

    # get Market Detail 24 hour volume
    def get_detail(self, symbol):
        """
        :param symbol
        :return:
        """
        params = {'symbol': symbol}

        url = self.market_url + '/market/detail'
        return self.http_get_request(url, params)

    # get available symbols
    def get_symbols(self, long_polling=None):
        """
        """
        params = {}
        if long_polling:
            params['long-polling'] = long_polling
        path = '/v1/common/symbols'
        return self.api_key_get(params, path)

    # Get available currencies
    def get_currencies(self):
        """
        :return:
        """
        params = {}
        url = self.market_url + '/v1/common/currencys'

        return self.http_get_request(url, params)

    # Get all the trading assets
    def get_trading_assets(self):
        """
        :return:
        """
        params = {}
        url = self.market_url + '/v1/common/symbols'

        return self.http_get_request(url, params)

    '''
    Trade/Account API
    '''

    def get_accounts(self):
        """
        :return:
        """
        path = "/v1/account/accounts"
        params = {}
        return self.api_key_get(params, path)

    # get account balance
    def get_balance(self, acct_id=None):
        """
        :param acct_id
        :return:
        """

        if not acct_id:
            accounts = self.get_accounts()
            acct_id = accounts['data'][0]['id']

        url = "/v1/account/accounts/{0}/balance".format(acct_id)
        params = {"account-id": acct_id}
        return self.api_key_get(params, url)

    # get balance for a currency
    def get_balance_currency(self, acct_id, currency):
        """
        获取某个币种的可用余额
        :param acct_id: account-id
        :param currency: e.g. etc
        :return:
        """
        try:
            balance = 0
            res = self.get_balance(acct_id=acct_id)
            l = []
            list = res['data']['list']
            for item in list:
                if item['type'] == 'trade':
                    l.append({item['currency']: item['balance']})
            for x in l:
                if '%s'%currency in x.keys():
                   balance = x['%s'%currency]
                else:
                    pass
            return {currency: balance}
        except Exception as msg:
            return msg

    # Making Orders
    def send_order(self, acct_id, amount, source, symbol, _type, price=0, stop_price=0, operator=None):
        """
        :param acct_id: account id
        :param amount:
        :param source: 如果使用借贷资产交易，请在下单接口,请求参数source中填写'margin-api'
        :param symbol:
        :param _type: options {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param price:
        :param stop_price:
        :param operator: gte – greater than and equal (>=), lte – less than and equal (<=)
        :return:
        """

        params = {"account-id": acct_id,
                  "amount": amount,
                  "symbol": symbol,
                  "type": _type,
                  "source": source}
        if price:
            params["price"] = price
        if stop_price:
            params["stop-price"] = stop_price
        if operator:
            params["operator"] = operator

        url = '/v1/order/orders/place'
        return self.api_key_post(params, url)

    # cancel an order
    def cancel_order(self, order_id):
        """
        :param order_id:
        :return:
        """
        params = {}
        url = "/v1/order/orders/{0}/submitcancel".format(order_id)
        return self.api_key_post(params, url)

    # get an order info
    def order_info(self, order_id):
        """
        :param order_id:
        :return:
        """
        params = {}
        url = "/v1/order/orders/{0}".format(order_id)
        return self.api_key_get(params, url)

    # get order results
    def order_matchresults(self, order_id):
        """
        :param order_id:
        :return:
        """
        params = {}
        url = "/v1/order/orders/{0}/matchresults".format(order_id)
        return self.api_key_get(params, url)

    # get order list
    def orders_list(self, symbol, states, types=None, start_date=None, end_date=None, _from=None, direct=None, size=None):
        """
        :param symbol:
        :param states: options {pre-submitted 准备提交, submitted 已提交, partial-filled 部分成交, partial-canceled 部分成交撤销, filled 完全成交, canceled 已撤销}
        :param types: options {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param start_date:
        :param end_date:
        :param _from:
        :param direct: options {prev 向前，next 向后}
        :param size:
        :return:
        """
        params = {'symbol': symbol,
                  'states': states}

        if types:
            params['types'] = types
        if start_date:
            params['start-date'] = start_date
        if end_date:
            params['end-date'] = end_date
        if _from:
            params['from'] = _from
        if direct:
            params['direct'] = direct
        if size:
            params['size'] = size
        url = '/v1/order/orders'
        return self.api_key_get(params, url)

    # get matched orders
    def orders_matchresults(self, symbol, types=None, start_date=None, end_date=None, _from=None, direct=None, size=None):
        """
        :param symbol:
        :param types: options {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param start_date:
        :param end_date:
        :param _from:
        :param direct: options {prev 向前，next 向后}
        :param size:
        :return:
        """
        params = {'symbol': symbol}

        if types:
            params['types'] = types
        if start_date:
            params['start-date'] = start_date
        if end_date:
            params['end-date'] = end_date
        if _from:
            params['from'] = _from
        if direct:
            params['direct'] = direct
        if size:
            params['size'] = size
        url = '/v1/order/matchresults'
        return self.api_key_get(params, url)

    # get open orders
    def open_orders(self, account_id, symbol, side='', size=10):
        """
        :param symbol:
        :return:
        """
        params = {}
        url = "/v1/order/openOrders"
        if symbol:
            params['symbol'] = symbol
        if account_id:
            params['account-id'] = account_id
        if side:
            params['side'] = side
        if size:
            params['size'] = size

        return self.api_key_get(params, url)

    # batch cancel orders
    def cancel_open_orders(self, account_id, symbol, side='', size=10):
        """
        :param symbol:
        :return:
        """
        params = {}
        url = "/v1/order/orders/batchCancelOpenOrders"
        if symbol:
            params['symbol'] = symbol
        if account_id:
            params['account-id'] = account_id
        if side:
            params['side'] = side
        if size:
            params['size'] = size

        return self.api_key_post(params, url)

    # withdraw currencies
    def withdraw(self, address, amount, currency, fee=0, addr_tag=""):
        """
        :param address_id:
        :param amount:
        :param currency:btc, ltc, bcc, eth, etc ...(火币Pro支持的币种)
        :param fee:
        :param addr-tag:
        :return: {
                  "status": "ok",
                  "data": 700
                }
        """
        params = {'address': address,
                  'amount': amount,
                  "currency": currency,
                  "fee": fee,
                  "addr-tag": addr_tag}
        url = '/v1/dw/withdraw/api/create'

        return self.api_key_post(params, url)

    # cancel withdraw order
    def cancel_withdraw(self, address_id):
        """
        :param address_id:
        :return: {
                  "status": "ok",
                  "data": 700
                }
        """
        params = {}
        url = '/v1/dw/withdraw-virtual/{0}/cancel'.format(address_id)

        return self.api_key_post(params, url)

    '''
    MARGIN API
    '''

    # create and send margin order
    def send_margin_order(self, account_id, amount, source, symbol, _type, price=0):
        """
        :param account_id:
        :param amount:
        :param source: 'margin-api'
        :param symbol:
        :param _type: options {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param price:
        :return:
        """
        try:
            accounts = self.get_accounts()
            acct_id = accounts['data'][0]['id']
        except BaseException as e:
            print('get acct_id error.%s' % e)
            acct_id = account_id

        params = {"account-id": acct_id,
                  "amount": amount,
                  "symbol": symbol,
                  "type": _type,
                  "source": 'margin-api'}
        if price:
            params["price"] = price

        url = '/v1/order/orders/place'
        return self.api_key_post(params, url)

    # exchange account to margin account
    def exchange_to_margin(self, symbol, currency, amount):
        """
        :param amount:
        :param currency:
        :param symbol:
        :return:
        """
        params = {"symbol": symbol,
                  "currency": currency,
                  "amount": amount}

        url = "/v1/dw/transfer-in/margin"
        return self.api_key_post(params, url)

    # margin account to exchange account
    def margin_to_exchange(self, symbol, currency, amount):
        """
        :param amount:
        :param currency:
        :param symbol:
        :return:
        """
        params = {"symbol": symbol,
                  "currency": currency,
                  "amount": amount}

        url = "/v1/dw/transfer-out/margin"
        return self.api_key_post(params, url)

    # get margin
    def get_margin(self, symbol, currency, amount):
        """
        :param amount:
        :param currency:
        :param symbol:
        :return:
        """
        params = {"symbol": symbol,
                  "currency": currency,
                  "amount": amount}
        url = "/v1/margin/orders"
        return self.api_key_post(params, url)

    # repay
    def repay_margin(self, order_id, amount):
        """
        :param order_id:
        :param amount:
        :return:
        """
        params = {"order-id": order_id,
                  "amount": amount}
        url = "/v1/margin/orders/{0}/repay".format(order_id)
        return self.api_key_post(params, url)

    # loan order
    def loan_orders(self, symbol, currency, start_date="", end_date="", start="", direct="", size=""):
        """
        :param symbol:
        :param currency:
        :param direct: prev 向前，next 向后
        :return:
        """
        params = {"symbol": symbol,
                  "currency": currency}
        if start_date:
            params["start-date"] = start_date
        if end_date:
            params["end-date"] = end_date
        if start:
            params["from"] = start
        if direct and direct in ["prev", "next"]:
            params["direct"] = direct
        if size:
            params["size"] = size
        url = "/v1/margin/loan-orders"
        return self.api_key_get(params, url)

    # get margin balance
    def margin_balance(self, symbol):
        """
        :param symbol:
        :return:
        """
        params = {}
        url = "/v1/margin/accounts/balance"
        if symbol:
            params['symbol'] = symbol

        return self.api_key_get(params, url)

    def http_get_request(self, url, params, add_to_headers=None):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        }
        if add_to_headers:
            headers.update(add_to_headers)
        postdata = urllib.parse.urlencode(params)
        response = requests.get(url, postdata, headers=headers, timeout=5)
        try:

            if response.status_code == 200:
                return response.json()
            else:
                return
        except BaseException as e:
            print("httpGet failed, detail is:%s,%s" % (response.text, e))
            return

    def http_post_request(self, url, params, add_to_headers=None):
        headers = {
            "Accept": "application/json",
            'Content-Type': 'application/json'
        }
        if add_to_headers:
            headers.update(add_to_headers)
        postdata = json.dumps(params)
        response = requests.post(url, postdata, headers=headers, timeout=10)

        try:

            if response.status_code == 200:
                return response.json()
            else:
                return
        except BaseException as e:
            print("httpPost failed, detail is:%s,%s" % (response.text, e))
            return

    def api_key_get(self, params, request_path):
        method = 'GET'
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params.update({'AccessKeyId': self.access_key,
                       'SignatureMethod': 'HmacSHA256',
                       'SignatureVersion': '2',
                       'Timestamp': timestamp})

        host_url = self.trade_url
        host_name = urllib.parse.urlparse(host_url).hostname
        host_name = host_name.lower()
        params['Signature'] = self.createSign(params, method, host_name, request_path, self.secret_key)

        url = host_url + request_path
        return self.http_get_request(url, params)

    def api_key_post(self, params, request_path):
        method = 'POST'
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params_to_sign = {'AccessKeyId': self.access_key,
                          'SignatureMethod': 'HmacSHA256',
                          'SignatureVersion': '2',
                          'Timestamp': timestamp}

        host_url = self.trade_url
        host_name = urllib.parse.urlparse(host_url).hostname
        host_name = host_name.lower()
        params_to_sign['Signature'] = self.createSign(params_to_sign, method, host_name, request_path, self.secret_key)
        url = host_url + request_path + '?' + urllib.parse.urlencode(params_to_sign)
        return self.http_post_request(url, params)

    def createSign(self, pParams, method, host_url, request_path, secret_key):
        sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)
        encode_params = urllib.parse.urlencode(sorted_params)
        payload = [method, host_url, request_path, encode_params]
        payload = '\n'.join(payload)
        payload = payload.encode(encoding='UTF8')
        secret_key = secret_key.encode(encoding='UTF8')

        digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest)
        signature = signature.decode()
        return signature


if __name__ == "__main__":
    svc = HuobiSVC('', '', url_type='aws')
    df = svc.get_kline_df('btcusdt', '60min', size=200)
    print(df)