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

import datetime
import unittest
import uuid

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
