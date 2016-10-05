import os
import sys
import unittest

sys.path.append(os.path.dirname(__file__))

from frf.tests import fakeproject  # noqa
from frf.cache.engines.dummy import DummyCacheEngine  # noqa
from frf import conf, cache, db  # noqa

#: NOTE: The tests here are initializeed when we import ``fakeproject`` above.


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
