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


import os.path
import md5
from subdownloader import *

SUBTITLES_EXT = ["srt","sub","txt","ssa"]

class SubtitleFile:
    """Contains the class that represents a SubtitleFile (SRT,SUB,etc)
    and provides easy methods to retrieve its attributes (Sizebytes, HASH, Validation,etc)
    """

    def __init__(self, online, id):
        self._language = None
        if online:
            self._online = True
            self._id_online = id
        else:
            self._filepath = id
            self.setFileName(os.path.basename(self.getFilePath()))
            self._size = os.path.getsize(self._filepath)
            self._hash = sub_md5hex = md5.new(file(self._filepath,mode='rb').read()).hexdigest()
        
    def setFileName(self,filename):
        self._filename = filename
    
    def getFileName(self):
        return self._filename
    
    def setIdOnline(self,_id_online):
        self._id_online = _id_online
    
    def getIdOnline(self):
        return self._id_online
    
    def getFilePath(self):
        return self._filepath
    
    def getSize(self):
        return self._size
    
    def getHash(self):
        return self._hash
    
    def setLanguage(self,language):
        self._language = language
    
    def getLanguage(self):
        return self._language
    
    def isOnline(self):
        return self._online
