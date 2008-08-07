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

LANGUAGES = [{'ISO639': 'sq', 'SubLanguageID': 'alb', 'LanguageName': 'Albanian'},
 {'ISO639': 'ar', 'SubLanguageID': 'ara', 'LanguageName': 'Arabic'},
 {'ISO639': 'hy', 'SubLanguageID': 'arm', 'LanguageName': 'Armenian'},
 {'ISO639': 'ay', 'SubLanguageID': 'ass', 'LanguageName': 'Assyrian'},
 {'ISO639': 'bs', 'SubLanguageID': 'bos', 'LanguageName': 'Bosnian'},
 {'ISO639': 'pb', 'SubLanguageID': 'pob', 'LanguageName': 'Brazilian'},
 {'ISO639': 'bg', 'SubLanguageID': 'bul', 'LanguageName': 'Bulgarian'},
 {'ISO639': 'ca', 'SubLanguageID': 'cat', 'LanguageName': 'Catalan'},
 {'ISO639': 'zh', 'SubLanguageID': 'chi', 'LanguageName': 'Chinese'},
 {'ISO639': 'hr', 'SubLanguageID': 'hrv', 'LanguageName': 'Croatian'},
 {'ISO639': 'cs', 'SubLanguageID': 'cze', 'LanguageName': 'Czech'},
 {'ISO639': 'da', 'SubLanguageID': 'dan', 'LanguageName': 'Danish'},
 {'ISO639': 'nl', 'SubLanguageID': 'dut', 'LanguageName': 'Dutch'},
 {'ISO639': 'en', 'SubLanguageID': 'eng', 'LanguageName': 'English'},
 {'ISO639': 'et', 'SubLanguageID': 'est', 'LanguageName': 'Estonian'},
 {'ISO639': 'fi', 'SubLanguageID': 'fin', 'LanguageName': 'Finnish'},
 {'ISO639': 'fr', 'SubLanguageID': 'fre', 'LanguageName': 'French'},
 {'ISO639': 'ka', 'SubLanguageID': 'geo', 'LanguageName': 'Georgian'},
 {'ISO639': 'de', 'SubLanguageID': 'ger', 'LanguageName': 'German'},
 {'ISO639': 'el', 'SubLanguageID': 'ell', 'LanguageName': 'Greek'},
 {'ISO639': 'he', 'SubLanguageID': 'heb', 'LanguageName': 'Hebrew'},
 {'ISO639': 'hu', 'SubLanguageID': 'hun', 'LanguageName': 'Hungarian'},
 {'ISO639': 'id', 'SubLanguageID': 'ind', 'LanguageName': 'Indonesian'},
 {'ISO639': 'it', 'SubLanguageID': 'ita', 'LanguageName': 'Italian'},
 {'ISO639': 'ja', 'SubLanguageID': 'jpn', 'LanguageName': 'Japanese'},
 {'ISO639': 'kk', 'SubLanguageID': 'kaz', 'LanguageName': 'Kazakh'},
 {'ISO639': 'ko', 'SubLanguageID': 'kor', 'LanguageName': 'Korean'},
 {'ISO639': 'lv', 'SubLanguageID': 'lav', 'LanguageName': 'Latvian'},
 {'ISO639': 'lt', 'SubLanguageID': 'lit', 'LanguageName': 'Lithuanian'},
 {'ISO639': 'lb', 'SubLanguageID': 'ltz', 'LanguageName': 'Luxembourgish'},
 {'ISO639': 'mk', 'SubLanguageID': 'mac', 'LanguageName': 'Macedonian'},
 {'ISO639': 'no', 'SubLanguageID': 'nor', 'LanguageName': 'Norwegian'},
 {'ISO639': 'fa', 'SubLanguageID': 'per', 'LanguageName': 'Persian'},
 {'ISO639': 'pl', 'SubLanguageID': 'pol', 'LanguageName': 'Polish'},
 {'ISO639': 'pt', 'SubLanguageID': 'por', 'LanguageName': 'Portuguese'},
 {'ISO639': 'ro', 'SubLanguageID': 'rum', 'LanguageName': 'Romanian'},
 {'ISO639': 'ru', 'SubLanguageID': 'rus', 'LanguageName': 'Russian'},
 {'ISO639': 'sr', 'SubLanguageID': 'scc', 'LanguageName': 'Serbian'},
 {'ISO639': 'sk', 'SubLanguageID': 'slo', 'LanguageName': 'Slovak'},
 {'ISO639': 'sl', 'SubLanguageID': 'slv', 'LanguageName': 'Slovenian'},
 {'ISO639': 'es', 'SubLanguageID': 'spa', 'LanguageName': 'Spanish'},
 {'ISO639': 'sv', 'SubLanguageID': 'swe', 'LanguageName': 'Swedish'},
 {'ISO639': 'th', 'SubLanguageID': 'tha', 'LanguageName': 'Thai'},
 {'ISO639': 'tr', 'SubLanguageID': 'tur', 'LanguageName': 'Turkish'},
 {'ISO639': 'uk', 'SubLanguageID': 'ukr', 'LanguageName': 'Ukrainian'},
 {'ISO639': 'vi', 'SubLanguageID': 'vie', 'LanguageName': 'Vietnamese'}]

def ListAll_xx():
    temp = []
    for lang in LANGUAGES:
        temp.append(lang['ISO639'])
    return temp

def ListAll_xxx():
    temp = []
    for lang in LANGUAGES:
        temp.append(lang['ISO639'])
    return temp

def ListAll_names():
    temp = []
    for lang in LANGUAGES:
        temp.append(lang['ISO639'])
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

#def AutoDetectLang(filepath):
#    if filepath.endswith("sub") or filepath.endswith("srt") or filepath.endswith("txt"):
#        subtitle_content = file(filepath,mode='rb').read()
#        
#        subtitle_content = CleanTagsFile(subtitle_content)
#        
#        n = autodetect_lang._NGram()
#        #FIXME: The LM path should depend the subdownloader path, not from the CWD 
#        l = autodetect_lang.NGram(os.path.join(os.getcwd(),'languages','lm'))
#        #print subtitle_content
#        percentage, lang = l.classify(subtitle_content)
#        log.debug('Autodetected file %s: %s, value: %s'% (filepath, lang, percentage))
#        pos = lang.rfind("-")
#        if pos != -1:
#            return lang[:pos]
#        else:
#            return lang
#    else:
#        return ""
