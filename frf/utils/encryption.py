import uuid
import hashlib
import base64
import hmac

from Crypto import Random
from Crypto.Cipher import AES

_MAGIC = '__frf_encrypted'


class DecryptionError(Exception):
    pass


class AESCipher(object):
    """Simple AES Encryption.

    Credits: http://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256  # noqa
    """
    def __init__(self, key=None):
        if not key:
            key = str(uuid.uuid4())
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def _update_key(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = '{}{}'.format(_MAGIC, raw)
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        ciphertext = cipher.encrypt(raw)
        cipher_msg = iv + ciphertext
        hmac_obj = hmac.new(self.key, msg=cipher_msg, digestmod='sha512')
        hmac_digest = hmac_obj.digest()

        return base64.b64encode(cipher_msg + hmac_digest)

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        try:
            data = self._unpad(
                cipher.decrypt(enc[AES.block_size:])).decode('utf-8')
        except UnicodeDecodeError:
            raise DecryptionError()

        try:
            magic = data[:len(_MAGIC)]
            if magic != _MAGIC:
                raise DecryptionError()
        except IndexError:
            raise DecryptionError()

        return data[len(_MAGIC):]

    def _pad(self, s):
        return (s + (self.bs - len(s) % self.bs) *
                chr(self.bs - len(s) % self.bs))

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]
