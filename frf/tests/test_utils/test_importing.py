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

import inspect
import unittest

from frf.utils import importing


class TestCase(unittest.TestCase):
    def test_import_class(self):
        cls = importing.import_class(
            'frf.tests.test_utils.dummy_class.DummyClass')

        self.assertTrue(inspect.isclass(cls))
        self.assertEqual('stuff', cls().woot())

    def test_fail_import_missing_import(self):
        with self.assertRaises(ImportError):
            importing.import_class('thisshould.not.import.12112')

    def test_fail_import_not_a_class(self):
        with self.assertRaises(ImportError) as context:
            importing.import_class('frf.tests.test_utils.test_importing')

        self.assertIn('does not refer to a class', str(context.exception))
