import json
import datetime
import dateutil.parser
import uuid
import re

from gettext import gettext as _

from frf.utils.json import deserialize
from frf import exceptions


class Field(object):
    """Base field - all other fields inherit from this field.

    Tbis is a field without a type, and data will not be transformed or cleaned
    at all.  The only validation that is done is making sure the value is in
    `choices`, if provided.

    You can define as many validators as you would like for your field.  They
    just need to be in the format:

    ``validate_[arbitrary_name](value)``.  For example:

    >>> def validate_is_string(self, value):
    >>> if not isinstance(value, str):
    >>>     raise exceptions.ValidationError('Is not a string.')

    The ``arbitrary_name`` can be any valid python name, and is not used for
    anything other then organization purposes.  Validators are validated in the
    order they are defined on the class.
    """
    requires_model_serializer = False

    def __init__(self, required=False, default=None,
                 read_only=False, update_read_only=False, write_only=False,
                 allow_none=None, choices=None, source=None, _debug=None):
        """Initialize the field.

        Args:
            required (bool): Set to True if this field is required.  The
                default is False.
            default (object): If this field is not required, and the data did
                not contain any values for this field, this default will be
                used instead.
            read_only (bool): Set to True if this should only be used for
                serialization and not deserialization.
            update_read_only (bool): Set to True if you want the field to only
                be read-only during an update or edit.
            write_only (bool): Set to True if you only want this field to be
                used during deserialization and not serialization.
            allow_none (bool): Allow 'None' to be passed for this field.  If
                you do not specify, it will be the opposite of the `required`
                param.
            choices (list): If passed, during validation, the system will check
                if the passed value is in the list of choices.
        """
        self._serializer = None
        self.validators = []
        self.required = required
        self.default = default
        self.choices = choices
        self.read_only = read_only
        self.write_only = write_only
        self.update_read_only = update_read_only

        if allow_none is None:
            allow_none = not required

        self.allow_none = allow_none
        self.field_name = None
        self.source = source
        self._debug = _debug

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if attr_name.startswith('validate_') and callable(attr):
                self.validators.append(attr)

    def validate_choices(self, obj, value, **kwargs):
        if self.choices:
            if value not in self.choices:
                raise exceptions.ValidationError(
                    _('"{value}" not in "{choices}"'.format(
                        value=value,
                        choices=', '.join(self.choices))))

    def validate_required(self, obj, data, value, **kwargs):
        if not obj and self.required and self.field_name not in data:
            raise exceptions.ValidationError(
                _('Field is required.'))

    def validate_read_only(self, obj, data, value, **kwargs):
        if self.field_name in data and self.read_only:
            raise exceptions.ValidationError(
                _('Field is read-only.'))

    def validate_update_read_only(self, obj, data, value, **kwargs):
        try:
            value = self.to_python(obj=obj, data=data, value=value, **kwargs)
        except exceptions.ValidationError:
            raise exceptions.ValidationError(
                _('Field is read-only when editing.'))

        if self.update_read_only and self.field_name in data and obj and \
                getattr(obj, self.field_name) != value:
            raise exceptions.ValidationError(
                _('Field is read-only when editing.'))

    def validate_allow_none(self, value, **kwargs):
        if self.required and not self.allow_none and value is None:
            raise exceptions.ValidationError(
                _('Field cannot be null.'))

    def validate(self, obj=None, value=None, data=None, **kwargs):
        errors = []

        for validator in self.validators:
            try:
                validator(obj=obj, value=value, data=data, **kwargs)
            except exceptions.ValidationError as error:
                errors.append(error.description)

        return errors

    def to_python(self, obj, value, **kwargs):
        return value

    def to_data(self, obj, value, **kwargs):
        return value


