#!coding: utf-8
import redis


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
NAME = 'natasha_bot'
redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)


def get_redis_instance():
    rc = redis.Redis(connection_pool=redis_pool)
    return rc


class SimpleCache():
    def __init__(self, app, opt):
        self.redis = get_redis_instance()
        self.opt_key = '%s:%s:%s' % (NAME, app, opt)

    def save(self, value, expire_time=None):
        if expire_time is not None:
            self.redis.setex(self.opt_key, value, expire_time)
        else:
            self.redis.set(self.opt_key, value)

    def get(self, delete=False):
        value = self.redis.get(self.opt_key)
        if value and delete:
            self.redis.delete(self.opt_key)
        return value
