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
