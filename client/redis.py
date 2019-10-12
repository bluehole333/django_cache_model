# -*- coding: utf-8 -*-
"""
redis 封装 客户端
"""
import pickle
from redis import StrictRedis, ConnectionError


class PickledRedis(StrictRedis):
    """
    a pickled redis client
    """

    def get(self, name):
        pickled_value = super(PickledRedis, self).get(name)
        if pickled_value is None:
            return None
        return pickle.loads(pickled_value)

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        # name:保存的key 类似 key|app.modles.friend|用户id
        # 先dumps 转成二进制 序列化 1和2是二进制  HIGHEST_PROTOCOL:是2  快而剩空间

        return super(PickledRedis, self).set(name, pickle.dumps(value, pickle.HIGHEST_PROTOCOL), ex, px, nx, xx)


class RedisClient(object):

    def __init__(self, config):
        """
        servers is a string like "IP:PORT; IP:PORT"
        """
        self.master = None
        self.slaves = []
        self.timeout = 0
        self.db = 1
        self.try_times = config.get("TRY_TIMES", 1)

        self._set_master_slavers(config['masters'])
        self._set_master_slavers(config['slaves'])

    def _set_master_slavers(self, servers):
        """
        set master and slavers
        """
        if isinstance(servers, str):
            try:
                host, port = servers.split(":")
                self.master = PickledRedis(host=host, port=int(port), db=self.db)
            except (ValueError, TypeError):
                pass
            return

        for server in servers:
            try:
                host, port = server.split(":")
                rclient = PickledRedis(host=host, port=int(port), db=self.db)
            except (ValueError, TypeError):
                pass
            else:
                self.slaves.append(rclient)

    def get_data(self, model_cls, pkey, default=None):
        return self.get(pkey, default=default)

    def put_data(self, model_cls, pkey, data, create_new):
        return self.set(pkey, data)

    def add(self, key, value, timeout=0, min_compress=50):
        """
        timeout:过期时间
        min_compress:压缩
        """
        return self.master.set(key, value, px=timeout)
