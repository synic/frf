Authentication
==============

Well, we have an api.  However, there are no restrictions, anyone can post any
blog post at any time.  We need to make an admin version of the api, and protect
it with a password.


Create Admin API
----------------

Let's create an admin version of the api, that will live at
``/api/admin/blog``...

Open up ``blog/viewsets.py`` and edit it to look like this:

.. code-block:: python
   :caption: viewsets.py


    from frf import viewsets
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

        def get_qs(self, req, **kwargs):
            return models.Article.query.order_by(
                models.Article.post_date.desc())


    class AdminArticleViewSet(ArticleViewSet):
        allowed_actions = ('list', 'retrieve', 'update', 'create', 'delete')
        authentication = (BasicAuthentication(authorize), )

        def create_pre_save(self, req, obj, **kwargs):
            obj.author = req.context.get('user', 'unknown')


Let's go over the changes we made.  First, we made a duplicate API that just
inherits from the first api.  It only changes a few things:

1.  We are changing what can happen on both apis with ``allowed_actions``.  For
    the non-admin api, it can only list and retrieve events, while the admin api
    can do everything.
2.  We are adding :class:`frf.authentication.BasicAuthentication` the admin api.
    This will decode the basic authentication header, and pass it to our newly
    defined ``authenticate`` function, which just checks the username and
    password against a new setting (that we will add soon) - ``PASSWORDS``.
3.  Added the ``create_pre_save`` that just assigns the currently logged in
    user to the ``author`` field.


Update the Serializer
---------------------

Now that we are determining the author automatically, we don't need it to be
required in the serializer.  Open up ``blog/serializers.py`` and remove the
``required=True`` parameter from ``author``:

.. code-block:: python
   :caption: serializers.py
   :emphasize-lines: 8

    from frf import serializers

    from blog import models


    class ArticleSerializer(serializers.ModelSerializer):
        uuid = serializers.UUIDField(read_only=True)
        author = serializers.StringField()  # change this field
        post_date = serializers.ISODateTimeField()
        title = serializers.StringField(required=True)
        text = serializers.StringField(required=True)

        class Meta:
            model = models.Article


Add the PASSWORDS Setting
-------------------------

Let's add our ``PASSWORDS`` setting to the settings file.  Open up
``blogapi/settings.py`` and add the following:

.. code-block:: python
   :caption: settings.py

    #: Admin passwords
    PASSWORDS = {
        'adam': 'onetwo34',
    }

Update URLS
--------------

Now we just need to tell the system about our new setting, so open up
``blog/urls.py`` and add the new api to ``urlpatterns``:

.. code-block:: python
   :caption: urls.py

    from blog import viewsets

    article_viewset = viewsets.ArticleViewSet()
    admin_article_viewset = viewsets.AdminArticleViewSet()

    urlpatterns = [
        ('/blog/articles/', article_viewset),
        ('/blog/articles/{uuid}/', article_viewset),
        ('/admin/blog/articles/', admin_article_viewset),
        ('/admin/blog/articles/{uuid}/', admin_article_viewset),
        ]

Try it Out!
-----------

Let's try posting to our old api and see what happens:

.. code-block:: text

    $ curl -v -H 'Content-Type: application/json' \
       -X POST -d '{"title": "Fantastic article", "text": "..."}' \
       http://0.0.0.0:8080/api/blog/articles/
    *   Trying 0.0.0.0...
    * Connected to 0.0.0.0 (127.0.0.1) port 8080 (#0)
    > POST /api/blog/articles/ HTTP/1.1
    > Host: 0.0.0.0:8080
    > User-Agent: curl/7.43.0
    > Accept: */*
    > Content-Type: application/json
    > Content-Length: 61
    >
    * upload completely sent off: 61 out of 61 bytes
    < HTTP/1.1 405 Method Not Allowed
    < Server: gunicorn/19.6.0
    < Date: Fri, 23 Sep 2016 16:46:48 GMT
    < Connection: close
    < content-type: application/json; charset=UTF-8
    < allow: GET
    < content-length: 0
    <
    * Closing connection 0fd

As you can see, we got a "Method Not Allowed" response, because we can no longer
post to that api.  Let's post to the new API and see what happens:

.. code-block:: text

    $ curl -v -H 'Content-Type: application/json' \
       -X POST -d '{"title": "Fantastic article", "text": "..."}' \
       http://0.0.0.0:8080/api/blog/articles/
    *   Trying 0.0.0.0...
    * Connected to 0.0.0.0 (127.0.0.1) port 8080 (#0)
    > POST /api/admin/blog/articles/ HTTP/1.1
    > Host: 0.0.0.0:8080
    > User-Agent: curl/7.43.0
    > Accept: */*
    > Content-Type: application/json
    > Content-Length: 61
    >
    * upload completely sent off: 61 out of 61 bytes
    < HTTP/1.1 401 Unauthorized
    < Server: gunicorn/19.6.0
    < Date: Fri, 23 Sep 2016 16:49:30 GMT
    < Connection: close
    < content-length: 698
    < content-type: application/json; charset=UTF-8
    < www-authenticate: T, o, k, e, n
    <
    * Closing connection 0
    {"title": "Not Authorized", "description": "Not Authorized", "traceback": "Traceback (most recent call last):\n  File \"/Users/synic/.virtualenvs/blogapi/lib/python3.5/site-packages/falcon-1.0.0-py3.5.egg/falcon/api.py\", line 189, in __call__\n    responder(req, resp, **params)\n  File \"/Users/synic/Projects/skedup/lib/frf/frf/views.py\", line 68, in on_post\n    self.dispatch('post', req, resp, **kwargs)\n  File \"/Users/synic/Projects/skedup/lib/frf/frf/viewsets.py\", line 59, in dispatch\n    self.authenticate(method, req, resp, **kwargs)\n  File \"/Users/synic/Projects/skedup/lib/frf/frf/views.py\", line 21, in authenticate\n    challenges='Token')\nfalcon.errors.HTTPUnauthorized\n"}

And we got a "Not Authorized" error message, because we are not supplying a
username or password.  Let's try doing that:

.. code-block:: text

    $ curl -v -H 'Content-Type: application/json' \
       -X POST -d '{"title": "Fantastic article", "text": "..."}' \
       --user "adam:onetwo34" \
       http://0.0.0.0:8080/api/blog/articles/
    * Connected to 0.0.0.0 (127.0.0.1) port 8080 (#0)
    * Server auth using Basic with user 'adam'
    > POST /api/admin/blog/articles/ HTTP/1.1
    > Host: 0.0.0.0:8080
    > Authorization: Basic YWRhbTpvbmV0d28zNA==
    > User-Agent: curl/7.43.0
    > Accept: */*
    > Content-Type: application/json
    > Content-Length: 60
    >
    * upload completely sent off: 60 out of 60 bytes
    < HTTP/1.1 201 Created
    < Server: gunicorn/19.6.0
    < Date: Fri, 23 Sep 2016 16:51:40 GMT
    < Connection: close
    < content-type: application/json; charset=UTF-8
    < content-length: 152
    <
    * Closing connection 0
    [{"text": "...", "post_date": "2016-09-23T16:51:40+00:00", "uuid": "4a7485f6-91cd-407d-8daa-1322b4f909d6", "title": "Fantastic article", "author": "adam"}]


And our post is created.  You can see that ``author`` is automatically sent to
your username.  It's as easy as that!