class StringField(Field):
    """String type field."""
    def __init__(self, min_length=None, max_length=None, trim_whitespace=True,
                 regex=None, allow_blank=True, **kwargs):
        """
        Args:
            min_length (int): Minumum length for the string.  If not passed, no
                validation on minimum length will be done.
            max_length (int): Maximum length for the string.
            trim_whitespace (bool): Set to True if you want to automatically
                clean any leading or trailing whitespace.   Default is *True*
            regex (str): Regular expression to match.  Leave blank for no
                matching.
            allow_blank (bool): Similar to *allow_none*, but applies to an
                empty string.
        """
        self.min_length = min_length
        self.max_length = max_length
        self.trim_whitespace = trim_whitespace
        self.allow_blank = allow_blank

        if isinstance(regex, str):
            regex = re.compile(regex)

        self.regex = regex
        super().__init__(**kwargs)

    def to_python(self, obj, value, **kwargs):
        if self.allow_none and value is None:
            return value

        if not isinstance(value, str):
            value = str(value)

        if self.trim_whitespace and value:
            value = value.strip()
        return value

    def validate_allow_blank(self, value, **kwargs):
        if not self.allow_blank and value == '':
            raise exceptions.ValidationError(_('Cannot be blank.'))

    def validate_is_string(self, obj, value, **kwargs):
        if self.allow_none and value is None:
            return value

        if not isinstance(value, str):
            raise exceptions.ValidationError(_('Must be a string.'))

    def validate_min_length(self, obj, value, **kwargs):
        value = str(value)
        if self.min_length and len(value) < self.min_length:
            raise exceptions.ValidationError(
                _('Must be at least {chars} '
                  'character(s) long.'.format(chars=self.min_length)))

    def validate_max_length(self, obj, value, **kwargs):
        value = str(value)
        if self.max_length and len(value) > self.max_length:
            raise exceptions.ValidationError(
                _('Must be at most {chars} character(s) long.'.format(
                    chars=self.max_length)))

    def validate_regex(self, obj, value, **kwargs):
        if self.allow_none and value is None:
            return value
        if self.regex:
            if not self.regex.match(value):
                raise exceptions.ValidationError(
                    _('Must match the pattern "{pattern}".'.format(
                        pattern=self.regex.pattern)))


class EmailField(StringField):
    """A string field that loseley validates an email address.

    This class follows the philosophy that any validation of an email address
    beyond simple format validation is pointless.  The user can still mistype
    the address, even if it's in the correct format, and there's no reliable
    way to connect to the remote server to check to see if the email address
    actually exists.  There is no way to correctly validate it, so we just do a
    simple efficient format validation.

    If you wish to change this behavior, subclass this field and override
    ``REGEX`` to supply your own regular expression.

    By default, this class converts email address to lowercase.  You can change
    this behavior, pass ``convert_to_lower=False`` to the constructor.
    """
    REGEX = '[^@]+@[^@]+\.[^@]+'

    def __init__(self, convert_to_lower=True, **kwargs):
        """
        Args:
            convert_to_lower (bool): Set to ``True`` to have the field
                automatically convert any input to lowercase.
        """
        self.convert_to_lower = convert_to_lower
        super().__init__(regex=self.REGEX, **kwargs)

    def to_python(self, obj, value, **kwargs):
        if isinstance(value, str) and self.convert_to_lower:
            return value.lower()
        return value

    def validate_regex(self, obj, value, **kwargs):
        if isinstance(value, str) and self.regex:
            if not self.regex.match(value):
                raise exceptions.ValidationError(
                    _('"{email}" does not appear to be a valid '
                      'email address.'.format(email=value)))


class IntField(Field):
    """Integer type field."""
    def __init__(self, min_value=None, max_value=None, **kwargs):
        """
        Args:
            min_value (int): The minimum value of the integer.  Leave as
                ``None`` to skip this validation.
            max_value (int): The maximum value of the integer.  Leave as
                ``None`` to skip this validation.
        """
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(**kwargs)

    def validate_is_int(self, obj, value, **kwargs):
        if self.allow_none and value is None:
            return value

        if not isinstance(value, int):
            raise exceptions.ValidationError(
                _('"{number}" does not appear to be an integer.'.format(
                    number=value)))

    def validate_min_value(self, value, **kwargs):
        if isinstance(value, int) and self.min_value is not None \
                and value < self.min_value:
            raise exceptions.ValidationError(
                _('Value cannot be smaller than {value}.'.format(
                    value=self.min_value)))

    def validate_max_value(self, value, **kwargs):
        if isinstance(value, int) and self.max_value is not None \
                 and value > self.max_value:
            raise exceptions.ValidationError(
                _('Value cannot be larger than {value}.'.format(
                    value=self.max_value)))


class BooleanField(Field):
    """Boolean type field."""
    def validate_boolean(self, obj, value, **kwargs):
        if not isinstance(value, bool):
            raise exceptions.ValidationError(_('Must be a boolean.'))


