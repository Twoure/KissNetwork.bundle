#!/usr/bin/python
__author__ = 'Thomas Dixon'
__license__ = 'MIT'

import copy, struct, sys

def new(m=None):
    return sha512(m)

class sha512(object):
    _k = (0x428a2f98d728ae22L, 0x7137449123ef65cdL, 0xb5c0fbcfec4d3b2fL, 0xe9b5dba58189dbbcL,
          0x3956c25bf348b538L, 0x59f111f1b605d019L, 0x923f82a4af194f9bL, 0xab1c5ed5da6d8118L,
          0xd807aa98a3030242L, 0x12835b0145706fbeL, 0x243185be4ee4b28cL, 0x550c7dc3d5ffb4e2L,
          0x72be5d74f27b896fL, 0x80deb1fe3b1696b1L, 0x9bdc06a725c71235L, 0xc19bf174cf692694L,
          0xe49b69c19ef14ad2L, 0xefbe4786384f25e3L, 0x0fc19dc68b8cd5b5L, 0x240ca1cc77ac9c65L,
          0x2de92c6f592b0275L, 0x4a7484aa6ea6e483L, 0x5cb0a9dcbd41fbd4L, 0x76f988da831153b5L,
          0x983e5152ee66dfabL, 0xa831c66d2db43210L, 0xb00327c898fb213fL, 0xbf597fc7beef0ee4L,
          0xc6e00bf33da88fc2L, 0xd5a79147930aa725L, 0x06ca6351e003826fL, 0x142929670a0e6e70L,
          0x27b70a8546d22ffcL, 0x2e1b21385c26c926L, 0x4d2c6dfc5ac42aedL, 0x53380d139d95b3dfL,
          0x650a73548baf63deL, 0x766a0abb3c77b2a8L, 0x81c2c92e47edaee6L, 0x92722c851482353bL,
          0xa2bfe8a14cf10364L, 0xa81a664bbc423001L, 0xc24b8b70d0f89791L, 0xc76c51a30654be30L,
          0xd192e819d6ef5218L, 0xd69906245565a910L, 0xf40e35855771202aL, 0x106aa07032bbd1b8L,
          0x19a4c116b8d2d0c8L, 0x1e376c085141ab53L, 0x2748774cdf8eeb99L, 0x34b0bcb5e19b48a8L,
          0x391c0cb3c5c95a63L, 0x4ed8aa4ae3418acbL, 0x5b9cca4f7763e373L, 0x682e6ff3d6b2b8a3L,
          0x748f82ee5defb2fcL, 0x78a5636f43172f60L, 0x84c87814a1f0ab72L, 0x8cc702081a6439ecL,
          0x90befffa23631e28L, 0xa4506cebde82bde9L, 0xbef9a3f7b2c67915L, 0xc67178f2e372532bL,
          0xca273eceea26619cL, 0xd186b8c721c0c207L, 0xeada7dd6cde0eb1eL, 0xf57d4f7fee6ed178L,
          0x06f067aa72176fbaL, 0x0a637dc5a2c898a6L, 0x113f9804bef90daeL, 0x1b710b35131c471bL,
          0x28db77f523047d84L, 0x32caab7b40c72493L, 0x3c9ebe0a15c9bebcL, 0x431d67c49c100d4cL,
          0x4cc5d4becb3e42b6L, 0x597f299cfc657e2aL, 0x5fcb6fab3ad6faecL, 0x6c44198c4a475817L)
    _h = (0x6a09e667f3bcc908L, 0xbb67ae8584caa73bL, 0x3c6ef372fe94f82bL, 0xa54ff53a5f1d36f1L,
          0x510e527fade682d1L, 0x9b05688c2b3e6c1fL, 0x1f83d9abfb41bd6bL, 0x5be0cd19137e2179L)
    _output_size = 8
   
    blocksize = 1
    block_size = 128
    digest_size = 64
   
    def __init__(self, m=None):       
        self._buffer = ''
        self._counter = 0
       
        if m is not None:
            if type(m) is not str:
                raise TypeError, '%s() argument 1 must be string, not %s' % (self.__class__.__name__, type(m).__name__)
            self.update(m)
       
    def _rotr(self, x, y):
        return ((x >> y) | (x << (64-y))) & 0xFFFFFFFFFFFFFFFF
                   
    def _sha512_process(self, chunk):
        w = [0]*80
        w[0:16] = struct.unpack('!16Q', chunk)
       
        for i in range(16, 80):
            s0 = self._rotr(w[i-15], 1) ^ self._rotr(w[i-15], 8) ^ (w[i-15] >> 7)
            s1 = self._rotr(w[i-2], 19) ^ self._rotr(w[i-2], 61) ^ (w[i-2] >> 6)
            w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xFFFFFFFFFFFFFFFF
       
        a,b,c,d,e,f,g,h = self._h
       
        for i in range(80):
            s0 = self._rotr(a, 28) ^ self._rotr(a, 34) ^ self._rotr(a, 39)
            maj = (a & b) ^ (a & c) ^ (b & c)
            t2 = s0 + maj
            s1 = self._rotr(e, 14) ^ self._rotr(e, 18) ^ self._rotr(e, 41)
            ch = (e & f) ^ ((~e) & g)
            t1 = h + s1 + ch + self._k[i] + w[i]
           
            h = g
            g = f
            f = e
            e = (d + t1) & 0xFFFFFFFFFFFFFFFF
            d = c
            c = b
            b = a
            a = (t1 + t2) & 0xFFFFFFFFFFFFFFFF
           
        self._h = [(x+y) & 0xFFFFFFFFFFFFFFFF for x,y in zip(self._h, [a,b,c,d,e,f,g,h])]
       
    def update(self, m):
        if not m:
            return
        if type(m) is not str:
            raise TypeError, '%s() argument 1 must be string, not %s' % (sys._getframe().f_code.co_name, type(m).__name__)
       
        self._buffer += m
        self._counter += len(m)
       
        while len(self._buffer) >= 128:
            self._sha512_process(self._buffer[:128])
            self._buffer = self._buffer[128:]
           
    def digest(self):
        mdi = self._counter & 0x7F
        length = struct.pack('!Q', self._counter<<3)
       
        if mdi < 112:
            padlen = 111-mdi
        else:
            padlen = 239-mdi
       
        r = self.copy()
        r.update('\x80'+('\x00'*(padlen+8))+length)
        return ''.join([struct.pack('!Q', i) for i in r._h[:self._output_size]])
       
    def hexdigest(self):
        return self.digest().encode('hex')
       
    def copy(self):
        return copy.deepcopy(self)
