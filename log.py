import logging

#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import time
import os


class Log(object):
    '''
封装后的logging
    '''

    def __init__(self, logger=None, log_cate='watch'):
        '''
            指定保存日志的文件路径，日志级别，以及调用文件
            将日志存入到指定的文件中
        '''

        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        # 创建一个handler，用于写入日志文件
        self.log_time = time.strftime("%Y_%m_%d")
        file_dir = os.getcwd() + '/../log'
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        self.log_path = file_dir
        self.log_name = self.log_path + "/" + log_cate + "." + self.log_time + '.log'
        # print(self.log_name)

        fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8')  # 这个是python3的
        fh.setLevel(logging.INFO)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = logging.Formatter(
            '[%(asctime)s] %(filename)s->%(funcName)s line:%(lineno)d [%(levelname)s]%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        #  添加下面一句，在记录日志之后移除句柄
        self.logger.removeHandler(ch)
        self.logger.removeHandler(fh)
        # 关闭打开的文件
        fh.close()
        ch.close()

    def getlog(self):
        return self.logger

# def get_logger(log_file):
#     logger_obj = logging.getLogger('')  # 创建一个logger对象
#     fh = logging.FileHandler(log_file)  # 创建一个文件输出流；
#     fh.setLevel(logging.DEBUG)  # 定义文件输出流的告警级别；
#     ch = logging.StreamHandler()  # 创建一个屏幕输出流；
#     ch.setLevel(logging.DEBUG)  # 定义屏幕输出流的告警级别；
#
#     formater = logging.Formatter(
#         '%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # 自定义日志的输出格式，这个格式可以被文件输出流和屏幕输出流调用；
#     fh.setFormatter(formater)  # 添加格式花输出，即调用我们上面所定义的格式，换句话说就是给这个handler选择一个格式；
#     ch.setFormatter(formater)
#
#     logger_obj.addHandler(fh)  # logger对象可以创建多个文件输出流（fh）和屏幕输出流（ch）哟
#     logger_obj.addHandler(ch)
#
#     return logger_obj  # 将我们创建好的logger对象返回
