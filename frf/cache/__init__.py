"""Cache interface.

If you have installed the ``redis`` python package, set the ``CACHE`` setting
in your settings:

.. code-block:: text

    CACHE = {
        'engine': 'frf.cache.engines.redis.RedisCacheEngine',
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': '',
        'default_timeout': 30,
    }

If the ``default_timeout`` key is not provided, ``30`` seconds will be
used.
"""
from gettext import gettext as _

from frf.utils.importing import import_class
from frf.cache import exceptions

_cache_engine = None


def init(args):
    """Set up the connection variables.

    Args:
        args (dict): Argument to use to initialize the cache engine.
    """
    global _cache_engine

    engine_cls_name = args.pop('engine')
    if not engine_cls_name:
        raise exceptions.CacheInvalidEngine(
            _('Invalid cache engine specified.'))

    if 'default_timeout' not in args:
        args['default_timeout'] = 30

    engine_cls = import_class(engine_cls_name)
    _cache_engine = engine_cls(**args)


def get_engine():
    """Return the current cache engine.

    Raises:
        :class:`frf.cache.exceptions.CacheNotInitializedError`: If the cache
            has not yet been initialized.

    Returns:
        :class:`frf.cache.engines.base.CacheEngine`: The current cache engine.
    """
    if _cache_engine is None:
        raise exceptions.CacheNotInitializedError()

    return _cache_engine


def get(key, default=None):
    """Get a value from the store.

    Args:
        key (str): The key
        default (object): Default to return if the backend returns None

    Raises:
        :class:`frf.cache.exceptions.CacheNotInitializedError`: If the cache
            has not yet been initialized.

    Returns:
        :class:`frf.cache.engines.base.CacheEngine`: The current cache engine.
    """
    if _cache_engine is None:
        raise exceptions.CacheNotInitializedError()

    return _cache_engine.get(key, default)


def set(key, value, timeout=None):
    """Set a value.

    Args:
        key (str): The key
        value (object): The value
        timeout (int): The expiration, in seconds.  If set to None, the
            ``DEFAULT_CACHE_TIMEOUT`` setting will be used. If set to 0, the
            value will not be set to expire.

    Raises:
        :class:`frf.cache.exceptions.CacheNotInitializedError`: If the cache
            has not yet been initialized.

    Returns:
        :class:`frf.cache.engines.base.CacheEngine`: The current cache engine.
    """
    if _cache_engine is None:
        raise exceptions.CacheNotInitializedError()

    _cache_engine.set(key, value, timeout)


def delete(key):
    """Delete a value from the store.

    Args:
        key (str): The key

    Raises:
        :class:`frf.cache.exceptions.CacheNotInitializedError`: If the cache
            has not yet been initialized.

    Returns:
        :class:`frf.cache.engines.base.CacheEngine`: The current cache engine.
    """
    if _cache_engine is None:
        raise exceptions.CacheNotInitializedError()

    _cache_engine.delete(key)


def clear():
    """Clear all items in the cache.

    Raises:
        :class:`frf.cache.exceptions.CacheNotInitializedError`: If the cache
            has not yet been initialized.

    Returns:
        :class:`frf.cache.engines.base.CacheEngine`: The current cache engine.
    """
    if _cache_engine is None:
        raise exceptions.CacheNotInitializedError()

    _cache_engine.clear()
