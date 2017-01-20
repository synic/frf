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

URL_REGISTRY = []


class IncludeURLs(list):
    def get_list(self, base_url):
        """Return the urls, each prepended with ``base_url``."""
        urls = []
        for pattern in self:
            if isinstance(pattern, (tuple, list)):
                if not isinstance(pattern, IncludeURLs):
                    url = pattern[0]

                    # here we are going to try and avoid two ``//`` in a row.
                    if base_url.endswith('/') and url.startswith('/'):
                        url = url[1:]

                    urls.append(
                        ('{}{}'.format(base_url, url), pattern[1]))
                else:
                    urls.append(pattern)

        return urls


class IncludeError(Exception):
    pass


def include(module, urlpatterns_name='urlpatterns'):
    """Include url patterns from a separate file.

    Usage:

    .. code-block:: python
       :caption: urls.py

       from frf.urls import include
       from myproject import views


       urlpatterns = [
          ('/index', views.some_view),
          include('calendars.urls'),
       ]

    Args:
        module (str or object): The absolute path to the module. Can also be
            a list of urls.
        urlpatterns_name (str): The name of the url patterns variable inside
           ``module``. ``urlpatterns`` will be used if this is not specified.
    """
    if isinstance(module, str):
        try:
            module = importlib.import_module(module)
            urlpatterns_attr = getattr(module, urlpatterns_name, None)
            if not urlpatterns_attr:
                logger.warning(
                    'Could not obtain urls paterns from url module {}'.format(
                        module))
                return []
            return IncludeURLs(urlpatterns_attr)
        except ImportError:
            logger.warning(
                'Could not load url module {}'.format(module))
            raise IncludeError()
    else:
        return IncludeURLs(module)
