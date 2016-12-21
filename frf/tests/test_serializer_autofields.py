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

from falcon.testing import TestCase as BaseTestCase
from frf import db, models, serializers
from frf.models import mixins


class User(mixins.TimestampMixin, models.Model):
    uuid = models.Column(models.GUID, default=uuid.uuid4, primary_key=True)
    username = models.Column(models.String(255), index=True)
    email = models.Column(models.String(255), index=True)
    first_name = models.Column(models.String(40), nullable=True)
    last_name = models.Column(models.String(40), nullable=True)
    age = models.Column(models.Integer, nullable=True)

    __tablename__ = 'users'


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    description = serializers.StringField(required=False, allow_none=True)

    class Meta:
        required = ('username', 'email')
        model = User


class UserSerializer2(serializers.ModelSerializer):
    user_age = serializers.IntField(source='age', required=False)
    description = serializers.StringField(required=False, allow_none=True)

    class Meta:
        fields = ('uuid', 'username', 'email', 'first_name', 'last_name',
                  'created_at', 'updated_at', 'user_age', )
        model = User


class TestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        db.init('sqlite://', echo=False)
        User.metadata.create_all(db.engine)

    def test_auto_fields(self):
        serializer = UserSerializer()
        f = serializer.fields

        self.assertEqual(len(f), 9)

        self.assertEqual(
            f['uuid'].__class__, serializers.UUIDField)
        self.assertEqual(
            f['created_at'].__class__, serializers.ISODateTimeField)
        self.assertEqual(
            f['updated_at'].__class__, serializers.ISODateTimeField)
        self.assertEqual(
            f['first_name'].__class__, serializers.StringField)
        self.assertEqual(
            f['last_name'].__class__, serializers.StringField)
        self.assertEqual(
            f['username'].__class__, serializers.StringField)
        self.assertEqual(
            f['email'].__class__, serializers.EmailField)
        self.assertEqual(
            f['age'].__class__, serializers.IntField)
        self.assertEqual(
            f['description'].__class__, serializers.StringField)

    def test_required_list(self):
        serializer = UserSerializer()

        required = []

        for name, field in serializer.fields.items():
            if field.required:
                required.append(name)

        self.assertEqual(len(required), 2)

        self.assertIn('email', required)
        self.assertIn('username', required)

    def test_override_replaces_source(self):
        # test that overriding a field and using a source removes the original
        # field from the automatically generated list of fields

        serializer = UserSerializer2()

        self.assertNotIn('age', serializer.fields)
        self.assertIn('user_age', serializer.fields)

        self.assertEqual(
            serializer.fields['user_age'].__class__,
            serializers.IntField)

    def test_meta_field_list_masks_fields(self):
        serializer = UserSerializer2()

        self.assertNotIn('description', serializer.fields)

    def test_automatic_string_length(self):
        serializer = UserSerializer()

        f = serializer.fields['username']

        self.assertEqual(f.min_length, 0)
        self.assertEqual(f.max_length, 255)

    def test_serialize(self):
        serializer = UserSerializer2()

        user = User(
            first_name='Adam',
            last_name='Olsen',
            email='arolsen@gmail.com',
            username='synic',
            age=36,
        )

        db.session.add(user)
        db.session.commit()

        data = serializer.serialize(user)

        self.assertEqual(len(data), 8)

        self.assertEqual(data['uuid'], str(user.uuid))
        self.assertEqual(data['created_at'], user.created_at.isoformat())
        self.assertEqual(data['updated_at'], user.created_at.isoformat())
        self.assertEqual(data['email'], 'arolsen@gmail.com')
        self.assertEqual(data['username'], 'synic')
        self.assertEqual(data['first_name'], 'Adam')
        self.assertEqual(data['last_name'], 'Olsen')
        self.assertEqual(data['user_age'], 36)
