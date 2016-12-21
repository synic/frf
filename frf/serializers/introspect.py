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

from sqlalchemy.inspection import inspect

from frf import models
from frf.serializers import fields


def string_converter(field):
    return fields.StringField(
        min_length=0, max_length=field.type.length, blank=field.nullable)


def isodatetime_converter(field):
    return fields.ISODateTimeField()


def guid_converter(field):
    return fields.UUIDField()


def boolean_converter(field):
    return fields.BooleanField()


def integer_converter(field):
    return fields.IntField()


def float_converter(field):
    return fields.FloatField()


def json_converter(field):
    return fields.JSONField()


def date_converter(field):
    return fields.DateField()


CONVERTER_MAP = {
    models.String:        string_converter,
    models.Text:          string_converter,
    models.CHAR:          string_converter,
    models.DateTime.impl: isodatetime_converter,
    models.DateTime:      isodatetime_converter,
    models.Date:          date_converter,
    models.GUID:          guid_converter,
    models.Boolean:       boolean_converter,
    models.Integer:       integer_converter,
    models.BigInteger:    integer_converter,
    models.Float:         float_converter,
    models.JSON:          json_converter,
    models.JSONB:         json_converter,
    }


def table_fields(serializer, model):
    """Get list of serializer fields from the table model.

    Args:
        serializer (frf.serializers.ModelSerializer): The serializer
        model (frf.models.Model): The database model
    """
    fields = {}

    info = inspect(model)

    columns = info.c.items()

    for attr_name, column in columns:
        if type(column.type) in CONVERTER_MAP:
            field = CONVERTER_MAP[type(column.type)](column)
            field.required = False
            field.nullable = column.nullable
            field.source = attr_name
            field.field_name = attr_name
            field._serializer = serializer

            fields[attr_name] = field

    return fields
