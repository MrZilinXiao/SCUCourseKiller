# -*- encoding: utf-8 -*-
"""
@File    : storeBack.py
@Time    : 2019/8/12 16:26
@Author  : MrZilinXiao
@Email   : me@mrxiao.net
@Software: PyCharm
"""
import random
import string
import time, datetime


def generate_code(length=16, n=200):
    """生成n个长度为len的随机序列码"""
    random.seed()
    chars = string.ascii_letters + string.digits
    return [''.join([random.choice(chars) for _ in range(length)]) for _ in range(n)]


def utc2local(utc_st):
    # UTC时间转本地时间（+8:00）
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st
