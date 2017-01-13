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

import sys

import pytest

from frf import conf, db
from frf.commands.base import BaseCommand


class Command(BaseCommand):
    description = 'run unittests'

    parse_arguments = False

    def setup_database(self):
        sqlalchemy_test_uri = conf.get('SQLALCHEMY_TEST_CONNECTION_URI')

        if conf.get('SQLALCHEMY_CONNECTION_URI') \
                and not sqlalchemy_test_uri:

            self.error(
                'You must set `SQLALCHEMY_TEST_CONNECTION_URI` in your '
                'settings file.')
            sys.exit(-1)

        if sqlalchemy_test_uri:
            self.info('Setting up testing database ... ', end='')
            db.init(sqlalchemy_test_uri)
            self.info('Done.')

            self.info('Creating tables ... ', end='')
            db.drop_all()
            db.create_all()
            self.info('Done.')

    def handle(self, args):
        conf['TESTING'] = True

        sys.argv = sys.argv[1:]

        self.setup_database()
        sys.exit(pytest.main())
