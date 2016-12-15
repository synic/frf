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

from frf.utils import encryption


class TestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.cipher = encryption.AESCipher(key='fruitloops')

    def test_encrypt_decrypt(self):
        data = 'this is some data'
        res = self.cipher.encrypt(data)
        self.assertIsInstance(res, bytes)
        res = self.cipher.decrypt(res)
        self.assertEqual(data, 'this is some data')

    def test_fail_decrypt_wrong_key(self):
        data = 'this is some data'
        res = self.cipher.encrypt(data)
        self.assertIsInstance(res, bytes)

        cipher = encryption.AESCipher(key='wrongkey')

        with self.assertRaises(encryption.DecryptionError):
            res = cipher.decrypt(res)

    def test_fail_each_encryption_output_is_different(self):
        data = 'this is some data'

        res1 = self.cipher.encrypt(data)
        res2 = self.cipher.encrypt(data)

        self.assertNotEqual(res1, res2)

        res1 = self.cipher.decrypt(res1)
        res2 = self.cipher.decrypt(res2)

        self.assertEqual(res1, res2)
        self.assertEqual(res1, 'this is some data')
