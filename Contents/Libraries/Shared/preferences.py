#!/usr/bin/env python

from lxml import etree, html
from lxml.html import soupparser
from BeautifulSoup import UnicodeDammit
import simplejson
import os

BUNDLE_NAME = 'KissNetwork.bundle'
IDENTIFIER = 'com.plexapp.plugins.kissnetwork'

def is_true(value):
    return value in (True, 1, 'true', 'True')


class XML(object):
    def __init__(self):
        self.base = None

    def _construct_el(self, el, text, kwargs):
        if text:
            el.text = text
        for key in kwargs:
            el.set(key, kwargs[key])
        return el

    def element(self, name, text=None, **kwargs):
        return self._construct_el(etree.Element(name), text, kwargs)

    def from_string(self, string, isHTML=False, encoding=None, remove_blank_text=False):
        if string is None: return None

        if encoding == None:
            ud = UnicodeDammit(str(string), isHTML=isHTML)
            markup = ud.markup.encode('utf-8')
        else:
            markup = str(string).encode(encoding)

        if isHTML:
            try:
                return html.fromstring(markup, parser=html_parser)
            except:
                return soupparser.fromstring(string)
        else:
            return etree.fromstring(markup, parser=(xml_parser if remove_blank_text else None))
XML = XML()


class Pref(object):
    def __init__(self, pref_type, label, default_value=None, secure=False, hidden=False):
        self.type = pref_type
        self.label = label
        self.default_value = self.encode_value(default_value)
        self.secure = secure
        self.hidden = hidden

    def encode_value(self, value):
        return value

    def decode_value(self, encoded_value):
        return encoded_value

    def info_dict(self, value=None, **kwargs):
        d = dict(
            label = self.label,
            type = self.type,
            secure = ('true' if self.secure else 'false'),
            value = self.default_value if value == None else self.encode_value(value),
            default = self.default_value,
        )

        d.update(**kwargs)
        return d

    def __str__(self):
        return "%s (%s)" % (type(self).__name__, self.label)


class TextPref(Pref):
    def __init__(self, label, default_value, options=[], secure=False, hidden=False):
        Pref.__init__(self, 'text', label, default_value, secure, hidden)
        self.options = options

    def info_dict(self, value=None, **kwargs):
        return Pref.info_dict(self, value, option=','.join(self.options), **kwargs)

    def encode_value(self, encoded_value):
        return '' if encoded_value == None else str(encoded_value)

    def decode_value(self, value):
        return None if value == None or len(value) == 0 else str(value)


class BooleanPref(Pref):
    def __init__(self, label, default_value, secure=False, hidden=False):
        self.sandbox = Pref.__init__(self, 'bool', label, default_value, secure, hidden)

    def encode_value(self, value):
        return 'true' if is_true(value) else 'false'

    def decode_value(self, encoded_value):
        return is_true(encoded_value)


class EnumPref(Pref):
    def __init__(self, label, default_value, values=[], secure=False, hidden=False):
        self.values = values
        Pref.__init__(self, 'enum', label, default_value, secure, hidden)

    def encode_value(self, value):
        return str(self.values.index(value)) if value in self.values else None

    def decode_value(self, encoded_value):
        try:
            int_val = int(encoded_value)
            if int_val < len(self.values):
                return self.values[int_val]
        except:
            pass

    def info_dict(self, value=None, **kwargs):
        value_labels = []
        for v in self.values:
            value_labels.append(v)
        return Pref.info_dict(self, value, values = '|'.join(value_labels))


