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
