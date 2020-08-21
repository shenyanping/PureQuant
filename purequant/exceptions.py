"""
Error/Exception definition.

Author: Gary-Hertel
Date:   2020/08/12
Email:  interstella.ranger2020@gmail.com
"""

class CunstomException(Exception):
    """自定义异常类"""
    defaul_msg = "一个错误发生了！"

    def __init__(self, msg=None):
        self.msg = msg if msg is not None else self.defaul_msg

    def __str__(self):
        str_msg = "{msg}".format(msg=self.msg)
        return str_msg

class ExchangeError(CunstomException):
    defaul_msg = "交易所设置错误!"

class KlineError(CunstomException):
    defaul_msg = "k线周期错误，只支持【1min 3min 5min 15min 30min 1hour 2hour 4hour 6hour 12hour 1day】!"

class SymbolError(CunstomException):
    defaul_msg = "合约ID错误，只可输入当季或者次季合约ID!"

class DataBankError(CunstomException):
    defaul_msg = "数据库设置错误，必须是mysql或mongodb!"

class MatchError(CunstomException):
    defaul_msg = "策略持仓与账户持仓比较失败！"

