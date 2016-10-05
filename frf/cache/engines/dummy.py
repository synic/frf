import datetime


from frf.utils import timezone

from .base import CacheEngine


class DummyItem(object):
    def __init__(self, value, timeout=None):
        self.value = value

        if timeout:
            self.expiration = timezone.now() + datetime.timedelta(
                seconds=timeout)
        else:
            self.expiration = None

    @property
    def is_expired(self):
        if not self.expiration:
            return False

        return timezone.now() > self.expiration

    def __str__(self):
        return self.value


class DummyCacheEngine(CacheEngine):
    def __init__(self, **kwargs):
        self.default_timeout = kwargs.pop('default_timeout')
        self.items = {}

    def get(self, key, default=None):
        value = self.items.get(key)

        if value is None or value.is_expired:
            if value and value.is_expired:
                del self.items[key]
            return default

        return value.value

    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout

        self.items[key] = DummyItem(value, timeout)

    def delete(self, key):
        if key in self.items:
            del self.items[key]

    def clear(self):
        self.items = {}
