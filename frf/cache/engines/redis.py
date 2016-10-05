from .base import CacheEngine


class RedisCacheEngine(CacheEngine):
    def __init__(self, **kwargs):
        import redis

        self.key_prefix = kwargs.pop('key_prefix', '__frf')
        self.default_timeout = kwargs.pop('default_timeout')
        self.connection = redis.StrictRedis(**kwargs)

    def get_connection(self):
        return self.connection

    def _get_key(self, key):
        return '{}:{}'.format(self.key_prefix, key)

    def get(self, key, default=None):
        value = self.connection.get(self._get_key(key))
        if value is None and default:
            value = default

        if isinstance(value, bytes):
            value = value.decode('utf8')

        return value

    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout

        self.connection.set(self._get_key(key), value)

        if timeout:
            self.connection.expire(key, timeout)

    def delete(self, key):
        self.connection.delete(self._get_key(key))

    def clear(self):
        for key in self.connection.scan_iter('{}:*'.format(self.key_prefix)):
            self.connection.delete(key)
