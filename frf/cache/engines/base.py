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
