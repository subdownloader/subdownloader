# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import re
import os.path
import logging

log = logging.getLogger("subdownloader.languages.Languages")

#FIXME: translation..
_ = lambda x: x


class NotALanguageException(ValueError):
    """
    Exception to inform that some value is not a valid Language.
    """
    pass


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