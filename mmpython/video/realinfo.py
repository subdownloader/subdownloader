#if 0
# $Id: realinfo.py,v 1.6 2003/07/02 09:09:41 the_krow Exp $
# $Log: realinfo.py,v $
# Revision 1.6  2003/07/02 09:09:41  the_krow
# i18n stuff added to AVI
# some debug outputs removed
#
# Revision 1.5  2003/06/30 13:17:20  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
#
# Revision 1.4  2003/06/29 11:59:35  dischi
# make some debug silent
#
# Revision 1.3  2003/06/20 19:17:22  dischi
# remove filename again and use file.name
#
# Revision 1.2  2003/06/12 18:53:19  the_krow
# OGM detection added.
# .ram is a valid extension to real files
#
# Revision 1.1  2003/06/12 14:43:22  the_krow
# Realmedia file parsing. Title, Artist, Copyright work. Couldn't find
# many technical parameters to retrieve.
# Some initial QT parsing
# added Real to __init__.py
#
#
#
# MMPython - Media Metadata for Python
# Copyright (C) 2003 Thomas Schueppel
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

import struct
import string

from mmpython import mediainfo
import mmpython

# http://www.pcisys.net/~melanson/codecs/rmff.htm
# http://www.pcisys.net/~melanson/codecs/

_print = mediainfo._debug

class RealInfo(mediainfo.AVInfo):
    def __init__(self,file):
        mediainfo.AVInfo.__init__(self)
        self.context = 'video'
        self.valid = 0
        self.mime = 'video/real'
        self.type = 'Real Video'
        h = file.read(10)        
        (object_id,object_size,object_version) = struct.unpack('>4sIH',h)
        if object_id == '.RMF':
            self.valid = 1
        else:
            return
        file_version, num_headers = struct.unpack('>II', file.read(8))
        _print("size: %d, ver: %d, headers: %d" % (object_size, file_version,num_headers))
        for i in range(0,num_headers):            
            (object_id,object_size,object_version) = struct.unpack('>4sIH',file.read(10))
            self._read_header(object_id, file.read(object_size-10))
            _print("%s [%d]" % (object_id,object_size-10))
        # Read all the following headers
        
    def _read_header(self,object_id,s):
        if object_id == 'PROP':
            prop = struct.unpack('>9IHH', s)
            _print(prop)
        if object_id == 'MDPR':
            mdpr = struct.unpack('>H7I', s[:30])
            _print(mdpr)
            self.length = mdpr[7]/1000
            (stream_name_size,) = struct.unpack('>B', s[30:31])
            stream_name = s[31:31+stream_name_size]
            pos = 31+stream_name_size
            (mime_type_size,) = struct.unpack('>B', s[pos:pos+1])
            mime = s[pos+1:pos+1+mime_type_size]
            pos += mime_type_size+1
            (type_specific_len,) = struct.unpack('>I', s[pos:pos+4])
            type_specific = s[pos+4:pos+4+type_specific_len]
            pos += 4+type_specific_len
            if mime[:5] == 'audio':
                ai = mediainfo.AudioInfo()
                ai.id = mdpr[0]
                ai.bitrate = mdpr[2]
                self.audio.append(ai)
            elif mime[:5] == 'video':
                vi = mediainfo.VideoInfo()
                vi.id = mdpr[0]
                vi.bitrate = mdpr[2]
                self.video.append(vi)
            else:
                _print("Unknown: %s" % mime)
        if object_id == 'CONT':
            pos = 0
            (title_len,) = struct.unpack('>H', s[pos:pos+2])
            self.title = s[2:title_len+2]
            pos += title_len+2
            (author_len,) = struct.unpack('>H', s[pos:pos+2])
            self.artist = s[pos+2:pos+author_len+2]
            pos += author_len+2
            (copyright_len,) = struct.unpack('>H', s[pos:pos+2])
            self.copyright = s[pos+2:pos+copyright_len+2]
            pos += copyright_len+2
            (comment_len,) = struct.unpack('>H', s[pos:pos+2])
            self.comment = s[pos+2:pos+comment_len+2]

mmpython.registertype( 'video/real', ('rm', 'ra', 'ram'), mediainfo.TYPE_AV, RealInfo )
