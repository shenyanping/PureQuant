# -*- coding:utf-8 -*-

"""
日志输出

Author: Gary-Hertel
Date:   2020/07/09
email: interstella.ranger2020@gmail.com
"""

import logging
from logging import handlers
from purequant.config import config
from concurrent_log_handler import ConcurrentRotatingFileHandler
import os
import colorlog
import traceback

log_colors_config = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'blue',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

class __LOGGER:

    def __init__(self):
        if not os.path.exists("./logs"):    # 如果logs文件夹不存在就自动创建
            os.makedirs("./logs")
        self.__path = './logs/purequant.log'
        self.__logger = logging.getLogger("purequant")

    def __initialize(self):
        if config.level == "debug":
            level = logging.DEBUG
        elif config.level == "info":
            level = logging.INFO
        elif config.level == "warning":
            level = logging.WARNING
        elif config.level == "error":
            level = logging.ERROR
        elif config.level == "critical":
            level = logging.CRITICAL
        else:
            level = logging.DEBUG
        self.__logger.setLevel(level=level)
        formatter = logging.Formatter(fmt='[%(asctime)s] -> [%(levelname)s] : %(message)s')
        # 文件输出按照时间分割
        time_rotating_file_handler = handlers.TimedRotatingFileHandler(filename=self.__path, when='MIDNIGHT',
                                                                       interval=1, backupCount=10)
        time_rotating_file_handler.setFormatter(formatter)
        time_rotating_file_handler.suffix = "%Y%m%d-%H%M%S.log"

        # 控制台输出
        console_formatter = colorlog.ColoredFormatter(
            fmt='%(log_color)s[%(asctime)s] -> [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S',
            log_colors=log_colors_config
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(console_formatter)

        # 文件输出按照大小分割
        rotatingHandler = ConcurrentRotatingFileHandler(self.__path, "a", 1024 * 1024, 10) # a为追加模式，按1M大小分割,保留最近10个文件
        rotatingHandler.setFormatter(formatter)

        if config.handler == "time":
            self.__logger.addHandler(time_rotating_file_handler)
        elif config.handler == "file":
            self.__logger.addHandler(rotatingHandler)
        else:
            self.__logger.addHandler(stream_handler)

    def debug(self, msg=None):
        self.__initialize()
        self.__logger.debug(msg) if msg is not None else self.__logger.debug(traceback.format_exc(limit=1))

    def info(self, msg=None):
        self.__initialize()
        self.__logger.info(msg) if msg is not None else self.__logger.info(traceback.format_exc(limit=1))

    def warning(self, msg=None):
        self.__initialize()
        self.__logger.warning(msg) if msg is not None else self.__logger.warning(traceback.format_exc(limit=1))

    def error(self, msg=None):
        self.__initialize()
        self.__logger.error(msg) if msg is not None else self.__logger.error(traceback.format_exc(limit=1))

    def critical(self, msg=None):
        self.__initialize()
        self.__logger.critical(msg) if msg is not None else self.__logger.critical(traceback.format_exc(limit=1))


logger = __LOGGER()

