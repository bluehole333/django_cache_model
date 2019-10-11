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
