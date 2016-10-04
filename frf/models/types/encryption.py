# -*- coding: utf-8 -*-
import json
import datetime

from sqlalchemy.types import Binary, String, TypeDecorator

from frf.models.types.scalar_coercible import ScalarCoercible
from frf.utils.encryption import AESCipher


class EncryptedType(TypeDecorator, ScalarCoercible):
    """EncryptedType provides a way to encrypt and decrypt values.

    Requires that the base type is a basic SQLAlchemy type, for example
    Unicode, String or even Boolean. On the way in, the value is encrypted and
    on the way out the stored value is decrypted.

    Credit: This class was borrowed from `sqlalchemy-utils`.

    It had some errors padding (it was using `*` as the padding character, so
    you could not have `*` in your data to be encrypted) so I forked and fixed
    it.

    Usage:

    ```
    from sqlalchemy.ext.mutable import MutableDict
    from sqlalchemy import Column, Text
    from frf.models.types import EncryptedType

    class SomeModel(models.Model):
        credentials = Column(EncryptedType(Text, key='encryptionkey'))))
    ```
    """

    impl = Binary

    def __init__(self, type_in=None, key=None, engine=None, **kwargs):
        """Initialization."""
        super().__init__(**kwargs)
        # set the underlying type
        if type_in is None:
            type_in = String()
        elif isinstance(type_in, type):
            type_in = type_in()
        self.underlying_type = type_in
        self._key = key
        if not engine:
            engine = AESCipher
        self.engine = engine()

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    def _update_key(self):
        key = self._key() if callable(self._key) else self._key
        self.engine._update_key(key)

    def process_bind_param(self, value, dialect):
        """Encrypt a value on the way in."""
        if value is not None:
            self._update_key()

            try:
                value = self.underlying_type.process_bind_param(
                    value, dialect
                )

            except AttributeError:
                # Doesn't have 'process_bind_param'

                # Handle 'boolean' and 'dates'
                type_ = self.underlying_type.python_type
                if issubclass(type_, bool):
                    value = 'true' if value else 'false'

                elif issubclass(type_, (datetime.date, datetime.time)):
                    value = value.isoformat()

            return self.engine.encrypt(value)

    def process_result_value(self, value, dialect):
        """Decrypt value on the way out."""
        if value is not None:
            self._update_key()
            decrypted_value = self.engine.decrypt(value)

            try:
                return self.underlying_type.process_result_value(
                    decrypted_value, dialect
                )

            except AttributeError:
                # Doesn't have 'process_result_value'

                # Handle 'boolean' and 'dates'
                type_ = self.underlying_type.python_type
                if issubclass(type_, bool):
                    return decrypted_value == 'true'

                elif issubclass(type_, datetime.datetime):
                    return datetime.datetime.strptime(
                        decrypted_value, '%Y-%m-%dT%H:%M:%S'
                    )

                elif issubclass(type_, datetime.time):
                    return datetime.datetime.strptime(
                        decrypted_value, '%H:%M:%S'
                    ).time()

                elif issubclass(type_, datetime.date):
                    return datetime.datetime.strptime(
                        decrypted_value, '%Y-%m-%d'
                    ).date()

                # Handle all others
                return self.underlying_type.python_type(decrypted_value)

    def _coerce(self, value):
        if isinstance(self.underlying_type, ScalarCoercible):
            return self.underlying_type._coerce(value)

        return value


class EncryptedDictionaryType(EncryptedType):
    """Encrypted dictionary!

    Usage:

    ```
    from sqlalchemy.ext.mutable import MutableDict
    from sqlalchemy import Column
    from frf.models.types import EncryptedDictionaryType

    class SomeModel(models.Model):
        credentials = Column(
            MutableDict.as_mutable(
                EncryptedDictionaryType(key='encryptionkey')))
            )
    ```
    """
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return super().process_bind_param(value, dialect)

    def process_result_value(self, value, dialect):
        value = super().process_result_value(value, dialect)
        if value is not None:
            return json.loads(value)
