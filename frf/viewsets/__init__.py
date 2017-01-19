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

from gettext import gettext as _
import json

import falcon

from frf import views
from frf.viewsets import mixins


class BasicViewSet(views.View):
    """Base ViewSet.

    A minimum usecase must define ``serializer`` and ``get_obj``, but you'll
    probably want to define a ``retrieve`` and ``list`` method, or use
    ``ReadOnlyViewSet``.
    """

    allowed_actions = ('list', 'retrieve', 'update', 'create', 'destroy')
    obj_lookup_kwarg = 'uuid'
    parsers = []
    renderers = []
    resource_name = 'result'
    resource_name_plural = 'results'
    serializer = None
    filters = []

    paginate = None

    method_map = {
        'list': 'GET',
        'retrieve': 'GET',
        'updated': 'PATCH',
        'create': 'POST',
        'destroy': 'DELETE',
    }

    reverse_method_map = {
        'get': 'list',
        'patch': 'update',
        'put': 'update',
        'post': 'create',
        'delete': 'destroy',
    }

    PAGINATOR_CONTEXT_KEY = '_frf_paginator'
    META_CONTEXT_KEY = '_frf_meta'

    def get_allowed_methods(self, req, **kwargs):
        """List of allowed methods, such as GET, POST, etc."""
        methods = []
        for action in self.get_allowed_actions(req, **kwargs):
            methods.append(self.method_map.get(action))

        return list(set(methods))

    def get_allowed_actions(self, req, **kwargs):
        """Get allowed actions.

        Normally this just returns ``self.allowed_actions``, but you can
        override to change this behavior.
        """
        return self.allowed_actions

    def dispatch(self, method, req, resp, **kwargs):
        self.authenticate(method, req, resp, **kwargs)
        mapped_method = self.reverse_method_map[method]
        assert mapped_method in (
            'list', 'retrieve', 'update', 'create', 'destroy')

        if mapped_method not in self.allowed_actions:
            raise falcon.HTTPMethodNotAllowed(
                allowed_methods=self.get_allowed_methods(req, **kwargs))

        #: update methods, make sure we can retrieve an object from the url
        if method in ('retrieve', 'update', 'destroy'):
            if self.obj_lookup_kwarg not in kwargs:
                raise falcon.HTTPBadRequest(
                    title=_('Lookup ID not found'),
                    description=_(
                        '{obj_lookup_kwarg} not passed for lookup').format(
                        obj_lookup_kwarg=self.obj_lookup_kwarg))

        self.check_permissions(req, **kwargs)

        if mapped_method == 'list' and self.obj_lookup_kwarg in kwargs:
            mapped_method = 'retrieve'

        if not hasattr(self, mapped_method):
            raise falcon.HttpBadReqeust(
                title=_('Operation not supported'),
                description=_(
                    'The operation {operation} is not supported '
                    'at this endpoint.').format(operation=mapped_method))

        getattr(self, mapped_method)(req, resp, **kwargs)

        resp.body = self.render(method, req, resp, resp.body, **kwargs)

    def get_qs(self, req, **kwargs):
        raise NotImplementedError()

    def get_obj(self, req, **kwargs):
        """Return target object.

        When performing an update, retrieve, or delete, this function will
        return the object that is being targeted. It uses
        ``ViewSet.obj_lookup_kwarg``, and this key MUST be in the route url,
        and MUST be the lookup key for the current model.

        If you wish to change the lookup key, set ``obj_lookup_kwarg`` in your
        subclass.

        When performing a create, this will return
        ``req.context.get('object')``. This needs to happen after the object is
        actually created. Useful for overriding ``create`` in your subclass,
        for instance:

        .. code-block:: python

            def create(self, req, resp, **kwargs):
                super().create(req, resp, **kwargs)

                obj = self.get_obj(req, **kwargs)
                tasks.perform_some_task.delay(obj)
        """
        raise NotImplementedError()

    def get_renderers(self, req, **kwargs):
        """Return renderers.

        By default, just returns ``self.renderers``.
        """
        return self.renderers

    def get_parsers(self, req, **kwargs):
        """Return response parsers.

        By default, it returns ```self.parsers``.
        """
        return self.parsers

    def get_filters(self, req, **kwargs):
        """Return queryset filters.

        By default, just returns ``self.filters``.
        """
        return self.filters

    def render(self, method, req, resp, data, **kwargs):
        for renderer in self.get_renderers(req, **kwargs):
            if not renderer.list_only or self.is_list(req, **kwargs):
                data = renderer.render(req, resp, self, data)

        data = json.dumps(data)

        return data

    def get_obj_lookup_kwargs(self, req, **kwargs):
        return {
            self.obj_lookup_kwarg: kwargs.get(self.obj_lookup_kwarg),
        }

    def is_list(self, req, **kwargs):
        """Return ``True`` if this is a list request."""
        return (
            req.method.lower() == 'get' and self.obj_lookup_kwarg not in kwargs
            )

    def get_filtered_qs(self, req, **kwargs):
        """Filter the queryset based on the `filters` list."""
        qs = self.get_qs(req, **kwargs)
        for filter in self.get_filters(req, **kwargs):
            if self.is_list(req, **kwargs) or not filter.list_only:
                qs = filter.filter(req, qs)

        return qs

    def paginate_qs(self, req, qs, **kwargs):
        """Paginate the queryset.

        Also sets ``req.context[ModelViewSet.META_CONTEXT_KEY]`` to a
        dictionary containing pagination information.

        If ``self.paginate`` is set to a list or tuple of 2 integers, the
        queryset will be paginated. The first integer in the list is the
        default page size, and the second is the maximum page size, otherwise,
        the queryset will be returned unchanged.

        Pagination is done using the ``page`` and ``per_page`` query string
        attributes.
        """
        raise NotImplementedError()

    def get_qs_len(self, req, qs, **kwargs):
        if isinstance(qs, (list, tuple)):
            return len(qs)
        else:
            return qs.count()

    def is_paginated(self, req, **kwargs):
        if isinstance(self.paginate, (list, tuple)) and \
                len(self.paginate) == 2:
            return True
        return False

    def get_serializer(self, req, **kwargs):
        """Return the serializer for this ``ViewSet``.

        In most circumstances, that will just be ``self.serializer``.  However,
        you can override this method and return a serializer that is determined
        at runtime.
        """
        if not self.serializer:
            raise falcon.HTTPInternalServerError(
                title='Serializer not defined.',
                description='You must define a serializer '
                'on the viewset {}'.format(self.__class__.__name__))
        return self.serializer


