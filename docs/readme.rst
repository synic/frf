Falcon Rest Framework
=====================

Falcon Rest Framework is a REST framework inspired by
`Django Rest Framework <http://www.django-rest-framework.org/>`_,
and written using the `Falcon <http://falcon.readthedocs.io>`_ web framework.
Falcon's claim to fame is speed, and it achieves this in part by
avoiding object instantiation of objects during the request as much as
possible.  If you think about it, a Django Rest Framwork viewset that looks
like this:

.. code-block:: python

   from rest_framework.viewsets import ViewSet
   from package import filters, serializers, permissions, models, authentication

   class SomeViewSet(ViewSet):
       queryset = models.Foo.objects.all()
       serializer_class = serializers.FooSerializer
       permission_classes = [permissions.IsStaffPermission]
       authentication_classes = [authentication.OAuth2Authentication]
       filter_backends = [filters.SearchFilter, filters.OrderingFilter]

       def update(self, request, *args, **kwargs):
           # update...

Every one of **serializers.FooSerializer**, **permissions.IsStaffPermission**,
**authentication.OAuth2Authentication**, **filters.SearchFilter**, and
**filters.OrderingFilter** are instantiated and destroyed as a part of the
request process.  This is in addition to any objects that
`Django <http://djangoproject.com>`_ itself creates.  Falcon tries to defer
this to the boot process, and only instantiates a very minimal set of
classes during the request.  Falcon Rest Framework follows this philosophy,
deferring everything from filters, middleware, authentication, parsers,
renders, serializers are all created during boot, not during the request.

A similar viewset in frf would look like this:

.. code-block:: python

   from frf.viewsets import ViewSet
   from package import filters, serializers, permissions, models, authentication

   class SomeViewSet(viewsets.ViewSet):
       model = models.Foo
       serializer = serializers.FooSerializer()
       permissions = [permissions.IsStaffPermission()]
       authentication = [authentication.OAuth2Authentication()]
       filters = [
           filters.SearchFilter(models.Foo.name),
           filters.OrderingFilter(models.Foo.name),
       ]

       def update(self, req, resp, **kwargs):
           # ... update


Read the `documentation <http://falcon-rest-framework.readthedocs.io/en/latest/>`_
to find out more!
