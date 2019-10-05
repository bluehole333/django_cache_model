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
