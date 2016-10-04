import unittest

from frf.tests import fakeproject  # noqa
from frf import conf


class TestCase(unittest.TestCase):
    def test_app_init(self):
        # app init happened above when we imported ``fakeproject``.  Now we
        # just need to see if it actually worked.

        self.assertEqual(
            conf['PROJECT_NAME'], 'fakeproject')
        self.assertEqual(conf['MAIN_MODULE'], 'fakeproject')
