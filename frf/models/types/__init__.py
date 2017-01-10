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

import uuid
import binascii
import pytz

from Crypto.Cipher import AES

import sqlalchemy

from sqlalchemy.types import CHAR, Text, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.mutable import Mutable

from frf.models.types.encryption import (  # noqa
    EncryptedType, EncryptedDictionaryType)


class DateTime(TypeDecorator):
    """Override for testing with sqlite.

    SQLite doesn't support timestamp with timezone, so assume everything is
    UTC, and add the UTC zoneinfo after reading the data from the db.
    """
    impl = sqlalchemy.DateTime

    def process_result_value(self, value, dialect):
        if dialect.name.lower() == 'sqlite' and value:
            value = pytz.UTC.localize(value)

        return value

    def process_bind_param(self, value, dialect):
        if dialect.name.lower() == 'sqlite' and value:
            value = value.astimezone(pytz.UTC)

        return value


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class MutableList(Mutable, list):
    """Mixin for a mutable list type object, or json with list at top level."""
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            value = Mutable.coerce(key, value)

        return value

    def __setitem__(self, key, value):
        old_value = list.__getitem__(self, key)
        for obj, key in self._parents.items():
            old_value._parents.pop(obj, None)

        list.__setitem__(self, key, value)
        for obj, key in self._parents.items():
            value._parents[obj] = key

        self.changed()

    def append(self, item):
        list.append(self, item)
        self.changed()

    def extend(self, iterable):
        list.extend(self, iterable)
        self.changed()

    def insert(self, index, item):
        list.insert(self, index, item)
        self.changed()

    def remove(self, value):
        list.remove(self, value)
        self.changed()

    def reverse(self):
        list.reverse(self)
        self.changed()

    def pop(self, index=-1):
        item = list.pop(self, index)
        self.changed()
        return item

    def sort(self, cmp=None, key=None, reverse=False):
        list.sort(self, cmp, key, reverse)
        self.changed()

    def __getstate__(self):
        return list(self)

    def __setstate__(self, state):
        self[:] = state


def aes_encrypt(data, key):
    cipher = AES.new(key)
    data = data + (" " * (16 - (len(data) % 16)))
    return binascii.hexlify(cipher.encrypt(data))


def aes_decrypt(data, key):
    cipher = AES.new(key)
    return cipher.decrypt(binascii.unhexlify(data)).rstrip()


class EncryptedValueType(TypeDecorator):
    impl = Text

    def __init__(self, encryption_key=None, **kwargs):
        if callable(encryption_key):
            self.encryption_key = encryption_key()
        else:
            self.encryption_key = encryption_key

        super().__init__(**kwargs)

    def process_bind_param(self, value, dialect):
        return aes_encrypt(value, self.encryption_key)

    def process_result_value(self, value, dialect):
        return aes_decrypt(value, self.encryption_key)
