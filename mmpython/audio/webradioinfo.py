#if 0
# -----------------------------------------------------------------------
# $Id: webradioinfo.py,v 1.7 2003/07/02 11:17:29 the_krow Exp $
# -----------------------------------------------------------------------
# $Log: webradioinfo.py,v $
# Revision 1.7  2003/07/02 11:17:29  the_krow
# language is now part of the table key
#
# Revision 1.6  2003/06/30 13:17:18  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
#
# Revision 1.5  2003/06/24 14:37:17  dischi
# small fix
#
# Revision 1.4  2003/06/24 13:52:06  the_krow
# 302 Handling is done by urllib so no further code for this is
# needed. Thanks to den_RDC for setting up a server to test it.
#
# Revision 1.3  2003/06/24 13:06:46  the_krow
# stream is being closed in fail-cases.
#
# Revision 1.2  2003/06/24 12:59:33  the_krow
# Added Webradio.
# Added Stream Type to mediainfo
#
# Revision 1.1  2003/06/23 22:23:16  the_krow
# First Import. Not yet integrated.
#
#
# -----------------------------------------------------------------------
# MMPython - Media Metadata for Python
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
# -----------------------------------------------------------------------
#endif

import urlparse
import string
import urllib

from mmpython import mediainfo
import mmpython

_print = mediainfo._debug

# http://205.188.209.193:80/stream/1006

ICY_tags = { 'title': 'icy-name',
             'genre': 'icy-genre',
             'bitrate': 'icy-br',
             'caption': 'icy-url',
           }

class WebRadioInfo(mediainfo.MusicInfo):
    def __init__(self, url):
        mediainfo.MusicInfo.__init__(self)
        tup = urlparse.urlsplit(url)
        scheme, location, path, query, fragment = tup
        if scheme != 'http':
            self.valid = 0
            return
        # Open an URL Connection
        fi = urllib.urlopen(url)        

        # grab the statusline
        self.statusline = fi.readline()
        try:
            statuslist = string.split(self.statusline)
        except ValueError:
            # assume it is okay since so many servers are badly configured
            statuslist = ["ICY", "200"]
                    
        if statuslist[1] != "200":
            self.valid = 0
            if fi:
                fi.close()
            return

        self.valid = 1
        self.type = 'audio'
        self.subtype = 'mp3'
        # grab any headers for a max of 10 lines
        linecnt = 0
        tab = {}
        lines = fi.readlines(512)        
        for linecnt in range(0,11):
            icyline = lines[linecnt]
            icyline = icyline.rstrip('\r\n')
            if len(icyline) < 4:
                break
            cidx = icyline.find(':')
            if cidx != -1:
                # break on short line (ie. really should be a blank line)
                # strip leading and trailing whitespace                
                tab[icyline[:cidx].strip()] = icyline[cidx+2:].strip()
        if fi:
            fi.close()
        self.appendtable('ICY', tab)
        self.tag_map = { ('ICY', 'en') : ICY_tags }
        # Copy Metadata from tables into the main set of attributes        
        for k in self.tag_map.keys():
            map(lambda x:self.setitem(x,self.gettable(k[0],k[1]),self.tag_map[k][x]), self.tag_map[k].keys())
        self.bitrate = string.atoi(self.bitrate)*1000        

mmpython.registertype( 'text/plain', mediainfo.EXTENSION_STREAM, mediainfo.TYPE_MUSIC, WebRadioInfo )

