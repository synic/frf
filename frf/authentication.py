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

import base64
import binascii
from gettext import gettext as _

import falcon


class BasicAuthentication(object):
    """Http basic password authentication."""
    def __init__(self, auth_callback):
        self.auth_callback = auth_callback

    def authenticate(self, req, view):
        try:
            auth = req.get_header('authorization').split()
        except AttributeError:
            return None

        if auth and len(auth) == 2:
            try:
                auth_parts = base64.b64decode(
                    auth[1]).decode('utf8').partition(':')

                user = self.auth_callback(auth_parts[0], auth_parts[2])
                if user:
                    return user
                else:
                    raise falcon.HTTPUnauthorized(
                        title=_('Unauthorized'),
                        description=_('Invalid credentials'),
                        challenges=('Basic',))

            except (TypeError, UnicodeDecodeError, binascii.Error):
                raise

    def __str__(self):
        return _('Basic')
