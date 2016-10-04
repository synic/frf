Try it Out
==========

The following examples use `curl <https://curl.haxx.se/>`_, please make sure
it's installed before beginning!

Create a Post
-------------

.. code-block:: text

   $ curl -H 'Content-Type: application/json' -X POST -d \
       '{"author": "adam", "title": "This is an article", "text":
       "How do you like this most amazing article?"}' \
       http://0.0.0.0:8080/api/blog/articles/


Now you can use the shell to see if it worked:

.. code-block:: text

    $ ./manage.py shell
    Python 3.5.1 (v3.5.1:37a07cee5969, Dec  5 2015, 21:12:44)
    [GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    (InteractiveConsole)
    >>> from blog import models
    >>> a = models.Article.query.first()
    >>> a.author
    'adam'
    >>> a.title
    'This is an article'
    >>> a.text
    'How do you like this most amazing article?'
    >>> a.post_date
    datetime.datetime(2016, 9, 22, 23, 20, 3, tzinfo=<UTC>)
    >>>
    >>> a.uuid
    UUID('1e1cbab1-c8b0-4cd7-a8e1-a471aead09e2')
    >>>

Do this a few more times, so that we have a few articles in the system.

List Posts
----------

.. code-block:: text

    $ curl -H 'Content-Type: application/json' -X GET \
        http://0.0.0.0:8080/api/blog/articles/ | python -m json.tool
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                    Dload  Upload   Total   Spent    Left  Speed
    100   715  100   715    0     0   224k      0 --:--:-- --:--:-- --:--:--  349k
    [
        {
            "text": "...",
            "author": "adam",
            "post_date": "2016-09-22T23:40:27+00:00",
            "title": "Fantastic article",
            "uuid": "14cb654e-e85d-4016-9196-28551eb52d6e"
        },
        {
            "text": "Test Article",
            "author": "adam",
            "post_date": "2016-09-22T23:39:03+00:00",
            "title": "This is an another article",
            "uuid": "8f44fafd-9190-425e-ab5a-08392f661912"
        },
        {
            "text": "How do you like this most amazing article?",
            "author": "adam",
            "post_date": "2016-09-22T23:38:28+00:00",
            "title": "This is an article",
            "uuid": "40dacbad-2374-4042-91b1-5d5d80b1701f"
        },
        {
            "text": "How do you like this most amazing article?",
            "author": "adam",
            "post_date": "2016-09-22T23:22:17+00:00",
            "title": "This is an article",
            "uuid": "1e1cbab1-c8b0-4cd7-a8e1-a471aead09e2"
        }
    ]

Retrieve a Post
---------------

Note a UUID from the last step, in my case, one of them was
``1e1cbab1-c8b0-4cd7-a8e1-a471aead09e2``.  Let's retrieve our article using the
api:

.. code-block:: text

    $ curl -H 'Content-Type: application/json' -X GET \
        http://0.0.0.0:8080/api/blog/articles/1e1cbab1-c8b0-4cd7-a8e1-a471aead09e2 | python -m json.tool
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                    Dload  Upload   Total   Spent    Left  Speed
    100   195  100   195    0     0  14773      0 --:--:-- --:--:-- --:--:-- 16250
    [
        {
            "text": "How do you like this most amazing article?",
            "author": "adam",
            "uuid": "1e1cbab1-c8b0-4cd7-a8e1-a471aead09e2",
            "post_date": "2016-09-22T23:20:03+00:00",
            "title": "This is an article"
        }
    ]


Update a Post
-------------

Let's update the author of the post to ``unknown``:

.. code-block:: text

   $ curl -H 'Content-Type: application/json' -X PUT -d \
       '{"author": "unknown"}' \
       http://0.0.0.0:8080/api/blog/articles/1e1cbab1-c8b0-4cd7-a8e1-a471aead09e2

Use the API to verify:

.. code-block:: text

    $ curl -H 'Content-Type: application/json' -X GET \
        http://0.0.0.0:8080/api/blog/articles/1e1cbab1-c8b0-4cd7-a8e1-a471aead09e2 | python -m json.tool
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                    Dload  Upload   Total   Spent    Left  Speed
    100   195  100   195    0     0  14773      0 --:--:-- --:--:-- --:--:-- 16250
    [
        {
            "text": "How do you like this most amazing article?",
            "author": "unknown",
            "uuid": "1e1cbab1-c8b0-4cd7-a8e1-a471aead09e2",
            "post_date": "2016-09-22T23:20:03+00:00",
            "title": "This is an article"
        }
    ]


Delete a Post
-------------

Finally, let's delete our post:

.. code-block:: text

  $ curl -H 'Content-Type: application/json' -X DELETE \
      http://0.0.0.0:8080/api/blog/articles/1e1cbab1-c8b0-4cd7-a8e1-a471aead09e2


And, verify using the shell:

.. code-block:: text

    $ ./manage.py shell
    Python 3.5.1 (v3.5.1:37a07cee5969, Dec  5 2015, 21:12:44)
    [GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    (InteractiveConsole)
    >>> from blog import models
    >>> a = models.Article.query.filter_by(
    ...     uuid='1e1cbab1-c8b0-4cd7-a8e1-a471aead09e2').first()
    >>> a is None
    True
