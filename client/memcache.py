# -*- coding: utf-8 -*-
"""
memcache封装 客户端
"""
try:
    import memcache, bmemcached

    _pylibmc = False
except ImportError as e:
    import pylibmc as memcache

    _pylibmc = True

import pickle
from django.conf import settings


def force_str(text, encoding="utf-8", errors='strict'):
    t_type = type(text)
    if t_type == str:
        return text.encode(encoding, errors)

    return str(text)


class MemcacheClient(object):
    def __init__(self, config):
        """
        servers is a string like ["121.199.7.23:11211", "42.121.145.76:11211"]
        """
        self._current = memcache.Client(config['servers'])
        # 阿里云cache
        # self._current = bmemcached.Client(('c2d22a186278499f.m.cnhzaliqshpub001.ocs.aliyuncs.com:11211', ), 'c2d22a186278499f', 'Lx19901008')

        # 如果用的是pylibmc库 添加配置
        if _pylibmc:
            self._current.behaviors['distribution'] = 'consistent'
            self._current.behaviors['tcp_nodelay'] = config['tcp_nodelay']

        self.default_timeout = config['default_timeout']

    def put_data(self, model_cls, pkey, data, create_new):
        # 获取保存的key   类似 key|app.modles.xxx|用户id
        cache_key = pkey
        # 先dumps 转成二进制 序列化 1和2是二进制  HIGHEST_PROTOCOL:是2  快而剩空间
        val = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        if create_new:
            flag = self._current.add(cache_key, val, self.default_timeout)
            if not flag:
                raise Exception('memcache client add failure, cache key: %s' % cache_key)
        else:
            flag = self._current.set(cache_key, val, self.default_timeout)
            if not flag:
                raise Exception('memcache client set failure, cache key: %s' % cache_key)

    def add(self, key, value, timeout=0, min_compress=50):
        """
        timeout:过期时间
        min_compress:压缩
        """
        return self._current.set(force_str(key), value, timeout or self.default_timeout, min_compress)

    def get_data(self, model_cls, pkey):
        """
        model_cls:  model类对象
        pkey:       model对象主键
        """
        val = self._current.get(pkey)
        if val is None:
            return None

        return pickle.loads(val)

    def get(self, key, default=None):
        try:
            val = self._current.get(force_str(key))
        except:
            val = self._current.get(force_str(key))
        if val is None:
            return default

        return val

    def set(self, key, value, timeout=0, min_compress=50):
        try:
            return self._current.set(force_str(key), value, timeout or self.default_timeout, min_compress)
        except:
            return self._current.set(force_str(key), value, timeout or self.default_timeout, min_compress)

    def delete(self, key):
        try:
            try:
                val = self._current.delete(force_str(key))
            except:
                val = self._current.delete(force_str(key))
            if type(val) == bool:
                val = 1
        except:
            val = 0

        return val

    def get_multi(self, keys):
        """
        获取多个key 返回字典类型  {key:value,....}
        """
        return self._current.get_multi(map(force_str, keys))

    def incr(self, key, delta=1):
        return self._current.incr(key, delta)

    def decr(self, key, delta=1):
        """
        自增变量加上delta，默认加delta = 1
        """
        return self._current.decr(key, delta)

    def current(self):
        return self._current