class ISODateTimeField(Field):
    """Date and Time field that uses ISO-8601 for parsing/serializing.

    This field's input is very specific, and follows strict ISO-8601
    formatting, which may or may not be what you need.

    To serialize, it simply calls ``isoformat()`` on the ``datetime.datetime``
    object, like so:

    >>> import datetime
    >>> now = datetime.datetime.now()
    >>> now
    datetime.datetime(2016, 9, 20, 20, 18, 1, 682945)
    >>> now.isoformat()
    '2016-09-20T20:18:01.682945'

    To deserialize, it uses ``dateutil.parser``:

    >>> import dateutil.parser
    >>> d = dateutil.parser.parse(''2016-09-20T20:18:01.682945')
    >>> d == now
    True
    """
    def validate_datetime(self, obj, value, **kwargs):
        if isinstance(value, datetime.datetime):
            return
        try:
            dateutil.parser.parse(value)
        except Exception as e:
            raise exceptions.ValidationError(
                _('Error converting datetime: {message}'.format(message=e)))

    def to_python(self, obj, value, **kwargs):
        if self.allow_none and value is None:
            return value

        if isinstance(value, datetime.datetime):
            return value
        return dateutil.parser.parse(value)

    def to_data(self, obj, value):
        return value.isoformat()


class UUIDField(Field):
    """Universally Unique Identifier field."""
    def validate_uuid(self, obj, value, **kwargs):
        if isinstance(value, uuid.UUID):
            return
        try:
            uuid.UUID(value)
        except Exception as e:
            raise exceptions.ValidationError(
                _('Error converting uuid: {message}'.format(message=e)))

    def to_python(self, obj, value, **kwargs):
        if value is not None and not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        return value

    def to_data(self, obj, value):
        return str(value)


class ListField(Field):
    """A list validation field.

    Takes another field as an argument and uses that for validation/cleaning of
    each element in the list.
    """
    def __init__(self, field, **kwargs):
        """
        Args:
            field (:class:`.Field`): The field to use for validation/cleaning
                of each element in the list.
        """
        self.field = field
        super().__init__(**kwargs)

    def set_field_name(self, name):
        self._field_name = name
        self.field.field_name = name

    def get_field_name(self):
        return self._field_name

    field_name = property(get_field_name, set_field_name)

    def validate_is_list(self, obj, value, **kwargs):
        if self.allow_none and value is None:
            return value
        if not isinstance(value, list):
            raise exceptions.ValidationError(
                _('Value must be a list.'))

    def validate_field(self, obj=None, value=None, data=None, **kwargs):
        errors = []

        for item in value:
            field_errors = self.field.validate(
                data=data, obj=obj, value=item, **kwargs)
            if field_errors:
                errors += [i for i in [e for e in field_errors]]

        if errors:
            raise exceptions.ValidationError(errors[0])

    def to_python(self, obj, value, **kwargs):
        if self.allow_none and value is None:
            return value
        ret = []

        for item in value:
            ret.append(self.field.to_python(obj=obj, value=item, **kwargs))

        return ret


class JSONField(Field):
    """Simple json validation field.

    Can use another serializer for validation.
    """
    def __init__(self, validating_serializer=None, many=False, **kwargs):
        """
        Args:
            many (bool): Set to ``True`` if this will be a list of json objects
                instead of a single object.
        """
        self.validating_serializer = validating_serializer
        self.many = many
        super().__init__(**kwargs)

    def validate_structure(self, value, **kwargs):
        if self.allow_none and value is None:
            return value
        if isinstance(value, str):
            try:
                value = deserialize(value)
            except json.JSONDecodeError:
                raise exceptions.ValidationError(
                    _('Does not appear to be valid json.'))

        if self.many and not isinstance(value, (list, tuple)):
            raise exceptions.ValidationError(_('Must be a list.'))

    def validate_fields(self, obj=None, value=None, data=None, **kwargs):
        if isinstance(value, str):
            value = deserialize(value)

        if self.validating_serializer and value:
            if self.many:
                for item in value:
                    self.validating_serializer.validate(
                        obj=obj, data=item, **kwargs)
            else:
                self.validating_serializer.validate(
                    obj=obj, data=value, **kwargs)

    def to_python(self, value=None, **kwargs):
        if isinstance(value, str):
            value = deserialize(value)

        items = []

        if self.validating_serializer:
            if self.many and value:
                for item in value:
                    items.append(
                        self.validating_serializer.validate(data=item))
            else:
                items.append(self.validating_serializer.validate(data=value))
        else:
            return value

        return items if self.many else items[0]

    def to_data(self, value, **kwargs):
        if isinstance(value, str):
            value = deserialize(value)

        return value


