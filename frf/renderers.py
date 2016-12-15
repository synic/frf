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

from frf.viewsets import ViewSet


class BaseRenderer(object):
    """Base Renderer.

    Subclass this to create your own renderers.
    """
    list_only = False  # whether or not this is a list only renderer

    def render(self, req, resp, view, data):
        return data


class ListMetaRenderer(BaseRenderer):
    """Render ``list`` with pagination information.

    If you are not using pagination, the meta dictionary will only contain a
    `total` key.

    Output will appear like this:

    .. code-block:: text

        {"results": [
            {
                "id": 1,
                "name": "something"
            },
            {
                "id": 1,
                "name": "something else"
            }
          "meta": {
              "total": 2,
              "page": 1,
              "per_page": 10,
              "page_limit": 100
          }
        }
    """
    list_only = True

    def render(self, req, resp, view, data):
        if isinstance(data, list):
            data = {
                'meta': req.context.get(ViewSet.META_CONTEXT_KEY, {}),
                'results': data,
            }

        return data
