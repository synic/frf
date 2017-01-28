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

import json

import falcon

from frf import db


class ListMixin(object):
    """List a queryset."""

    def list(self, req, resp, **kwargs):
        """List instances of this object.

        If ``self.paginate`` is set to a list or tuple of 2 integers, the
        queryset will be paginated. The first integer in the list is the
        default page size, and the second is the maximum page size.
        """
        qs = self.get_filtered_qs(req, **kwargs)
        if self.is_paginated(req, **kwargs):
            qs = self.paginate_qs(req, qs, **kwargs)
        else:
            req.context[self.META_CONTEXT_KEY] = {
                'total': self.get_qs_len(req, qs, **kwargs)}

        resp.body = self.get_serializer(req, **kwargs).serialize(qs, many=True)


class RetrieveMixin(object):
    """Retrieve an instance."""

    def retrieve(self, req, resp, **kwargs):
        """Retrieve and return target object."""
        obj = self.get_obj(req, **kwargs)
        resp.body = self.get_serializer(req, **kwargs).serialize(obj)


class CreateMixin(object):
    """Create an instance."""

    def create_pre_save(self, req, obj, **kwargs):
        pass

    def create(self, req, resp, **kwargs):
        """Create an instance of this object.

        Called for a POST, it should create and save the object specified in
        the post body.

        Args:
            req (falcon.request.Request): The request object
            resp (falcon.response.Response): The response object
            commit (bool): Default ``True``. For :class:`ModelViewSet`
                subclasses, set this to ``False`` if you would like to commit
                yourself.
        """
        data = json.loads(req.stream.read().decode('utf-8'))

        for parser in self.parsers:
            data = parser.parse(req, self, data)

        req.context['json'] = data

        # obtain the write serializer
        serializer = self.get_write_serializer(req, **kwargs)
        obj = serializer.save(data=data, ctx={'req': req})

        self.create_pre_save(req, obj, **kwargs)
        self.create_save_obj(req, obj, **kwargs)

        req.context['object'] = obj

        # obtain the read serializer
        serializer = self.get_serializer(req, **kwargs)
        resp.body = serializer.serialize(obj)
        resp.status = falcon.HTTP_201

    def create_save_obj(self, req, obj, **kwargs):
        raise NotImplementedError()


class UpdateMixin(object):
    """Update an instance."""

    def update_pre_save(self, req, obj, **kwargs):
        pass

    def update_save_obj(self, req, obj, **kwargs):
        raise NotImplementedError()

    def update(self, req, resp, **kwargs):
        """Update an instance of this object.

        Requires that you have passed ``obj_lookup_kwarg`` in the url for
        lookup.

        Args:
            req (falcon.request.Request): The request object
            resp (falcon.response.Response): The response object
            commit (bool): Default ``True``.  For model-viewsets, set this to
                ``False`` if you would like to commit yourself.
        """
        obj = self.get_obj(req, **kwargs)
        data = json.loads(req.stream.read().decode('utf-8'))

        for parser in self.get_parsers(req, **kwargs):
            data = parser.parse(req, self, data)

        req.context['json'] = data

        serializer = self.get_write_serializer(req, **kwargs)
        serializer.save(obj=obj, data=data, ctx={'req': req})

        self.update_pre_save(req, obj, **kwargs)
        self.update_save_obj(req, obj, **kwargs)

        resp.status = falcon.HTTP_204


class DestroyMixin(object):
    """Delete/Remove an instance."""

    def destroy_remove_obj(self, req, obj, **kwargs):
        raise NotImplementedError()

    def destroy(self, req, resp, **kwargs):
        """Remove an instance of this object.

        If you wish to change what happens when a delete occurs, override
        ``destroy_remove_obj``.

        Args:
            req (falcon.request.Request): The request object
            resp (falcon.response.Response): The response object
            commit (bool): Default ``True``. For :class:`ModelViewSet`
                subclasses, set this to ``False`` if you would like to commit
                yourself.
        """
        obj = self.get_obj(req, **kwargs)
        self.destroy_remove_obj(req, obj, **kwargs)
        resp.status = falcon.HTTP_204


class CreateModelMixin(CreateMixin):
    """Create a model instance."""

    def create_save_obj(self, req, obj, **kwargs):
        db.session.add(obj)

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise


class UpdateModelMixin(UpdateMixin):
    """Update a model instance."""

    def update_save_obj(self, req, obj, **kwargs):
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise


class DestroyModelMixin(DestroyMixin):
    """Delete/Remove a model instance."""

    def destroy_remove_obj(self, req, obj, **kwargs):
        db.session.delete(obj)

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
