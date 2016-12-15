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

class BaseFilter(object):
    """Base Filter.

    Provides a filter contract, and some utility methods for filters.
    """
    list_only = True

    def get_field_values(self, req, query_field=None,
                         multi_query_field=None, multi=True):
        """Return the values present for a field.

        Checks the query string for flags, or their plural version (usually
        represented with a ``[]``) and returns a list containing all the
        values; both plural and not.
        """

        if not multi_query_field:
            multi_query_field = '{}s[]'.format(query_field)

        if multi:
            values = req.get_param_as_list(multi_query_field) or []
        else:
            values = []

        single = req.get_param(query_field)

        if single:
            values.append(single)

        return values

    def filter(self, req, qs):
        raise NotImplementedError()


class FieldMatchFilter(BaseFilter):
    """A basic field exact match filter.

    Will return all the rows where ``model_field`` equals the value of
    ``query_field``.
    """
    def __init__(self, model_field, query_field=None,
                 multi_query_field=None, multi=True):
        """Initialize the filter.

        Args:
            model_field (object): SQLAlchemy model field to check.
            query_field (str): The query string field to look for.
            multi_query_field (str): The query string field for multiple.  If
                not present, ``'{}s[]'.format(query_field)`` will be used.
            multi (bool): If True, also check ``multi_query_field`` in the
                query string, otherwise, only use ``query_field``.
        """
        super().__init__()
        self.model_field = model_field

        if not query_field:
            query_field = model_field.key

        self.query_field = query_field
        self.multi_query_field = multi_query_field
        self.multi = multi

    def filter(self, req, qs):
        values = self.get_field_values(
            req=req,
            query_field=self.query_field,
            multi_query_field=self.multi_query_field,
            multi=self.multi)

        if values:
            qs = qs.filter(self.model_field.in_(values))

        return qs


class FlagFilter(BaseFilter):
    """Flag style filter.

    Flags are boolean filters, available through the ``filter`` and
    ``filter[]`` query string parameters.

    If a certain flag for this flag is present in ``filter`` or ``filter[]`` in
    the query string, perform a different method for filtering than when the
    flag is not present.
    """
    def filter_flag_present(self, req, qs):
        """Override this function to filter when the flag is present."""
        return qs

    def filter_default(self, req, qs):
        """Override this function to filter when the flag is not present."""
        return qs

    def __init__(self, flag, filter_default_func=None,
                 filter_flag_present_func=None):
        """Initialize the filter.

        Args:
            flag (str): They flag to look for in ``filter`` or ``filter[]``.
            filter_default_func (function): The function to call when the flag
                is not present.
            filter_flag_present_func (function): The function to call when the
                flag is present.
        """
        if not filter_default_func:
            filter_default_func = self.filter_default

        if not filter_flag_present_func:
            filter_flag_present_func = self.filter_flag_present
        self.flag = flag
        self.filter_default_func = filter_default_func
        self.filter_flag_present_func = filter_flag_present_func

    def filter(self, req, qs):
        filters = self.get_field_values(req, 'filter', 'filter[]')

        if self.flag in filters:
            qs = self.filter_flag_present_func(req=req, qs=qs)
        else:
            qs = self.filter_default_func(req=req, qs=qs)

        return qs


class CompoundFilter(BaseFilter):
    """A filter made up of other filters.

    Useful for creating pairs of ``FlagFilter``s, for instance, if you had an
    ``active`` field on your model, you might want the ``active`` and
    ``inactive`` flag filters, and this provides an easy way to organize them
    together.
    """
    def __init__(self, filters=tuple()):
        self.filters = filters

    def filter(self, req, qs):
        for f in self.filters:
            qs = f.filter(req, qs)

        return qs


class ArchiveFlagFilter(FlagFilter):
    """Filter by `deleted_at`, for `frf.models.mixins.ArchiveMixin`.

    By default, does not include rows where `deleted_at` is not null.  If the
    filter flag `deleted` is present, rows where `deleted_at` is not null will
    also be present.
    """
    def filter_default(self, req, qs):
        return qs.filter(self.model_field.is_(None))

    def __init__(self, model_field):
        self.model_field = model_field
        super().__init__('deleted')


class SearchFilter(BaseFilter):
    """Filter allowing for a text search on a field."""
    def __init__(self, model_field, query_field='search',
                 case_insensitive=True):
        """Initialize the filter.

        Args:
            model_field (object): The SQLAlchemy field
            query_field (str): The field to look for in the query string.
                Default is ``search``.
            case_insensitive (bool): Set to True to use case insensitive
                searching.
        """
        self.model_field = model_field
        self.query_field = query_field
        self.case_insensitive = case_insensitive
        self.func = getattr(model_field, 'like')
        if case_insensitive:
            self.func = getattr(model_field, 'ilike')

    def filter(self, req, qs):
        search = req.get_param('search')
        if search is not None:
            qs = qs.filter(self.func(r'%{}%'.format(search)))

        return qs
