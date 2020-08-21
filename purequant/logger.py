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

class LOGGER:

    def __init__(self, config_file):
        config.loads(config_file=config_file)
        self.__logger = logging.getLogger('test')
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
        formatter = logging.Formatter('%(asctime)s  - %(levelname)s: %(message)s')
        # 文件输出按照时间分割
        time_rotating_file_handler = handlers.TimedRotatingFileHandler(filename='./logger/readme.log', when='MIDNIGHT',
                                                                       interval=1, backupCount=10)
        time_rotating_file_handler.setFormatter(formatter)
        time_rotating_file_handler.suffix = "%Y%m%d-%H%M%S.log"

        # 控制台输出
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # 文件输出按照大小分割
        rotatingHandler = logging.handlers.RotatingFileHandler(filename='./logger/readme.log', maxBytes=1 * 1024 * 1024, backupCount=10)
        rotatingHandler.setFormatter(formatter)

        if config.handler == "time":
            self.__logger.addHandler(time_rotating_file_handler)
        elif config.handler == "file":
            self.__logger.addHandler(rotatingHandler)
        else:
            self.__logger.addHandler(stream_handler)


    def debug(self, msg):
        self.__logger.debug(msg)

    def info(self, msg):
        self.__logger.info(msg)

    def warning(self, msg):
        self.__logger.warning(msg)

    def error(self, msg):
        self.__logger.error(msg)

    def critical(self, msg):
        self.__logger.critical(msg)


