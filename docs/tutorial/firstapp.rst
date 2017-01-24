Create the Blog Application
===========================

FRF applications are arranged by apps.  For instance,
our ``blogapi`` repository might have a ``blog`` app for serving blog entries,
but we might also have a ``users`` app for user authentication or a
``gallery`` app for serving up pictures.

Let's create our ``blog`` app:

.. code-block:: text

   $ ./manage.py startapp blog

This will create a directory structure like the following:

.. code-block:: text

   blogapi
   |-- blog
   |   |-- __init__.py
   |   |-- models.py
   |   |-- tests.py
   |   |-- urls.py
   |   |-- serializers.py
   |   +-- viewsets.py
   +-- blogapi
       |-- __init__.py
       +-- settings.py

Create Models
-------------

Lets create a model for our blog articles.  Open up ``blog/models.py``, and
edit it to look like this:

.. code-block:: python
   :caption: models.py

   import uuid

   from frf import models


   class Article(models.Model):
       __tablename__ = 'blog_article'
       uuid = models.Column(models.GUID, primary_key=True, default=uuid.uuid4)
       author = models.Column(models.String(40), index=True)
       post_date = models.Column(
           models.DateTime(timezone=True),
           default=models.func.current_timestamp())
       title = models.Column(models.String(255))
       text = models.Column(models.Text)

Let's tell FRF that we are ready to use our new model.  Open up
``blogapi/settings.py`` and find the line that says ``INSTALLED_APPS`` and
change it to look like this:

.. code-block:: python
   :caption: settings.py

   #: Database configuration
   INSTALLED_APPS = ['blog']

Now we can tell FRF to actually create the table in the database for us:

.. code-block:: text

   $ ./manage.py syncdb
   Creating table blog_article... Done.

Create a Serializer
-------------------

We need a serializer to convert our blog posts to and from json.  Open up
``blog/serializers.py`` and edit it to look like this:

.. code-block:: python
   :caption: serializers.py

    from frf import serializers

    from blog import models


    class ArticleSerializer(serializers.ModelSerializer):
        uuid = serializers.UUIDField(read_only=True)

        class Meta:
            fields = ('uuid', 'author', 'post_date', 'title', 'text')
            required = ('author', 'title', 'text')
            model = models.Article

Most primitive type fields are detected from the model automatically.  Here we
are overriding the ``uuid`` field so we can make it read-only.  The other
fields are detected and added automatically.

Create a ViewSet
----------------

Let's create a view to serve up our blog entries.  Open up ``blog/viewsets.py``
and edit it to look like this:

.. code-block:: python
   :caption: viewsets.py

    from frf import viewsets

    from blog import models, serializers


    class ArticleViewSet(viewsets.ModelViewSet):
        serializer = serializers.ArticleSerializer()

        def get_qs(self, req, **kwargs):
            return models.Article.query.order_by(
                models.Article.post_date.desc())

Add a URL Route
-----------

We need to tell FRF how to map what url to this new ViewSet.  Open
``blog/urls.py`` and edit it to look like this:

.. code-block:: python
   :caption: urls.py

    from blog import viewsets

    article_viewset = viewsets.ArticleViewSet()

    urlpatterns = [
        ('/blog/articles/', article_viewset),
        ('/blog/articles/{uuid}/', article_viewset),
        ]

Now we need to tell our app to use the blog url routes. Open
``blogapi/urls.py`` and edit it to look like this:

.. code-block:: python
   :caption: urls.py

    from frf.urls import include, route  # noqa

    urlpatterns = [
        ('/api/', include('blog.urls')),
    ]


Start the Server
----------------

Start up the webserver:

.. code-block:: text

    $ ./managed.py runserver
    Oh hai, starting gunicorn...
    [2016-09-22 17:11:41 -0600] [11875] [INFO] Starting gunicorn 19.6.0
    [2016-09-22 17:11:41 -0600] [11875] [INFO] Listening at: http://0.0.0.0:8080 (11875)
    [2016-09-22 17:11:41 -0600] [11875] [INFO] Using worker: sync
    [2016-09-22 17:11:41 -0600] [11878] [INFO] Booting worker with pid: 11878
    [2016-09-22 17:11:41 -0600] [11879] [INFO] Booting worker with pid: 11879

Congratulations!!! You now have a blog api ready for requests.  Let's give it a try...
