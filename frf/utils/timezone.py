import pytz
import logging
import datetime

from frf import conf

logger = logging.getLogger(__name__)


def now():
    """Return a timezone aware version of `now`.

    Converts the time to the timezone mentioned in the ``TIMEZONE`` setting, or
    ``UTC`` if the ``TIMEZONE`` setting is not provided.
    """
    dt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

    if conf.get('TIMEZONE'):
        dt = dt.astimezone(pytz.timezone(conf.get('TIMEZONE')))

    return dt