class ReadOnlyViewSet(
        mixins.ListMixin,
        mixins.RetrieveMixin,
        BasicViewSet):
    """A read-only version of :class:`BasicViewSet`.

    Provides the ``list`` and ``retrieve`` operations.
    """
    pass


class ViewSet(
        mixins.ListMixin,
        mixins.RetrieveMixin,
        mixins.CreateMixin,
        mixins.UpdateMixin,
        mixins.DestroyMixin,
        BasicViewSet):
    """Fully featured ViewSet.

    Provides the ``list``, ``retrieve``, ``create``, ``update``, and
    ``destroy`` operations.
    """
    pass


class BasicModelViewSet(BasicViewSet):
    """A basic model based ViewSet for use on a specific model.

    Requires that you define the ``get_qs`` method, that should return the full
    queryset that the current user has access to, for instance, something like
    this:

    .. code-block:: python

        def get_qs(self, req, **kwargs):
            return models.Calendar.query.filter_by(
                company_uuid=req.context['user'].company_uuid)
    """
    model = None

    def get_obj(self, req, **kwargs):
        if 'object' in req.context:
            return req.context.get('object')

        qs = self.get_filtered_qs(req, **kwargs)
        obj = qs.filter_by(**self.get_obj_lookup_kwargs(req, **kwargs)).first()
        if not obj:
            raise falcon.HTTPNotFound()
        return obj

    def get_qs(self, req, **kwargs):
        if not self.model:
            raise ValueError(_('You must specify a model or queryset.'))

        return self.model.query

    def paginate_qs(self, req, qs, **kwargs):
        """Paginate the queryset.

        Also sets ``req.context[ModelViewSet.META_CONTEXT_KEY]`` to a
        dictionary containing pagination information.

        If ``self.paginate`` is set to a list or tuple of 2 integers, the
        queryset will be paginated. The first integer in the list is the
        default page size, and the second is the maximum page size, otherwise,
        the queryset will be returned unchanged.

        Pagination is done using the ``page`` and ``per_page`` query string
        attributes.
        """
        default_page_by = self.paginate[0]
        maximum_page_by = self.paginate[1]
        meta = {
            'page': req.get_param_as_int('page') or 1,
            'per_page': min([
                req.get_param_as_int('per_page') or default_page_by,
                maximum_page_by,
                ]),
            'page_limit': maximum_page_by,
        }
        req.context[self.META_CONTEXT_KEY] = meta

        paginator = qs.paginate(
            page=meta.get('page'),
            per_page=meta.get('per_page'))
        # get count from the paginator so we're not executing the count SQL
        # twice
        meta['total'] = paginator.total
        req.context[self.PAGINATOR_CONTEXT_KEY] = paginator
        return paginator.items


class ReadOnlyModelViewSet(
        mixins.ListMixin,
        mixins.RetrieveMixin,
        BasicModelViewSet):
    """A read-only version of :class:`BasicModelViewSet`.

    Provides the ``list`` and ``retrieve`` operations.
    """
    pass


class ModelViewSet(mixins.ListMixin,
                   mixins.RetrieveMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   BasicModelViewSet):
    """Fully featured model ViewSet.

    Provides the ``list``, ``retrieve``, ``create``, ``update``, and
    ``destroy`` operations.
    """
    pass
