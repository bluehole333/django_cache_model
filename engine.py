# coding=utf-8
"""
数据存储封装 可以添加多个缓存来写入
"""
from conf import ENGINS

KEY_PREFIX = "BLUEHOLE_CACHE_MODEL_PACKAGE_"


def import_by_name(name):
    """
    动态导入
    """
    tmp = name.split(".")
    module_name = ".".join(tmp[0:-1])
    obj_name = tmp[-1]
    module = __import__(module_name, globals(), locals(), [obj_name])

    return getattr(module, obj_name)


# 获取存储实例
app = {}
for engine_name, engine in ENGINS.iteritems():
    engine_class = engine['class']
    engine_conf = engine['config']
    app[engine_name] = import_by_name(engine_class)(engine_conf)
