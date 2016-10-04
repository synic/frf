"""Cache interface.

Currently only supports redis.  If you have installed the ``redis`` python
package, set the ``CACHE`` setting in your settings:

.. code-block:: text

    CACHE = {
        'engine': 'frf.cache.engines.RedisEngine',
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': '',
        'default_timeout': 30,
    }

Currently, the ``engine`` key is ignore, and is reserved for future
engine support.

If the ``default_timeout`` key is not provided, ``30`` seconds will be
used.
"""
from gettext import gettext as _

try:
    import redis
except ImportError:
    redis = None

_redis_client = None
_connection_args = None
_prefix = None
_default_timeout = None


def init(args):
    """Set up the connection variables.

    Args:
        args (dict): A list of arguments to pass to ``StrictRedis``, such as
            "host", "port", "db", "password", etc.
    """
    global _connection_args, _prefix, _default_timeout

    if not redis:
        raise ValueError(
            _('Redis settings present in configuration, but the'
                ' `redis` python package is not installed.'))
    _connection_args = args
    _prefix = args.pop('key_prefix', '__frf')
    _default_timeout = args.pop('default_timeout', 30)

    # engine is currently unused
    args.pop('engine', None)


def get_redis():
    global _redis_client

    if not _redis_client:
        _redis_client = redis.StrictRedis(**_connection_args)
    return _redis_client


def get(key, default=None, encoding='utf8'):
    """Get a value from the store.

    Args:
        key (str): The key
        default (object): Default to return if the backend returns None
        encoding (str): If the data returned from the backend is encoded,
            use this encoding to decode it.  If you set this to None, no
            automatic conversion will be attempted.
    """
    key = '{}:{}'.format(_prefix, key)
    value = get_redis().get(key)
    if value is None:
        value = default

    if isinstance(value, bytes) and encoding:
        value = value.decode(encoding)

    return value


def set(key, value, timeout=None):
    """Set a value.

    Args:
        key (str): The key
        value (object): The value
        timeout (int): The expiration, in seconds.  If set to None, the
            ``DEFAULT_CACHE_TIMEOUT`` setting will be used. If set to 0, the
            value will not be set to expire.
    """
    key = '{}:{}'.format(_prefix, key)
    if timeout is None:
        timeout = _default_timeout

    get_redis().set(key, value)
    if timeout != 0:
        get_redis().expire(key, timeout)


def delete(key):
    """Delete a value from the store.

    Args:
        key (str): The key
    """
    key = '{}:{}'.format(_prefix, key)
    get_redis().delete(key)


def clear():
    """Clear all items in the cache."""
    for key in get_redis().scan_iter('{}:*'.format(_prefix)):
        get_redis().delete(key)
