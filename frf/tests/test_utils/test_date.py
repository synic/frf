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

import pytz

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
