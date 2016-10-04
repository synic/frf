import unittest
import pytz

from frf.utils import timezone
from frf import conf


class TestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        conf.init('frf.tests.fakeproject.settings')

    def test_timezone_now(self):
        n = timezone.now()

        self.assertEquals(
            str(n.tzinfo),
            str(pytz.timezone(conf.get('TIMEZONE'))))
