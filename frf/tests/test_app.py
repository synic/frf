import unittest

from frf.tests import fakeproject  # noqa
from frf.cache.engines.dummy import DummyCacheEngine
from frf import conf, cache, db

#: NOTE: The tests here are initialed when we import ``fakeproject`` above.


class TestCase(unittest.TestCase):
    def test_app_init_cache(self):
        engine = cache.get_engine()

        self.assertIsInstance(engine, DummyCacheEngine)

    def test_app_init_db(self):
        engine = db.get_engine()

        self.assertEqual(engine.dialect.name, 'sqlite')

    def test_app_init_conf(self):
        self.assertTrue(conf.DEBUG)
        self.assertEqual(conf['TIMEZONE'], 'US/Mountain')
