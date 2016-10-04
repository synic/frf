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
