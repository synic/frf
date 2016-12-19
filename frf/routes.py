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

import importlib
import logging

logger = logging.getLogger(__name__)

ROUTE_REGISTRY = []


class IncludeRoutes(list):
    def get_routelist(self, base_url):
        """Return the routes, each prepended with ``base_url``."""
        routes = []
        for route in self:
            if isinstance(route, (tuple, list)):
                if not isinstance(route, IncludeRoutes):
                    url = route[0]

                    # here we are going to try and avoid two ``//`` in a row.
                    if base_url.endswith('/') and url.startswith('/'):
                        url = url[1:]

                    routes.append(
                        ('{}{}'.format(base_url, url), route[1]))
                else:
                    routes.append(route)

        return routes


class IncludeError(Exception):
    pass


def include(module, route_name='routes'):
    """Include routes from a separate file.

    Usage:

    .. code-block:: python
       :caption: routes.py

       from frf.routes import include
       from myproject import views


       routes = [
          ('/index', views.some_view),
          include('calendars.routes'),
       ]

    Args:
        module (str or object): The absolute path to the routes. Can also be
            the routes themselves.
        route_name (str): The name of the routes variable inside ``module``.
           ``routes`` will be used if this is not specified.
    """
    if isinstance(module, str):
        try:
            module = importlib.import_module(module)
            routes_attr = getattr(module, route_name, None)
            if not routes_attr:
                logger.warning(
                    'Could not obtain routes from route module {}'.format(
                        module))
            return IncludeRoutes(routes_attr)
        except ImportError:
            logger.warning(
                'Could not load routes from module {}'.format(module))
            raise IncludeError()
    else:
        return IncludeRoutes(module)
