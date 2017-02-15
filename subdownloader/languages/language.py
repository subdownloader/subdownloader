# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import re
import langdetect
import logging

from subdownloader.util import asciify

log = logging.getLogger("subdownloader.languages.Languages")

# FIXME: translation..
_ = lambda x: x


class NotALanguageException(ValueError):
    """
    Exception to inform that some value is not a valid Language.
    """
    pass

class Language:
    """
    Instances of the class represent a language.
    """
    def __init__(self, entry):
        """
        Create a new Language object. Values should be strings.
        :param entry: dict having keys: ('locale', 'ISO639', 'LanguageID', 'LanguageName')
        """
        self._locale = entry['locale']
        self._iso639 = entry['ISO639']
        self._langid = entry['LanguageID']
        self._name = entry['LanguageName']

    def locale(self):
        """
        Get locale of Language
        :return: locale as string
        """
        return self._locale

    def xx(self):
        """
        Get ISO639 of Language
        :return: ISO639 as string
        """
        return self._iso639

    def xxx(self):
        """
        Get LanguageID of Language
        :return: LanguageID as string
        """
        return self._langid

    def name(self):
        """
        Return readable name of Language
        :return: Readable name as string
        """
        return self._name

    def __eq__(self, other):
        """
        Check if other is the same as self.
        :param other: other object
        :return: True if other is the same as self
        """
        if other is None:
            return False
        if type(self) != type(other):
            return False
        return self._iso639 == other._iso639

    def __hash__(self):
        """
        Return hash of this object.
        :return: hash integer
        """
        return hash(self._iso639)

    def __repr__(self):
        """
        Return representation of this instance
        :return: string representation of self
        """
        return '<Language:xx={}>'.format(self._iso639)

    @classmethod
    def from_locale(cls, locale):
        """
        Create a new Language instance from a locale string
        :param locale: locale as string
        :return: Language instance with instance.locale() == locale
        """
        locale = str(locale)
        return cls._from_XYZ('locale', locale)

    @classmethod
    def from_xx(cls, xx):
        """
        Create a new Language instance from a ISO639 string
        :param xx: ISO639 as string
        :return: Language instance with instance.xx() == xx
        """
        xx = str(xx).lower()
        if xx == 'gr':
            xx = 'el'
        return cls._from_XYZ('ISO639', xx)

    @classmethod
    def from_xxx(cls, xxx):
        """
        Create a new Language instance from a LanguageID string
        :param xxx: LanguageID as string
        :return: Language instance with instance.xxx() == xxx
        """
        xxx = str(xxx).lower()
        return cls._from_XYZ('LanguageID', xxx)

    @classmethod
    def from_name(cls, name):
        """
        Create a new Language instance from a name as string
        :param name: name as string
        :return: Language instance with instance.name() == name
        """
        name = str(name).lower()
        return cls._from_XYZ('LanguageName', name)

    @classmethod
    def _from_XYZ(cls, xyzkey, xyzvalue):
        """
        Private helper function to create new Language instance.
        :param xyzkey: one of ('locale', 'ISO639', 'LanguageID', 'LanguageName')
        :param xyzvalue: corresponding value of xyzkey
        :return: Language instance
        """
        for l in LANGUAGES:
            if l[xyzkey] == xyzvalue:
                return cls(l)
        raise NotALanguageException('Illegal language {}: {}'.format(xyzkey, xyzvalue))

    @classmethod
    def from_unknown(cls, value, xx=True, xxx=True, locale=True, name=True):
        """
        Try to create a Language instance having only some limited data about the Language.
        If no corresponding Language is found, a NotALanguageException is thrown.
        :param value: data known about the language as string
        :param xx: True if the value may be a locale
        :param xxx: True if the value may be a LanguageID
        :param locale: True if the value may be a locale
        :param name: True if the value may be a LanguageName
        :return: Language Instance if a matching Language was found
        """
        # Use 2 lists instead of dict ==> order known
        keys = ['ISO639', 'LanguageID', 'locale', 'LanguageName']
        truefalses = [xx, xxx, locale, name]
        for key, doKey in zip(keys, truefalses):
            if doKey:
                try:
                    return cls._from_XYZ(key, value)
                except:
                    pass
        raise NotALanguageException('Illegal language "{}"'.format(value))

    @classmethod
    def from_file(cls, filename, chunk_size=-1):
        """
        Try do determine the language of a text file.
        :param filename: string file path
        :param chunk_size: amount of bytes of file to read to determine language
        :return: Language instance if detection succeeded, otherwise a NotALanguageException is thrown
        """
        log.debug('Language.from_file: "{}", chunk={} ...'.format(filename, chunk_size))
        with open(filename, 'rb') as f:
            data = f.read(chunk_size)
        data_ascii = asciify(data)
        try:
            lang_xx = langdetect.detect(data_ascii)
            lang = cls.from_xx(lang_xx)
            log.debug('... Success: language={}'.format(lang))
            return lang
        except NotALanguageException:
            log.debug('... Failed: Detector returned unknown language "{}"'.format(lang_xx))
            raise
        except:
            log.debug('... Failed:  Language detector library failed')
            raise NotALanguageException('Could not detect language from subtitle content')


