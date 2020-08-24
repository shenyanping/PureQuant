# -*- coding:utf-8 -*-

"""
服务配置

Author: Gary-Hertel
Date:   2020/07/09
email: interstella.ranger2020@gmail.com
"""

import json

class Config:
    """服务配置"""

    def __init__(self):
        pass


    def loads(self, config_file=None):
        """
        加载配置。
        :param config_file:json配置文件
        :return:
        """
        with open(config_file) as json_file:
            configures = json.load(json_file)
        # exchange
        self.access_key = configures['EXCHANGE']['access_key']
        self.secret_key = configures['EXCHANGE']['secret_key']
        self.passphrase = configures['EXCHANGE']['passphrase']
        # push
        self.ding_talk_api = configures['DINGTALK']['ding_talk_api']
        self.accountSID = configures['TWILIO']['accountSID']
        self.authToken = configures['TWILIO']['authToken']
        self.myNumber = configures['TWILIO']['myNumber']
        self.twilio_Number = configures['TWILIO']['twilio_Number']
        self.from_addr = configures['SENDMAIL']['from_addr']
        self.password = configures['SENDMAIL']['password']
        self.to_addr = configures['SENDMAIL']['to_addr']
        self.smtp_server = configures['SENDMAIL']['smtp_server']
        self.mail_port = configures['SENDMAIL']['port']
        self.sendmail = configures['PUSH']['sendmail']
        self.dingtalk = configures['PUSH']['dingtalk']
        self.twilio = configures['PUSH']['twilio']
        # logger
        self.level = configures['LOG']['level']
        self.handler = configures['LOG']['handler']
        # markets server
        markets_server_list = []
        for item in configures["MARKETS_SERVER"]["platform"]:
            markets_server_list.append(item)
        self.markets_server_platform = markets_server_list[0]
        self.markets_channels_list = configures["MARKETS_SERVER"]["platform"][self.markets_server_platform]["channels"]
        self.mongodb_database = configures["MARKETS_SERVER"]["platform"][self.markets_server_platform]["database"]
        self.mongodb_collection = configures["MARKETS_SERVER"]["platform"][self.markets_server_platform]["collection"]
        self.mongodb_console = configures["MARKETS_SERVER"]["platform"][self.markets_server_platform]["console"]
        # position server
        position_server_list = []
        for item in configures["POSITION_SERVER"]["platform"]:
            position_server_list.append(item)
        self.position_server_platform = position_server_list[0]
        if self.position_server_platform == "okex":
            self.delivery_date = configures['POSITION_SERVER']["platform"][self.position_server_platform]['delivery_date']
            self.okex_futures_usd = configures['POSITION_SERVER']["platform"][self.position_server_platform]['futures_usd']
            self.okex_futures_usdt = configures['POSITION_SERVER']["platform"][self.position_server_platform]['futures_usdt']
            self.okex_swap_usd = configures['POSITION_SERVER']["platform"][self.position_server_platform]['swap_usd']
            self.okex_swap_usdt = configures['POSITION_SERVER']["platform"][self.position_server_platform]['swap_usdt']
            self.okex_spot = configures['POSITION_SERVER']["platform"][self.position_server_platform]['spot']
            self.okex_margin = configures['POSITION_SERVER']["platform"][self.position_server_platform]['margin']
        if self.position_server_platform == "huobi":
            self.huobi_futures = configures['POSITION_SERVER']["platform"][self.position_server_platform]['futures']
            self.huobi_swap = configures['POSITION_SERVER']["platform"][self.position_server_platform]['swap']
        # synchronize
        overprice_range_str = configures["SYNCHRONIZE"]["overprice"]["range"]
        self.overprice_range = float((overprice_range_str.split("%"))[0]) / 100   # 超价幅度，浮点数类型
        # first_run
        self.first_run = configures["STATUS"]["first_run"]
        # ASSISTANT
        price_cancellation_amplitude_str = configures["ASSISTANT"]["amplitude"]
        self.price_cancellation_amplitude = float((price_cancellation_amplitude_str.split("%"))[0]) / 100
        self.time_cancellation = configures["ASSISTANT"]["time_cancellation"]
        self.time_cancellation_seconds = configures["ASSISTANT"]["seconds"]
        self.price_cancellation = configures["ASSISTANT"]["price_cancellation"]
        reissue_order_overprice_range_str = configures["ASSISTANT"]["reissue_order"]
        self.reissue_order = float((reissue_order_overprice_range_str.split("%"))[0]) / 100
        self.automatic_cancellation = configures["ASSISTANT"]["automatic_cancellation"]
        # MONGODB AUTHORIZATION
        self.mongodb_authorization = configures["MONGODB"]["authorization"]
        self.mongodb_user_name = configures["MONGODB"]["user_name"]
        self.mongodb_password = configures["MONGODB"]["password"]
        # MYSQL AUTHORIZATION
        self.mysql_authorization = configures["MYSQL"]["authorization"]
        self.mysql_user_name = configures["MYSQL"]["user_name"]
        self.mysql_password = configures["MYSQL"]["password"]
        # BACKTEST
        self.backtest = configures["MODE"]["backtest"]

    def update_config(self, config_file, config_content):
        """
        更新配置文件
        :param config_file: 配置文件路径及名称，如"config.json"
        :param config_content: 配置文件中的具体字典内容，将以当前content内容替换掉原配置文件中的内容
        :return: 打印"配置文件已更新！"
        """
        with open(config_file, 'w') as json_file:
            json.dump(config_content, json_file, indent=4)
        print("配置文件已更新！")

config = Config()