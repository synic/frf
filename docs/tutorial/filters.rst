Filtering
=========

Let's add a filter to our api, so we can view posts from specific authors by
passing a query string argument, like:
``http://0.0.0.0:8080/api/blog/articles/?author=adam``.

Open up ``blog/viewsets.py`` and edit it to look like this:

.. code-block:: python
   :caption: viewsets.py

    from frf import viewsets, filters
    from frf.authentication import BasicAuthentication

    from blog import models, serializers

    from blogapi import conf


    def authorize(username, password):
        check_password = conf.get('PASSWORDS', {}).get(username)

        if not password or check_password != password:
            return None

        return username


    class ArticleViewSet(viewsets.ModelViewSet):
        serializer = serializers.ArticleSerializer()
        allowed_actions = ('list', 'retrieve')
        filters = [filters.FieldMatchFilter(models.Article.author)]

        def get_qs(self, req, **kwargs):
            return models.Article.query.order_by(
                models.Article.post_date.desc())


    class AdminArticleViewSet(ArticleViewSet):
        allowed_actions = ('list', 'retrieve', 'update', 'create', 'delete')
        authentication = [BasicAuthentication(authorize)]

        def create_pre_save(self, req, obj, **kwargs):
            obj.author = req.context.get('user', 'unknown')


Bam!  Now we can filter by author.

Custom Filters
--------------

Let's make a custom filter that limits the number of blog articles displayed by
listing articles to the 5 most recent, unless a flag (``?filter=all``) is in the
query string. Again, open up ``blog/viewsets.py`` and edit it to look like this:

.. code-block:: python
   :caption: viewsets.py

    from frf import viewsets, filters
    from frf.authentication import BasicAuthentication

    from blog import models, serializers

    from blogapi import conf


    class RecentFlagFilter(filters.FlagFilter):
        def __init__(self, *args, **kwargs):
            super().__init__(flag='all')

        def filter_default(self, req, qs):
            return qs.limit(conf.get('DEFAULT_ARTICLE_COUNT', 5))


    def authorize(username, password):
        check_password = conf.get('PASSWORDS', {}).get(username)

        if not password or check_password != password:
            return None

        return username


    class ArticleViewSet(viewsets.ModelViewSet):
        serializer = serializers.ArticleSerializer()
        allowed_actions = ('list', 'retrieve')
        filters = [
            filters.FieldMatchFilter(models.Article.author),
            RecentFlagFilter(),
            ]

        def get_qs(self, req, **kwargs):
            return models.Article.query.order_by(
                models.Article.post_date.desc())


    class AdminArticleViewSet(ArticleViewSet):
        allowed_actions = ('list', 'retrieve', 'update', 'create', 'delete')
        authentication = [BasicAuthentication(authorize)]

        def create_pre_save(self, req, obj, **kwargs):
            obj.author = req.context.get('user', 'unknown')


Here, we are using a specific type of filter called a *Flag Filter*.  Flag
filters apply a filter when no *flag* is present (flags are denoted by
``?filter=[flag]``, and a different filter when the flag is present.  Here, we
limit our queryset by the setting ``DEFAULT_ARTICLE_COUNT`` (which doesn't
exist, but defaults to 5) when the flag is NOT present, and we do nothing when
the flag is present.  Thus, when we put ``?filter=all`` on the query string, the
queryset is NOT limited, and we get all the results back, otherwise, we only see
the latest 5.

By using the setting ``DEFAULT_ARTICLE_COUNT`` here, we can change the default
number of articles returned by changing that setting in our ``settings.py``.
