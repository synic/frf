Renderers
=========

Let's give our users some hints about what page they are on, by changing the
output of a list request.  We want the output of ``/api/blog/articles/`` to look
like this:

.. code-block:: text

  {
    "results": [
      {
        "post"_date: "2016-09-23T16:53:34+00:00",
        "author": "adam",
        "text": "...",
        "title": "Fantastic article",
        "uuid": "6068530e-b10c-4cc4-ba4f-b6cf1b041a85"
      },
      {
        "post"_date: "2016-09-23T16:56:44+00:00",
        "author": "adam",
        "text": "another article",
        "title": "Another Article",
        "uuid": "8068530a-a10c-fcc4-ba4f-c6cf1b041a8f"
      },
    ],
    "meta": {
      "total": 2,
      "page": 1,
      "per_page": 10,
      "page_limit": 100,
    }
  }

We call objects that change the output like this *renderers*.  Open up
``blog/viewsets.py`` and add the "list meta" renderer, like this:

.. code-block:: python
   :caption: viewsets.py
   :emphasize-lines: 1, 12

    from frf import viewsets, filters, renderers
    from frf.authentication import BasicAuthentication

    from blog import models, serializers

    # ... snip

    class ArticleViewSet(viewsets.ModelViewSet):
        serializer = serializers.ArticleSerializer()
        paginate = (10, 100)
        allowed_actions = ('list', 'retrieve')
        renderers = [renderers.ListMetaRenderer()]

    # ... snip

And, now our output should have paging information:

.. code-block:: text

  $ curl -H 'Content-Type: application/json' -X GET \
      http://0.0.0.0:8080/api/blog/articles/ | python -m json.tool
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  100   830  100   830    0     0  29363      0 --:--:-- --:--:-- --:--:-- 28620
  {
    "results": [
      {
        "uuid": "6068530e-b10c-4cc4-ba4f-b6cf1b041a85",
        "title": "Fantastic article",
        "post_date": "2016-09-23T16:53:34+00:00",
        "author": "adam",
        "text": "..."
      },
      {
        "uuid": "4a7485f6-91cd-407d-8daa-1322b4f909d6",
        "title": "Fantastic article",
        "post_date": "2016-09-23T16:51:40+00:00",
        "author": "adam",
        "text": "..."
      },
      {
        "uuid": "9ba4dffc-b1b7-426a-81b3-a25a67c55666",
        "title": "title",
        "post_date": "2016-09-23T01:27:37+00:00",
        "author": "fred",
        "text": "text"
      },
      {
        "uuid": "ed5a8f18-51c7-492e-b778-474bf087e23f",
        "title": "title",
        "post_date": "2016-09-23T01:27:06+00:00",
        "author": "adam",
        "text": "text"
      },
      {
        "uuid": "aa72fe4d-0df0-471a-9519-8f3fbbd6615d",
        "title": "another title",
        "post_date": "2016-09-23T01:26:08+00:00",
        "author": "guy",
        "text": "guy's article"
      }
    ],
    "meta": {
      "per_page": 10,
      "page": 1,
      "page_limit": 100,
      "total": 5
    }
  }
