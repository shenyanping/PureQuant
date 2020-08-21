"""
账户信息存储至数据库模块

Author: Gary-Hertel
Date:   2020/07/09
email: interstella.ranger2020@gmail.com

MongoDB数据库创建管理员与授权验证步骤：
按照教程安装好mongodb，并将其配置为windows服务
在bin目录下，
> mongo
> use admin
> db.createUser({user:"root",pwd:"5:hK)rcGU1yyPnxj_2sp",roles:["root"]})    #创建数据库管理员账号密码
在mongod.cfg文件中修改，ip地址改为0.0.0.0
将安全选项更改为：
security:
   authorization: 'enabled'

重启mongodb服务，在bin下运行
> mongo
> use admin
> db.auth("root","5:hK)rcGU1yyPnxj_2sp")
"""


from purequant.exchange.okex.spot_api import SpotAPI as _okspot
from purequant.exchange.okex.futures_api import FutureAPI as _okfutures
from purequant.exchange.okex.swap_api import SwapAPI as _okswap
from purequant.storage import storage
from purequant.config import config
from purequant.exceptions import *
from purequant.time import get_localtime


class Okex:
    """OKEX交易所账户信息数据库可视化"""

    def __init__(self):
        self.spot = False
        self.futures_usdt_crossed = False
        self.futures_usd_crossed = False
        self.futures_usdt_fixed = False
        self.futures_usd_fixed = False
        self.swap_usdt_crossed = False
        self.swap_usd_crossed = False
        self.swap_usdt_fixed = False
        self.swap_usd_fixed = False

    def __persistence_okex_spot_account(self, databank, access_key, secret_key, passphrase):
        spot_dict = {}
        okex_spot = _okspot(access_key, secret_key, passphrase)
        spot_accounts_info = okex_spot.get_account_info()
        for item in spot_accounts_info:
            if float(item['balance']) > 0:
                if databank == "mysql":
                    storage.mysql_save_okex_spot_accounts("okex账户", "现货", item['currency'], item['balance'], item['hold'], item['available'])
                elif databank == "mongodb":
                    self.spot = True
                    spot_dict[item['currency']] = {
                        "余额": item['balance'],
                        "冻结": item['hold'],
                        "可用": item['hold']
                    }
                else:
                    raise DataBankError
        if self.spot == True and databank == "mongodb":
            storage.mongodb_save(database="okex账户", collection="现货", data={"data": {"时间": get_localtime(), "账户": "现货"},"accounts": spot_dict})

    def __persistence_okex_futures_account(self, databank, access_key, secret_key, passphrase):
        futures_usdt_crossed_dict = {}
        futures_usd_crossed_dict = {}
        futures_usdt_fixed_dict = {}
        futures_usd_fixed_dict = {}
        okex_futures = _okfutures(access_key, secret_key, passphrase)
        futures_accounts_info = okex_futures.get_accounts()["info"]
        for key, value in futures_accounts_info.items():
            if "usdt" in key and value["margin_mode"] == "crossed":     # USDT本位的全仓模式
                symbol = value["underlying"]
                currency = value["currency"]
                margin_mode = value["margin_mode"]
                equity = value["equity"]
                total_avail_balance = value["total_avail_balance"]
                margin = value["margin"]
                margin_frozen = value["margin_frozen"]
                margin_for_unfilled = value["margin_for_unfilled"]
                realized_pnl = value["realized_pnl"]
                unrealized_pnl = value["unrealized_pnl"]
                margin_ratio = value["margin_ratio"]
                maint_margin_ratio = value["maint_margin_ratio"]
                liqui_mode = value["liqui_mode"]
                can_withdraw = value["can_withdraw"]
                liqui_fee_rate = value["liqui_fee_rate"]
                if databank == "mysql":
                    storage.mysql_save_okex_crossedfutures_accounts("okex账户", "交割合约usdt全仓模式", symbol, currency, margin_mode,
                                                                    equity, total_avail_balance, margin, margin_frozen,
                                                                    margin_for_unfilled, realized_pnl, unrealized_pnl,
                                                                    margin_ratio, maint_margin_ratio, liqui_mode,
                                                                    can_withdraw, liqui_fee_rate)
                elif databank == "mongodb":
                    self.futures_usdt_crossed = True
                    futures_usdt_crossed_dict[symbol] = {
                        "余额币种": currency,
                        "账户类型": margin_mode,
                        "账户权益": equity,
                        "账户余额": total_avail_balance,
                        "保证金": margin,
                        "持仓已用保证金": margin_frozen,
                        "挂单冻结保证金": margin_for_unfilled,
                        "已实现盈亏": realized_pnl,
                        "未实现盈亏": unrealized_pnl,
                        "保证金率": margin_ratio,
                        "维持保证金率": maint_margin_ratio,
                        "强平模式": liqui_mode,
                        "可划转数量": can_withdraw,
                        "强平手续费": liqui_fee_rate
                    }
                else:
                    raise DataBankError

            if "usdt" not in key and value["margin_mode"] == "crossed":  # 币本位的全仓模式
                symbol = value["underlying"]
                currency = value["currency"]
                margin_mode = value["margin_mode"]
                equity = value["equity"]
                total_avail_balance = value["total_avail_balance"]
                margin = value["margin"]
                margin_frozen = value["margin_frozen"]
                margin_for_unfilled = value["margin_for_unfilled"]
                realized_pnl = value["realized_pnl"]
                unrealized_pnl = value["unrealized_pnl"]
                margin_ratio = value["margin_ratio"]
                maint_margin_ratio = value["maint_margin_ratio"]
                liqui_mode = value["liqui_mode"]
                can_withdraw = value["can_withdraw"]
                liqui_fee_rate = value["liqui_fee_rate"]
                if databank == "mysql":
                    storage.mysql_save_okex_crossedfutures_accounts("okex账户", "交割合约usd全仓模式", symbol, currency, margin_mode,
                                                                    equity, total_avail_balance, margin, margin_frozen,
                                                                    margin_for_unfilled, realized_pnl, unrealized_pnl,
                                                                    margin_ratio, maint_margin_ratio, liqui_mode,
                                                                    can_withdraw, liqui_fee_rate)
                elif databank == "mongodb":
                    self.futures_usd_crossed = True
                    futures_usd_crossed_dict[symbol] = {
                        "余额币种": currency,
                        "账户类型": margin_mode,
                        "账户权益": equity,
                        "账户余额": total_avail_balance,
                        "保证金": margin,
                        "持仓已用保证金": margin_frozen,
                        "挂单冻结保证金": margin_for_unfilled,
                        "已实现盈亏": realized_pnl,
                        "未实现盈亏": unrealized_pnl,
                        "保证金率": margin_ratio,
                        "维持保证金率": maint_margin_ratio,
                        "强平模式": liqui_mode,
                        "可划转数量": can_withdraw,
                        "强平手续费": liqui_fee_rate
                    }
                else:
                    raise DataBankError

            if "usdt" in key and value["margin_mode"] == "fixed" and len(value["contracts"]) > 0:     # USDT本位的逐仓模式
                v = value["contracts"][0]
                symbol = v["instrument_id"][0:8]
                fixed_balance = v["fixed_balance"]
                available_qty = v["available_qty"]
                margin_frozen = v["margin_frozen"]
                margin_for_unfilled = v["margin_for_unfilled"]
                realized_pnl = v["realized_pnl"]
                unrealized_pnl = v["unrealized_pnl"]
                total_avail_balance = value["total_avail_balance"]
                currency = value["currency"]
                margin_mode = value["margin_mode"]
                equity = value["equity"]
                auto_margin = value["auto_margin"]
                liqui_mode = value["liqui_mode"]
                can_withdraw = value["can_withdraw"]
                if databank == "mysql":
                    storage.mysql_save_okex_fixedfutures_accounts("okex账户", "交割合约usdt逐仓模式", symbol, currency, margin_mode, equity, fixed_balance, available_qty, margin_frozen, margin_for_unfilled, realized_pnl, unrealized_pnl, total_avail_balance, auto_margin, liqui_mode, can_withdraw)
                elif databank == "mongodb":
                    self.futures_usdt_fixed = True
                    futures_usdt_fixed_dict[symbol] = {
                        "余额币种": currency,
                        "账户类型": margin_mode,
                        "账户动态权益": equity,
                        "逐仓账户余额": fixed_balance,
                        "逐仓可用余额": available_qty,
                        "持仓已用保证金": margin_frozen,
                        "挂单冻结保证金": margin_for_unfilled,
                        "已实现盈亏": realized_pnl,
                        "未实现盈亏": unrealized_pnl,
                        "账户静态权益": total_avail_balance,
                        "是否自动追加保证金": auto_margin,
                        "强平模式": liqui_mode,
                        "可划转数量": can_withdraw
                    }
                else:
                    raise DataBankError

            if "usdt" not in key and value["margin_mode"] == "fixed" and len(value["contracts"]) > 0:     # 币本位的逐仓模式
                v = value["contracts"][0]
                symbol = v["instrument_id"][0:7]
                fixed_balance = v["fixed_balance"]
                available_qty = v["available_qty"]
                margin_frozen = v["margin_frozen"]
                margin_for_unfilled = v["margin_for_unfilled"]
                realized_pnl = v["realized_pnl"]
                unrealized_pnl = v["unrealized_pnl"]
                total_avail_balance = value["total_avail_balance"]
                currency = value["currency"]
                margin_mode = value["margin_mode"]
                equity = value["equity"]
                auto_margin = value["auto_margin"]
                liqui_mode = value["liqui_mode"]
                can_withdraw = value["can_withdraw"]
                if databank == "mysql":
                    storage.mysql_save_okex_fixedfutures_accounts("okex账户", "交割合约usd逐仓模式", symbol, currency, margin_mode, equity, fixed_balance, available_qty, margin_frozen, margin_for_unfilled, realized_pnl, unrealized_pnl, total_avail_balance, auto_margin, liqui_mode, can_withdraw)
                elif databank == "mongodb":
                    self.futures_usd_fixed = True
                    futures_usd_fixed_dict[symbol] = {
                        "余额币种": currency,
                        "账户类型": margin_mode,
                        "账户动态权益": equity,
                        "逐仓账户余额": fixed_balance,
                        "逐仓可用余额": available_qty,
                        "持仓已用保证金": margin_frozen,
                        "挂单冻结保证金": margin_for_unfilled,
                        "已实现盈亏": realized_pnl,
                        "未实现盈亏": unrealized_pnl,
                        "账户静态权益": total_avail_balance,
                        "是否自动追加保证金": auto_margin,
                        "强平模式": liqui_mode,
                        "可划转数量": can_withdraw
                    }
                else:
                    raise DataBankError
        if self.futures_usdt_crossed == True and databank == "mongodb":
            storage.mongodb_save(database="okex账户", collection="交割合约usdt全仓模式", data={
                "data": {"时间": get_localtime(), "账户": "交割合约usdt全仓模式"}, "accounts": futures_usdt_crossed_dict
            })
        if self.futures_usd_crossed == True and databank == "mongodb":
            storage.mongodb_save(database="okex账户", collection="交割合约usd全仓模式", data={
                "data": {"时间": get_localtime(), "账户": "交割合约usd全仓模式"}, "accounts": futures_usd_crossed_dict
            })
        if self.futures_usd_fixed == True and databank == "mongodb":
            storage.mongodb_save(database="okex账户", collection="交割合约usd逐仓模式", data={
                "data": {"时间": get_localtime(), "账户": "交割合约usd逐仓模式"}, "accounts": futures_usd_fixed_dict
            })
        if self.futures_usdt_fixed == True and databank == "mongodb":
            storage.mongodb_save(database="okex账户", collection="交割合约usdt逐仓模式", data={
                "data": {"时间": get_localtime(), "账户": "交割合约usdt逐仓模式"}, "accounts": futures_usdt_fixed_dict
            })

    def __persistence_okex_swap_account(self, databank, access_key, secret_key, passphrase):
        swap_usdt_crossed_dict = {}
        swap_usdt_fixed_dict = {}
        swap_usd_crossed_dict = {}
        swap_usd_fixed_dict = {}
        okex_swap = _okswap(access_key, secret_key, passphrase)
        swap_accounts_info = okex_swap.get_accounts()["info"]
        for item in swap_accounts_info:
            currency = item["currency"]
            equity = item["equity"]
            fixed_balance = item["fixed_balance"]
            maint_margin_ratio = item["maint_margin_ratio"]
            margin = item["margin"]
            margin_frozen = item["margin_frozen"]
            margin_mode = item["margin_mode"]
            margin_ratio = item["margin_ratio"]
            max_withdraw = item["max_withdraw"]
            realized_pnl = item["realized_pnl"]
            timestamp = item["timestamp"]
            total_avail_balance = item["total_avail_balance"]
            symbol = item["underlying"]
            unrealized_pnl = item["unrealized_pnl"]

            if currency == "USDT" and margin_mode == "crossed" and float(equity) > 0:   # 永续合约USDT全仓模式
                if databank == "mysql":
                    storage.mysql_save_okex_swap_accounts("okex账户", "永续合约usdt全仓模式", timestamp, symbol, currency, margin_mode, equity, total_avail_balance, fixed_balance, margin, margin_frozen, realized_pnl, unrealized_pnl, margin_ratio, maint_margin_ratio, max_withdraw)
                elif databank == "mongodb":
                    self.swap_usdt_crossed = True
                    swap_usdt_crossed_dict[symbol] = {
                        "账户余额币种": currency,
                        "账户权益": equity,
                        "逐仓账户余额": fixed_balance,
                        "维持保证金率": maint_margin_ratio,
                        "已用保证金": margin,
                        "开仓冻结保证金": margin_frozen,
                        "仓位模式": margin_mode,
                        "保证金率": margin_ratio,
                        "可划转数量": max_withdraw,
                        "已实现盈亏": realized_pnl,
                        "时间": timestamp,
                        "账户余额": total_avail_balance,
                        "未实现盈亏": unrealized_pnl
                    }
                else:
                    raise DataBankError
            if currency != "USDT" and margin_mode == "crossed" and float(equity) > 0:   # 永续合约币本位全仓模式
                if databank == "mysql":
                    storage.mysql_save_okex_swap_accounts("okex账户", "永续合约usd全仓模式", timestamp, symbol, currency, margin_mode, equity, total_avail_balance, fixed_balance, margin, margin_frozen, realized_pnl, unrealized_pnl, margin_ratio, maint_margin_ratio, max_withdraw)
                elif databank == "mongodb":
                    self.swap_usd_crossed = True
                    swap_usd_crossed_dict[symbol] = {
                        "账户余额币种": currency,
                        "账户权益": equity,
                        "逐仓账户余额": fixed_balance,
                        "维持保证金率": maint_margin_ratio,
                        "已用保证金": margin,
                        "开仓冻结保证金": margin_frozen,
                        "仓位模式": margin_mode,
                        "保证金率": margin_ratio,
                        "可划转数量": max_withdraw,
                        "已实现盈亏": realized_pnl,
                        "时间": timestamp,
                        "账户余额": total_avail_balance,
                        "未实现盈亏": unrealized_pnl
                    }
                else:
                    raise DataBankError
            if currency == "USDT" and margin_mode == "fixed" and float(equity) > 0:   # 永续合约USDT逐仓模式
                if databank == "mysql":
                    storage.mysql_save_okex_swap_accounts("okex账户", "永续合约usdt逐仓模式", timestamp, symbol, currency, margin_mode, equity, total_avail_balance, fixed_balance, margin, margin_frozen, realized_pnl, unrealized_pnl, margin_ratio, maint_margin_ratio, max_withdraw)
                elif databank == "mongodb":
                    self.swap_usdt_fixed = True
                    swap_usdt_fixed_dict[symbol] = {
                        "账户余额币种": currency,
                        "账户权益": equity,
                        "逐仓账户余额": fixed_balance,
                        "维持保证金率": maint_margin_ratio,
                        "已用保证金": margin,
                        "开仓冻结保证金": margin_frozen,
                        "仓位模式": margin_mode,
                        "保证金率": margin_ratio,
                        "可划转数量": max_withdraw,
                        "已实现盈亏": realized_pnl,
                        "时间": timestamp,
                        "账户余额": total_avail_balance,
                        "未实现盈亏": unrealized_pnl
                    }
                else:
                    raise DataBankError
            if currency != "USDT" and margin_mode == "fixed" and float(equity) > 0:   # 永续合约USDT本位全仓模式
                if databank == "mysql":
                    storage.mysql_save_okex_swap_accounts("okex账户", "永续合约usd逐仓模式", timestamp, symbol, currency, margin_mode, equity, total_avail_balance, fixed_balance, margin, margin_frozen, realized_pnl, unrealized_pnl, margin_ratio, maint_margin_ratio, max_withdraw)
                elif databank == "mongodb":
                    self.swap_usd_fixed = True
                    swap_usd_fixed_dict[symbol] = {
                        "账户余额币种": currency,
                        "账户权益": equity,
                        "逐仓账户余额": fixed_balance,
                        "维持保证金率": maint_margin_ratio,
                        "已用保证金": margin,
                        "开仓冻结保证金": margin_frozen,
                        "仓位模式": margin_mode,
                        "保证金率": margin_ratio,
                        "可划转数量": max_withdraw,
                        "已实现盈亏": realized_pnl,
                        "时间": timestamp,
                        "账户余额": total_avail_balance,
                        "未实现盈亏": unrealized_pnl
                    }
                else:
                    raise DataBankError
        if self.swap_usdt_crossed == True and databank == "mongodb":
            storage.mongodb_save(database="okex账户", collection="永续合约usdt全仓模式", data={
                "data": {"时间": get_localtime(), "账户": "永续合约usdt全仓模式"}, "accounts": swap_usdt_crossed_dict
            })
        if self.swap_usd_crossed == True and databank == "mongodb":
            storage.mongodb_save(database="okex账户", collection="永续合约usd全仓模式", data={
                "data": {"时间": get_localtime(), "账户": "永续合约usd全仓模式"}, "accounts": swap_usd_crossed_dict
            })
        if self.swap_usdt_fixed == True and databank == "mongodb":
            storage.mongodb_save(database="okex账户", collection="永续合约usdt逐仓模式", data={
                "data": {"时间": get_localtime(), "账户": "永续合约usdt逐仓模式"}, "accounts": swap_usdt_fixed_dict
            })
        if self.swap_usd_fixed == True and databank == "mongodb":
            storage.mongodb_save(database="okex账户", collection="永续合约usd逐仓模式", data={
                "data": {"时间": get_localtime(), "账户": "永续合约usd逐仓模式"}, "accounts": swap_usd_fixed_dict
            })

    def visualize(self, databank, access_key=None, secret_key=None, passphrase=None):
        try:
            access_key = access_key if access_key is not None else config.access_key
            secret_key = secret_key if secret_key is not None else config.secret_key
            passphrase = passphrase if passphrase is not None else config.passphrase

            # 先删除数据库，然后再去创建并插入数据，实现旧数据覆盖新数据
            if databank == "mysql":
                storage.delete_mysql_database("okex账户")
            elif databank == "mongodb":
                storage.delete_mongodb_database("okex账户")
            else:
                raise DataBankError

            self.__persistence_okex_spot_account(databank, access_key, secret_key, passphrase)
            self.__persistence_okex_futures_account(databank, access_key, secret_key, passphrase)
            self.__persistence_okex_swap_account(databank, access_key, secret_key, passphrase)
        except Exception as e:
            pass

okex = Okex()