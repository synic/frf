import falcon
import uuid
import unittest
import datetime

from frf.utils import timezone
from frf import serializers, exceptions, db
from frf.tests.base import BaseTestCase
from frf.utils.json import serialize

from frf.tests import fakeproject  # noqa
from frf.tests.fakemodule import models


class DummySerializer(serializers.Serializer):
    name = serializers.StringField(required=True)
    email = serializers.EmailField(required=True, update_read_only=True)
    title = serializers.StringField(max_length=30)
    is_awesome = serializers.BooleanField(required=False, default=True)


class FakeQuery(object):
    def filter(self):
        return []


class FakeModel(object):
    def __init__(self):
        self.query = FakeQuery()


def new_serializer_class(**kwargs):
    return type('Serializer', (serializers.Serializer,), kwargs)()


class TestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.serializer = DummySerializer()

    def test_validate_all_valid_data(self):
        data = {
            'name': 'Adam Olsen',
            'email': 'AROLSEN@GMAIL.COM',
            'title': 'Sweet',
        }

        self.serializer.validate(data=data)

    def test_validate_missing_required_fields(self):
        with self.assertRaises(exceptions.ValidationError) as context:
            self.serializer.validate(data={})

        for item in ('email', 'name'):
            self.assertEqual(1, len(context.exception.description[item]))
            self.assertEqual(context.exception.description[item][0],
                             'Field is required.')

    def test_validate_invalid_email(self):
        with self.assertRaises(exceptions.ValidationError) as context:
            self.serializer.validate(data={'email': 'test'})

        self.assertEqual(
            context.exception.description['name'][0], 'Field is required.')
        self.assertEqual(
            context.exception.description['email'][0],
            '"test" does not appear to be a valid email address.')

    def test_create_object(self):
        data = {
            'name': 'Adam Olsen',
            'email': 'AROLSEN@GMAIL.COM',
            'title': 'Sweet',
        }

        obj = self.serializer.save(data=data)

        self.assertEqual(obj.name, data['name'])
        self.assertEqual(obj.email, data['email'].lower())
        self.assertEqual(obj.title, data['title'])
        self.assertTrue(obj.is_awesome)

    def test_update_object(self):
        obj = serializers.SerializerObject(**{
            'name': 'Adam Olsen',
            'email': 'AROLSEN@GMAIL.COM',
            'title': 'Sweet',
        })

        obj = self.serializer.save(data={'title': 'woot'}, obj=obj)

        self.assertEqual(obj.email, 'AROLSEN@GMAIL.COM')
        self.assertEqual(obj.name, 'Adam Olsen')
        self.assertEqual(obj.title, 'woot')

    def test_serialize_objs(self):
        objs = []
        objs.append(
            serializers.SerializerObject(**{
                'name': 'Adam Olsen',
                'email': 'AROLSEN@GMAIL.COM',
                'title': 'Sweet',
                }))

        objs.append(
            serializers.SerializerObject(**{
                'name': 'Robert Paulson',
                'email': 'rob@rob.com',
                'title': 'woot',
                }))

        data = self.serializer.serialize(objs, many=True)

        for i, item in enumerate(data):
            self.assertEqual(item['name'], objs[i].name)
            self.assertEqual(item['email'], objs[i].email)
            self.assertEqual(item['title'], objs[i].title)

    def test_update_update_read_only_field_same_value(self):
        """Test that an update_read_only field allows the update if the value
        is the same as the one that's already on the object, after calling
        `to_python` on the passed value.
        """
        obj = serializers.SerializerObject(**{
            'name': 'Adam Olsen',
            'email': 'arolsen@gmail.com',
            'title': 'Sweet',
        })

        obj = self.serializer.save(
            data={'email': 'AROLSEN@GMAIL.COM'}, obj=obj)

        self.assertEqual(obj.email, 'arolsen@gmail.com')

    def test_string_field_min_length(self):
        serializer = new_serializer_class(
            name=serializers.StringField(min_length=3),
            )

        with self.assertRaises(exceptions.ValidationError) as context:
            serializer.validate(data={'name': '12'})

        self.assertEqual(
            context.exception.description['name'][0],
            'Must be at least 3 character(s) long.')

    def test_string_field_max_length(self):
        serializer = new_serializer_class(
            name=serializers.StringField(min_length=4, max_length=2),
            )

        with self.assertRaises(exceptions.ValidationError) as context:
            serializer.validate(data={'name': '123'})

        self.assertEqual(
            context.exception.description['name'][1],
            'Must be at least 4 character(s) long.')
        self.assertEqual(
            context.exception.description['name'][0],
            'Must be at most 2 character(s) long.')

    def test_fail_string_field_match_regex(self):
        serializer = new_serializer_class(
            name=serializers.StringField(regex='\d\d'),
            )

        with self.assertRaises(exceptions.ValidationError) as context:
            serializer.validate(data={'name': ''})

        self.assertIn(
            'match the pattern', context.exception.description['name'][0],
            )

    def test_string_field_match_regex(self):
        serializer = new_serializer_class(
            name=serializers.StringField(regex='\d\d'),
            )

        serializer.validate(data={'name': '22'})

    def test_validate_integer_non_integer(self):
        serializer = new_serializer_class(
            name=serializers.IntField(),
            )

        with self.assertRaises(exceptions.ValidationError) as context:
            serializer.validate(data={'name': 'one'})

        self.assertIn(
            'does not appear to be an integer',
            context.exception.description['name'][0])

    def test_validate_integer_min_value(self):
        serializer = new_serializer_class(
            name=serializers.IntField(min_value=10),
            )

        with self.assertRaises(exceptions.ValidationError) as context:
            serializer.validate(data={'name': 9})

        self.assertIn(
            'Value cannot be smaller than 10.',
            context.exception.description['name'][0])

    def test_validate_integer_max_value(self):
        serializer = new_serializer_class(
            name=serializers.IntField(max_value=9),
            )

        with self.assertRaises(exceptions.ValidationError) as context:
            serializer.validate(data={'name': 10})

        self.assertIn(
            'Value cannot be larger than 9.',
            context.exception.description['name'][0])

    def test_validate_boolean_non_boolean(self):
        serializer = new_serializer_class(
            name=serializers.BooleanField(),
            )

        with self.assertRaises(exceptions.ValidationError) as context:
            serializer.validate(data={'name': 1})

        self.assertIn(
            'Must be a boolean', context.exception.description['name'][0])

    def test_email_convert_to_lowercase(self):
        serializer = new_serializer_class(
            name=serializers.EmailField(),
            )

        cleaned_data = serializer.validate(data={'name': 'TEST@TEST.COM'})
        self.assertEqual(cleaned_data['name'], 'test@test.com')

    def test_validation_order(self):
        serializer = new_serializer_class(
            name=serializers.StringField(
                min_length=4, max_length=2, allow_blank=False, regex='\d\d'),
            )

        with self.assertRaises(exceptions.ValidationError) as context:
            serializer.validate(data={'name': ''})

        matches = ('Cannot be blank', 'be at least 4', 'match the pattern')
        for i, match in enumerate(matches):
            self.assertIn(match, context.exception.description['name'][i])

    def test_fail_update_email_read_only(self):
        obj = serializers.SerializerObject(**{
            'name': 'Adam Olsen',
            'email': 'AROLSEN@GMAIL.COM',
            'title': 'Sweet',
        })

        with self.assertRaises(exceptions.ValidationError) as context:
            obj = self.serializer.save(
                data={'email': 'bwent@bwent.com'}, obj=obj)

        self.assertEqual(context.exception.description['email'][0],
                         'Field is read-only when editing.')

    def test_validate_is_string(self):
        serializer = new_serializer_class(
            name=serializers.StringField(max_length=4),
            )

        with self.assertRaises(exceptions.ValidationError) as context:
            serializer.validate(data={'name': 12})

        self.assertIn(
            'Must be a string', context.exception.description['name'][0])

    def test_must_be_a_dictionary(self):
        serializer = new_serializer_class()

        with self.assertRaises(exceptions.ValidationError) as context:
            serializer.validate(data=1)

        self.assertIn(
            'not a dictionary',
            context.exception.description['non_field_errors'])

    def test_validate_isodatetime(self):
        serializer = new_serializer_class(
            date=serializers.ISODateTimeField(),
            )

        dt = timezone.now()

        obj = serializer.save(data={'date': dt.isoformat()})

        self.assertIsInstance(obj.date, datetime.datetime)
        self.assertEqual(dt, obj.date)

    def test_validate_uuid(self):
        serializer = new_serializer_class(
            uuid=serializers.UUIDField(),
            )

        u = uuid.uuid4()

        obj = serializer.save(data={'uuid': u})

        self.assertIsInstance(obj.uuid, uuid.UUID)
        self.assertEqual(obj.uuid, u)

    def test_validate_uuid_as_string(self):
        serializer = new_serializer_class(
            uuid=serializers.UUIDField(),
            )

        u = uuid.uuid4()

        obj = serializer.save(data={'uuid': str(u)})

        self.assertIsInstance(obj.uuid, uuid.UUID)
        self.assertEqual(obj.uuid, u)

    def test_validate_json_field(self):
        settings = new_serializer_class(
            stay_logged_in=serializers.BooleanField(default=True),
        )

        credentials = new_serializer_class(
            username=serializers.StringField(
                required=True, allow_blank=False, allow_none=False),
            password=serializers.StringField(
                required=True, allow_blank=False, allow_none=False),
            settings=serializers.JSONField(
                validator=settings, default={}, allow_none=True),
            )

        serializer = new_serializer_class(
            credentials=serializers.SerializerField(
                credentials, required=True),
            )

        obj = serializer.save(data={
            'credentials': {
                'username': 'synic',
                'password': 'test',
            }})

        self.assertEqual(obj.credentials.username, 'synic')
        self.assertEqual(obj.credentials.password, 'test')
        self.assertTrue(obj.credentials.settings['stay_logged_in'])

    def test_validate_allow_none(self):
        serializer = new_serializer_class(
            name=serializers.StringField(required=True, allow_none=True),
            )

        obj = serializer.save(data={'name': None})

        self.assertIsNone(obj.name)

    def test_validate_list_field_invalid_value(self):
        serializer = new_serializer_class(
            name=serializers.ListField(
                serializers.IntField(min_value=0), required=True),
            )

        with self.assertRaises(exceptions.ValidationError) as context:
            serializer.validate(data={'name': [1, 2, '3', 4]})

        self.assertIn(
            'does not appear to be an integer',
            context.exception.description['name'][0])

    def test_fail_invalid_field_needs_model_serializer(self):
        with self.assertRaises(serializers.InvalidFieldException):
            new_serializer_class(
                field=serializers.PrimaryKeyRelatedField(
                    model=FakeModel()),)


class FakeProjectTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        models.Author.metadata.create_all(db.engine)
        models.Book.metadata.create_all(db.engine)
        models.Company.metadata.create_all(db.engine)

        models.Company.query.delete()
        models.Author.query.delete()
        models.Book.query.delete()

        self.api = fakeproject.app.api

        self.company = models.Company(name='Ender Labs')

        # create some fake objects
        self.adam = models.Author(name='Adam Olsen', company=self.company)
        self.ross = models.Author(name='Ross Buchanan', company=self.company)

        self.books = [
            models.Book(author=self.adam,
                        title='Gone with the wind.'),
            models.Book(author=self.adam,
                        title='Sinbad'),
            models.Book(author=self.ross,
                        title='Vanishing Friend'),
            models.Book(author=self.ross,
                        title='Wherefore art thou?'),
        ]

        db.session.add(self.company)
        db.session.add(self.adam)
        db.session.add(self.ross)

        for book in self.books:
            db.session.add(book)

        db.session.commit()

    def test_index_companies(self):
        res = self.simulate_get('/api/companies/')
        self.assertEqual(falcon.HTTP_200, res.status)

        json = res.json
        self.assertEqual(1, len(json))
        company = json[0]

        self.assertEqual(3, len(company))

        self.assertIsInstance(company['authors'], list)
        self.assertIsInstance(company['id'], int)
        self.assertIsInstance(company['name'], str)

        self.assertEquals(2, len(company['authors']))
        self.assertEquals(2, len(company['authors'][0]))

        self.assertEquals(company['authors'][0]['uuid1'], str(self.adam.uuid1))
        self.assertEquals(company['authors'][0]['uuid2'], str(self.adam.uuid2))

        self.assertEquals(company['authors'][1]['uuid1'], str(self.ross.uuid1))
        self.assertEquals(company['authors'][1]['uuid2'], str(self.ross.uuid2))

    def test_update_company(self):
        c = models.Company(name='SOC')
        db.session.add(c)
        db.session.commit()

        update_data = {
            'authors': [
                {'uuid1': self.adam.uuid1, 'uuid2': self.adam.uuid2},
            ]
        }

        res = self.simulate_patch(
            '/api/companies/{id}/'.format(id=c.id),
            body=serialize(update_data))

        self.assertEqual(res.status, falcon.HTTP_204)

        db.session.refresh(c)

        self.assertEqual(len(c.authors), 1)
        self.assertEqual(c.authors[0], self.adam)

    def test_index_books(self):
        res = self.simulate_get('/api/books/')
        self.assertEqual(falcon.HTTP_200, res.status)

        json = res.json

        self.assertEqual(len(json), 4)

        for item in json:
            self.assertEqual(len(item['author']), 2)
            self.assertIsInstance(item['author'], dict)
            self.assertIsInstance(item['id'], int)
            self.assertIsInstance(item['title'], str)

            author = item['author']
            self.assertIsInstance(author['uuid1'], str)
            self.assertIsInstance(author['uuid2'], str)

    def test_create_book(self):
        create_data = {
            'title': 'Book Time',
            'author': {
                'uuid1': self.ross.uuid1,
                'uuid2': self.ross.uuid2,
            },
        }

        res = self.simulate_post(
            '/api/books/', body=serialize(create_data))

        self.assertEqual(res.status, falcon.HTTP_201)

        json = res.json
        author = json['author']
        self.assertEqual(author['uuid1'], str(self.ross.uuid1))
        self.assertEqual(author['uuid2'], str(self.ross.uuid2))

    def test_index_authors(self):
        res = self.simulate_get('/api/authors/')
        self.assertEquals(falcon.HTTP_200, res.status)

        json = res.json

        self.assertEqual(2, len(json))

        for author in json:
            self.assertEqual(5, len(author))

            self.assertIsInstance(author['books'], list)
            self.assertIsInstance(author['name'], str)
            self.assertIsInstance(author['uuid1'], str)
            self.assertIsInstance(author['uuid2'], str)
            self.assertIsInstance(author['company'], int)

            if author['name'] == 'Adam Olsen':
                self.assertIn(1, author['books'])
                self.assertIn(2, author['books'])
            else:
                self.assertIn(3, author['books'])
                self.assertIn(4, author['books'])

    def test_update_author(self):
        book = self.books[3]

        update_data = {
            'books': [book.id],
        }

        res = self.simulate_patch('/api/authors/{uuid1}/{uuid2}/'.format(
            uuid1=str(self.adam.uuid1),
            uuid2=str(self.adam.uuid2)), body=serialize(update_data))

        self.assertEqual(res.status, falcon.HTTP_204)

        db.session.refresh(self.adam)

        self.assertEqual(1, len(self.adam.books))
        self.assertEqual(self.adam.books[0], book)
