#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Copyright (C) 2007 Ivan Garcia contact@ivangarcia.org
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


import os
import md5
import subdownloader.languages.Languages as languages

SUBTITLES_EXT = ["srt","sub","txt","ssa"]
SELECT_SUBTITLES = "Subtitle Files (*.%s)"% " *.".join(SUBTITLES_EXT)

class SubtitleFile(object):
    """Contains the class that represents a SubtitleFile (SRT,SUB,etc)
    and provides easy methods to retrieve its attributes (Sizebytes, HASH, Validation,etc)
    """
    def __init__(self, online, id=None):
        self._language = None
        self._video = None
        self._online = online
        self._path = ""
        self._onlineId = ""
        if online:
            self._onlineId = id
        else:
            self._path = id
            self.setFileName(os.path.basename(self._path))
        self._uploader = None
        self._languageXX = None
        self._languageXXX = None
        self._languageName = None
        self.rating = 0
        if not online:
            self._size = os.path.getsize(self._path)
            self._hash = md5.new(file(self._path,mode='rb').read()).hexdigest()
        
    def setFileName(self,filename):
        self._filename = filename
    
    def getFileName(self):
        return self._filename
    
    def setVideo(self, _video):
        self._video = _video
        
    def getVideo(self):
        return self._video 
        
    def setUploader(self,uploader):
        self._uploader = uploader
    
    def getUploader(self):
        return self._uploader
    
    def setIdOnline(self,_id_online):
        self._path = _id_online
    
    def getIdOnline(self):
        return self._onlineId
    
    def getFilePath(self):
        return self._path
    
    #It could be the case when isLocal and isOnline are both true
    def isOnline(self): 
        return len(self._onlineId)
        
    def isLocal(self): 
        return len(self._path)
    
    def getSize(self):
        return self._size
    
    def setHash(self, hash):
        self._hash = hash
    
    def getHash(self):
        return self._hash
    
    def setLanguage(self,language):
        self.setLanguageXXX(language)
        
    def getLanguage(self):
        return self.getLanguageXXX()
    
    def setLanguageXX(self,xx):
        self._languageXX = xx
        self._languageXXX = languages.xx2xxx(xx)
        self._languageName= languages.xx2name(xx)
    
    def getLanguageXX(self):
        if self._languageXX:
            return self._languageXX.lower()
        else:
            return None
    
    def setLanguageXXX(self,xxx):
        self._languageXXX = xxx
        self._languageXX = languages.xxx2xx(xxx)
        self._languageName= languages.xxx2name(xxx)
    
    def getLanguageXXX(self):
        if self._languageXXX:
            return self._languageXXX.lower()
        else:
            return None
    
    def getLanguageName(self): 
        if self._languageName:
            return self._languageName.lower()
        else:
            return None
    
    def setLanguageName(self,language):
        self._languageName = language
        self._languageXXX = languages.name2xxx(language)
        self._languageXX = languages.name2xx(language)


    def setRating(self, rating):
        self.rating = rating
        
    def getRating(self):
        return self.rating
