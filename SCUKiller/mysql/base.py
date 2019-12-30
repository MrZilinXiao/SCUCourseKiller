# -*- coding: utf-8 -*-
import random
from django.core.exceptions import ImproperlyConfigured

try:
    import MySQLdb as Database
except ImportError as err:
    raise ImproperlyConfigured(
        'Error loading MySQLdb module.\n'
        'Did you install mysqlclient?'
    ) from err

from django.db.backends.mysql.base import *
from django.db.backends.mysql.base import DatabaseWrapper as _DatabaseWrapper


class DatabaseWrapper(_DatabaseWrapper):
    def get_new_connection(self, conn_params):
        pool_size = self.settings_dict.get('POOL_SIZE') or 1
        return ConnectPool.instance(conn_params, pool_size).get_connection()

    def _close(self):
        return None  # 覆盖掉原来的close方法，查询结束后连接不会自动关闭


class ConnectPool(object):
    def __init__(self, conn_params, pool_size):
        self.conn_params = conn_params
        self.pool_size = pool_size
        self.connects = []

    # 实现连接池的单例
    @staticmethod
    def instance(conn_params, pool_size):
        if not hasattr(ConnectPool, '_instance'):
            ConnectPool._instance = ConnectPool(conn_params, pool_size)
        return ConnectPool._instance

    def get_connection(self):
        if len(self.connects) < self.pool_size:
            new_connect = Database.connect(**self.conn_params)
            self.connects.append(new_connect)
            return new_connect
        index = random.randint(0, self.pool_size - 1)  # 注意这里和range不一样，要减1
        try:
            self.connects[index].ping()
        except:
            self.connects[index] = Database.connect(**self.conn_params)
        return self.connects[index]