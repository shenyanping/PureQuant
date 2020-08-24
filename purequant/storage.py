# -*- coding:utf-8 -*-

"""
数据存储与读取

Author: Gary-Hertel
Date:   2020/07/09
email: interstella.ranger2020@gmail.com
"""
import logging, mysql.connector, pymongo
from purequant import time
from purequant.indicators import INDICATORS
import pandas as pd
from purequant.config import config

class Storage:
    """K线等各种数据的存储与读取"""

    def __init__(self):
        self.__old_kline = 0

    def save_asset_and_profit(self, database, data_sheet, profit, asset):
        """存储单笔交易盈亏与总资金信息至mysql数据库"""
        # 检查数据库是否存在，如不存在则创建
        user = config.mysql_user_name if config.mysql_authorization == "enabled" else 'root'
        password = config.mysql_password if config.mysql_authorization == "enabled" else 'root'
        conn1 = mysql.connector.connect(user=user, password=password)
        cursor1 = conn1.cursor()
        cursor1.execute("SHOW DATABASES")
        list1 = []
        for item in cursor1:
            for x in item:
                list1.append(x)
        if database in list1:
            pass
        else:
            cursor1.execute("CREATE DATABASE {}".format(database))
        conn1.commit()
        cursor1.close()
        conn1.close()
        # 检查数据表是否存在，如不存在则创建
        conn2 = mysql.connector.connect(user=user, password=password, database=database)
        cursor2 = conn2.cursor()
        cursor2.execute("SHOW TABLES")
        list2 = []
        for item in cursor2:
            for x in item:
                list2.append(x)
        if data_sheet in list2:
            pass
        else:
            cursor2.execute("CREATE TABLE {} (timestamp TEXT, profit FLOAT, asset FLOAT)".format(data_sheet))
        # 插入数据
        cursor2.execute(
            'insert into {} (timestamp, profit, asset) values (%s, %s, %s)'.format(
                data_sheet),
            [time.get_localtime(), profit, asset])
        conn2.commit()
        cursor2.close()
        conn2.close()

    def mysql_save_strategy_position(self, database, data_sheet, direction, amount):
        """存储持仓方向与持仓数量信息至mysql数据库"""
        # 检查数据库是否存在，如不存在则创建
        user = config.mysql_user_name if config.mysql_authorization == "enabled" else 'root'
        password = config.mysql_password if config.mysql_authorization == "enabled" else 'root'
        conn1 = mysql.connector.connect(user=user, password=password)
        cursor1 = conn1.cursor()
        cursor1.execute("SHOW DATABASES")
        list1 = []
        for item in cursor1:
            for x in item:
                list1.append(x)
        if database in list1:
            pass
        else:
            cursor1.execute("CREATE DATABASE {}".format(database))
        conn1.commit()
        cursor1.close()
        conn1.close()
        # 检查数据表是否存在，如不存在则创建
        conn2 = mysql.connector.connect(user=user, password=password, database=database)
        cursor2 = conn2.cursor()
        cursor2.execute("SHOW TABLES")
        list2 = []
        for item in cursor2:
            for x in item:
                list2.append(x)
        if data_sheet in list2:
            pass
        else:
            cursor2.execute("CREATE TABLE {} (timestamp TEXT, direction TEXT, amount FLOAT)".format(data_sheet))
        # 插入数据
        cursor2.execute(
            'insert into {} (timestamp, direction, amount) values (%s, %s, %s)'.format(
                data_sheet),
            [time.get_localtime(), direction, amount])
        conn2.commit()
        cursor2.close()
        conn2.close()

    def __save_kline_func(self, database, data_sheet, timestamp, open, high, low, close, volume, currency_volume):
        """此函数专为k线存储的函数使用"""
        # 检查数据库是否存在，如不存在则创建
        user = config.mysql_user_name if config.mysql_authorization == "enabled" else 'root'
        password = config.mysql_password if config.mysql_authorization == "enabled" else 'root'
        conn1 = mysql.connector.connect(user=user, password=password)
        cursor1 = conn1.cursor()
        cursor1.execute("SHOW DATABASES")
        list1 = []
        for item in cursor1:
            for x in item:
                list1.append(x)
        if database in list1:
            pass
        else:
            cursor1.execute("CREATE DATABASE {}".format(database))
        conn1.commit()
        cursor1.close()
        conn1.close()
        # 检查数据表是否存在，如不存在则创建
        conn2 = mysql.connector.connect(user=user, password=password, database=database)
        cursor2 = conn2.cursor()
        cursor2.execute("SHOW TABLES")
        list2 = []
        for item in cursor2:
            for x in item:
                list2.append(x)
        if data_sheet in list2:
            pass
        else:
            cursor2.execute("CREATE TABLE {} (timestamp TEXT, open FLOAT, high FLOAT, low FLOAT, close FLOAT, volume FLOAT, currency_volume FLOAT)".format(data_sheet))
        # 插入数据
        cursor2.execute(
            'insert into {} (timestamp, open, high, low, close, volume, currency_volume) values (%s, %s, %s, %s, %s, %s, %s)'.format(
                data_sheet),
            [timestamp, open, high, low, close, volume, currency_volume])
        # 提交事务
        conn2.commit()
        # 关闭游标和连接
        cursor2.close()
        conn2.close()

    def kline_save(self, platform, database, data_sheet, instrument_id, time_frame):
        """
        从交易所获取k线数据，并将其存储至数据库中
        :param platform: 交易所
        :param database: 数据库名称
        :param data_sheet: 数据表名称
        :param instrument_id: 要获取k线数据的交易对名称或合约ID
        :param time_frame: k线周期，如'60'为一分钟，'86400'为一天，字符串格式
        :return: "获取的历史数据已存储至mysql数据库！"
        """
        result = platform.get_kline(time_frame)
        result.reverse()
        for data in result:
            self.__save_kline_func(database, data_sheet, data[0], data[1], data[2], data[3], data[4], data[5], data[6])
        print("获取的历史数据已存储至mysql数据库！")

    def kline_storage(self, platform, database, data_sheet, instrument_id, time_frame):
        """
        实时获取上一根k线存储至数据库中。
        :param database: 数据库名称
        :param data_sheet: 数据表名称
        :param instrument_id: 交易对或合约id
        :param time_frame: k线周期，如'1m', '1d'，字符串格式
        :return:
        """
        indicators = INDICATORS(platform, instrument_id, time_frame)
        if indicators.BarUpdate() == True:
            last_kline = platform.get_kline(time_frame)[1]
            if last_kline != self.__old_kline:    # 若获取得k线不同于已保存的上一个k线
                timestamp = last_kline[0]
                open = last_kline[1]
                high = last_kline[2]
                low = last_kline[3]
                close = last_kline[4]
                volume = last_kline[5]
                currency_volume = last_kline[6]
                self.__save_kline_func(database, data_sheet, timestamp, open, high, low, close, volume, currency_volume)
                print("时间：{} 实时k线数据已保存至MySQL数据库中！".format(time.get_localtime()))
                self.__old_kline = last_kline  # 将刚保存的k线设为旧k线
            else:
                return

    def read_mysql_datas(self, data, database, datasheet, field, operator):  # 获取数据库满足条件的数据
        """
        查询数据库中满足条件的数据
        :param data: 要查询的数据，数据类型由要查询的数据决定
        :param database: 数据库名称
        :param datasheet: 数据表名称
        :param field: 字段
        :return: 返回值查询到的数据，如未查询到则返回None
        """
        # 连接数据库
        user = config.mysql_user_name if config.mysql_authorization == "enabled" else 'root'
        password = config.mysql_password if config.mysql_authorization == "enabled" else 'root'
        conn = mysql.connector.connect(user=user, password=password, database=database, buffered = True)
        # 打开游标
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM {} WHERE {} {} '{}'".format(datasheet, field, operator, data))
        LogData = cursor.fetchall()  # 取出了数据库数据
        # 关闭游标和连接
        cursor.close()
        conn.close()
        return LogData

    def read_mysql_specific_data(self, data, database, datasheet, field):  # 获取数据库满足条件的数据
        """
        查询数据库中满足条件的数据
        :param data: 要查询的数据，数据类型由要查询的数据决定
        :param database: 数据库名称
        :param datasheet: 数据表名称
        :param field: 字段
        :return: 返回值查询到的数据，如未查询到则返回None
        """
        # 连接数据库
        user = config.mysql_user_name if config.mysql_authorization == "enabled" else 'root'
        password = config.mysql_password if config.mysql_authorization == "enabled" else 'root'
        conn = mysql.connector.connect(user=user, password=password, database=database, buffered = True)
        # 打开游标
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM {} WHERE {} = '{}'".format(datasheet, field, data))
        LogData = cursor.fetchone()  # 取出了数据库数据
        # 关闭游标和连接
        cursor.close()
        conn.close()
        return LogData

    def text_save(self, content, filename, mode='a'):
        """
        保存数据至txt文件。
        :param content: 要保存的内容,必须为string格式
        :param filename:文件路径及名称
        :param mode:
        :return:
        """
        file = open(filename, mode)
        file.write(content + '\n')
        file.close()

    def text_read(self, filename):
        """
        读取txt文件中的数据。
        :param filename: 文件路径、文件名称。
        :return:返回一个包含所有文件内容的列表，其中元素均为string格式
        """
        try:
            file = open(filename, 'r')
        except IOError:
            error = '打开txt文件失败，请检查文件！'
            return error
        content = file.readlines()
        for i in range(len(content)):
            content[i] = content[i][:len(content[i]) - 1]
            file.close()
        return content

    def mongodb_save(self, data, database, collection):
        """保存数据至mongodb"""
        client = pymongo.MongoClient(host='localhost', port=27017)
        if config.mongodb_authorization == "enabled":   # 如果启用了授权验证
            client.admin.authenticate(config.mongodb_user_name, config.mongodb_password, mechanism='SCRAM-SHA-1')
        db = client[database]
        col = db[collection]
        col.insert_one(data)

    def mongodb_read_data(self, database, collection):
        """读取mongodb数据库中某集合中的所有数据，并保存至一个列表中"""
        client = pymongo.MongoClient(host='localhost', port=27017)
        if config.mongodb_authorization == "enabled":  # 如果启用了授权验证
            client.admin.authenticate(config.mongodb_user_name, config.mongodb_password, mechanism='SCRAM-SHA-1')
        db = client[database]
        col = db[collection]
        datalist = []
        for item in col.find():
            datalist.append([item])
        return datalist

    def export_mongodb_to_csv(self, database, collection, csv_file_path):
        """导出mongodb集合中的数据至csv文件"""
        client = pymongo.MongoClient(host='localhost', port=27017)
        if config.mongodb_authorization == "enabled":  # 如果启用了授权验证
            client.admin.authenticate(config.mongodb_user_name, config.mongodb_password, mechanism='SCRAM-SHA-1')
        db = client[database]
        sheet_table = db[collection]
        df1 = pd.DataFrame(list(sheet_table.find()))
        df1.to_csv(csv_file_path)
        print("MongoDB【{}】数据库中【{}】集合的数据已导出至【{}】文件！".format(database, collection, csv_file_path))

    def mysql_save_okex_spot_accounts(self, database, data_sheet, currency, balance, frozen, available, timestamp=None):
        """存储okex现货账户信息至mysql数据库"""
        timestamp = timestamp if timestamp is not None else time.get_localtime()   # 默认是自动填充本地时间，也可以传入*****来做数据分割
        # 检查数据库是否存在，如不存在则创建
        user = config.mysql_user_name if config.mysql_authorization == "enabled" else 'root'
        password = config.mysql_password if config.mysql_authorization == "enabled" else 'root'
        conn1 = mysql.connector.connect(user=user, password=password)
        cursor1 = conn1.cursor()
        cursor1.execute("SHOW DATABASES")
        list1 = []
        for item in cursor1:
            for x in item:
                list1.append(x)
        if database in list1:
            pass
        else:
            cursor1.execute("CREATE DATABASE {}".format(database))
        conn1.commit()
        cursor1.close()
        conn1.close()
        # 检查数据表是否存在，如不存在则创建
        conn2 = mysql.connector.connect(user=user, password=password, database=database)
        cursor2 = conn2.cursor()
        cursor2.execute("SHOW TABLES")
        list2 = []
        for item in cursor2:
            for x in item:
                list2.append(x)
        if data_sheet in list2:
            pass
        else:  # 如果数据表不存在就创建
            cursor2.execute("CREATE TABLE {} (时间 TEXT, 币种 TEXT, 余额 TEXT, 冻结 TEXT, 可用 TEXT)".format(data_sheet))
        # 插入新数据
        cursor2.execute(
            'insert into {} (时间, 币种, 余额, 冻结, 可用) values (%s, %s, %s, %s, %s)'.format(
                data_sheet),
            [timestamp, currency, balance, frozen, available])
        conn2.commit()
        cursor2.close()
        conn2.close()

    def mysql_save_okex_fixedfutures_accounts(self, database, data_sheet, symbol, currency, margin_mode,
                                                                equity, fixed_balance, available_qty, margin_frozen,
                                                                margin_for_unfilled, realized_pnl, unrealized_pnl,
                                                                total_avail_balance, auto_margin, liqui_mode,
                                                                can_withdraw, timestamp=None):
        """存储okex逐仓模式交割合约账户信息至mysql数据库"""
        timestamp = timestamp if timestamp is not None else time.get_localtime()   # 默认是自动填充本地时间，也可以传入*****来做数据分割
        # 检查数据库是否存在，如不存在则创建
        user = config.mysql_user_name if config.mysql_authorization == "enabled" else 'root'
        password = config.mysql_password if config.mysql_authorization == "enabled" else 'root'
        conn1 = mysql.connector.connect(user=user, password=password)
        cursor1 = conn1.cursor()
        cursor1.execute("SHOW DATABASES")
        list1 = []
        for item in cursor1:
            for x in item:
                list1.append(x)
        if database in list1:
            pass
        else:
            cursor1.execute("CREATE DATABASE {}".format(database))
        conn1.commit()
        cursor1.close()
        conn1.close()
        # 检查数据表是否存在，如不存在则创建
        conn2 = mysql.connector.connect(user=user, password=password, database=database)
        cursor2 = conn2.cursor()
        cursor2.execute("SHOW TABLES")
        list2 = []
        for item in cursor2:
            for x in item:
                list2.append(x)
        if data_sheet in list2:
            pass
        else:  # 如果数据表不存在就创建
            cursor2.execute("CREATE TABLE {} (时间 TEXT, 币对 TEXT, 余额币种 TEXT, 账户类型 TEXT, 账户权益 TEXT, 逐仓账户余额 TEXT, 逐仓可用余额 TEXT, 持仓已用保证金 TEXT, 挂单冻结保证金 TEXT, 已实现盈亏 TEXT, 未实现盈亏 TEXT, 账户静态权益 TEXT, 是否自动追加保证金 TEXT, 强平模式 TEXT, 可划转数量 TEXT)".format(data_sheet))
        # 插入新数据
        cursor2.execute(
            'insert into {} (时间, 币对, 余额币种, 账户类型, 账户权益, 逐仓账户余额, 逐仓可用余额, 持仓已用保证金, 挂单冻结保证金, 已实现盈亏, 未实现盈亏, 账户静态权益, 是否自动追加保证金, 强平模式, 可划转数量) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(
                data_sheet),
            [timestamp, symbol, currency, margin_mode, equity, fixed_balance, available_qty, margin_frozen,
             margin_for_unfilled, realized_pnl, unrealized_pnl, total_avail_balance, auto_margin, liqui_mode, can_withdraw])
        conn2.commit()
        cursor2.close()
        conn2.close()

    def mysql_save_okex_crossedfutures_accounts(self, database, data_sheet, symbol, currency, margin_mode, equity, total_avail_balance, margin,
                                                margin_frozen, margin_for_unfilled, realized_pnl, unrealized_pnl, margin_ratio, maint_margin_ratio,
                                                liqui_mode, can_withdraw, liqui_fee_rate, timestamp=None):
        """存储okex全仓模式交割合约账户信息至mysql数据库"""
        timestamp = timestamp if timestamp is not None else time.get_localtime()   # 默认是自动填充本地时间，也可以传入*****来做数据分割
        # 检查数据库是否存在，如不存在则创建
        user = config.mysql_user_name if config.mysql_authorization == "enabled" else 'root'
        password = config.mysql_password if config.mysql_authorization == "enabled" else 'root'
        conn1 = mysql.connector.connect(user=user, password=password)
        cursor1 = conn1.cursor()
        cursor1.execute("SHOW DATABASES")
        list1 = []
        for item in cursor1:
            for x in item:
                list1.append(x)
        if database in list1:
            pass
        else:
            cursor1.execute("CREATE DATABASE {}".format(database))
        conn1.commit()
        cursor1.close()
        conn1.close()
        # 检查数据表是否存在，如不存在则创建
        conn2 = mysql.connector.connect(user=user, password=password, database=database)
        cursor2 = conn2.cursor()
        cursor2.execute("SHOW TABLES")
        list2 = []
        for item in cursor2:
            for x in item:
                list2.append(x)
        if data_sheet in list2:
            pass
        else:  # 如果数据表不存在就创建
            cursor2.execute("CREATE TABLE {} (时间 TEXT, 币对 TEXT, 余额币种 TEXT, 账户类型 TEXT, 账户权益 TEXT, 账户余额 TEXT, 保证金 TEXT, 持仓已用保证金 TEXT, 挂单冻结保证金 TEXT, 已实现盈亏 TEXT, 未实现盈亏 TEXT, 保证金率 TEXT, 维持保证金率 TEXT, 强平模式 TEXT, 可划转数量 TEXT, 强平手续费 TEXT)".format(data_sheet))
        # 插入新数据
        cursor2.execute(
            'insert into {} (时间, 币对, 余额币种, 账户类型, 账户权益, 账户余额, 保证金, 持仓已用保证金, 挂单冻结保证金, 已实现盈亏, 未实现盈亏, 保证金率, 维持保证金率, 强平模式, 可划转数量, 强平手续费) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(
                data_sheet),
            [timestamp, symbol, currency, margin_mode, equity, total_avail_balance, margin,
                                                margin_frozen, margin_for_unfilled, realized_pnl, unrealized_pnl, margin_ratio, maint_margin_ratio,
                                                liqui_mode, can_withdraw, liqui_fee_rate])
        conn2.commit()
        cursor2.close()
        conn2.close()

    def mysql_save_okex_swap_accounts(self, database, data_sheet, timestamp, symbol, currency, margin_mode, equity, total_avail_balance, fixed_balance, margin, margin_frozen, realized_pnl, unrealized_pnl, margin_ratio, maint_margin_ratio, max_withdraw):
        """存储okex全仓模式交割合约账户信息至mysql数据库"""
        # 检查数据库是否存在，如不存在则创建
        user = config.mysql_user_name if config.mysql_authorization == "enabled" else 'root'
        password = config.mysql_password if config.mysql_authorization == "enabled" else 'root'
        conn1 = mysql.connector.connect(user=user, password=password)
        cursor1 = conn1.cursor()
        cursor1.execute("SHOW DATABASES")
        list1 = []
        for item in cursor1:
            for x in item:
                list1.append(x)
        if database in list1:
            pass
        else:
            cursor1.execute("CREATE DATABASE {}".format(database))
        conn1.commit()
        cursor1.close()
        conn1.close()
        # 检查数据表是否存在，如不存在则创建
        conn2 = mysql.connector.connect(user=user, password=password, database=database)
        cursor2 = conn2.cursor()
        cursor2.execute("SHOW TABLES")
        list2 = []
        for item in cursor2:
            for x in item:
                list2.append(x)
        if data_sheet in list2:
            pass
        else:  # 如果数据表不存在就创建
            cursor2.execute("CREATE TABLE {} (时间 TEXT, 币对 TEXT, 余额币种 TEXT, 账户类型 TEXT, 账户权益 TEXT, 账户余额 TEXT, 逐仓账户余额 TEXT, 持仓已用保证金 TEXT, 挂单冻结保证金 TEXT, 已实现盈亏 TEXT, 未实现盈亏 TEXT, 保证金率 TEXT, 维持保证金率 TEXT, 可划转数量 TEXT)".format(data_sheet))
        # 插入新数据
        cursor2.execute(
            'insert into {} (时间, 币对, 余额币种, 账户类型, 账户权益, 账户余额, 逐仓账户余额, 持仓已用保证金, 挂单冻结保证金, 已实现盈亏, 未实现盈亏, 保证金率, 维持保证金率, 可划转数量) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(
                data_sheet),
            [timestamp, symbol, currency, margin_mode, equity, total_avail_balance, fixed_balance, margin, margin_frozen, realized_pnl, unrealized_pnl, margin_ratio, maint_margin_ratio, max_withdraw])
        conn2.commit()
        cursor2.close()
        conn2.close()

    def delete_mysql_database(self, database):
        """删除mysql中的数据库"""
        # 连接数据库
        user = config.mysql_user_name if config.mysql_authorization == "enabled" else 'root'
        password = config.mysql_password if config.mysql_authorization == "enabled" else 'root'
        conn = mysql.connector.connect(user=user, password=password)
        cursor = conn.cursor()
        # 删除数据库
        sql = "DROP DATABASE IF EXISTS {}".format(database)
        cursor.execute(sql)
        # 保存更改并关闭连接
        conn.commit()
        cursor.close()
        conn.close()

    def delete_mongodb_database(self, database):
        """删除mongodb的数据库"""
        client = pymongo.MongoClient(host='localhost', port=27017)
        if config.mongodb_authorization == "enabled":  # 如果启用了授权验证
            client.admin.authenticate(config.mongodb_user_name, config.mongodb_password, mechanism='SCRAM-SHA-1')
        db = client[database]
        db.command("dropDatabase")

    def mysql_save_strategy_run_info(self, database, data_sheet, timestamp, action, price, amount, turnover, hold_price, hold_direction, hold_amount, profit, total_profit, total_asset):
        """
        保存策略运行过程中的数据信息到mysql数据库中，可以是回测的信息或者是实盘运行过程中的信息
        :param database: 数据库名称
        :param data_sheet: 数据表名称
        :param timestamp: 时间戳
        :param action: 交易类型，如"买入开多"等等
        :param price: 下单价格
        :param amount: 下单数量
        :param turnover: 成交金额
        :param hold_price: 当前持仓价格
        :param hold_direction: 当前持仓方向
        :param hold_amount: 当前持仓数量
        :param profit: 此次交易盈亏
        :param total_profit: 策略运行总盈亏
        :param total_asset: 当前总资金
        :return:
        """
        # 检查数据库是否存在，如不存在则创建
        user = config.mysql_user_name if config.mysql_authorization == "enabled" else 'root'
        password = config.mysql_password if config.mysql_authorization == "enabled" else 'root'
        conn1 = mysql.connector.connect(user=user, password=password)
        cursor1 = conn1.cursor()
        cursor1.execute("SHOW DATABASES")
        list1 = []
        for item in cursor1:
            for x in item:
                list1.append(x)
        if database in list1:
            pass
        else:
            cursor1.execute("CREATE DATABASE {}".format(database))
        conn1.commit()
        cursor1.close()
        conn1.close()
        # 检查数据表是否存在，如不存在则创建
        conn2 = mysql.connector.connect(user=user, password=password, database=database)
        cursor2 = conn2.cursor()
        cursor2.execute("SHOW TABLES")
        list2 = []
        for item in cursor2:
            for x in item:
                list2.append(x)
        if data_sheet in list2:
            pass
        else:  # 如果数据表不存在就创建
            cursor2.execute(
                "CREATE TABLE {} (时间 TEXT, 类型 TEXT, 价格 FLOAT, 数量 FLOAT, 成交金额 FLOAT, 当前持仓价格 FLOAT, 当前持仓方向 TEXT, 当前持仓数量 FLOAT, 此次盈亏 FLOAT, 总盈亏 FLOAT, 总资金 FLOAT)".format(data_sheet))
        # 插入新数据
        cursor2.execute(
            'insert into {} (时间, 类型, 价格, 数量, 成交金额, 当前持仓价格, 当前持仓方向, 当前持仓数量, 此次盈亏, 总盈亏, 总资金) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(data_sheet),
            [timestamp, action, price, amount, turnover, hold_price, hold_direction, hold_amount, profit, total_profit, total_asset])
        conn2.commit()
        cursor2.close()
        conn2.close()


    def read_purequant_server_datas(self, datasheet):  # 获取数据库满足条件的数据
        """
        查询PureQuant服务器数据库中满足条件的数据
        :param datasheet:
        :return:
        """
        # 连接数据库
        user = 'root'
        password = '123456'
        conn = mysql.connector.connect(host="62.234.75.102", user=user, password=password, database="kline", buffered=True)
        cursor = conn.cursor()
        # 打开游标
        cursor.execute("SELECT * FROM {} WHERE {} {} '{}'".format(datasheet, "open", ">", 0))
        LogData = cursor.fetchall()  # 取出了数据库数据
        # 关闭游标和连接
        cursor.close()
        conn.close()
        return LogData

storage = Storage()