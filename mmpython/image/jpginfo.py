#if 0
# -----------------------------------------------------------------------
# $Id: jpginfo.py,v 1.21 2005/04/16 17:08:40 dischi Exp $
# -----------------------------------------------------------------------
# $Log: jpginfo.py,v $
# Revision 1.21  2005/04/16 17:08:40  dischi
# read metadata from epeg
#
# Revision 1.20  2005/04/16 15:01:15  dischi
# convert exif tags to str
#
# Revision 1.19  2004/05/20 15:56:31  dischi
# use Python Imaging for more info and gif/bmp support
#
# Revision 1.18  2003/06/30 13:17:19  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
#
# Revision 1.17  2003/06/20 19:17:22  dischi
# remove filename again and use file.name
#
# Revision 1.16  2003/06/10 13:02:32  the_krow
# Softened JPEG parser a little so it accepts jpegs that do not end in FFD9.
#
# Revision 1.15  2003/06/09 14:31:57  the_krow
# fixes on the mpeg parser
# resolutions, fps and bitrate should be reported correctly now
#
# Revision 1.14  2003/06/09 12:50:08  the_krow
# mp3 now fills tables
#
# Revision 1.13  2003/06/08 19:55:22  dischi
# added bins metadata support
#
# Revision 1.12  2003/06/08 16:48:08  dischi
# Changed self.exif to exif_info and the same for ipc. We should extract
# everything we need to self.xxx and don't remember where the info came
# from (it's bad for the cache, we cache everything twice).
# Also added thumbnail to the list of things we want
#
# Revision 1.11  2003/06/08 13:44:57  dischi
# Changed all imports to use the complete mmpython path for mediainfo
#
# Revision 1.10  2003/06/08 13:11:51  dischi
# removed print at the end and moved it into register
#
# Revision 1.9  2003/06/07 21:48:47  the_krow
# Added Copying info
# started changing riffinfo to new AV stuff
#
# Revision 1.8  2003/05/13 18:28:17  the_krow
# JPEG Resolution
#
# Revision 1.7  2003/05/13 17:49:41  the_krow
# IPTC restructured\nEXIF Height read correctly\nJPEG Endmarker read
#
# Revision 1.6  2003/05/13 15:52:42  the_krow
# Caption added
#
# Revision 1.5  2003/05/13 15:23:59  the_krow
# IPTC
#
# Revision 1.4  2003/05/13 15:00:23  the_krow
# Tiff parsing
#
# Revision 1.3  2003/05/13 12:31:11  the_krow
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

import ImageInfo

# interesting file format info:
# http://www.dcs.ed.ac.uk/home/mxr/gfx/2d-hi.html
# http://www.funducode.com/freec/Fileformats/format3/format3b.htm

SOF = { 0xC0 : "Baseline",   
        0xC1 : "Extended sequential",   
        0xC2 : "Progressive",   
        0xC3 : "Lossless",   
        0xC5 : "Differential sequential",   
        0xC6 : "Differential progressive",   
        0xC7 : "Differential lossless",   
        0xC9 : "Extended sequential, arithmetic coding",   
        0xCA : "Progressive, arithmetic coding",   
        0xCB : "Lossless, arithmetic coding",   
        0xCD : "Differential sequential, arithmetic coding",   
        0xCE : "Differential progressive, arithmetic coding",   
        0xCF : "Differential lossless, arithmetic coding",
}

_debug = mediainfo._debug

class JPGInfo(mediainfo.ImageInfo):

    def __init__(self,file):
        mediainfo.ImageInfo.__init__(self)
        iptc_info = None        
        self.mime = 'image/jpeg'
        self.type = 'jpeg image'
        self.valid = 1
        if file.read(2) != '\xff\xd8':
            self.valid = 0
            return
        file.seek(-2,2)
        if file.read(2) != '\xff\xd9':
            # Normally an JPEG should end in ffd9. This does not however
            # we assume it's an jpeg for now
            mediainfo._debug("Wrong encode found for jpeg")
        file.seek(2)
        app = file.read(4)
        self.meta = {}
        while (len(app) == 4):
            (ff,segtype,seglen) = struct.unpack(">BBH", app)
            if ff != 0xff: break
            _debug("SEGMENT: 0x%x%x, len=%d" % (ff,segtype,seglen))
            if segtype == 0xd9:
                break
            elif SOF.has_key(segtype):
                data = file.read(seglen-2)
                (precision,self.height,self.width,num_comp) = struct.unpack('>BHHB', data[:6])
                #_debug("H/W: %i / %i" % (self.height, self.width))
            elif segtype == 0xed:
                app = file.read(seglen-2)
                iptc_info = IPTC.flatten(IPTC.parseiptc(app))
                break
            elif segtype == 0xe7:
                # information created by libs like epeg
                data = file.read(seglen-2)
                if data.count('\n') == 1:
                    key, value = data.split('\n')
                    self.meta[key] = value
            else:
                file.seek(seglen-2,1)
            app = file.read(4)
        file.seek(0)
        exif_info = EXIF.process_file(file)
        if exif_info:
            self.setitem( 'date', exif_info, 'Image DateTime', True )            
            self.setitem( 'artist', exif_info, 'Image Artist', True )
            self.setitem( 'hardware', exif_info, 'Image Model', True )
            self.setitem( 'software', exif_info, 'Image Software', True )
            self.setitem( 'thumbnail', exif_info, 'JPEGThumbnail', True )
            self.appendtable( 'EXIF', exif_info )
        if iptc_info:
            self.setitem( 'title', iptc_info, 517, True ) 
            self.setitem( 'date' , iptc_info, 567, True )
            self.setitem( 'comment', iptc_info, 617, True )
            self.setitem( 'keywords', iptc_info, 537, True )
            self.setitem( 'artist', iptc_info, 592, True )
            self.setitem( 'country', iptc_info, 612, True ) 
            self.setitem( 'caption', iptc_info, 632, True )
            self.appendtable( 'IPTC', iptc_info )            

        if len(self.meta.keys()):
            self.appendtable( 'JPGMETA', self.meta )
        for key, value in self.meta.items():
            if key.startswith('Thumb:') or key == 'Software':
                setattr(self, key, value)
                if not key in self.keys:
                    self.keys.append(key)

        ImageInfo.add(file.name, self)
        return
       

mmpython.registertype( 'image/jpeg', ('jpg','jpeg'), mediainfo.TYPE_IMAGE, JPGInfo )
