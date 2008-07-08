#if 0 /*
# -----------------------------------------------------------------------
# vcdinfo.py - parse vcd track informations
# -----------------------------------------------------------------------
# $Id: vcdinfo.py,v 1.8 2004/06/25 13:20:35 dischi Exp $
#
# $Log: vcdinfo.py,v $
# Revision 1.8  2004/06/25 13:20:35  dischi
# FreeBSD patches
#
# Revision 1.7  2003/06/30 13:17:19  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
#
# Revision 1.6  2003/06/10 22:11:36  dischi
# some fixes
#
# Revision 1.5  2003/06/09 12:47:53  dischi
# more track info
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

import mmpython
from mmpython import mediainfo
from discinfo import DiscInfo
import cdrom

class VCDInfo(DiscInfo):
    def __init__(self,device):
        DiscInfo.__init__(self)
        self.context = 'video'
        self.offset = 0
        self.valid = self.isDisc(device)
        self.mime = 'video/vcd'
        self.type = 'CD'        
        self.subtype = 'video'

    def isDisc(self, device):
        type = None
        if DiscInfo.isDisc(self, device) != 2:
            return 0
        
        # brute force reading of the device to find out if it is a VCD
        f = open(device,'rb')
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

        # read the tracks to generate the title list
        device = open(device)
        (first, last) = cdrom.toc_header(device)

        lmin = 0
        lsec = 0

        num = 0
        for i in range(first, last + 2):
            if i == last + 1:
                min, sec, frames = cdrom.leadout(device)
            else:
                min, sec, frames = cdrom.toc_entry(device, i)
            if num:
                vi = mediainfo.VideoInfo()
                # XXX add more static information here, it's also possible
                # XXX to scan for more informations like fps
                # XXX Settings to MPEG1/2 is a wild guess, maybe the track
                # XXX isn't playable at all (e.g. the menu)
                if type == 'VCD':
                    vi.codec = 'MPEG1'
                else:
                    vi.codec = 'MPEG2'
                vi.length = (min-lmin) * 60 + (sec-lsec)
                self.tracks.append(vi)
            num += 1
            lmin, lsec = min, sec
        device.close()
        return 1

    
mmpython.registertype( 'video/vcd', mediainfo.EXTENSION_DEVICE, mediainfo.TYPE_AV, VCDInfo )
