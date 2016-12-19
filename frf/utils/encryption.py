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

import uuid
import hashlib
import base64
import hmac

from Crypto import Random
from Crypto.Cipher import AES


class DecryptionError(Exception):
    pass


class AESCipher(object):
    """Simple AES Encryption.

    Credits: http://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256  # noqa
    """
    def __init__(self, key=None):
        if not key:
            # Get 32 bytes (256 bits) of data from /dev/urandom
            key = Random.new().read(32)
        if type(key) != bytes:
            key = key.encode()
        self.bs = AES.block_size
        self.key = hashlib.sha256(key).digest()

    def _update_key(self, key):
        if type(key) != bytes:
            key = key.encode()
        self.key = hashlib.sha256(key).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        ciphertext = cipher.encrypt(raw)
        cipher_msg = iv + ciphertext
        hmac_obj = hmac.new(self.key, msg=cipher_msg, digestmod='sha512')
        hmac_digest = hmac_obj.digest()

        return base64.b64encode(cipher_msg + hmac_digest)

    def decrypt(self, enc):
        hmac_digest_size = hashlib.sha512().digest_size
        enc = base64.b64decode(enc)

        try:
            iv = enc[:AES.block_size]
            hmac_digest = enc[-hmac_digest_size:]
            ciphertext = enc[AES.block_size:-hmac_digest_size]
        except IndexError:
            raise DecryptionError()

        # Verify the HMAC before decrypting
        hmac_obj = hmac.new(self.key, msg=iv+ciphertext, digestmod='sha512')
        if not hmac.compare_digest(hmac_digest, hmac_obj.digest()):
            raise DecryptionError('HMAC could not be verified')

        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        try:
            data = self._unpad(
                cipher.decrypt(ciphertext)).decode('utf-8')
        except UnicodeDecodeError:
            raise DecryptionError()

        return data

    def _pad(self, s):
        pad_length = AES.block_size - (len(s) % AES.block_size)

        # Add pad even if it is a multiple already as per RFC 5652
        if pad_length == 0:
            pad_length = AES.block_size
        pad = pad_length.to_bytes(1, 'big') * pad_length

        return s.encode() + pad

    def _unpad(self, s):
        # As per PKCS#7, the padded length is on any of the bits, just grab
        # the last one.
        pad_length = s[-1]
        return s[:-pad_length]
