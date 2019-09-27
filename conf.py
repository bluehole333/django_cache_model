ENGINS = {
    "memcache": {
        "class": "mccache.MemcacheClient",
        "config": {
            "servers": [
                "127.0.0.1:11211",
            ],
            "default_timeout": 600,
            "tcp_nodelay": True,
        }
    },
    "redis": {
        "class": "redis_base.RedisClient",
        "config": {
            "host": "127.0.0.1",
            "port": 11214,
            "db": 1,
            "time_out": 3600,
        }
    },
}
