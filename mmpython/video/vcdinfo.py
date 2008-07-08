#if 0 /*
# -----------------------------------------------------------------------
# vcdinfo.py - parse vcd track informations from cue/bin files
# -----------------------------------------------------------------------
# $Id: vcdinfo.py,v 1.7 2004/06/25 13:20:34 dischi Exp $
#
# $Log: vcdinfo.py,v $
# Revision 1.7  2004/06/25 13:20:34  dischi
# FreeBSD patches
#
# Revision 1.6  2003/06/30 13:17:20  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
#
# Revision 1.5  2003/06/29 11:59:55  dischi
# bugfix
#
# Revision 1.4  2003/06/20 19:17:22  dischi
# remove filename again and use file.name
#
# Revision 1.3  2003/06/10 11:17:39  the_krow
# - OGG Fixes
# - changed one DiscInfo reference in vcdinfo I missed before
#
# Revision 1.2  2003/06/10 10:56:54  the_krow
# - Build try-except blocks around disc imports to make it run on platforms
#   not compiling / running the C extensions.
# - moved DiscInfo class to disc module
# - changed video.VcdInfo to be derived from CollectionInfo instead of
#   DiskInfo so it can be used without the cdrom extensions which are
#   hopefully not needed for bin-files.
#
# Revision 1.1  2003/06/09 16:09:18  dischi
# first version of a cue/bin vcd parser
#
#
# -----------------------------------------------------------------------
# Copyright (C) 2003 Thomas Schueppel, Dirk Meyer
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
# ----------------------------------------------------------------------- */
#endif


from mmpython import mediainfo
import mmpython
import os

class VCDInfo(mediainfo.CollectionInfo):
    def __init__(self, file):
        mediainfo.CollectionInfo.__init__(self)
        self.context = 'video'
        self.offset = 0
        self.valid = self.isVCD(file)
        self.mime = 'video/vcd'
        self.type = 'vcd video'        

    def isVCD(self, file):
        type = None

        buffer = file.readline()

        if not buffer[:6] == 'FILE "':
            return 0

        bin = os.path.join(os.path.dirname(file.name), buffer[6:buffer[6:].find('"')+6])
        if not os.path.isfile(bin):
            return 0

        # At this point this really is a cue/bin disc
        
        # brute force reading of the bin to find out if it is a VCD
        f = open(bin,'rb')
        f.seek(32768, 0)
        buffer = f.read(60000)
        f.close()

        if buffer.find('SVCD') > 0 and buffer.find('TRACKS.SVD') > 0 and \
               buffer.find('ENTRIES.SVD') > 0:
            type = 'SVCD'

        elif buffer.find('INFO.VCD') > 0 and buffer.find('ENTRIES.VCD') > 0:
            type = 'VCD'

        else:
            return 0

        counter = 0
        while 1:
            buffer = file.readline()
            if not len(buffer):
                return 1
            if buffer[:8] == '  TRACK ':
                counter += 1
                # the first track is the directory, that doesn't count
                if counter > 1:
                    vi = mediainfo.VideoInfo()
                    if type == 'VCD':
                        vi.codec = 'MPEG1'
                    else:
                        vi.codec = 'MPEG2'
                    self.tracks.append(vi)


mmpython.registertype( 'video/vcd', ('cue',), mediainfo.TYPE_AV, VCDInfo )
