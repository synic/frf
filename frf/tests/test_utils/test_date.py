import unittest
import pytz
import datetime

from frf.utils import date as dateutils


class TestCase(unittest.TestCase):
    def test_start_end_of(self):
        d = datetime.datetime(2016, 1, 1, 10, 32, 1)

        start, end = dateutils.start_and_end_of(d)

        self.assertEqual(start, datetime.datetime(2016, 1, 1, 0, 0, 0))
        self.assertEqual(end, datetime.datetime(2016, 1, 1, 23, 59, 59))

    def test_timestamp_from_datetime(self):
        d = datetime.datetime(2016, 1, 1, 10, 32, 1)

        ts = dateutils.timestamp_from_datetime(d)
        self.assertEqual(ts, 1451644321.0)

    def test_datetime_from_timestamp(self):
        ts = 1451644321.0

        d = dateutils.datetime_from_timestamp(ts, None)

        self.assertEqual(d, datetime.datetime(2016, 1, 1, 10, 32, 1))

    def test_timestamp_from_datetime_timezone(self):
        tzinfo = pytz.timezone('US/Mountain')
        d = datetime.datetime(2016, 1, 1, 10, 32, 1, tzinfo=tzinfo)

        ts = dateutils.timestamp_from_datetime(d)
        self.assertEqual(ts, 1451669521.0)

    def test_datetime_from_timestamp_timezone(self):
        tzinfo = pytz.timezone('US/Mountain')
        ts = 1451669521.0

        d = dateutils.datetime_from_timestamp(ts, tzinfo=tzinfo)

        self.assertEqual(
            d, datetime.datetime(2016, 1, 1, 10, 32, 1, tzinfo=tzinfo))
