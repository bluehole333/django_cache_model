"""
格式:
缓存: {

}
"""
ENGINS = {
    "memcache": {
        "class": "client.memcache.MemcacheClient",
        "config": {
            "servers": [
                "127.0.0.1:11211",
            ],
            "default_timeout": 600,
            "debug": False,
        }
    },
    "redis": {
        "class": "client.redis.RedisClient",
        "config": {
            "host": "127.0.0.1",
            "port": 11214,
            "db": 1,
            "time_out": 3600,
        }
    },
}
