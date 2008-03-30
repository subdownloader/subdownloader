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

SUBTITLES_EXT = ["srt","sub","txt","ssa"]
SELECT_SUBTITLES = "Subtitle Files (*.srt *.sub *.txt *.ssa)"

class SubtitleFile(object):
    """Contains the class that represents a SubtitleFile (SRT,SUB,etc)
    and provides easy methods to retrieve its attributes (Sizebytes, HASH, Validation,etc)
    """
    def __init__(self, online, id):
        self._language = None
        self._video = None
        if online:
            self._online = True
            self._id_online = id
            self._uploader = None
        else:
            self._online = False
            self._filepath = id
            self.setFileName(self.getFilePath())
            self._languageXX = None
            self._languageXXX = None
            self._languageName = None
            self._size = os.path.getsize(self._filepath)
            self._hash = md5.new(file(self._filepath,mode='rb').read()).hexdigest()
            self.rating = 0
        
    def setFileName(self,filename):
        self._filename = filename
    
    def getFileName(self):
        return os.path.basename(self._filepath)
    
    def setVideo(self, _video):
        self._video = _video
        
    def getVideo(self):
        return self._video 
        
    def setUploader(self,uploader):
        self._uploader = uploader
    
    def getUploader(self):
        return self._uploader
    
    def setIdOnline(self,_id_online):
        self._id_online = _id_online
    
    def getIdOnline(self):
        return self._id_online
    
    def getFilePath(self):
        return self._filepath
    
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
    
    def setLanguageXX(self,language):
        self._languageXX = language
    
    def getLanguageXX(self):
        return self._languageXX
    
    def setLanguageXXX(self,language):
        self._languageXXX = language
    
    def getLanguageXXX(self):
        return self._languageXXX
    
    def getLanguageName(self): 
        return self._languageName
    
    def setLanguageName(self,language):
        self._languageName = language
    
    def isOnline(self):
        return self._online

    def setRating(self, rating):
        self.rating = rating
        
    def getRating(self):
        return self.rating
