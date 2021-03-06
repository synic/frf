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

import unittest

from frf.tests import fakeproject  # noqa
from frf.cache.engines.dummy import DummyCacheEngine  # noqa
from frf import conf, cache, db  # noqa

#: NOTE: The tests here are initializeed when we import ``fakeproject`` above.


class TestCase(unittest.TestCase):
    def test_app_init_cache(self):
        engine = cache.get_engine()

        self.assertIsInstance(engine, DummyCacheEngine)

    def test_app_init_db(self):
        engine = db.get_engine()

        self.assertEqual(engine.dialect.name, 'sqlite')

    def test_app_init_conf(self):
        self.assertTrue(conf.DEBUG)
        self.assertEqual(conf['TIMEZONE'], 'US/Mountain')
