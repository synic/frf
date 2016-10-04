import falcon
import binascii
import base64
from gettext import gettext as _


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
