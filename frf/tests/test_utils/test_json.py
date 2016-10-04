import uuid
import datetime
import unittest

from frf.utils import json


class TestCase(unittest.TestCase):
    def test_serialize_datetime(self):
        d = datetime.datetime(2016, 1, 1, 10, 32, 1)

        data = {
            'date': d,
        }

        res = json.deserialize(json.serialize(data))

        self.assertEqual(res['date'], '2016-01-01T10:32:01')

    def test_serialize_uuid(self):
        d = uuid.UUID('abea9b06-43a1-4e84-ad75-fc0346a64497')

        data = {
            'uuid': d,
        }

        res = json.deserialize(json.serialize(data))
        self.assertEqual(
            res['uuid'], 'abea9b06-43a1-4e84-ad75-fc0346a64497')

