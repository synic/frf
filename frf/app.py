"""Main application object.

Use this to initialize FRF, which will set up Falcon, the database, the
configuration system, cache, etc.

From your main module, you should import app, conf, db, cache and call
``app.init``, for example, if your app main module is ``skedup``, your
``skedup/__init__.py`` would look something like this:

.. code-block:: python

    import os

    from frf import app, conf, db, cache  # noqa

    settingsfile = os.getenv('FRF_SETTINGS_FILE', 'skedup.settings')
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
import falcon
import importlib
import os
import logging
import logging.config

from frf.utils.importing import import_class
from frf.routes import IncludeRoutes, ROUTE_REGISTRY
from frf import exceptions

from . import db, conf, cache

logger = logging.getLogger(__name__)

api = None


def _flatten_routes(route_list, routes):
    for route in route_list:
        if isinstance(route, IncludeRoutes):
            _flatten_routes(route, routes)
        else:
            routes.append(route)


def _add_routes(app, route_list):
    routes = []
    _flatten_routes(route_list, routes)

    routes += ROUTE_REGISTRY

    for route in routes:
        if route:
            app.add_route(route[0], route[1])


def init(project_name, settings_file, base_dir, main_module=None):
    """Initialize frf.

    Args:
        settings_file (str): string path to the main settings file, such as
            `skedup.settings` (if your project name was skedup).
        base_dir (str): The base directory of your project.
        main_module (str): The main module name.  If you do not pass this, the
            basename of ``base_dir`` will be used.
    """
    global api

    if not main_module:
        main_module = project_name

    # conf object setup
    conf.init(settings_file, base_dir)
    conf['PROJECT_NAME'] = project_name
    conf['MAIN_MODULE'] = main_module

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
    db.init(
        conf.get('SQLALCHEMY_CONNECTION_URI', 'sqlite://'),
        echo=conf.get('SQLALCHEMY_ECHO', False),
        use_greenlet_scope=conf.get('USING_GREENLET', False))

    # set up the cache
    if conf.get('CACHE'):
        cache.init(conf.get('CACHE') or {})

    api = falcon.API(middleware=middleware)
    # api.add_error_handler(Exception, exceptions.error_handler)
    api.set_error_serializer(exceptions.error_serializer)

    route_module_name = '{}.routes'.format(os.path.basename(conf.BASE_DIR))
    try:
        route_module = importlib.import_module(route_module_name)
        module_routes = getattr(route_module, 'routes', None)
        if module_routes:
            _add_routes(api, module_routes)
        else:
            if module_routes is None:
                logger.warning(
                    'Could not find routes in base module {}'.format(
                        route_module_name))
    except ImportError:
        logger.warning(
            'Base route module {} could not be imported.'.format(
                route_module_name))
