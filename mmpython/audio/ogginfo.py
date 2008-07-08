#if 0
# -----------------------------------------------------------------------
# $Id: ogginfo.py,v 1.16 2004/05/18 21:56:18 dischi Exp $
# -----------------------------------------------------------------------
# $Log: ogginfo.py,v $
# Revision 1.16  2004/05/18 21:56:18  dischi
# do not pare the whole file to get the length
#
# Revision 1.15  2003/09/22 16:21:20  the_krow
# o ogg parsing should basically work
# o utf-8 for vorbis comments
#
# Revision 1.14  2003/06/30 13:17:18  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
#
# Revision 1.13  2003/06/29 12:03:15  dischi
# make some debug silent
#
# Revision 1.12  2003/06/20 19:17:22  dischi
# remove filename again and use file.name
#
# Revision 1.11  2003/06/10 11:17:39  the_krow
# - OGG Fixes
# - changed one DiscInfo reference in vcdinfo I missed before
#
# Revision 1.10  2003/06/08 19:53:38  dischi
# also give the filename to init for additional data tests
#
# Revision 1.9  2003/06/08 13:44:56  dischi
# Changed all imports to use the complete mmpython path for mediainfo
#
# Revision 1.8  2003/06/08 13:11:25  dischi
# removed print at the end and moved it into register
#
# Revision 1.7  2003/06/07 23:32:11  the_krow
# changed names to new format
# debug messages
#
# Revision 1.6  2003/05/13 15:23:59  the_krow
# IPTC
#
# Revision 1.5  2003/05/13 12:31:43  the_krow
# + Copyright Notice
#
# -----------------------------------------------------------------------
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

import re
import os, stat
import struct

from mmpython import mediainfo
import mmpython

VORBIS_PACKET_INFO = '\01vorbis'
VORBIS_PACKET_HEADER = '\03vorbis'
VORBIS_PACKET_SETUP = '\05vorbis'

_print = mediainfo._debug

class OggInfo(mediainfo.MusicInfo):
    def __init__(self,file):
        mediainfo.MusicInfo.__init__(self)
        h = file.read(4+1+1+20+1)
        if h[:5] != "OggS\00":
            _print("Invalid header")
            self.valid = 0
            return
        if ord(h[5]) != 2:
            _print("Invalid header type flag (trying to go ahead anyway)")
        self.pageSegCount = ord(h[-1])
        # Skip the PageSegCount
        file.seek(self.pageSegCount,1)
        h = file.read(7)
        if h != VORBIS_PACKET_INFO:
            _print("Wrong vorbis header type, giving up.")
            self.valid = 0
            return
        self.valid = 1
        self.mime = 'application/ogg'
        header = {}
        info = file.read(23)
        self.version, self.channels, self.samplerate, bitrate_max, self.bitrate, bitrate_min, blocksize, framing = struct.unpack('<IBIiiiBB',info[:23])
        # INFO Header, read Oggs and skip 10 bytes
        h = file.read(4+10+13)        
        if h[:4] == 'OggS':
            (serial, pagesequence, checksum, numEntries) = struct.unpack( '<14xIIIB', h )
            # skip past numEntries
            file.seek(numEntries,1)
            h = file.read(7)
            if h != VORBIS_PACKET_HEADER:
                # Not a corrent info header
                return                        
            self.encoder = self._extractHeaderString(file)
            numItems = struct.unpack('<I',file.read(4))[0]
            for i in range(numItems):
                s = self._extractHeaderString(file)
                a = re.split('=',s)
                header[(a[0]).upper()]=a[1]
            # Put Header fields into info fields
            if header.has_key('TITLE'):
                self.title = header['TITLE']
            if header.has_key('ALBUM'):
                self.album = header['ALBUM']
            if header.has_key('ARTIST'):
                self.artist = header['ARTIST']            
            if header.has_key('COMMENT'):
                self.comment = header['COMMENT']
            if header.has_key('DATE'):
                self.date = header['DATE']
            if header.has_key('ENCODER'):
                self.encoder = header['ENCODER']
            if header.has_key('TRACKNUMBER'):
                self.trackno = header['TRACKNUMBER']
            self.type = 'OGG Vorbis'
            self.subtype = ''
            self.length = self._calculateTrackLength(file)
            self.appendtable('VORBISCOMMENT',header)
                                            
    def _extractHeaderString(self,f):
        len = struct.unpack( '<I', f.read(4) )[0]
        return unicode(f.read(len), 'utf-8')
    

    def _calculateTrackLength(self,f):
        # seek to the end of the stream, to avoid scanning the whole file
        if (os.stat(f.name)[stat.ST_SIZE] > 20000):
            f.seek(os.stat(f.name)[stat.ST_SIZE]-10000)

        # read the rest of the file into a buffer
        h = f.read()
        granule_position = 0
        # search for each 'OggS' in h        
        if len(h):
            idx = h.rfind('OggS')
            if idx < 0:
                return 0
            pageSize = 0
            h = h[idx+4:]
            (check, type, granule_position, absPos, serial, pageN, crc, segs) = struct.unpack( '<BBIIIIIB', h[:23] )            
            if check != 0:
                _print(h[:10])
                return
            _print("granule = %d / %d" % (granule_position, absPos))
        # the last one is the one we are interested in
        return (granule_position / self.samplerate)

mmpython.registertype( 'application/ogg', ('ogg',), mediainfo.TYPE_MUSIC, OggInfo )
