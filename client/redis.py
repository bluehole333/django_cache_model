# -*- coding: utf-8 -*-
"""
redis 封装 客户端
"""
import random
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
        # name:保存的key 类似 key|app.modles.MODEL_Name|pk
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

    def get(self, key, default=None):
        """
        这里取2遍 如果实在去不到就return None slaves随机取一个
        """
        if not self.slaves:
            return None

        idx_dict = dict.fromkeys(range(len(self.slaves)))
        res = None
        for i in range(self.try_times):
            if len(idx_dict) > 0:
                idx = random.choice(idx_dict.keys())
                client = self.slaves[idx]
                try:
                    res = client.get(key)
                except ConnectionError:
                    idx_dict.pop(idx, None)
                else:
                    break

        if not res:
            return default

        return res

    def set(self, key, value, timeout=0, min_compress=50):
        if not self.master:
            return

        if timeout is None:
            px = self.timeout
        else:
            px = timeout

        try:
            self.master.set(key, value, px=px)
        except Exception as e:
            print("redis.client.set:", e)
            self.master.set(key, value, px=px)

    def delete(self, key):
        if not self.master:
            return

        try:
            try:
                val = self.master.delete(key)
            except:
                val = self.master.delete(key)
            if type(val) == bool:
                val = 1
        except Exception as e:
            print("redis.client.delete:", e)
            val = 0

        return val

    def current(self):
        return self._current