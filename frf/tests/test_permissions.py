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
