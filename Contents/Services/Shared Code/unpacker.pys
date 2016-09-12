#!/usr/bin/env python
####################################################################################################
"""
    urlresolver XBMC Addon
    Copyright (C) 2013 Bstrdsmkr

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Adapted for use in xbmc from:
    https://github.com/einars/js-beautify/blob/master/python/jsbeautifier/unpackers/packer.py

Unpacker for Dean Edward's p.a.c.k.e.r
"""

def unpack(source):
    """Unpacks P.A.C.K.E.R. packed js code."""
    payload, symtab, radix, count = filterargs(source)

    if count != len(symtab):
        raise UnpackingError('Malformed p.a.c.k.e.r. symtab.')

    try:
        unbase = Unbaser(radix)
    except TypeError:
        Log.Exception('Unknown p.a.c.k.e.r. encoding.')
        raise UnpackingError('Unknown p.a.c.k.e.r. encoding.')

    def lookup(match):
        """Look up symbols in the synthetic symtab."""
        word  = match.group(0)
        return symtab[unbase(word)] or word

    source = Regex(r'\b\w+\b').sub(lookup, payload)
    return replacestrings(source)

def filterargs(source):
    """Juice from a source file the four args needed by decoder."""
    juicers = [ (r"}\('(.*)',\s*?(\d+),\s*?(\d+),\s*?[\(\'](.+?)[\'\)]\.split\([\'\"](.+?)[\'\"]\),\s*?(\d+),\s*?(.*?)\)"),
                (r"}\('(.*)',\s*?(\[\]),\s*?(\d+),\s*?[\(\'](.+?)[\'\)]\.split\([\'\"](.+?)[\'\"]\),\s*?(\d+),\s*?(.*?)\)"),
                (r"}\('(.*)',\s*?(\d+),\s*?(\d+),\s*?[\(\'](.+?)[\'\)]\.split\([\'\"](.+?)[\'\"]\)"),
                (r"}\('(.*)',\s*?(\[\]),\s*?(\d+),\s*?[\(\'](.+?)[\'\)]\.split\([\'\"](.+?)[\'\"]\)"),
              ]
    for juicer in juicers:
        args = Regex(juicer).search(source, Regex.DOTALL)
        if args:
            a = args.groups()
            try:
                a1 = 36 if a[1] == '[]' else int(a[1])
                a3 = ''.join([b.strip("'") for b in a[3].split('+')]) if '+' in a[3] else a[3]
                return a[0], a3.split(a[4]), a1, int(a[2])
            except ValueError:
                raise UnpackingError('Corrupted p.a.c.k.e.r. data.')

    # could not find a satisfying regex
    raise UnpackingError('Could not make sense of p.a.c.k.e.r data (unexpected code structure)')

def replacestrings(source):
    """Strip string lookup table (list) and replace values in source."""
    match = Regex(r'var *(_\w+)\=\["(.*?)"\];').search(source, Regex.DOTALL)

    if match:
        varname, strings = match.groups()
        startpoint = len(match.group(0))
        lookup = strings.split('","')
        variable = '%s[%%d]' % varname
        for index, value in enumerate(lookup):
            source = source.replace(variable % index, '"%s"' % value)
        return source[startpoint:]
    return source

class Unbaser(object):
    """Functor for a given base. Will efficiently convert
    strings to natural numbers."""
    ALPHABET  = {
        53 : '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQ',
        59 : '0123456789abcdefghijklmnopqrstuvwABCDEFGHIJKLMNOPQRSTUVWXYZ',
        62 : '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        64 : '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/',
        95 : (' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            '[\]^_`abcdefghijklmnopqrstuvwxyz{|}~')
    }

    def __init__(self, base):
        self.base = base

        # If base can be handled by int() builtin, let it do it for us
        if 2 <= base <= 36:
            self.unbase = lambda string: int(string, base)
        else:
            # Build conversion dictionary cache
            try:
                self.dictionary = dict((cipher, index) for
                    index, cipher in enumerate(self.ALPHABET[base]))
            except KeyError:
                try:
                    self.dictionary = dict((cipher, index) for
                        index, cipher in enumerate(self.ALPHABET[64][:base]))
                except KeyError:
                    Log.Exception('Unsupported base encoding.')
                    raise TypeError('Unsupported base encoding.')

            self.unbase = self.dictunbaser

    def __call__(self, string):
        return self.unbase(string)

    def dictunbaser(self, string):
        """Decodes a  value to an integer."""
        ret = 0
        for index, cipher in enumerate(string[::-1]):
            ret += (self.base ** index) * self.dictionary[cipher]
        return ret

class UnpackingError(Exception):
    """Badly packed source or general error. Argument is a
    meaningful description."""
    pass
