#if 0
# -----------------------------------------------------------------------
# $Id: table.py,v 1.9 2004/05/28 12:26:24 dischi Exp $
# -----------------------------------------------------------------------
# $Log: table.py,v $
# Revision 1.9  2004/05/28 12:26:24  dischi
# Replace __str__ with unicode to avoid bad transformations. Everything
# inside mmpython should be handled as unicode object.
#
# Revision 1.8  2003/07/02 11:17:29  the_krow
# language is now part of the table key
#
# -----------------------------------------------------------------------
# MMPython - Media Metadata for Python
# Copyright (C) 2003 Thomas Schueppel, Dirk Meyer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
# 
# -----------------------------------------------------------------------
#endif

from gettext import GNUTranslations
import os

LOCALEDIR = 'i18n'

class Table:
    def __init__(self, hashmap, name, language='en'):
        self.dict = hashmap
        self.name = name
        self.language = language
        self.translations = {}
        self.languages = []
        self.i18ndir = os.path.join(LOCALEDIR, name.lower())
        try:
            self.read_translations()
        except:
            pass
    
    def read_translations(self):
        for filename in [x for x in os.listdir(self.i18ndir) if x.endswith('.mo')]:
            lang = filename[:-3]
            filename = os.path.join(self.i18ndir, filename)
            f = open(filename, 'rb')
            self.translations[lang] = GNUTranslations(f)
            f.close()
        self.languages = self.translations.keys()
        
    def gettext(self, message, language = None):
        try:
            return self.translations[language].gettext(unicode(message))
        except KeyError:
            return unicode(message)
        
    def __setitem__(self,key,value):
        self.dict[key] = value
        
    def __getitem__(self,key):
        try:
            return self.dict[key]
        except KeyError:
            return None
         
    def getstr(self,key):
        s = self[key]
        try:
            if s and len(unicode(s)) < 100: 
                return s
            else:
                return "Not Displayable"
        except UnicodeDecodeError:
            return "Not Displayable"
         
    def has_key(self, key):
        return self.dict.has_key(key)    
    
    def getEntry(self, key, language = 'en'):
        pair = (self.gettext(key), unicode(self.dict[key]))
    
    def __unicode__(self):
        header = "\nTable %s (%s):" % (self.name, self.language)
        result = reduce( lambda a,b: self[b] and "%s\n        %s: %s" % \
                         (a, self.gettext(b,'en'), self.getstr(b)) or \
                         a, self.dict.keys(), header )
        return result

    def accept(self,mi):
        pass
