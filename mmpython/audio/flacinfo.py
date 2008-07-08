#if 0
# -----------------------------------------------------------------------
# $Id: flacinfo.py,v 1.7 2003/10/05 21:06:24 outlyer Exp $
# -----------------------------------------------------------------------
# $Log: flacinfo.py,v $
# Revision 1.7  2003/10/05 21:06:24  outlyer
# Cram the VORBIS_COMMENT fields into our standard artist/album/etc. fields
# so they work in Freevo.
#
# The only thing missing from having perfect FLAC support is a way to
# calculate the song length.
#
# Revision 1.6  2003/10/05 20:45:09  outlyer
# Fix some minor python issues. It works from mediatest.py now, but Freevo
# isn't using the tag information yet. I don't know why.
#
# Revision 1.5  2003/09/22 16:21:20  the_krow
# o ogg parsing should basically work
# o utf-8 for vorbis comments
#
# Revision 1.4  2003/08/30 09:36:22  dischi
# turn off some debug based on DEBUG
#
# Revision 1.3  2003/08/27 02:53:48  outlyer
# Still doesn't do anything, but at least compiles now; problem is I don't
# know how to conver the endian "headers" in to the types we expect, and I'm
# hardly an expert on binary data.
#
# But I flushed out the header types from the FLAC documentation and
# hopefully Thomas will know what to do...
#
# I can provide a FLAC file if necessary...
#
# Revision 1.2  2003/08/26 21:21:18  outlyer
# Fix two more Python 2.3 warnings.
#
# Revision 1.1  2003/08/18 13:39:52  the_krow
# Initial Import. Started on frame parsing.
#
# -----------------------------------------------------------------------
# MMPython - Media Metadata for Python
# Copyright (C) 2003 Thomas Schueppel, et. al
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

from mmpython import mediainfo
import mmpython.audio.ogginfo as ogginfo
import mmpython
import struct
import re

# See: http://flac.sourceforge.net/format.html


class FlacInfo(mediainfo.MusicInfo):
    def __init__(self,file):
        mediainfo.MusicInfo.__init__(self)
        if file.read(4) != 'fLaC':
            self.valid = 0
            return
        self.valid = 1
        while 1:
            (blockheader,) = struct.unpack('>I',file.read(4))
            lastblock = (blockheader >> 31) & 1
            type = (blockheader >> 24) & 0x7F
            numbytes = blockheader & 0xFFFFFF
            if mmpython.mediainfo.DEBUG:
                print "Last?: %d, NumBytes: %d, Type: %d" % (lastblock, numbytes, type)                                
            # Read this blocks the data
            data = file.read(numbytes)
            if type == 0:
                # STREAMINFO
                bits = struct.unpack('>L', data[10:14])[0]
                self.samplerate = (bits >> 12) & 0xFFFFF
                self.channels = ((bits >> 9) & 7) + 1
                self.samplebits = ((bits >> 4) & 0x1F) + 1
                md5 = data[18:34]
            elif type == 1:
                # PADDING
                pass            
            elif type == 2:
                # APPLICATION 
                pass            
            elif type == 3:
                # SEEKTABLE 
                pass            
            elif type == 4:
                # VORBIS_COMMENT                
                skip, self.vendor = self._extractHeaderString(data)
                num, = struct.unpack('<I', data[skip:skip+4])
                start = skip+4
                header = {}
                for i in range(num):
                    (nextlen, s) = self._extractHeaderString(data[start:])
                    start += nextlen
                    a = re.split('=',s)
                    header[(a[0]).upper()]=a[1]
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
 
                self.appendtable('VORBISCOMMENT', header)
            elif type == 5:
                # CUESHEET 
                pass
            else:
                # UNKNOWN TYPE
                pass
            if lastblock:
                break

    def _extractHeaderString(self,header):
        len = struct.unpack( '<I', header[:4] )[0]
        return (len+4,unicode(header[4:4+len], 'utf-8'))

                
mmpython.registertype( 'application/flac', ('flac',), mediainfo.TYPE_MUSIC, FlacInfo )                
