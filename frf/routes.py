import importlib
import logging

logger = logging.getLogger(__name__)

ROUTE_REGISTRY = []


class IncludeRoutes(list):
    pass


class IncludeError(Exception):
    pass


def include(routes):
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
        include (str): The absolute path to the routes.  Can also be the routes
            themselves.
    """
    if isinstance(routes, str):
        try:
            module = importlib.import_module(routes)
            routes_attr = getattr(module, 'routes', None)
            if not routes_attr:
                logger.warning(
                    'Could not obtain routes from route module {}'.format(
                        routes))
            return IncludeRoutes(routes_attr)
        except ImportError:
            logger.warning(
                'Could not load routes from module {}'.format(routes))
            raise IncludeError()
    else:
        return IncludeRoutes(routes)
