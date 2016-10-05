class CacheEngine(object):
    def get(self, key, default, encoding='utf8'):
        """Get a value from the store.

        Args:
            key (str): The key
            default (object): Default to return if the backend returns None
            encoding (str): If the data returned from the backend is encoded,
                use this encoding to decode it.  If you set this to None, no
                automatic conversion will be attempted.
        """
        raise NotImplementedError()

    def set(self, key, timeout=None):
        """Set a value.

        Args:
            key (str): The key
            value (object): The value
            timeout (int): The expiration, in seconds. If set to None, the
                ``DEFAULT_CACHE_TIMEOUT`` setting will be used. If set to 0,
                the value will not be set to expire.
        """
        raise NotImplementedError()

    def delete(self, key):
        """Delete a value from the store.

        Args:
            key (str): The key
        """
        raise NotImplementedError()

    def clear(self):
        """Clear all items in the cache."""
        raise NotImplementedError()
