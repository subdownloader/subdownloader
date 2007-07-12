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
    """Contains the class that represents a VideoFile (SRT,SUB,etc)
    and provides easy methods to retrieve its attributes (Sizebytes, HASH, Validation,etc)
    """
   
    def __init__(self, filepath):
	self._filepath = filepath
        self._size = os.path.getsize(filepath)
        self._hash = sub_md5hex = md5.new(file(filepath,mode='rb').read()).hexdigest()
        
    def getFilePath(self):
	return self._filepath
    
    def getSize(self):
        return self._size
    
    def getHash(self):
        return self._hash
    
    