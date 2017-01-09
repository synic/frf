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

import functools

import falcon

from frf.views import View
from frf.utils.conf import OverrideSettingsManager


class SimpleView(View):
    """A simple view for use with the :func:`.simpleview` decorator.

    See :func:`.simpleview` for usage.
    """
    def __init__(self, function, methods=('get', ), **kwargs):
        super().__init__()
        self.function = function
        self.methods = []
        for method in methods:
            self.methods.append(method.lower())

        for key, value in kwargs.items():
            setattr(self, key, value)

    def _call_func(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __getattr__(self, key):
        if key in self.methods:
            return self._call_func
        elif key in ('post', 'put', 'patch', 'delete', 'get'):
            raise falcon.HTTPMethodNotAllowed(
                [m.upper() for m in self.methods])

        raise AttributeError(key)


def simpleview(methods=('get', ), **kwargs):
    """Decorator for making simple function based views.

    While most of FRF is centered around making APIs, sometimes you just need a
    simple view, akin to Django views, for things like webhook callbacks,
    pushes from google, oauth, etc.

    Usage example:

    .. code-block:: python
       :caption: views.py

        from frf.decorators import simpleview

        from myproject import authentication, models, db


        def simple_view_policy_kwargs():
            '''Return a dictionary of possible authentication, parsers, etc'''
            return {
                'authentication': authentication.OAuth2Authentication(),
            }


        @simpleview(methods=('post', ), **simple_view_policy_kwargs())
        def delete_user(req, resp, user_uuid):
            user = models.User.query.filter_by(uuid=uuid).first()
            db.session.delete()
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise

    .. code-block:: python
       :caption: routes.py

       from myproject.views import delete_user

       routes = [
           ('/delete_user/{uuid}/', delete_user),
       ]
    """
    def wrapper(function):
        simpleview = SimpleView(function=function, methods=methods, **kwargs)
        simpleview.__doc__ = function.__doc__
        return simpleview

    return wrapper


def override_settings(**variables):
    """Temporarily override configuration settings.

    See :class:`frf.utils.conf.override_settings` for more information.

    This is the same as the context manager, except in function form for
    overriding specific test cases, etc.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with OverrideSettingsManager(**variables):
                retval = func(*args, **kwargs)
            return retval
        return wrapper
    return decorator
