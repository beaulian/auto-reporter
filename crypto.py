import re
import random

import base64
from Crypto.Cipher import AES

chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'


def _rds(n):
    return ''.join([chars[int(random.random() * len(chars))]
                    for i in range(n)])


def _add_16(text):
    pad = 16 - len(text.encode('utf-8')) % 16
    text = text + pad * chr(pad)
    return text.encode('utf-8')


def _encrypt(data, key0, iv0):
    data = _add_16(data.strip())
    key = key0.encode('utf-8')
    iv = iv0.encode('utf-8')
    cryptos = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cryptos.encrypt(data)
    return base64.b64encode(cipher_text).decode('utf-8')


def encrypt(data, key):
    return _encrypt(_rds(64) + data, key, _rds(16))
