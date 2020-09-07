# -*- coding:utf-8 -*-

"""
智能渠道推送工具包

Author: Gary-Hertel
Date:   2020/07/09
email: interstella.ranger2020@gmail.com
"""
from purequant.config import config
import requests, json, smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from twilio.rest import Client
from purequant.storage import storage
from purequant.time import get_localtime

def __dingtalk(text):
    """
    推送钉钉消息。
    :param data: 要推送的数据内容，字符串格式
    :return:
    """
    json_text = {
        "msgtype": "text",
        "at": {
            "atMobiles": [
                ""
            ],
            "isAtAll": True
        },
        "text": {
            "content": text
        }
    }

    headers = {'Content-Type': 'application/json;charset=utf-8'}
    api_url = config.ding_talk_api
    dingtalk_result = requests.post(api_url, json.dumps(json_text), headers=headers).content    # 发送钉钉消息并返回发送结果
    storage.text_save("时间：" + str(get_localtime()) + "  发送状态：" + str(dingtalk_result) + "发送内容：" + str(text),
                      './dingtalk.txt')  # 将发送时间、结果和具体发送内容保存至当前目录下text文件中

def __sendmail(data):
    """
    推送邮件信息。
    :param data: 要推送的信息内容，字符串格式
    :return:
    """
    from_addr = config.from_addr
    password = config.password
    to_addr = config.to_addr
    smtp_server = config.smtp_server
    port = config.mail_port

    msg = MIMEText(data, 'plain', 'utf-8')
    name, addr = parseaddr('Alert <%s>' % from_addr)
    msg['From'] = formataddr((Header(name, 'utf-8').encode(), addr))
    name, addr = parseaddr('交易者 <%s>' % to_addr)
    msg['To'] = formataddr((Header(name, 'utf-8').encode(), addr))
    msg['Subject'] = Header('交易提醒', 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, port)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

def __twilio(message):
    """
    使用twilio推送信息到短信。
    :param message: 要推送的信息，字符串格式。
    :return:
    """
    accountSID = config.accountSID
    authToken = config.authToken
    myNumber = config.myNumber
    twilio_Number = config.twilio_Number
    twilioCli = Client(accountSID, authToken)
    twilioCli.messages.create(body=message, from_=twilio_Number, to=myNumber)

def push(message):
    """集成推送工具，配置模块中选择具体的推送渠道"""
    if config.backtest != "enabled":    # 仅实盘模式时推送信息
        if config.sendmail == 'true':
            __sendmail(message)
        if config.dingtalk == 'true':
            __dingtalk(message)
        if config.twilio == 'true':
            __twilio(message)
