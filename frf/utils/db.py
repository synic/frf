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

import falcon

from math import ceil

from sqlalchemy import orm
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.sql import func


class DatabaseError(Exception):
    pass


class Pagination(object):
    """Internal helper class returned by `BaseQuery.paginate`.

    You can also construct it from any other SQLAlchemy query object if you are
    working with other libraries.  Additionally it is possible to pass `None`
    as query object in which case the `prev` and `next` will
    no longer work.

    This class was borrowed from http://flask-sqlalchemy.pocoo.org/2.1/
    """

    def __init__(self, query, page, per_page, total, items):
        #: the unlimited query object that was used to create this
        #: pagination object.
        self.query = query
        #: the current page number (1 indexed)
        self.page = page
        #: the number of items to be displayed on a page.
        self.per_page = per_page
        #: the total number of items matching the query
        self.total = total
        #: the items for the current page
        self.items = items

    @property
    def pages(self):
        """The total number of pages."""
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    def prev(self, error_out=False):
        """Return a `Pagination` object for the previous page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page - 1, self.per_page, error_out)

    @property
    def prev_num(self):
        """Number of the previous page."""
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists."""
        return self.page > 1

    def next(self, error_out=False):
        """Return a `Pagination` object for the next page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page + 1, self.per_page, error_out)

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page."""
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        """Iterate over the page numbers in the pagination.

        The four parameters control the thresholds how many numbers should be
        produced from the sides. Skipped page numbers are represented as
        `None`.
        """
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class BaseQuery(orm.Query):
    """SQLAlchemy `sqlalchemy.orm.query.Query` subclass.

    Includes convenience methods for querying in a web application. This is the
    default `Model.query` object used for models, and exposed as
    `SQLAlchemy.Query`. Override the query class for an individual model by
    subclassing this and setting `Model.query_class`.
    """
    def __init__(self, *args, **kwargs):
        self.count_column = kwargs.pop('count_column', None)
        super().__init__(*args, **kwargs)

    def count(self):
        if not self.count_column:
            return super().count()
        col = func.count(self.count_column)
        return self.from_self(col).scalar()

    def get_or_404(self, ident):
        """Like `get` but aborts with 404 if not found."""

        rv = self.get(ident)
        if rv is None:
            raise falcon.HTTPNotFound()
        return rv

    def first_or_404(self):
        """Like first` but aborts with 404 if not found."""

        rv = self.first()
        if rv is None:
            raise falcon.HTTPNotFound()
        return rv

    def paginate(self, page=None, per_page=None, error_out=True):
        """Return `per_page` items from page `page`.

        If no items are found and `page` is greater than 1, or if page is
        less than 1, it aborts with 404. This behavior can be disabled by
        passing `error_out=False`.

        If the values are not ints and `error_out` is `True`, it aborts
        with 404. If there is no request or they aren't in the query, they
        default to 1 and 20 respectively. Returns a `Pagination` object.
        """

        if page is None:
            page = 1

        if per_page is None:
            per_page = 20

        if error_out and page < 1:
            raise falcon.HTTPNotFound()

        if self._limit is None or per_page < self._limit:
            items = self.limit(per_page).offset((page - 1) * per_page).all()
        else:
            items = self.all()

        if not items and page != 1 and error_out:
            raise falcon.HTTPNotFound()

        # No need to count if we're on the first page and there are fewer
        # items than we expected.
        if page == 1 and len(items) < per_page:
            total = len(items)
        else:
            total = self.order_by(None).count()

        return Pagination(self, page, per_page, total, items)


class _QueryProperty(object):
    def __init__(self, session):
        self.session = session

    def __get__(self, obj, type):
        try:
            mapper = orm.class_mapper(type)
            count_column = getattr(type, 'uuid', None)
            if mapper:
                return type.query_class(mapper, session=self.session(),
                                        count_column=count_column)
        except UnmappedClassError:
            return None
