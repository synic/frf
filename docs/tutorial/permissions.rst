Permissions
===========

Fred keeps going through and editing your articles, putting a blurb at the
bottom stating that tabs are better than spaces.

Fred is wrong.

Let's add the idea of a "superuser" and make it so that non-superusers
can create articles, but cannot edit or delete existing articles that
don't belong to them.

To do this, we can use FRF's permissions system.


Create a Permission Class
-------------------------

Let's create a ``HasEditPermission`` class.  Open up ``blog/permissions.py``
and add the following code:

.. code-block:: python
   :caption: permissions.py

    from frf import permissions

    from blogapi import conf


    class HasEditPermission(permissions.BasePermission):
        def has_permission(self, req, view, **kwargs):
            user = req.context.get('user', None)
            if not user:
                return False

            if req.method in ('PUT', 'PATCH', 'DELETE'):
                obj = view.get_obj(req, **kwargs)
                return user == obj.author or user in conf.get('SUPERUSERS', [])

            return True


Update Viewsets
---------------

Let's add this new permission to the admin viewset.  Open up
``blog/viewsets.py`` and make the following change:

.. code-block:: python
   :caption: viewsets.py
   :emphasize-lines: 4, 30


    from frf import viewsets
    from frf.authentication import BasicAuthentication

    from blog import models, serializers, permissions

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
        permissions = (permissions.HasEditPermission(), )

        def create_pre_save(self, req, obj, **kwargs):
            obj.author = req.context.get('user', 'unknown')


Add the SUPERUSERS Setting
--------------------------

And, finally, we need to add the list of superusers to the settings file.

Open up ``blogapi/settings.py`` and add the following:

.. code-block:: python
   :caption: settings.py

   #: Superusers
   SUPERUSERS = ['synic', 'yourusernamehere', ]
