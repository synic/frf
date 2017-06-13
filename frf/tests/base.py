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

from frf import conf
from falcon.testing import TestCase
from sqlalchemy import event


class BaseTestCase(TestCase):
    database = None  # frf database object

    def setUp(self):
        super().setUp()
        # start an sqlalchemy transaction to encompass the test case, so that
        # we can roll it back after the test is complete to get a fresh
        # database.
        if self.database:
            if conf.TESTING:
                self.database.create_all()

            self.session = self.database.session
            self.connection = self.database.engine.connect()
            self.trans = self.connection.begin()
            self.session.remove()
            self.session.configure(bind=self.connection)
            self.session.begin_nested()

            @event.listens_for(self.session, 'after_transaction_end')
            def restart_savepoint(session, t):
                if t.nested and not t._parent.nested:
                    session.expire_all()
                    session.begin_nested()

    def tearDown(self):
        self.trans.rollback()
        self.session.close()
        self.connection.close()

        if conf.TESTING:
            self.database.drop_all()
        super().tearDown()
