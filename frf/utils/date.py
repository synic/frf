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

import pytz
import six
import datetime


def start_and_end_of(date):
    """Return the start and end datetime of a given date.

    Given a date, it will return the ``datetime.datetime`` for both the first
    second of the current day, and the last second of the current day.

    Args:
        date (datetime.datetime): The date.

    Returns:
        tuple: Beginning of the day, end of the day
    """
    y, m, d = date.year, date.month, date.day

    if getattr(date, 'tzinfo', None) is None:

        return (
            datetime.datetime(y, m, d, 00, 00, 00),
            datetime.datetime(y, m, d, 23, 59, 59)
        )
    else:
        return (
            datetime.datetime(y, m, d, 00, 00, 00, tzinfo=date.tzinfo),
            datetime.datetime(y, m, d, 23, 59, 59, tzinfo=date.tzinfo)
        )


def datetime_from_timestamp(timestamp, tzinfo=pytz.utc):
    """Convert a (unix) timestamp to a timezone-aware datetime.

    Args:
        timestamp (float): The timestamp to convert.  If passed as a string, it
            will be converted to an float.
        tzinfo (pytz.timezone): The timezone you want the newly created
            datetime to have.  UTC will be the default if you exclude this
            argument.
    Returns:
        datetime.datetime
    """
    if isinstance(timestamp, six.string_types):
        timestamp = float(timestamp)

    dt = datetime.datetime.utcfromtimestamp(timestamp)

    if tzinfo:
        return dt.replace(tzinfo=pytz.utc).astimezone(tzinfo)
    else:
        return dt


def timestamp_from_datetime(date):
    """Convert a datetime to a unix timestamp.

    Args:
        date (datetime.datetime): The datetime you want to convert.
    """
    if getattr(date, 'tzinfo', None) is None:
        return (date - datetime.datetime(1970, 1, 1)).total_seconds()
    else:
        return (date - datetime.datetime(
            1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
