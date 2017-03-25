#!/usr/bin/env python

"""
Kissasian and Kisscaroon decryption
Created by: Twoure
Date:       03/20/2017
"""

from binascii import a2b_hex, a2b_base64
from crypto.cipher.aes_cbc import AES_CBC

class KissDecryptkit(object):
    def __init__(self):
        #kissasian
        di = String.Base64Decode("XzMyYjgxMmU5YTEzMjFhZTBlODRhZjY2MGM0NzIyYjNhXw==")[1:-1]
        self.div = a2b_hex(di)
        #kisscartoon
        ci = String.Base64Decode("X2E1ZThkMmU5YzE3MjFhZTBlODRhZDY2MGM0NzJjMWYzXw==")[1:-1]
        self.civ = a2b_hex(ci)
        #kissanime
        ai = String.Base64Decode("X2E1ZThkMmU5YzE3MjFhZTBlODRhZDY2MGM0NzJjMWYzXw==")[1:-1]
        self.aiv = a2b_hex(ai)
        #kissmanga
        mi = String.Base64Decode("X2E1ZThlMmU5YzI3MjFiZTBhODRhZDY2MGM0NzJjMWYzXw==")[1:-1]
        self.miv = a2b_hex(mi)

    def ensure_unicode(self, v):
        if isinstance(v, str):
            v = v.decode('utf8')
        return unicode(v)

    def decrypt(self, f, kind, key):
        if kind == 'anime':
            iv = self.aiv
        elif kind == 'cartoon':
            iv = self.civ
        elif kind == 'drama':
            iv = self.div
        elif kind == 'manga':
            iv = self.miv
        else:
            return False

        cipher = AES_CBC(key=Hash.SHA256(key, True), keySize=32)
        return self.ensure_unicode(cipher.decrypt(a2b_base64(f), iv))

KissDecrypt = KissDecryptkit()