def ListAll_xx():
    temp = []
    for lang in LANGUAGES:
        temp.append(lang['ISO639'])
    return temp


def ListAll_xxx():
    temp = []
    for lang in LANGUAGES:
        temp.append(lang['LanguageID'])
    return temp


def ListAll_locale():
    temp = []
    for lang in LANGUAGES:
        temp.append(lang['locale'])
    return temp


def ListAll_names():
    temp = []
    for lang in LANGUAGES:
        temp.append(lang['LanguageName'])
    return temp


def xx2xxx(xx):
    for lang in LANGUAGES:
        if lang['ISO639'] == xx:
            return lang['LanguageID']


def xxx2xx(xxx):
    for lang in LANGUAGES:
        if lang['LanguageID'] == xxx:
            return lang['ISO639']


def xxx2name(xxx):
    for lang in LANGUAGES:
        if lang['LanguageID'] == xxx:
            return lang['LanguageName']


def locale2name(locale):
    for lang in LANGUAGES:
        if lang['locale'] == locale:
            return lang['LanguageName']


def xx2name(xx):
    for lang in LANGUAGES:
        if lang['ISO639'] == xx:
            return lang['LanguageName']


def name2xx(name):
    for lang in LANGUAGES:
        if lang['LanguageName'].lower() == name.lower():
            return lang['ISO639']


def name2xxx(name):
    for lang in LANGUAGES:
        if lang['LanguageName'].lower() == name.lower():
            return lang['LanguageID']


def CleanTagsFile(text):
    p = re.compile(b'<.*?>')
    return p.sub(b'', text)

