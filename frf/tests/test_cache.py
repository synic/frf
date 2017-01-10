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
import unittest

import mock
import pytz

from frf import cache


class DummyCacheEngineTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        cache.init({'engine': 'frf.cache.engines.dummy.DummyCacheEngine'})
        cache.clear()

    def test_cache_get_set(self):
        cache.set('testing', 'onetwothree')

        self.assertEqual(cache.get('testing'), 'onetwothree')

    def test_cache_get_default(self):
        self.assertEqual('bwent', cache.get('woot', 'bwent'))

    @mock.patch('frf.utils.timezone.now')
    def test_cache_set_timeout(self, tznow_mock):
        tznow_mock.return_value = datetime.datetime(
            2016, 10, 5, 10, 10, 10, tzinfo=pytz.UTC)

        cache.set('test', 'value', timeout=30)

        # fast forward 29 seconds.
        tznow_mock.return_value = datetime.datetime(
            2016, 10, 5, 10, 10, 39, tzinfo=pytz.UTC)

        self.assertEqual(cache.get('test'), 'value')

        # fast forward 29 seconds.
        tznow_mock.return_value = datetime.datetime(
            2016, 10, 5, 10, 10, 41, tzinfo=pytz.UTC)

        # should be expired now
        self.assertIsNone(cache.get('test'))

    def test_cache_delete(self):
        cache.set('test', 'one')

        self.assertEqual(cache.get('test'), 'one')

        cache.delete('test')

        self.assertIsNone(cache.get('test'))

    def test_cache_clear(self):
        for i in range(3):
            cache.set(str(i), str(i))

        self.assertEqual(len(cache._cache_engine.items), 3)

        cache.clear()

        self.assertEqual(len(cache._cache_engine.items), 0)


class RedisCacheEngineTestCase(unittest.TestCase):
    # couldn't figure out how to test redis timeout, because I can't mock the
    # datetime for redis itself.
    def setUp(self):
        super().setUp()

        cache.init({
            'engine': 'frf.cache.engines.redis.RedisCacheEngine',
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': '',
            'default_timeout': 30,
            })
        cache.clear()

    def test_cache_get_set(self):
        cache.set('testing', 'onetwothree')

        self.assertEqual(cache.get('testing'), 'onetwothree')

    def test_cache_get_default(self):
        self.assertEqual('bwent', cache.get('woot', 'bwent'))

    def test_cache_delete(self):
        cache.set('test', 'one')

        self.assertEqual(cache.get('test'), 'one')

        cache.delete('test')

        self.assertIsNone(cache.get('test'))

    def test_cache_clear(self):
        for i in range(3):
            cache.set(str(i), str(i))

        cache.clear()

        for i in range(3):
            self.assertIsNone(cache.get(str(i)))
