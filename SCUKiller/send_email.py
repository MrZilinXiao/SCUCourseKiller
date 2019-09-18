# -*- encoding: utf-8 -*-
"""
@File    : send_email.py
@Time    : 2019/9/18 20:39
@Author  : MrZilinXiao
@Email   : me@mrxiao.net
@Software: PyCharm
"""
# coding:utf-8
from django.template import loader
from django.conf import settings
from django.core.mail import EmailMessage
import threading

# 继承Thread，需要实现run方法
from SCUKiller.models import EmailVerifyRecord
from SCUKiller.pay import random_str


class SendHtmlEmail(threading.Thread):
    """send html email"""

    def __init__(self, subject, html_content, send_from, to_list, fail_silently=False):
        self.subject = subject
        self.html_content = html_content
        self.send_from = send_from
        self.to_list = to_list
        self.fail_silently = fail_silently  # 默认fail_silently=True发送异常不报错
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.html_content, self.send_from, self.to_list)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send(self.fail_silently)


def send_email_by_template(subject, module, data, to_list):
    """
        使用模版发送邮件，发件人默认使用配置的
        subject: string, 主题
        module:  string, 模版名称
        data:    dict,   数据
        to_list: list,   收件人
    """
    html_content = loader.render_to_string(module, data)
    send_from = settings.DEFAULT_FROM_EMAIL

    send_email = SendHtmlEmail(subject, html_content, send_from, to_list)
    send_email.start()  # 开启线程，自动运行线程里面的run方法


def send_html_email(subject, html_content, to_list):
    """发送html邮件"""
    send_from = settings.DEFAULT_FROM_EMAIL
    send_email = SendHtmlEmail(subject, html_content, send_from, to_list)
    send_email.start()


def send_register_email(email, send_type="register"):
    """
    发送邮件功能
    :param email: 收件人地址
    :param send_type: 发送类型为 注册或找回密码
    :return:
    """
    email_record = EmailVerifyRecord()
    code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()  # 将验证码 邮件地址 发送类型 保存到EmailVerifyRecord数据表中
    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = "SCUKiller注册激活链接"
        email_body = "请点击下面的链接激活你的账号：{url}/active/{code}".format(url=settings.URL, code=code)
        send_html_email(email_title, email_body, [email])
