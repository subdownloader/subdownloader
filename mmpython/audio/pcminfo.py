#if 0
# -----------------------------------------------------------------------
# $Id: pcminfo.py,v 1.8 2003/06/30 13:17:18 the_krow Exp $
# -----------------------------------------------------------------------
# $Log: pcminfo.py,v $
# Revision 1.8  2003/06/30 13:17:18  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
#
# Revision 1.7  2003/06/20 19:17:22  dischi
# remove filename again and use file.name
#
# Revision 1.6  2003/06/08 19:53:38  dischi
# also give the filename to init for additional data tests
#
# Revision 1.5  2003/06/08 13:44:56  dischi
# Changed all imports to use the complete mmpython path for mediainfo
#
# Revision 1.4  2003/06/08 13:11:25  dischi
# removed print at the end and moved it into register
#
# Revision 1.3  2003/05/13 15:23:59  the_krow
# IPTC
#
# -----------------------------------------------------------------------
# Revision 1.2  2003/05/13 12:31:43  the_krow
# + Copyright Notice
#
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

import sndhdr
from mmpython import mediainfo
import mmpython

class PCMInfo(mediainfo.AudioInfo):
    def _what(self,f):
        """Recognize sound headers"""
        h = f.read(512)
        for tf in sndhdr.tests:
            res = tf(h, f)
            if res:
                return res
        return None

    def __init__(self,file):
       mediainfo.AudioInfo.__init__(self)
       t = self._what(file)
       if t:
           (self.type, self.samplerate, self.channels, self.bitrate, self.samplebits) = t
           self.mime = "audio/%s" % self.type
           self.valid = 1
       else:
           self.valid = 0
           return
       

mmpython.registertype( 'application/pcm', ('wav','aif','voc','au'), mediainfo.TYPE_AUDIO, PCMInfo )