class SerializerField(Field):
    """Validate another serializer as a field."""
    def __init__(self, serializer, many=False, **kwargs):
        """
        Args:
            serializer (:class:`frf.serializers.Serializer`): The serializer.
            many (bool): Set to ``True`` if this should be a list of objects,
                instead of just a single object.
        """
        self.serializer = serializer
        self.many = many
        super().__init__(**kwargs)

    def validate(self, obj=None, value=None, data=None, **kwargs):
        errors = []
        if isinstance(value, str):
            try:
                value = deserialize(value)
            except json.JSONDecodeError:
                raise exceptions.ValidationError(
                    _('Does not appear to be valid json.'))

        if self.many and not isinstance(value, (list, tuple)):
            raise exceptions.ValidationError(
                _('Value must be a list.'))

        if not self.many:
            try:
                self.serializer.validate(
                    obj=obj, data=value, **kwargs)
            except exceptions.ValidationError as exception:
                errors.append(exception.description)
        else:
            for item in value:
                try:
                    self.serializer.validate(obj=obj, data=item, **kwargs)
                except exceptions.ValidationError as exception:
                    errors.append(exception.description)

        if errors:
            raise exceptions.ValidationError(errors)

    def to_data(self, value, **kwargs):
        items = []

        if self.many:
            for item in value:
                items.append(self.serializer.serialize(data=item))
        else:
            items.append(self.serializer.serialize(data=value))

        return items if self.many else items[0]

    def to_python(self, obj=None, value=None, data=None, **kwargs):
        items = []
        if isinstance(value, str):
            value = deserialize(value)

        if self.many:
            for item in value:
                items.append(
                    self.serializer.save(obj=obj, data=item, **kwargs))
        else:
            items.append(self.serializer.save(obj=obj, data=value, **kwargs))

        return items if self.many else items[0]


class PrimaryKeyRelatedField(Field):
    """Represent objects as a list of related keys.

    Requires that you use this field on a
    :class:`frf.serializers.ModelSerializer`
    """
    requires_model_serializer = True
    MESSAGES = {
        'multikey': _('The table {table} has a composite primary key. You '
                      'must submit all keys in the format {{"key1": value1, '
                      '"key2": "value2"}}'),
    }

    def __init__(self, model, queryset=None, many=False, *args, **kwargs):
        self.model = model
        self.many = many
        self.queryset = queryset if queryset else self.model.query.filter()

        super().__init__(*args, **kwargs)

    def get_primary_keys(self):
        mapper = self.model.__mapper__
        keys = [
            mapper.get_property_by_column(column).key
            for column in mapper.primary_key
            ]

        return keys[0] if len(keys) == 1 else keys

    def to_data(self, value, **kwargs):
        keys = self.get_primary_keys()

        if not isinstance(keys, (list, tuple)):
            if self.many:
                values = []
                for item in value:
                    values.append(getattr(item, keys))
            else:
                values = getattr(value, keys)
        else:
            values = {}
            for key in self.keys:
                if self.many:
                    values = []
                    for item in value:
                        values.append(getattr(item, keys))
                else:
                    values[key] = getattr(value, key)

        return values

    def to_python(self, value, **kwargs):
        keys = self.get_primary_keys()
        items = []

        if value:
            if self.many:
                if not isinstance(keys, (list, tuple)):
                    for item in value:
                        if not isinstance(keys, list):
                            items.append(
                                self.queryset.filter_by(
                                    **{keys: item}).first())
                        else:
                            items.append(
                                self.queryset.filter_by(
                                    **self.build_lookup(keys, item)).first())
            else:
                if not isinstance(keys, list):
                    items.append(
                        self.queryset.filter_by(**{keys: value}).first())
                else:
                    items.append(self.queryset.filter_by(
                        **self.build_lookup(keys, value)).first())

        return items if self.many else items[0]

    def validate_ids(self, value, **kwargs):
        keys = self.get_primary_keys()
        items = []

        if value:
            if self.many:
                for item in value:
                    if not isinstance(keys, (list, tuple)):
                        items.append(
                            self.queryset.filter_by(**{keys: item}).first())
                    else:
                        if not isinstance(value, dict):
                            raise exceptions.ValidationError(
                                self.MESSAGES['multikey'].format(
                                    table=self.model.__tablename__))
                        items.append(self.queryset.filter_by(
                            **self.build_lookup(keys, item)).first())
            else:
                if not isinstance(keys, (list, tuple)):
                    items.append(
                        self.queryset.filter_by(**{keys: value}).first())
                else:
                    if not isinstance(value, dict):
                            raise exceptions.ValidationError(
                                self.MESSAGES['multikey'].format(
                                    table=self.model.__tablename__))
                    items.append(self.queryset.filter_by(
                        **self.build_lookup(keys, value)).first())

        if not items and value:
            raise exceptions.ValidationError(
                _('A row with the key "{key}" does'
                  ' not exist in the database.'.format(key=keys)))
