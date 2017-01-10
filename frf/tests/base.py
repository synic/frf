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

from falcon.testing import TestCase

from frf import conf, db
from frf.exceptions import TestingError


class BaseTestCase(TestCase):
    def setUp(self):
        conf['TESTING'] = True

        self.sqlalchemy_test_uri = conf.get('SQLALCHEMY_TEST_CONNECTION_URI')
        if conf.get('SQLALCHEMY_CONNECTION_URI') \
                and not self.sqlalchemy_test_uri:
            raise TestingError(
                'You must set `SQLALCHEMY_TEST_CONNECTION_URI` in your '
                'settings file.')

        if self.sqlalchemy_test_uri:
            # set up the test database
            db.init(self.sqlalchemy_test_uri, echo=False)
            db.create_all()

        super().setUp()

    def tearDown(self):
        super().tearDown()

        if self.sqlalchemy_test_uri:
            db.truncate_all()
