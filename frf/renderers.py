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
