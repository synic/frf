import json
import falcon

from frf.tests.base import BaseTestCase

from frf.tests import fakeproject


class FakeProjectTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.api = fakeproject.app.api

    def test_permissions(self):
        res = self.simulate_get('/api/test_permissions_view/')
        self.assertEqual(res.status, falcon.HTTP_200)

        res = self.simulate_post('/api/test_permissions_view/',
                                 body=json.dumps({'test': 1}))

        self.assertEqual(res.status, falcon.HTTP_403)
