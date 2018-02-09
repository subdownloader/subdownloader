# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import itertools
import logging

try:
    from langdetect import detect
    from langdetect.lang_detect_exception import LangDetectException
    def langdetect_detect(*args):
        try:
            return detect(*args)
        except LangDetectException:
            return UnknownLanguage.create_generic()
except ImportError:
    def langdetect_detect(*args):
        return UnknownLanguage.create_generic()

from subdownloader.util import asciify

log = logging.getLogger("subdownloader.languages.language")


class NotALanguageException(ValueError):
    """
    Exception to inform that some value is not a valid Language.
    """
    def __init__(self, value, message):
        ValueError.__init__(self, message)
        self._value = value

    @property
    def value(self):
        return self._value


# WORKAROUND:
# FOR: python 2 and pyQt5
# WHAT: Language subclasses str
# REASON: pyqtSignal apparently only accepts string or ASCII unicode.
# FIXES: TypeError: string or ASCII unicode expected not 'classobj'
class Language(str):
    """
    Instances of the class represent a language.
    """

    def __init__(self, lang_id):
        """
        Create a new Language object. Values should be strings.
        :param lang_id: index in LANGUAGES list of dicts having keys: ('locale', 'ISO639', 'LanguageID', 'LanguageName')
        """
        self._id = lang_id
        str.__init__(self)

    def locale(self):
        """
        Get locale of Language
        :return: locale as string
        """
        return LANGUAGES[self._id]['locale'][0]

    def xx(self):
        """
        Get ISO639 of Language
        :return: ISO639 as string
        """
        return LANGUAGES[self._id]['ISO639'][0]

    def xxx(self):
        """
        Get LanguageID of Language
        :return: LanguageID as string
        """
        return LANGUAGES[self._id]['LanguageID'][0]

    def name(self):
        """
        Return readable name of Language
        :return: Readable name as string
        """
        return _(LANGUAGES[self._id]['LanguageName'][0])

    def generic_name(self):
        """
        Return readable name of Language
        :return: Readable name as string
        """
        return self.name()

    def is_generic(self):
        return False

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
        return self.raw_data() == other.raw_data()

    def __hash__(self):
        """
        Return hash of this object.
        :return: hash integer
        """
        return hash(self._id)

    def __repr__(self):
        """
        Return string representation of this instance.
        :return: string representation of self
        """
        return '<Language:xx={}>'.format(LANGUAGES[self._id]['ISO639'][0])

    def __str__(self):
        """
        Return short string representation of this instance.
        :return: short string representation of self
        """
        return self.xx()

    def raw_data(self):
        """
        Return raw internal represenation of this instance.
        :return: raw internal representation
        """
        return self._id

    @classmethod
    def from_raw_data(cls, raw_data):
        """
        Return Language Instance from raw_data.
        :return: Language instance
        """
        if raw_data == 0:
            return UnknownLanguage.create_generic()
        return cls(raw_data)

    @classmethod
    def from_locale(cls, locale):
        """
        Create a new Language instance from a locale string
        :param locale: locale as string
        :return: Language instance with instance.locale() == locale if locale is valid else instance of Unknown Language
        """
        locale = str(locale)
        if locale is 'unknown':
            return UnknownLanguage(locale)
        try:
            return cls._from_xyz('locale', locale)
        except NotALanguageException:
            log.warning('Unknown locale: {}'.format(locale))
            return UnknownLanguage(locale)

    @classmethod
    def from_xx(cls, xx):
        """
        Create a new Language instance from a ISO639 string
        :param xx: ISO639 as string
        :return: Language instance with instance.xx() == xx if xx is valid else instance of UnknownLanguage
        """
        xx = str(xx).lower()
        if xx is 'unknown':
            return UnknownLanguage(xx)
        try:
            return cls._from_xyz('ISO639', xx)
        except NotALanguageException:
            log.warning('Unknown ISO639: {}'.format(xx))
            return UnknownLanguage(xx)

    @classmethod
    def from_xxx(cls, xxx):
        """
        Create a new Language instance from a LanguageID string
        :param xxx: LanguageID as string
        :return: Language instance with instance.xxx() == xxx if xxx is valid else instance of UnknownLanguage
        """
        xxx = str(xxx).lower()
        if xxx is 'unknown':
            return UnknownLanguage(xxx)
        try:
            return cls._from_xyz('LanguageID', xxx)
        except NotALanguageException:
            log.warning('Unknown LanguageId: {}'.format(xxx))
            return UnknownLanguage(xxx)

    @classmethod
    def from_name(cls, name):
        """
        Create a new Language instance from a name as string
        :param name: name as string
        :return: Language instance with instance.name() == name if name is valid else instance of UnknownLanguage
        """
        name = str(name).lower()
        if name is 'unknown' or name is _('unknown'):
            return UnknownLanguage(name)
        try:
            return cls._from_xyz('LanguageName', name)
        except NotALanguageException:
            log.warning('Unknown LanguageName: {}'.format(name))
            return UnknownLanguage(name)

    @classmethod
    def _from_xyz(cls, xyzkey, xyzvalue):
        """
        Private helper function to create new Language instance.
        :param xyzkey: one of ('locale', 'ISO639', 'LanguageID', 'LanguageName')
        :param xyzvalue: corresponding value of xyzkey
        :return: Language instance
        """
        if xyzvalue == 'unknown' or xyzvalue == _('unknown'):
            return UnknownLanguage(xyzvalue)
        for lang_id, lang_data in enumerate(LANGUAGES):
            for data_value in lang_data[xyzkey]:
                if xyzvalue == data_value.lower():
                    return cls(lang_id)
        raise NotALanguageException(xyzvalue, 'Illegal language {}: {}'.format(xyzkey, xyzvalue))

    @classmethod
    def from_unknown(cls, value, xx=False, xxx=False, locale=False, name=False):
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
        value = value.lower()
        for key, doKey in zip(keys, truefalses):
            if doKey:
                try:
                    return cls._from_xyz(key, value)
                except NotALanguageException:
                    pass
        raise NotALanguageException(value, 'Illegal language "{}"'.format(value))

    @classmethod
    def from_file(cls, filepath, chunk_size=None):
        """
        Try do determine the language of a text file.
        :param filepath: string file path
        :param chunk_size: amount of bytes of file to read to determine language
        :return: Language instance if detection succeeded, otherwise return UnknownLanguage
        """
        log.debug('Language.from_file: "{}", chunk={} ...'.format(filepath, chunk_size))
        with filepath.open('rb') as f:
            data = f.read(-1 if chunk_size is None else chunk_size)
        data_ascii = asciify(data)
        lang_xx = langdetect_detect(data_ascii)
        lang = cls.from_xx(lang_xx)
        log.debug('... result language={}'.format(lang))
        return lang