"""
    List of dict of known languages.
"""
LANGUAGES = [
    {'locale': 'sq', 'ISO639': 'sq', 'LanguageID': 'alb',
        'LanguageName': _('Albanian')},
    {'locale': 'ar', 'ISO639': 'ar', 'LanguageID': 'ara',
        'LanguageName': _('Arabic')},
    {'locale': 'hy', 'ISO639': 'hy', 'LanguageID': 'arm',
        'LanguageName': _('Armenian')},
    {'locale': 'ms', 'ISO639': 'ms',
        'LanguageID': 'may', 'LanguageName': _('Malay')},
    {'locale': 'bs', 'ISO639': 'bs', 'LanguageID': 'bos',
        'LanguageName': _('Bosnian')},
    {'locale': 'bg', 'ISO639': 'bg', 'LanguageID': 'bul',
        'LanguageName': _('Bulgarian')},
    {'locale': 'ca', 'ISO639': 'ca', 'LanguageID': 'cat',
        'LanguageName': _('Catalan')},
    {'locale': 'eu', 'ISO639': 'eu', 'LanguageID': 'eus',
        'LanguageName': _('Basque')},
    {'locale': 'zh_CN', 'ISO639': 'zh', 'LanguageID': 'chi',
        'LanguageName': _('Chinese (China)')},
    {'locale': 'zh', 'ISO639': 'zh', 'LanguageID': 'zht',
        'LanguageName': _('Chinese (traditional)')},
    {'locale': 'hr', 'ISO639': 'hr', 'LanguageID': 'hrv',
        'LanguageName': _('Croatian')},
    {'locale': 'cs', 'ISO639': 'cs',
        'LanguageID': 'cze', 'LanguageName': _('Czech')},
    {'locale': 'da', 'ISO639': 'da', 'LanguageID': 'dan',
        'LanguageName': _('Danish')},
    {'locale': 'nl', 'ISO639': 'nl',
        'LanguageID': 'dut', 'LanguageName': _('Dutch')},
    {'locale': 'en', 'ISO639': 'en', 'LanguageID': 'eng',
        'LanguageName': _('English (US)')},
    {'locale': 'en_GB', 'ISO639': 'en', 'LanguageID': 'bre',
        'LanguageName': _('English (UK)')},
    {'locale': 'eo', 'ISO639': 'eo', 'LanguageID': 'epo',
        'LanguageName': _('Esperanto')},
    {'locale': 'et', 'ISO639': 'et', 'LanguageID': 'est',
        'LanguageName': _('Estonian')},
    {'locale': 'fi', 'ISO639': 'fi', 'LanguageID': 'fin',
        'LanguageName': _('Finnish')},
    {'locale': 'fr', 'ISO639': 'fr', 'LanguageID': 'fre',
        'LanguageName': _('French')},
    {'locale': 'gl', 'ISO639': 'gl', 'LanguageID': 'glg',
        'LanguageName': _('Galician')},
    {'locale': 'ka', 'ISO639': 'ka', 'LanguageID': 'geo',
        'LanguageName': _('Georgian')},
    {'locale': 'de', 'ISO639': 'de', 'LanguageID': 'ger',
        'LanguageName': _('German')},
    {'locale': 'el', 'ISO639': 'el',
        'LanguageID': 'ell', 'LanguageName': _('Greek')},
    {'locale': 'he', 'ISO639': 'he', 'LanguageID': 'heb',
        'LanguageName': _('Hebrew')},
    {'locale': 'hu', 'ISO639': 'hu', 'LanguageID': 'hun',
        'LanguageName': _('Hungarian')},
    {'locale': 'id', 'ISO639': 'id', 'LanguageID': 'ind',
        'LanguageName': _('Indonesian')},
    {'locale': 'it', 'ISO639': 'it', 'LanguageID': 'ita',
        'LanguageName': _('Italian')},
    {'locale': 'ja', 'ISO639': 'ja', 'LanguageID': 'jpn',
        'LanguageName': _('Japanese')},
    {'locale': 'kk', 'ISO639': 'kk', 'LanguageID': 'kaz',
        'LanguageName': _('Kazakh')},
    {'locale': 'ko', 'ISO639': 'ko', 'LanguageID': 'kor',
        'LanguageName': _('Korean')},
    {'locale': 'lv', 'ISO639': 'lv', 'LanguageID': 'lav',
        'LanguageName': _('Latvian')},
    {'locale': 'lt', 'ISO639': 'lt', 'LanguageID': 'lit',
        'LanguageName': _('Lithuanian')},
    {'locale': 'lb', 'ISO639': 'lb', 'LanguageID': 'ltz',
        'LanguageName': _('Luxembourgish')},
    {'locale': 'mk', 'ISO639': 'mk', 'LanguageID': 'mac',
        'LanguageName': _('Macedonian')},
    {'locale': 'no', 'ISO639': 'no', 'LanguageID': 'nor',
        'LanguageName': _('Norwegian')},
    {'locale': 'fa', 'ISO639': 'fa', 'LanguageID': 'per',
        'LanguageName': _('Persian')},
    {'locale': 'pl', 'ISO639': 'pl', 'LanguageID': 'pol',
        'LanguageName': _('Polish')},
    {'locale': 'pt_PT', 'ISO639': 'pt', 'LanguageID': 'por',
        'LanguageName': _('Portuguese (Portugal)')},
    {'locale': 'pt_BR', 'ISO639': 'pb', 'LanguageID': 'pob',
        'LanguageName': _('Portuguese (Brazil)')},
    {'locale': 'ro', 'ISO639': 'ro', 'LanguageID': 'rum',
        'LanguageName': _('Romanian')},
    {'locale': 'ru', 'ISO639': 'ru', 'LanguageID': 'rus',
        'LanguageName': _('Russian')},
    {'locale': 'sr', 'ISO639': 'sr', 'LanguageID': 'scc',
        'LanguageName': _('Serbian')},
    {'locale': 'sk', 'ISO639': 'sk', 'LanguageID': 'slo',
        'LanguageName': _('Slovak')},
    {'locale': 'sl', 'ISO639': 'sl', 'LanguageID': 'slv',
        'LanguageName': _('Slovenian')},
    {'locale': 'es_ES', 'ISO639': 'es', 'LanguageID': 'spa',
        'LanguageName': _('Spanish (Spain)')},
    {'locale': 'sv', 'ISO639': 'sv', 'LanguageID': 'swe',
        'LanguageName': _('Swedish')},
    {'locale': 'th', 'ISO639': 'th',
        'LanguageID': 'tha', 'LanguageName': _('Thai')},
    {'locale': 'tr', 'ISO639': 'tr', 'LanguageID': 'tur',
        'LanguageName': _('Turkish')},
    {'locale': 'uk', 'ISO639': 'uk', 'LanguageID': 'ukr',
        'LanguageName': _('Ukrainian')},
    {'locale': 'vi', 'ISO639': 'vi', 'LanguageID': 'vie',
        'LanguageName': _('Vietnamese')}]