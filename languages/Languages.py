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

LANGUAGES = [{'locale':'sq', 'ISO639': 'sq', 'SubLanguageID': 'alb', 'LanguageName': _('Albanian')},
 {'locale':'ar', 'ISO639': 'ar', 'SubLanguageID': 'ara', 'LanguageName': _('Arabic')},
 {'locale':'hy', 'ISO639': 'hy', 'SubLanguageID': 'arm', 'LanguageName': _('Armenian')},
 {'locale':'ms', 'ISO639': 'ms', 'SubLanguageID': 'may', 'LanguageName': _('Malay')},
 {'locale':'bs', 'ISO639': 'bs', 'SubLanguageID': 'bos', 'LanguageName': _('Bosnian')},
 {'locale':'pt_BR', 'ISO639': 'pb', 'SubLanguageID': 'pob', 'LanguageName': _('Brazilian')}, 
 {'locale':'bg', 'ISO639': 'bg', 'SubLanguageID': 'bul', 'LanguageName': _('Bulgarian')},
 {'locale':'ca', 'ISO639': 'ca', 'SubLanguageID': 'cat', 'LanguageName': _('Catalan')},
 {'locale':'eu', 'ISO639': 'eu', 'SubLanguageID': 'eus', 'LanguageName': _('Basque')},
 {'locale':'zh_CN', 'ISO639': 'zh', 'SubLanguageID': 'chi', 'LanguageName': _('Chinese')},
 {'locale':'hr', 'ISO639': 'hr', 'SubLanguageID': 'hrv', 'LanguageName': _('Croatian')},
 {'locale':'cs', 'ISO639': 'cs', 'SubLanguageID': 'cze', 'LanguageName': _('Czech')},
 {'locale':'da', 'ISO639': 'da', 'SubLanguageID': 'dan', 'LanguageName': _('Danish')},
 {'locale':'nl', 'ISO639': 'nl', 'SubLanguageID': 'dut', 'LanguageName': _('Dutch')},
 {'locale':'en', 'ISO639': 'en', 'SubLanguageID': 'eng', 'LanguageName': _('English')},
 {'locale':'en_GB', 'ISO639': 'en', 'SubLanguageID': 'eng', 'LanguageName': _('British English')},
 {'locale':'eo', 'ISO639': 'eo', 'SubLanguageID': 'epo', 'LanguageName': _('Esperanto')},
 {'locale':'et', 'ISO639': 'et', 'SubLanguageID': 'est', 'LanguageName': _('Estonian')},
 {'locale':'fi', 'ISO639': 'fi', 'SubLanguageID': 'fin', 'LanguageName': _('Finnish')},
 {'locale':'fr', 'ISO639': 'fr', 'SubLanguageID': 'fre', 'LanguageName': _('French')},
 {'locale':'ka', 'ISO639': 'ka', 'SubLanguageID': 'geo', 'LanguageName': _('Georgian')},
 {'locale':'de', 'ISO639': 'de', 'SubLanguageID': 'ger', 'LanguageName': _('German')},
 {'locale':'el', 'ISO639': 'el', 'SubLanguageID': 'ell', 'LanguageName': _('Greek')},
 {'locale':'he', 'ISO639': 'he', 'SubLanguageID': 'heb', 'LanguageName': _('Hebrew')},
 {'locale':'hu', 'ISO639': 'hu', 'SubLanguageID': 'hun', 'LanguageName': _('Hungarian')},
 {'locale':'id', 'ISO639': 'id', 'SubLanguageID': 'ind', 'LanguageName': _('Indonesian')},
 {'locale':'it', 'ISO639': 'it', 'SubLanguageID': 'ita', 'LanguageName': _('Italian')},
 {'locale':'ja', 'ISO639': 'ja', 'SubLanguageID': 'jpn', 'LanguageName': _('Japanese')},
 {'locale':'kk', 'ISO639': 'kk', 'SubLanguageID': 'kaz', 'LanguageName': _('Kazakh')},
 {'locale':'ko', 'ISO639': 'ko', 'SubLanguageID': 'kor', 'LanguageName': _('Korean')},
 {'locale':'lv', 'ISO639': 'lv', 'SubLanguageID': 'lav', 'LanguageName': _('Latvian')},
 {'locale':'lt', 'ISO639': 'lt', 'SubLanguageID': 'lit', 'LanguageName': _('Lithuanian')},
 {'locale':'lb', 'ISO639': 'lb', 'SubLanguageID': 'ltz', 'LanguageName': _('Luxembourgish')},
 {'locale':'mk', 'ISO639': 'mk', 'SubLanguageID': 'mac', 'LanguageName': _('Macedonian')},
 {'locale':'no', 'ISO639': 'no', 'SubLanguageID': 'nor', 'LanguageName': _('Norwegian')},
 {'locale':'fa', 'ISO639': 'fa', 'SubLanguageID': 'per', 'LanguageName': _('Persian')},
 {'locale':'pl', 'ISO639': 'pl', 'SubLanguageID': 'pol', 'LanguageName': _('Polish')},
 {'locale':'pt', 'ISO639': 'pt', 'SubLanguageID': 'por', 'LanguageName': _('Portuguese')},
 {'locale':'ro', 'ISO639': 'ro', 'SubLanguageID': 'rum', 'LanguageName': _('Romanian')},
 {'locale':'ru', 'ISO639': 'ru', 'SubLanguageID': 'rus', 'LanguageName': _('Russian')},
 {'locale':'sr', 'ISO639': 'sr', 'SubLanguageID': 'scc', 'LanguageName': _('Serbian')},
 {'locale':'sk', 'ISO639': 'sk', 'SubLanguageID': 'slo', 'LanguageName': _('Slovak')},
 {'locale':'sl', 'ISO639': 'sl', 'SubLanguageID': 'slv', 'LanguageName': _('Slovenian')},
 {'locale':'es', 'ISO639': 'es', 'SubLanguageID': 'spa', 'LanguageName': _('Spanish')},
 {'locale':'sv', 'ISO639': 'sv', 'SubLanguageID': 'swe', 'LanguageName': _('Swedish')},
 {'locale':'th', 'ISO639': 'th', 'SubLanguageID': 'tha', 'LanguageName': _('Thai')},
 {'locale':'tr', 'ISO639': 'tr', 'SubLanguageID': 'tur', 'LanguageName': _('Turkish')},
 {'locale':'uk', 'ISO639': 'uk', 'SubLanguageID': 'ukr', 'LanguageName': _('Ukrainian')},
 {'locale':'vi', 'ISO639': 'vi', 'SubLanguageID': 'vie', 'LanguageName': _('Vietnamese')}]

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
            return lang['SubLanguageID']
def xxx2xx(xxx):
    for lang in LANGUAGES:
        if lang['SubLanguageID'] == xxx:
            return lang['ISO639']
                
def xxx2name(xxx):
    for lang in LANGUAGES:
        if lang['SubLanguageID'] == xxx:
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
            return lang['SubLanguageID']
        
def CleanTagsFile(text):
    p = re.compile( '<.*?>')
    return p.sub('',text)
