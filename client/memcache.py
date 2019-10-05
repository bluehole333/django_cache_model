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
