# Copyright 2016 by Teem, and other contributors,
# as noted in the individual source code files.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By contributing to this project, you agree to also license your source
# code under the terms of the Apache License, Version 2.0, as described
# above.

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
