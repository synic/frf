from __future__ import absolute_import

import six
import sqlalchemy as sa

from sqlalchemy.dialects.postgresql.base import ischema_names

from frf.utils.json import serialize, deserialize

try:
    from sqlalchemy.dialects.postgresql import JSON as PGJSON
    from sqlalchemy.dialects.postgresql import JSONB as PGJSONB
    has_postgres_json = True
except ImportError:
    class PostgresJSONType(sa.types.UserDefinedType):
        """
        Text search vector type for postgresql.
        """
        def get_col_spec(self):
            return 'json'

    ischema_names['json'] = PostgresJSONType
    has_postgres_json = False
    PGJSON = PostgresJSONType
    PGJSONB = PostgresJSONType


class JSON(sa.types.TypeDecorator):
    """
    JSONType offers way of saving JSON data structures to database. On
    PostgreSQL the underlying implementation of this data type is 'json' while
    on other databases its simply 'text'.

    ::


        from sqlalchemy_utils import JSONType


        class Product(Base):
            __tablename__ = 'product'
            id = sa.Column(sa.Integer, autoincrement=True)
            name = sa.Column(sa.Unicode(50))
            details = sa.Column(JSONType)


        product = Product()
        product.details = {
            'color': 'red',
            'type': 'car',
            'max-speed': '400 mph'
        }
        session.commit()
    """
    impl = sa.UnicodeText

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            # Use the native JSON type.
            return dialect.type_descriptor(PGJSON())
        else:
            return dialect.type_descriptor(self.impl)

    def process_bind_param(self, value, dialect):
        if dialect.name == 'postgresql' and has_postgres_json:
            return value
        if value is not None:
            value = six.text_type(serialize(value))
        return value

    def process_result_value(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        if value is not None:
            value = deserialize(value)
        return value


class JSONB(JSON):
    def load_dialect_impl(self, dialect):
        t = super().load_dialect_impl(dialect)
        if isinstance(t, PGJSON):
            return dialect.type_descriptor(PGJSONB())
        return t
