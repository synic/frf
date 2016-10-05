from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict  # noqa
from sqlalchemy import (  # noqa
    func,
    Column,
    String,
    Text,
    DateTime,
    Date,
    BigInteger,
    Boolean,
    Integer,
    Enum,
    Date,
    PrimaryKeyConstraint,
    UniqueConstraint,
    Index,

    # relationships
    ForeignKey,

    # operators
    or_,
    and_,
    )

from sqlalchemy.orm import (  # noqa
    relationship,
    backref,
    )

from frf.models.types import (  # noqa
    EncryptedType,
    EncryptedDictionaryType,
    JSON,
    JSONB,
    GUID,
    MutableList,
    DateTime)

from frf.utils.db import BaseQuery


class Choices(list):
    def __init__(self, *choices):
        self.clear()
        for choice in choices:
            self.append(choice)

    def __getattr__(self, key):
        if key in self:
            return key
        raise AttributeError(key)


class _BaseModel(object):
    pass


Model = declarative_base(
    cls=_BaseModel,
    name='Model',
    metadata=None,
    )


# in `_db.Database`, `Model.query` is set, after initializing the database.
Model.query_class = BaseQuery

choices = Choices
