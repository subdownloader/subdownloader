#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Copyright (C) 2007 Ivan Garcia capiscuas@gmail.com
##    This program is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License along
##    with this program; if not, write to the Free Software Foundation, Inc.,
##    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import languages.autodetect_lang as autodetect_lang
import re
import os.path
import logging
log = logging.getLogger("subdownloader.languages.Languages")
import  __builtin__
__builtin__._ = lambda x : x

LANGUAGES = [{'ISO639': 'sq', 'SubLanguageID': 'alb', 'LanguageName': _('Albanian')},
 {'ISO639': 'ar', 'SubLanguageID': 'ara', 'LanguageName': _('Arabic')},
 {'ISO639': 'hy', 'SubLanguageID': 'arm', 'LanguageName': _('Armenian')},
 {'ISO639': 'ay', 'SubLanguageID': 'ass', 'LanguageName': _('Assyrian')},
 {'ISO639': 'ms', 'SubLanguageID': 'may', 'LanguageName': _('Malayalam')},
 {'ISO639': 'bs', 'SubLanguageID': 'bos', 'LanguageName': _('Bosnian')},
 {'ISO639': 'pb', 'SubLanguageID': 'pob', 'LanguageName': _('Brazilian')}, #TODO: some ISO639 call it 'bp', check, maybe local pt_BR
 {'ISO639': 'bg', 'SubLanguageID': 'bul', 'LanguageName': _('Bulgarian')},
 {'ISO639': 'ca', 'SubLanguageID': 'cat', 'LanguageName': _('Catalan')},
 {'ISO639': 'zh', 'SubLanguageID': 'chi', 'LanguageName': _('Chinese')},
 {'ISO639': 'hr', 'SubLanguageID': 'hrv', 'LanguageName': _('Croatian')},
 {'ISO639': 'cs', 'SubLanguageID': 'cze', 'LanguageName': _('Czech')},
 {'ISO639': 'da', 'SubLanguageID': 'dan', 'LanguageName': _('Danish')},
 {'ISO639': 'nl', 'SubLanguageID': 'dut', 'LanguageName': _('Dutch')},
 {'ISO639': 'en', 'SubLanguageID': 'eng', 'LanguageName': _('English')},
 {'ISO639': 'et', 'SubLanguageID': 'est', 'LanguageName': _('Estonian')},
 {'ISO639': 'fi', 'SubLanguageID': 'fin', 'LanguageName': _('Finnish')},
 {'ISO639': 'fr', 'SubLanguageID': 'fre', 'LanguageName': _('French')},
 {'ISO639': 'ka', 'SubLanguageID': 'geo', 'LanguageName': _('Georgian')},
 {'ISO639': 'de', 'SubLanguageID': 'ger', 'LanguageName': _('German')},
 {'ISO639': 'el', 'SubLanguageID': 'ell', 'LanguageName': _('Greek')},
 {'ISO639': 'he', 'SubLanguageID': 'heb', 'LanguageName': _('Hebrew')},
 {'ISO639': 'hu', 'SubLanguageID': 'hun', 'LanguageName': _('Hungarian')},
 {'ISO639': 'id', 'SubLanguageID': 'ind', 'LanguageName': _('Indonesian')},
 {'ISO639': 'it', 'SubLanguageID': 'ita', 'LanguageName': _('Italian')},
 {'ISO639': 'ja', 'SubLanguageID': 'jpn', 'LanguageName': _('Japanese')},
 {'ISO639': 'kk', 'SubLanguageID': 'kaz', 'LanguageName': _('Kazakh')},
 {'ISO639': 'ko', 'SubLanguageID': 'kor', 'LanguageName': _('Korean')},
 {'ISO639': 'lv', 'SubLanguageID': 'lav', 'LanguageName': _('Latvian')},
 {'ISO639': 'lt', 'SubLanguageID': 'lit', 'LanguageName': _('Lithuanian')},
 {'ISO639': 'lb', 'SubLanguageID': 'ltz', 'LanguageName': _('Luxembourgish')},
 {'ISO639': 'mk', 'SubLanguageID': 'mac', 'LanguageName': _('Macedonian')},
 {'ISO639': 'no', 'SubLanguageID': 'nor', 'LanguageName': _('Norwegian')},
 {'ISO639': 'fa', 'SubLanguageID': 'per', 'LanguageName': _('Persian')},
 {'ISO639': 'pl', 'SubLanguageID': 'pol', 'LanguageName': _('Polish')},
 {'ISO639': 'pt', 'SubLanguageID': 'por', 'LanguageName': _('Portuguese')},
 {'ISO639': 'ro', 'SubLanguageID': 'rum', 'LanguageName': _('Romanian')},
 {'ISO639': 'ru', 'SubLanguageID': 'rus', 'LanguageName': _('Russian')},
 {'ISO639': 'sr', 'SubLanguageID': 'scc', 'LanguageName': _('Serbian')},
 {'ISO639': 'sk', 'SubLanguageID': 'slo', 'LanguageName': _('Slovak')},
 {'ISO639': 'sl', 'SubLanguageID': 'slv', 'LanguageName': _('Slovenian')},
 {'ISO639': 'es', 'SubLanguageID': 'spa', 'LanguageName': _('Spanish')},
 {'ISO639': 'sv', 'SubLanguageID': 'swe', 'LanguageName': _('Swedish')},
 {'ISO639': 'th', 'SubLanguageID': 'tha', 'LanguageName': _('Thai')},
 {'ISO639': 'tr', 'SubLanguageID': 'tur', 'LanguageName': _('Turkish')},
 {'ISO639': 'uk', 'SubLanguageID': 'ukr', 'LanguageName': _('Ukrainian')},
 {'ISO639': 'vi', 'SubLanguageID': 'vie', 'LanguageName': _('Vietnamese')}]

def ListAll_xx():
    temp = []
    for lang in LANGUAGES:
        temp.append(lang['ISO639'])
    return temp

def ListAll_xxx():
    temp = []
    for lang in LANGUAGES:
        temp.append(lang['SubLanguageID'])
    return temp

def ListAll_names():
    temp = []
    for lang in LANGUAGES:
        temp.append(lang['LanguageName'])
    return temp

def xx2xxx(xx):
    for lang in LANGUAGES:
        if lang['ISO639'] == xx:
            return lang['SubLanguageID']
def xxx2xx(xxx):
    for lang in LANGUAGES:
        if lang['SubLanguageID'] == xxx:
            return lang['ISO639']
                
def xxx2name(xxx):
    for lang in LANGUAGES:
        if lang['SubLanguageID'] == xxx:
            return lang['LanguageName'].lower()
            
def xx2name(xx):
    for lang in LANGUAGES:
        if lang['ISO639'] == xx:
            return lang['LanguageName'].lower()
    
def name2xx(name):
    for lang in LANGUAGES:
        if lang['LanguageName'].lower() == name.lower():
            return lang['ISO639']

def name2xxx(name):
    for lang in LANGUAGES:
        if lang['LanguageName'].lower() == name.lower():
            return lang['SubLanguageID']
        
def CleanTagsFile(text):
    p = re.compile( '<.*?>')
    return p.sub('',text)