class UnknownLanguage(Language):
    def __init__(self, code):
        Language.__init__(self, 0)
        self._code = code

    # FIXME: better name for & check generic logic

    @classmethod
    def create_generic(cls):
        """
        Return a UnknownLanguage instance..
        :return: UnknownLanguage instance.
        """
        return cls('unknown')  # NO internationalization!

    def name(self):
        """
        Return readable name of Language. Contains info about the unknown Language.
        :return: Readable name as string
        """
        return _(self._code)

    def generic_name(self):
        """
        Return readable name of Language. Contains no info about the unknown Language.
        :return: Readable name as string
        """
        return Language.name(self)

    def is_generic(self):
        return self._code == 'unknown'  # NO internationalization!

    def __eq__(self, other):
        """
        Tests if other has the same type of this and the same unknown language code.
        :return: True if other is of the same type and has the same unknown language code
        """
        if not Language.__eq__(self, other):
            return False
        return self._code == other._code

    def __hash__(self):
        """
        Return hash of this object.
        :return: hash integer
        """
        return hash((self._id, self._code))

    def __repr__(self):
        """
        Return representation of this instance
        :return: string representation of self
        """
        return '<UnknownLanguage:code={code}>'.format(code=self._code)


def name2xxx(name):
    for lang in LANGUAGES:
        if lang['LanguageName'][0].lower() == name.lower():
            return lang['LanguageID'][0]


def legal_languages():
    """
    Return an iterator of all Language objects excluding the UnknownLanguage
    :return: iterator of Language objects
    """
    return map(Language, range(1, len(LANGUAGES)))


def all_languages():
    """
    Return an iterator of all Language objects, including the UnknownLanguage
    :return: iterator of all Language objects
    """
    return itertools.chain([UnknownLanguage.create_generic()], legal_languages())


# FIXME: translation..
def _(text):
    return text


"""
    List of dict of languages.
    The unknown language is at index 0.
"""

