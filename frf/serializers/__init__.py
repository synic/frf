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

from .fields import (  # noqa
    Field, StringField, EmailField, BooleanField,
    ISODateTimeField, SerializerField, ListField, UUIDField, JSONField,
    IntField, PrimaryKeyRelatedField,
)
from frf.exceptions import InvalidFieldException,  ValidationError


class SerializerObject(object):
    """Used by non-modal serializers to represent an unserialized object.

    Any values passed to the constructor will be available on the class, for
    example:

    >>> from frf import serializers
    >>> obj = serializers.SerializerObject(stuff='test', test='woot')
    >>> obj.test
    'woot'
    >>> obj.stuff
    'test'
    >>>

    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Serializer(object):
    """Serialization and deserialization of arbitrary python objects.

    Usage, given the following class:

    .. code-block:: python

        class TestSerializer(serializers.Serializer):
            name = serializers.StringField(required=True)
            email = serializers.EmailField(required=True)
            title = serializers.StringField(max_length=30)
            is_awesome = serializers.BooleanField(required=False, default=True)

    >>> serializer = TestSerializer()
    >>> obj = serializer.save(data={
    ...     'name': 'Adam Olsen',
    ...     'email': 'AROLSEN@GMAIL.COM',
    ...     'title': 'Sweet',
    ... })
    >>> obj.name
    'Adam Olsen'
    >>> obj.email
    'arolsen@gmail.com'
    >>> obj.title
    'Sweet'
    >>> obj.is_awesome
    True
    >>>
    """

    def __init__(self, initial_fields=None):
        """Initialize the serializer."""

        field_source_map = {}

        if initial_fields is None:
            self.fields = {}
        else:
            self.fields = initial_fields
            field_source_map = {f.source: k
                                for k, f in initial_fields.items()}

        self.validators = {}

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, Field):
                # check to see if this is a field that requires a
                # ``ModelSerializer``, and if it's not, raise an exception.
                if attr.requires_model_serializer and not isinstance(
                        self, ModelSerializer):
                    raise InvalidFieldException(_(
                        'The field {field} requires a ModelSerializer'.format(
                            field=attr_name)))
                attr.field_name = attr_name
                attr._serializer = self

                if attr.source is None:
                    attr.source = attr_name

                if attr.source in field_source_map:
                    name = field_source_map[attr.source]
                    if name in self.fields:
                        del self.fields[name]

                self.fields[attr_name] = attr

        # get the validator/clean methods
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if attr_name.startswith('clean_') and callable(attr):
                self.validators[attr_name[6:]] = attr

        if hasattr(self, 'Meta'):
            required = getattr(self.Meta, 'required', [])

            for field in required:
                if field in self.fields:
                    self.fields[field].required = True

    def validate(self, obj=None, data=None, ctx=None):
        """Validate data.

        Args:
            obj (object):  When editing, this will be the object you are
                editing, otherwise, it will be None.  If specified, field
                requirements will be lifted.
            data (dict): The data to validate.
            ctx (dict): Any additional data you want to pass. Useful for
                serializer subclasses that want to have acccess to things like
                the falcon Request object.

        Return:
           dict: The cleaned and validated data.
        """
        if data is None:
            data = {}

        if ctx is None:
            ctx = {}

        if not isinstance(data, dict):
            raise ValidationError(
                {'non_field_errors': _('Data passed is not a dictionary.')})

        errors = {}
        cleaned_data = {}

        for field_name, field in self.fields.items():
            source_name = field.source
            if field_name not in data and field.required and not obj:
                errors[field_name] = [_('Field is required.')]
                continue

            if field_name not in data and obj:
                continue

            if field_name not in data and not field.required \
                    and not obj \
                    and not isinstance(field, (SerializerField, JSONField)):
                default = field.default
                if callable(default):
                    default = default()
                cleaned_data[source_name] = default
                continue

            value = data.get(field_name, None)

            if value is None and not field.nullable:
                errors[field_name] = [_('Field cannot be `None`.')]
                continue

            # first run the field validation
            field_errors = field.validate(
                obj=obj, value=value, data=data, ctx=ctx)

            # if there is a serializer level validator for this
            # field...
            if field_name in self.validators:
                try:
                    value = self.validators[field_name](
                        obj=obj, data=data, ctx=ctx)
                except ValidationError as error:
                    field_errors.append(error.description)

            if not field_errors:
                cleaned_data[source_name] = field.to_python(
                    obj=obj, data=data, value=value, ctx=ctx)

            if field_errors:
                errors[field_name] = field_errors

        try:
            cleaned_data = self.clean(
                obj=obj, data=data, cleaned_data=cleaned_data, ctx=ctx)
        except ValidationError as error:
            errors['non_field_errors'] = error.message

        if errors:
            raise ValidationError(errors)

        return cleaned_data

    def post_save(self, obj, data, cleaned_data, ctx=None):
        pass

    def clean(self, obj, data, cleaned_data, ctx=None):
        """Called after all other validation is done.
        Override if you want to perform any further validation or data
        scrubbing.

        Args:
            obj (object): When editing, this will be the object you are
                editing, otherwise it will be None.
            data (dict): The passed data.
            cleaned_data (dict): The cleaned/validated data so far.

        Returns:
            dict: The cleaned data
        """
        return cleaned_data

    def create(self, data, cleaned_data, ctx=None):
        """Create the object.  Override if you want to change this behavior.

        Args:
            data (dict): The passed data.
            cleaned_data (dict): The cleaned and validated data.  You generally
                want to use this data to create the object.

        Return:
            object: The newly created object.  Fields will not yet be set, that
                is done by ``save_fields`` after object creation.
        """
        obj = SerializerObject()
        return obj

    def update(self, obj, data, cleaned_data, ctx=None):
        self.save_fields(obj, data, cleaned_data, ctx=ctx)

    def save_fields(self, obj, data, cleaned_data, ctx=None):
        for key, value in cleaned_data.items():
            field = self.fields.get(key)
            if not field.write_only:
                setattr(obj, key, value)

    def save(self, obj=None, data=None, ctx=None):
        """Save object using provided data.

        Args:
            obj (object): The object to save.  Provide this if you are editing,
                if you are creating, a new object will be created and returned.
            data (dict): The data
            **kwargs (dict): Any additional arguments you want to pass to the
                serializer. Useful if you want the serializer to have access to
                the falcon request, etc.

        Return:
            object: The saved object.  Note that the serializer doens't perform
                any type of commit, that is the responsibility of the
                developer.
        """
        if ctx is None:
            ctx = {}

        cleaned_data = self.validate(obj, data, ctx=ctx)
        if not obj:
            obj = self.create(data, cleaned_data, ctx=ctx)
            self.save_fields(obj, data, cleaned_data, ctx=ctx)
            self.post_save(obj, data, cleaned_data, ctx=ctx)
        else:
            self.update(obj, data, cleaned_data, ctx=ctx)
            self.post_save(obj, data, cleaned_data, ctx=ctx)

        return obj

    def serialize(self, objs, many=False, ctx=None):
        """Serialize an object or objects.

        Args:
            objs (object): The object or objects to serialize.
            many (bool): Set to True if `objs` is a list of more than one
                object.

        Returns:
            dict: The serialized data.
        """
        if ctx is None:
            ctx = {}

        if not many:
            objs = [objs]

        serialized_objs = []

        for obj in objs:
            serialized_obj = {}
            for field_name, field in self.fields.items():
                source_name = field.source
                value = getattr(obj, source_name, None)
                serialized_obj[field_name] = field.to_data(
                    obj=obj, value=value, ctx=ctx)

            serialized_objs.append(serialized_obj)

        return serialized_objs[0] if not many else serialized_objs


class ModelSerializer(Serializer):
    """An SQLAlchemy model serializer.

    Same as :class:`.Serializer`, but uses **self.Meta.model** during object
    creation.

    For example:

    .. code-block:: python

        from frf import serializers
        from project import models

        class SomeSerializer(serializers.Serializer):
            class Meta:
                model = models.SomeModel
    """
    class Meta:
        model = None
        fields = None

    def __init__(self):
        from frf.serializers import introspect

        if not self.Meta.model:
            raise ValueError(_('You must specify a model.'))

        initial_fields = introspect.table_fields(self, self.Meta.model)

        super().__init__(initial_fields=initial_fields)

        if getattr(self.Meta, 'fields', None) is not None:
            fields = list(self.fields.keys())

            for field in fields:
                if field not in self.Meta.fields:
                    del self.fields[field]

    def create(self, cleaned_data, obj, ctx=None):
        return self.Meta.model()
