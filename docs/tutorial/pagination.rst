Pagination
==========

What if, over the years, we end up having thousands of articles - it would be
too much data to return to the api in one go.  Lets add basic pagination support
to our viewset.

Open up ``blog/viewsets.py`` and add the ``paginate`` line from below:

.. code-block:: python
   :caption: viewsets.py
   :emphasize-lines: 5

    # ... snip

    class ArticleViewSet(viewsets.ModelViewSet):
        serializer = serializers.ArticleSerializer()
        paginate = (10, 100)  # add this line!
        allowed_actions = ('list', 'retrieve')

    # ... snip


And, that's it!  Your api will now page by 10, and your users can request a
certain page by passing ``?page=[num]`` on the query string.  Note that
pagination starts at page 1, not page 0.

Your users can also change the number of results they receive per page, by
passing the query string parameter ``?per_page=[num]``.  In our line above, we
have ``paginate = (10, 100)``.  In that scenario, the ``10`` is the default
number of items per page, and ``100`` is the *maximum* number that can be
requested by passing ``per_page``.  Easy!