class PreferenceSet(object):
    def __init__(self):
        self.pref_names = list()
        self.prefs_dict = None
        self.user_values_dict = dict()
        self.mtimes = {}
        self.last_modified = os.path.getmtime

    def file_exists(self, path):
        return os.path.exists(path)

    def has_changed(self, path, mtime_key):
        if not self.file_exists(path):
            return False

        mtime_key_id = id(mtime_key)
        return mtime_key_id not in self.mtimes or path in self.mtimes[mtime_key_id] and self.last_modified(path) != self.mtimes[mtime_key_id][path]

    @property
    def user_file_path(self):
        return os.path.join(
            os.getcwd().lstrip('\\\?').split('Plug-in Support')[0],
            'Plug-in Support', 'Preferences', '{}.xml'.format(IDENTIFIER)
            )

    def load(self, filename, mtime_key=None):
        filename = os.path.abspath(filename)
        data = None
        try:
            with open(filename, 'rb') as f:
                data = f.read()
        except Exception, e:
            raise KeyError(u'* cannot load info from \'{}\'\n\n{}'.format(filename, e))
        return data

    def load_default_file(self):
        file_path = self.default_prefs_path
        el = XML.element('PluginPreferences')

        for name, pref in self.prefs.items():
            el.append(XML.element(name, self.user_values_dict.get(name, pref.encode_value(pref.default_value))))
        return el

    def load_user_file(self):
        file_path = self.user_file_path
        user_values = dict()

        if not os.path.exists(file_path):
            prefs_xml = self.load_default_file()
        else:
            try:
                prefs_xml_str = self.load(file_path, mtime_key=self)
                prefs_xml = XML.from_string(prefs_xml_str)
            except Exception, e:
                raise KeyError(u'* cannot load info from \'{}\'\n\n{}'.format(file_path, e))

        for el in prefs_xml:
            pref_name = str(el.tag)

            if el.text != None and pref_name in self.prefs:
                user_values[pref_name] = str(el.text)

        self.user_values_dict = user_values

    @property
    def user_values(self):
        if os.path.exists(self.user_file_path) == False or self.has_changed(self.user_file_path, mtime_key=self):
            self.load_user_file()
        else:
            raise KeyError(u'* cannot load info from \'{}\''.format(self.user_file_path))
        return self.user_values_dict

    @property
    def prefs(self):
        if self.prefs_dict == None:
            self.load_prefs()
        return self.prefs_dict

    @property
    def default_prefs_path(self):
        return os.path.join(
            os.getcwd().lstrip('\\\?').split('Plug-in Support')[0],
            'Plug-ins', BUNDLE_NAME, 'Contents', 'DefaultPrefs.json'
            )

    def load_prefs(self):
        prefs_dict = dict()
        prefs_json = list()

        file_path = self.default_prefs_path
        if self.file_exists(file_path):
            try:
                data = self.load(file_path)
                json_array = simplejson.loads(data)
                prefs_json.extend(json_array)
            except Exception, e:
                return (u'* cannot load info from \'{}\'\n\n{}'.format(file_path, e))

        for pref in prefs_json:
            name = pref['id']

            if name not in self.pref_names:
                pref_type = pref['type']
                pref_secure = 'secure' in pref and (pref['secure'] == True or str(pref['secure']).lower() == 'true')
                pref_hidden = 'hidden' in pref and (pref['hidden'] == True or str(pref['hidden']).lower() == 'true')

            if 'default' in pref:
                pref_default = pref['default']
            else:
                pref_default = None
            pref_label = pref['label']

            if pref_type == 'text':
                if 'option' in pref:
                    pref_option = pref['option'].split(',')
                else:
                    pref_option = list()
                prefs_dict[name] = TextPref(pref_label, pref_default, pref_option, pref_secure, pref_hidden)
            elif pref_type == 'bool':
                prefs_dict[name] = BooleanPref(pref_label, pref_default, pref_secure, pref_hidden)
            elif pref_type == 'enum':
                if 'values' in pref:
                    pref_values = pref['values']
                else:
                    pref_values = list()
                prefs_dict[name] = EnumPref(pref_label, pref_default, pref_values, pref_secure, pref_hidden)
            else:
                continue

            self.pref_names.append(name)
        self.prefs_dict = prefs_dict

    def __getitem__(self, name):
        pref = self.prefs.get(name)

        if pref:
            if self.user_values:
                value = self.user_values.get(name, pref.default_value)
                return pref.decode_value(value if value else pref.default_value)
            else:
                raise KeyError(u'* No user_values within pref \'{}\''.format(pref))
        else:
            raise KeyError(u'* No pref found')
        raise KeyError(u'* No preference named \'{}\' found.'.format(name))

Prefs = PreferenceSet()
