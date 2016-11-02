Create the Blog Module
=======================

FRF applications are arranged in modules.  For instance,
our ``blogapi`` app might have a ``blog`` module for serving blog entries,
but we might also have a ``users`` module for user authentication or a
``gallery`` module for serving up pictures.

Let's create our ``blog`` module:

.. code-block:: text

   $ ./manage.py startmodule blog

This will create a directory structure like the following:

.. code-block:: text

   blogapi
   |-- blog
   |   |-- __init__.py
   |   |-- models.py
   |   |-- tests.py
   |   |-- routes.py
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
``blogapi/settings.py`` and find the line that says ``INSTALLED_MODULES`` and
change it to look like this:

.. code-block:: python
   :caption: settings.py

   #: Database configuration
   INSTALLED_MODULES = ['blog']

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
        author = serializers.StringField(required=True)
        post_date = serializers.ISODateTimeField()
        title = serializers.StringField(required=True)
        text = serializers.StringField(required=True)

        class Meta:
            model = models.Article

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

Add a Route
-----------

We need to tell FRF how to map what url to this new ViewSet.  Open
``blog/routes.py`` and edit it to look like this:

.. code-block:: python
   :caption: routes.py

    from blog import viewsets

    article_viewset = viewsets.ArticleViewSet()

    routes = [
        ('/blog/articles/', article_viewset),
        ('/blog/articles/{uuid}/', article_viewset),
        ]

Now we need to tell our app to use the blog routes.  Open ``blogapi/routes.py``
and edit it to look like this:

.. code-block:: python
   :caption: routes.py

    from frf.routes import include, route  # noqa

    routes = [
      ('/api/', include('blog.routes')),
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
