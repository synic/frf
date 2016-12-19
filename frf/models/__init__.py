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
