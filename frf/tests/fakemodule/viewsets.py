from frf import viewsets, permissions, views

from frf.tests.fakemodule import serializers
from frf.tests.fakemodule import models


class CompanyViewSet(viewsets.ModelViewSet):
    obj_lookup_kwarg = 'id'
    model = models.Company
    serializer = serializers.CompanySerializer()


class AuthorViewSet(viewsets.ModelViewSet):
    model = models.Author
    serializer = serializers.AuthorSerializer()
    obj_lookup_kwarg = 'uuid1'

    def get_obj_lookup_kwargs(self, req, **kwargs):
        return {
            'uuid1': kwargs['uuid1'],
            'uuid2': kwargs['uuid2'],
        }


class BookViewSet(viewsets.ModelViewSet):
    model = models.Book
    serializer = serializers.BookSerialzier()


class TestPermission(permissions.BasePermission):
    def has_permission(self, req, view, **kwargs):
        return req.method != 'POST'


class TestView(views.View):
    permissions = (TestPermission(), )

    def get(self, req, resp, **kwargs):
        return None

    def post(self, req, resp, **kwargs):
        return None
