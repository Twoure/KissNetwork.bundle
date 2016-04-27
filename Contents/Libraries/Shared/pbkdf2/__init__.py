#!/usr/bin/env python3.3
# -*- coding: utf-8 -*-
"""Fast PBKDF2_HMAC() for Python 2 and Python 3

Christian Heimes <christian@python.org>
"""
from __future__ import unicode_literals
from hashlib import new as _hashlib_new
import sys as _sys

__all__ = ('pbkdf2_hmac', 'compare_digest')

if _sys.version_info[0] == 2:
    from binascii import hexlify as _hexlify
    from binascii import unhexlify as _unhexlify
    from struct import pack as _pack

    _PY3 = False
    _text_type = unicode
    _string_type = basestring
    _trans_5C = b''.join(chr(x ^ 0x5C) for x in xrange(256))
    _trans_36 = b''.join(chr(x ^ 0x36) for x in xrange(256))

    if _sys.version_info < (2, 7):
        memoryview = buffer

    def _loop_counter(loop, pack=_pack):
        return pack(b'>I', loop)

    # hack from django.utils.crypto
    def _from_bytes(value, endianess, hexlify=_hexlify, int=int):
        return int(hexlify(value), 16)

    def _to_bytes(value, length, endianess, unhexlify=_unhexlify):
        fmt = '%%0%ix' % (2 * length)
        return _unhexlify(fmt % value)

else:
    _trans_5C = bytes((x ^ 0x5C) for x in range(256))
    _trans_36 = bytes((x ^ 0x36) for x in range(256))

    _PY3 = True
    _text_type = str
    _string_type = str
    _from_bytes = int.from_bytes
    _to_bytes = int.to_bytes

    def _loop_counter(loop):
        return loop.to_bytes(4, 'big')


def pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None):
    """Password based key derivation function 2 (PKCS #5 v2.0)

    This Python implementations based on the hmac module about as fast
    as OpenSSL's PKCS5_PBKDF2_HMAC for short passwords and much faster
    for long passwords.

    Timings in seconds for pbkdf2_hmac('sha256', b'password10', b'salt', 50000)
    on an Intel I7 with 2.50 GHz:

    len(password)  Python 3.3  OpenSSL 1.0.1e  OpenSSL patched
    -------------  ----------  --------------  ---------------
    10             0.408       0.431           0.233
    100            0.418       0.509           0.228
    500            0.433       1.01            0.230
    1000           0.435       1.61            0.228
    -------------  ----------  --------------  ---------------

    On Python 2.7 the code runs about 50% slower than on Python 3.3.
    """
    if not isinstance(hash_name, _string_type):
        raise TypeError(hash_name)

    # no unicode, memoryview and other bytes-like objects are too hard to
    # support on 2.6 to 3.4
    if not isinstance(password, (bytes, bytearray)):
        password = memoryview(password).tobytes()
    if not isinstance(salt, (bytes, bytearray)):
        salt = memoryview(salt).tobytes()

    # Fast inline HMAC implementation
    inner = _hashlib_new(hash_name)
    outer = _hashlib_new(hash_name)
    blocksize = getattr(inner, 'block_size', 64)
    if len(password) > blocksize:
        password = _hashlib_new(hash_name, password).digest()
    password = password + b'\x00' * (blocksize - len(password))
    inner.update(password.translate(_trans_36))
    outer.update(password.translate(_trans_5C))

    def prf(msg, inner=inner, outer=outer):
        # PBKDF2_HMAC uses the password as key. We can re-use the same
        # digest objects and and just update copies to skip initialization.
        icpy = inner.copy()
        ocpy = outer.copy()
        icpy.update(msg)
        ocpy.update(icpy.digest())
        return ocpy.digest()

    if iterations < 1:
        raise ValueError(iterations)
    if dklen is None:
        dklen = outer.digest_size
    if dklen < 1:
        raise ValueError(dklen)

    from_bytes = _from_bytes
    to_bytes = _to_bytes
    loop_counter = _loop_counter

    dkey = b''
    loop = 1
    while len(dkey) < dklen:
        prev = prf(salt + loop_counter(loop))
        # endianess doesn't matter here as long to / from use the same
        rkey = from_bytes(prev, 'big')
        for i in range(iterations - 1):
            prev = prf(prev)
            # rkey = rkey ^ prev
            rkey ^= from_bytes(prev, 'big')
        loop += 1
        dkey += to_bytes(rkey, inner.digest_size, 'big')

    return dkey[:dklen]

py_pbkdf2_hmac = pbkdf2_hmac

try:
    from backports.pbkdf2._pbkdf2 import pbkdf2_hmac  # noqa
except ImportError:
    pass


def compare_digest(a, b):
    """Constant timing comparison
    """
    if isinstance(a, _text_type) and isinstance(b, _text_type):
        try:
            a = a.encode("ascii")
        except UnicodeEncodeError:
            raise TypeError(a)
        try:
            b = b.encode("ascii")
        except UnicodeEncodeError:
            raise TypeError(b)

    if isinstance(a, (bytes, bytearray)):
        left = bytes(a)
    else:
        raise TypeError(a)
    if isinstance(b, (bytes, bytearray)):
        right = bytes(b)
    else:
        raise TypeError(b)

    len_a = len(a)
    len_b = len(b)

    if len_a == len_b:
        result = 0
    # loop count depends on length of b
    if len_a != len_b:
        result = 1
        left = right
    if _PY3:
        for l, r in zip(left, right):
            result |= l ^ r
    if not _PY3:
        _ord = ord
        for l, r in zip(left, right):
            result |= _ord(l) ^ _ord(r)
    return result == 0
