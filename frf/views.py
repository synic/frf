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

    def authenticate(self, method, req, resp, **kwargs):
        """Loop through authentication methods.

        If the first authentication method fails, it will move onto the next
        method.  If one passes, that one will be used.  If none pass, a
        forbidden response will be returned.
        """
        #: authentication
        user = None
        if self.authentication:
            for auth_method in self.authentication:
                user = auth_method.authenticate(req, self)
                if user:
                    break
            if not user:
                raise falcon.HTTPUnauthorized(
                    title='Not Authorized',
                    description='Not Authorized',
                    challenges='Token')
            else:
                req.context['user'] = user
        else:
            # no authentication on the class, so set the user to `None`
            req.context['user'] = None

    def check_permissions(self, method, req, resp, **kwargs):
        """Check permissions.

        Will check the permissions classes in order.  The first one that fails
        will be the one that causes a forbidden exception to be raised, and the
        rest will be ignored.  If none fail, the request will be allowed to
        continue.
        """
        #: permissions
        if self.permissions:
            user = req.context.get('user', None)
            if not user:
                raise falcon.HTTPUnauthorized(
                    title='Not Authorized',
                    description='No user is currently authenticated.',
                    challenges='Token')
            for permission in self.permissions:
                if not permission.has_permission(req, **kwargs):
                    raise falcon.HTTPForbidden(
                        title='Forbidden',
                        description='You do not have permission to access '
                        'this resource.')

    def dispatch(self, method, req, resp, **kwargs):
        """Route the request to the appropriate method.

        Also runs through the permissions (if there are any) and checks them
        against the current user.
        """
        if method not in self.allowed_methods:
            raise falcon.HTTPMethodNotAllowed(
                allowed_methods=self.allowed_methods())

        self.authenticate(method, req, resp, **kwargs)
        self.check_permissions(method, req, resp, **kwargs)

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
