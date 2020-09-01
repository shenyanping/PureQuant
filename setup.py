# -*- coding:utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


setup(
    name="purequant",
    version="0.1.9",
    packages=[
        "purequant",
        "purequant/exchange/huobi",
        "purequant/exchange/okex",
        "purequant/exchange/binance",
        "purequant/example/double_moving_average_strategy",
        "purequant/example/plot_signal",
        "purequant/example/boll_breakthrough_strategy"
    ],
    platforms="any",
    description="数字货币程序化交易开源框架，助力中小投资者快速搭建程序化交易系统。",
    url="https://github.com/Gary-Hertel/PureQuant",
    author="Gary-Hertel",
    author_email="interstella.ranger2020@gmail.com",
    license="MIT",
    keywords=[
        "purequant", "quant", "framework", "okex", "trade", "btc"
    ],
    install_requires=[
        "chardet==3.0.4",
        "certifi==2020.4.5.1",
        "finplot==0.9.0",
        "idna==2.9",
        "mysql==0.0.2",
        "mysqlclient==2.0.1",
        "mysql-connector-python==8.0.21",
        "numpy==1.19.1",
        "pymongo==3.10.1",
        "requests==2.23.0",
        "six==1.14.0",
        "twilio==6.44.0",
        "urllib3==1.25.8",
        "websockets==8.1"
    ],
    package_data={
        "purequant/example/double_moving_average_strategy": ["*.json"],
        "purequant/example/plot_signal": ["*.json"],
    },
)
