import mock
import pytz
import datetime
import unittest

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
