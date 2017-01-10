# Copyright 2016 by Teem, and other contributors,
# as noted in the individual source code files.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By contributing to this project, you agree to also license your source
# code under the terms of the Apache License, Version 2.0, as described
# above.

from frf import permissions, views, viewsets
from frf.tests.fakemodule import models, serializers


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
