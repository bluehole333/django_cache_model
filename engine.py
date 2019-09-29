# coding=utf-8
"""
数据存储封装 可以添加多个缓存来写入
"""
import pickle
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


class Engine(object):

    def __init__(self):
        super(Engine, self).__init__()
        self.save_list = []

    @classmethod
    def generate_cache_key(cls, pkey):
        """
        生成key
        sign_key:
            如果需要刷新此model的所有cache，在model定义中修改 sign_key 即可
        """
        if hasattr(cls, "sign_key"):
            return KEY_PREFIX + cls.sign_key + "|" + cls.__module__ + "." + cls.__name__ + '|' + str(pkey)
        else:
            return KEY_PREFIX + "|" + cls.__module__ + "." + cls.__name__ + '|' + str(pkey)

    def get_pkey(self):
        """
        根据子类对象获取key
        """
        return self.__class__.generate_cache_key(self.id)

    @classmethod
    def get(cls, pkey):
        """
        cache_key:cache key
        pkey:uid 唯一标示
        """
        data = None
        level = 0
        cache_key = cls.generate_cache_key(pkey)
        # 从存储层获取dumps后的对象数据  对应这配置文件的 现在就配置了 memcached  还可以有其他的 mysql redis等等
        for engine_name in cls.save_list:
            # 根据配置的引擎 获取一个对象 比如memcache的实例
            engine_obj = app[engine_name]
            level += 1
            data = engine_obj.get_data(cls, cache_key)
            # 如果取到了 就不再 遍历
            if data is not None:
                break
        # 如果实在取不到就是没有数据
        if data is None:
            return None

        # 获取到dumps数据，转换成为对象实例  这时候对象是 字典类型的
        # 如果从底层数据库中读取出来的  再缓存到更上层cache中
        obj = pickle.loads(data)
        if level > 1:
            top_engine_obj = app[ENGINS.keys()[0]]
            top_engine_obj.put_data(cls, cache_key, data, False)

        return obj

    def put(self):
        cls = self.__class__
        data = pickle.dumps(self)
        pkey = self.get_pkey()
        for engine_name in cls.save_list:
            engine_obj = app[engine_name]
            engine_obj.put_data(cls, pkey, data, False)
