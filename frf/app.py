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

"""Main application object.

Use this to initialize FRF, which will set up Falcon, the database, the
configuration system, cache, etc.

From your main module, you should import app, conf, db, cache and call
``app.init``, for example, if your app main module is ``skedup``, your
``skedup/__init__.py`` would look something like this:

.. code-block:: python

    import os

    from frf import app, conf, db, cache  # noqa

    settingsfile = os.getenv('FRF_SETTINGS_MODULE', 'skedup.settings')
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    app.init('skedup', settingsfile, base_dir)

Then, throughout your app, when you need to use db, conf, cache, etc, you
import it from your main module.  This assures that your code is initialized
when you need it.  For example:

>>> from skedup import conf
>>> conf.DEBUG
False
>>>

**NOTE**: If you used the ``frf-startproject`` script to create your project,
this should already be done for you.
"""

import importlib
import logging
import logging.config

import falcon

from frf import exceptions
from frf.routes import IncludeRoutes, ROUTE_REGISTRY
from frf.utils.importing import import_class

from . import cache, conf, db

logger = logging.getLogger(__name__)

api = None


def _flatten_routes(route_list, routes):
    for route in route_list:
        if isinstance(route, IncludeRoutes):
            _flatten_routes(route, routes)
        elif isinstance(route[1], IncludeRoutes):
            _flatten_routes(route[1].get_routelist(
                base_url=route[0]), routes)
        else:
            routes.append(route)


def _add_routes(app, route_list):
    routes = []
    _flatten_routes(route_list, routes)

    routes += ROUTE_REGISTRY

    for route in routes:
        if route:
            app.add_route(route[0], route[1])


def init(project_name, settings_file, base_dir, main_app=None):
    """Initialize frf.

    Args:
        settings_file (str): string path to the main settings file, such as
            `skedup.settings` (if your project name was skedup).
        base_dir (str): The base directory of your project.
        main_app (str): The main app name.  If you do not pass this, the
            basename of ``base_dir`` will be used.
    """
    global api

    if not main_app:
        main_app = project_name

    # conf object setup
    conf.init(settings_file, base_dir)
    conf['PROJECT_NAME'] = project_name
    conf['MAIN_APP'] = main_app

    # set up logging
    if 'LOGGING' in conf:
        logging.config.dictConfig(conf.get('LOGGING'))

    # set up middleware classes
    middleware_classes = conf.get('MIDDLEWARE_CLASSES', [])

    middleware = []

    for cls_name in middleware_classes:
        cls = import_class(cls_name)
        middleware.append(cls())

    # set up the database
    if conf.get('SQLALCHEMY_CONNECTION_URI'):
        db.init(
            conf.get('SQLALCHEMY_CONNECTION_URI', 'sqlite:///:memory:'),
            echo=conf.get('SQLALCHEMY_ECHO', False),
            use_greenlet_scope=conf.get('USING_GREENLET', False))

    # set up the cache
    cache.init(conf.get(
        'CACHE', {'engine': 'frf.cache.engines.dummy.DummyCacheEngine'}))

    # call app ``init_app`` functions
    for app_name in conf.get('INSTALLED_APPS', []):
        try:
            app = importlib.import_module(app_name)
        except ImportError:
            logger.error(
                'Could not import app {} which was referenced by '
                'INSTALLED_APP in the application settings.'.format(
                    app_name))
            raise

        init_app_func = getattr(app, 'init_app', None)
        if callable(init_app_func):
            init_app_func()

    api = falcon.API(middleware=middleware)
    api.set_error_serializer(exceptions.error_serializer)

    route_module_name = '{}.routes'.format(main_app)
    try:
        route_module = importlib.import_module(route_module_name)
        app_routes = getattr(route_module, 'routes', None)
        if app_routes:
            _add_routes(api, app_routes)
        else:
            if app_routes is None:
                logger.warning(
                    'Could not find routes in base route module: {}'.format(
                        route_module_name))
    except ImportError as e:
        logger.warning(
            'Base route module {} could not be imported.'.format(
                route_module_name))
        logger.error(e)
