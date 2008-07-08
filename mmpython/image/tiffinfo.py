#if 0
# -----------------------------------------------------------------------
# $Id: tiffinfo.py,v 1.11 2004/05/20 15:56:31 dischi Exp $
# -----------------------------------------------------------------------
# $Log: tiffinfo.py,v $
# Revision 1.11  2004/05/20 15:56:31  dischi
# use Python Imaging for more info and gif/bmp support
#
# Revision 1.10  2003/06/30 13:17:20  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
#
# Revision 1.9  2003/06/20 19:17:22  dischi
# remove filename again and use file.name
#
# Revision 1.8  2003/06/09 16:11:57  the_krow
# TIFF parser changed to new tables structure
# debug statements removed / changed to _debug
#
# Revision 1.7  2003/06/08 19:55:22  dischi
# added bins metadata support
#
# Revision 1.6  2003/06/08 13:44:58  dischi
# Changed all imports to use the complete mmpython path for mediainfo
#
# Revision 1.5  2003/06/08 13:11:51  dischi
# removed print at the end and moved it into register
#
# Revision 1.4  2003/05/13 15:52:43  the_krow
# Caption added
#
# Revision 1.3  2003/05/13 15:23:59  the_krow
# IPTC
#
# Revision 1.2  2003/05/13 15:16:02  the_krow
# width+height hacked
#
# Revision 1.1  2003/05/13 15:00:23  the_krow
# Tiff parsing
#
# -----------------------------------------------------------------------
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

from mmpython import mediainfo
import mmpython
import IPTC
import EXIF
import struct
import ImageInfo

MOTOROLASIGNATURE = 'MM\x00\x2a'
INTELSIGNATURE = 'II\x2a\x00'

# http://partners.adobe.com/asn/developer/pdfs/tn/TIFF6.pdf

_debug = mediainfo._debug

class TIFFInfo(mediainfo.ImageInfo):

    def __init__(self,file):
        mediainfo.ImageInfo.__init__(self)
        self.iptc = None        
        self.mime = 'image/tiff'
        self.type = 'TIFF image'
        self.intel = 0
        self.valid = 0
        iptc = {}
        header = file.read(8)
        if header[:4] == MOTOROLASIGNATURE:
            self.valid = 1
            self.intel = 0
            (offset,) = struct.unpack(">I", header[4:8])
            file.seek(offset)
            (len,) = struct.unpack(">H", file.read(2))
            app = file.read(len*12)
            for i in range(len):
                (tag, type, length, value, offset) = struct.unpack('>HHIHH', app[i*12:i*12+12])
                _debug("[%i/%i] tag: 0x%.4x, type 0x%.4x, len %d, value %d, offset %d)" % (i,len,tag,type,length,value,offset))
                if tag == 0x8649:
                    file.seek(offset,0)
                    iptc = IPTC.flatten(IPTC.parseiptc(file.read(1000)))
                elif tag == 0x0100:
                    if value != 0:
                        self.width = value
                    else:
                        self.width = offset
                elif tag == 0x0101:
                    if value != 0:
                        self.height = value
                    else:
                        self.height = offset

        elif header[:4] == INTELSIGNATURE:
            self.valid = 1
            self.intel = 1
            (offset,) = struct.unpack("<I", header[4:8])
            file.seek(offset,0)
            (len,) = struct.unpack("<H", file.read(2))
            app = file.read(len*12)
            for i in range(len):
                (tag, type, length, offset, value) = struct.unpack('<HHIHH', app[i*12:i*12+12])
                _debug("[%i/%i] tag: 0x%.4x, type 0x%.4x, len %d, value %d, offset %d)" % (i,len,tag,type,length,value,offset))
                if tag == 0x8649:
                    file.seek(offset)
                    iptc = IPTC.flatten(IPTC.parseiptc(file.read(1000)))
                elif tag == 0x0100:
                    if value != 0:
                        self.width = value
                    else:
                        self.width = offset
                elif tag == 0x0101:
                    if value != 0:
                        self.height = value
                    else:
                        self.height = offset
        else:
            ImageInfo.add(file.name, self)
            return
            
        if iptc:
            self.setitem( 'title', iptc, 517 ) 
            self.setitem( 'date' , iptc, 567 )
            self.setitem( 'comment', iptc, 617 )
            self.setitem( 'keywords', iptc, 537 )
            self.setitem( 'artist', iptc, 592 )
            self.setitem( 'country', iptc, 612 ) 
            self.setitem( 'caption', iptc, 632 )
            self.appendtable('IPTC', iptc)

        ImageInfo.add(file.name, self)
        return
            

mmpython.registertype( 'image/tiff', ('tif','tiff'), mediainfo.TYPE_IMAGE, TIFFInfo )
