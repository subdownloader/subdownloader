#if 0
# -----------------------------------------------------------------------
# $Id: pnginfo.py,v 1.11 2005/04/16 17:09:12 dischi Exp $
# -----------------------------------------------------------------------
# $Log: pnginfo.py,v $
# Revision 1.11  2005/04/16 17:09:12  dischi
# add thumbnail data to internal vars
#
# Revision 1.10  2004/05/20 15:56:31  dischi
# use Python Imaging for more info and gif/bmp support
#
# Revision 1.9  2003/06/30 13:17:20  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
#
# Revision 1.8  2003/06/23 20:59:11  the_krow
# PNG should now fill a correct table.
#
# Revision 1.7  2003/06/20 19:17:22  dischi
# remove filename again and use file.name
#
# Revision 1.6  2003/06/08 20:27:42  dischi
# small fix for broken files and fixed a wrong bins_data call
#
# Revision 1.5  2003/06/08 19:55:22  dischi
# added bins metadata support
#
# Revision 1.4  2003/06/08 13:44:58  dischi
# Changed all imports to use the complete mmpython path for mediainfo
#
# Revision 1.3  2003/06/08 13:11:51  dischi
# removed print at the end and moved it into register
#
# Revision 1.2  2003/05/13 15:00:23  the_krow
# Tiff parsing
#
# Revision 1.1  2003/05/13 12:31:11  the_krow
# + GNU Copyright Notice
# + PNG Parsing
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

from mmpython import mediainfo
import mmpython
import IPTC
import EXIF
import struct
import zlib
import ImageInfo

# interesting file format info:
# http://www.libpng.org/pub/png/png-sitemap.html#programming
# http://pmt.sourceforge.net/pngmeta/

PNGSIGNATURE = "\211PNG\r\n\032\n"

_print = mediainfo._debug

class PNGInfo(mediainfo.ImageInfo):

    def __init__(self,file):
        mediainfo.ImageInfo.__init__(self)
        self.iptc = None        
        self.mime = 'image/png'
        self.type = 'PNG image'
        self.valid = 1
        signature = file.read(8)
        if ( signature != PNGSIGNATURE ):
            self.valid = 0
            return
        self.meta = {}
        while self._readChunk(file):
            pass
        if len(self.meta.keys()):
            self.appendtable( 'PNGMETA', self.meta )
        for key, value in self.meta.items():
            if key.startswith('Thumb:') or key == 'Software':
                setattr(self, key, value)
                if not key in self.keys:
                    self.keys.append(key)
        ImageInfo.add(file.name, self)
        return       
        
    def _readChunk(self,file):
        try:
            (length, type) = struct.unpack('>I4s', file.read(8))
        except:
            return 0
        if ( type == 'tEXt' ):
          _print('latin-1 Text found.')
          (data, crc) = struct.unpack('>%isI' % length,file.read(length+4))
          (key, value) = data.split('\0')
          self.meta[key] = value
          _print("%s -> %s" % (key,value))
        elif ( type == 'zTXt' ):
          _print('Compressed Text found.')
          (data,crc) = struct.unpack('>%isI' % length,file.read(length+4))
          split = data.split('\0')
          key = split[0]
          value = "".join(split[1:])
          compression = ord(value[0])
          value = value[1:]
          if compression == 0:
              decompressed = zlib.decompress(value)
              _print("%s (Compressed %i) -> %s" % (key,compression,decompressed))
          else:
              _print("%s has unknown Compression %c" % (key,compression))
          self.meta[key] = value
        elif ( type == 'iTXt' ):
          _print('International Text found.')
          (data,crc) = struct.unpack('>%isI' % length,file.read(length+4))
          (key, value) = data.split('\0')
          self.meta[key] = value
          _print("%s -> %s" % (key,value))
        else:
          file.seek(length+4,1)
          _print("%s of length %d ignored." % (type, length))
        return 1


mmpython.registertype( 'image/png', ('png',), mediainfo.TYPE_IMAGE, PNGInfo )
