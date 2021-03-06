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

from gettext import gettext as _

import falcon


class View(object):
    """Simple View object.

    This takes care of the authentication and permissions classes, and converts
    the falcon way of routing HTTP methods through a dispatcher so that we can
    perform tasks before/after every type of request.

    Example:

    .. code-block:: python
       :members: views.python

       from frf import views, authentication


       class SomeView(View):
           allowed_methods = ('get', )
           authentication = (authentication.BasicAuthentication(), )

           def get(self, req, resp, **kwargs):
               resp.body = 'Hello, world!'
    """
    permissions = []
    authentication = []
    allowed_methods = ('get', 'put', 'patch', 'post', 'delete')

    def get_authentication(self, req, **kwargs):
        """Get the authentication methods.

        By default, just returns ``self.authentication``.
        """
        return self.authentication

    def get_permissions(self, req, **kwargs):
        """Get permissions.

        By default, just returns ``self.permissions``.
        """
        return self.permissions

    def authenticate(self, method, req, resp, **kwargs):
        """Loop through authentication methods.

        If the first authentication method fails, it will move onto the next
        method.  If one passes, that one will be used.  If none pass, a
        forbidden response will be returned.
        """
        # authentication
        user = None
        auth_methods = self.get_authentication(req, **kwargs)

        if auth_methods:
            for auth_method in auth_methods:
                user = auth_method.authenticate(req, self)
                if user:
                    break
            if not user:
                raise falcon.HTTPUnauthorized(
                    title=_('Not Authorized'),
                    description=_('Not Authorized'),
                    challenges=[str(m) for m in auth_methods])
            else:
                req.context['user'] = user
        else:
            # no authentication on the class, so set the user to `None`
            req.context['user'] = None

    def check_permissions(self, req, **kwargs):
        """Check permissions.

        Will check the permissions classes in order.  The first one that fails
        will be the one that causes a forbidden exception to be raised, and the
        rest will be ignored.  If none fail, the request will be allowed to
        continue.
        """
        permissions = self.get_permissions(req, **kwargs)
        if permissions:
            for permission in permissions:
                if not permission.has_permission(req, self, **kwargs):
                    raise falcon.HTTPForbidden(
                        title=_('Forbidden'),
                        description=_(
                            'You do not have permission to access '
                            'this resource.'))

    def get_allowed_methods(self, req, **kwargs):
        """Return the allowed methods.

        Returns ``self.allowed_methods`` by default.
        """
        return self.allowed_methods

    def dispatch(self, method, req, resp, **kwargs):
        """Route the request to the appropriate method.

        Also runs through the permissions (if there are any) and checks them
        against the current user.

        Args:
            method (str): The HTTP method, can be one of ``get``, ``put``,
                ``patch``, ``post``, ``delete``.
        """
        if method not in self.get_allowed_methods(req, **kwargs):
            raise falcon.HTTPMethodNotAllowed(
                allowed_methods=self.allowed_methods())

        self.authenticate(method, req, resp, **kwargs)
        self.check_permissions(req, **kwargs)

        getattr(self, method)(req, resp, **kwargs)
        resp.content_type = 'application/json'

    def on_get(self, req, resp, **kwargs):
        self.dispatch('get', req, resp, **kwargs)

    def on_put(self, req, resp, **kwargs):
        self.dispatch('put', req, resp, **kwargs)

    def on_patch(self, req, resp, **kwargs):
        self.dispatch('patch', req, resp, **kwargs)

    def on_post(self, req, resp, **kwargs):
        self.dispatch('post', req, resp, **kwargs)

    def on_delete(self, req, resp, **kwargs):
        self.dispatch('delete', req, resp, **kwargs)