LANGUAGES = [
    {
        'locale': ['unknown'],
        'ISO639': ['unknown'],
        'LanguageID': ['unknown'],
        'LanguageName': [_('Unknown')]
    }, {
        'locale': ['sq'],
        'ISO639': ['sq'],
        'LanguageID': ['alb'],
        'LanguageName': [_('Albanian')]
    }, {
        'locale': ['ar'],
        'ISO639': ['ar'],
        'LanguageID': ['ara'],
        'LanguageName': [_('Arabic')]
    }, {
        'locale': ['hy'],
        'ISO639': ['hy'],
        'LanguageID': ['arm'],
        'LanguageName': [_('Armenian')]
    }, {
        'locale': ['ms'],
        'ISO639': ['ms'],
        'LanguageID': ['may'],
        'LanguageName': [_('Malay')]
    }, {
        'locale': ['bs'],
        'ISO639': ['bs'],
        'LanguageID': ['bos'],
        'LanguageName': [_('Bosnian')]
    }, {
        'locale': ['bg'],
        'ISO639': ['bg'],
        'LanguageID': ['bul'],
        'LanguageName': [_('Bulgarian')]
    }, {
        'locale': ['ca'],
        'ISO639': ['ca'],
        'LanguageID': ['cat'],
        'LanguageName': [_('Catalan')]
    }, {
        'locale': ['eu'],
        'ISO639': ['eu'],
        'LanguageID': ['eus'],
        'LanguageName': [_('Basque')]
    }, {
        'locale': ['zh_CN'],
        'ISO639': ['zh'],
        'LanguageID': ['chi'],
        'LanguageName': [_('Chinese (China)')]
    }, {
        'locale': ['zh', 'zt'],
        'ISO639': ['zh', 'zt'],
        'LanguageID': ['zht'],
        'LanguageName': [_('Chinese (traditional)')]
    }, {
        'locale': ['hr'],
        'ISO639': ['hr'],
        'LanguageID': ['hrv'],
        'LanguageName': [_('Croatian')]
    }, {
        'locale': ['cs'],
        'ISO639': ['cs'],
        'LanguageID': ['cze'],
        'LanguageName': [_('Czech')]
    }, {
        'locale': ['da'],
        'ISO639': ['da'],
        'LanguageID': ['dan'],
        'LanguageName': [_('Danish')]
    }, {
        'locale': ['nl'],
        'ISO639': ['nl'],
        'LanguageID': ['dut'],
        'LanguageName': [_('Dutch')]
    }, {
        'locale': ['en'],
        'ISO639': ['en'],
        'LanguageID': ['eng'],
        'LanguageName': [_('English (US)')]
    }, {
        'locale': ['en_GB'],
        'ISO639': ['en'],
        'LanguageID': ['bre'],
        'LanguageName': [_('English (UK)')]
    }, {
        'locale': ['eo'],
        'ISO639': ['eo'],
        'LanguageID': ['epo'],
        'LanguageName': [_('Esperanto')]
    }, {
        'locale': ['et'],
        'ISO639': ['et'],
        'LanguageID': ['est'],
        'LanguageName': [_('Estonian')]
    }, {
        'locale': ['fi'],
        'ISO639': ['fi'],
        'LanguageID': ['fin'],
        'LanguageName': [_('Finnish')]
    }, {
        'locale': ['fr'],
        'ISO639': ['fr'],
        'LanguageID': ['fre'],
        'LanguageName': [_('French')]
    }, {
        'locale': ['gl'],
        'ISO639': ['gl'],
        'LanguageID': ['glg'],
        'LanguageName': [_('Galician')]
    }, {
        'locale': ['ka'],
        'ISO639': ['ka'],
        'LanguageID': ['geo'],
        'LanguageName': [_('Georgian')]
    }, {
        'locale': ['de'],
        'ISO639': ['de'],
        'LanguageID': ['ger'],
        'LanguageName': [_('German')]
    }, {
        'locale': ['el', 'gr'],
        'ISO639': ['el', 'gr'],
        'LanguageID': ['ell'],
        'LanguageName': [_('Greek')]
    }, {
        'locale': ['he'],
        'ISO639': ['he'],
        'LanguageID': ['heb'],
        'LanguageName': [_('Hebrew')]
    }, {
        'locale': ['hu'],
        'ISO639': ['hu'],
        'LanguageID': ['hun'],
        'LanguageName': [_('Hungarian')]
    }, {
        'locale': ['id'],
        'ISO639': ['id'],
        'LanguageID': ['ind'],
        'LanguageName': [_('Indonesian')]
    }, {
        'locale': ['it'],
        'ISO639': ['it'],
        'LanguageID': ['ita'],
        'LanguageName': [_('Italian')]
    }, {
        'locale': ['ja'],
        'ISO639': ['ja'],
        'LanguageID': ['jpn'],
        'LanguageName': [_('Japanese')]
    }, {
        'locale': ['kk'],
        'ISO639': ['kk'],
        'LanguageID': ['kaz'],
        'LanguageName': [_('Kazakh')]
    }, {
        'locale': ['ko'],
        'ISO639': ['ko'],
        'LanguageID': ['kor'],
        'LanguageName': [_('Korean')]
    }, {
        'locale': ['lv'],
        'ISO639': ['lv'],
        'LanguageID': ['lav'],
        'LanguageName': [_('Latvian')]
    }, {
        'locale': ['lt'],
        'ISO639': ['lt'],
        'LanguageID': ['lit'],
        'LanguageName': [_('Lithuanian')]
    }, {
        'locale': ['lb'],
        'ISO639': ['lb'],
        'LanguageID': ['ltz'],
        'LanguageName': [_('Luxembourgish')]
    }, {
        'locale': ['mk'],
        'ISO639': ['mk'],
        'LanguageID': ['mac'],
        'LanguageName': [_('Macedonian')]
    }, {
        'locale': ['no'],
        'ISO639': ['no'],
        'LanguageID': ['nor'],
        'LanguageName': [_('Norwegian')]
    }, {
        'locale': ['oc'],
        'ISO639': ['oc'],
        'LanguageID': ['oci'],
        'LanguageName': [_('Occitan')]
    }, {
        'locale': ['fa'],
        'ISO639': ['fa'],
        'LanguageID': ['per'],
        'LanguageName': [_('Persian')]
    }, {
        'locale': ['pl'],
        'ISO639': ['pl'],
        'LanguageID': ['pol'],
        'LanguageName': [_('Polish')]
    }, {
        'locale': ['pt_PT', 'pt'],
        'ISO639': ['pt'],
        'LanguageID': ['por'],
        'LanguageName': [_('Portuguese (Portugal)')]
    }, {
        'locale': ['pt_BR'],
        'ISO639': ['pb'],
        'LanguageID': ['pob'],
        'LanguageName': [_('Portuguese (Brazil)')]
    }, {
        'locale': ['ro'],
        'ISO639': ['ro'],
        'LanguageID': ['rum'],
        'LanguageName': [_('Romanian')]
    }, {
        'locale': ['ru'],
        'ISO639': ['ru'],
        'LanguageID': ['rus'],
        'LanguageName': [_('Russian')]
    }, {
        'locale': ['sr'],
        'ISO639': ['sr'],
        'LanguageID': ['scc'],
        'LanguageName': [_('Serbian')]
    }, {
        'locale': ['sk'],
        'ISO639': ['sk'],
        'LanguageID': ['slo'],
        'LanguageName': [_('Slovak')]
    }, {
        'locale': ['sl'],
        'ISO639': ['sl'],
        'LanguageID': ['slv'],
        'LanguageName': [_('Slovenian')]
    }, {
        'locale': ['es_ES'],
        'ISO639': ['es'],
        'LanguageID': ['spa'],
        'LanguageName': [_('Spanish (Spain)')]
    }, {
        'locale': ['sv'],
        'ISO639': ['sv'],
        'LanguageID': ['swe'],
        'LanguageName': [_('Swedish')]
    }, {
        'locale': ['th'],
        'ISO639': ['th'],
        'LanguageID': ['tha'],
        'LanguageName': [_('Thai')]
    }, {
        'locale': ['tr'],
        'ISO639': ['tr'],
        'LanguageID': ['tur'],
        'LanguageName': [_('Turkish')]
    }, {
        'locale': ['uk'],
        'ISO639': ['uk'],
        'LanguageID': ['ukr'],
        'LanguageName': [_('Ukrainian')]
    }, {
        'locale': ['vi'],
        'ISO639': ['vi'],
        'LanguageID': ['vie'],
        'LanguageName': [_('Vietnamese')]
    }
]

del _
