from falcon.testing import TestCase

from frf import conf


class BaseTestCase(TestCase):
    def setUp(self):
        conf['TESTING'] = True
        super().setUp()
