#if 0
# -----------------------------------------------------------------------
# $Id: IPTC.py,v 1.9 2004/05/04 22:03:17 dischi Exp $
# -----------------------------------------------------------------------
# $Log: IPTC.py,v $
# Revision 1.9  2004/05/04 22:03:17  dischi
# handle bad jpeg
#
# Revision 1.8  2003/06/09 16:11:57  the_krow
# TIFF parser changed to new tables structure
# debug statements removed / changed to _debug
#
# Revision 1.7  2003/06/07 21:48:47  the_krow
# Added Copying info
# started changing riffinfo to new AV stuff
#
# Revision 1.6  2003/05/13 17:49:41  the_krow
# IPTC restructured
# EXIF Height read correctly
# JPEG Endmarker read
#
# Revision 1.5  2003/05/13 15:23:59  the_krow
# IPTC
#
# Revision 1.4  2003/05/13 15:16:02  the_krow
# width+height hacked
#
# Revision 1.3  2003/05/13 15:00:23  the_krow
# Tiff parsing
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

# http://www.ap.org/apserver/userguide/codes.htm

from struct import unpack

def flatten(list):
    try:
        for i in list.keys():
            val = list[i]
            if len(val) == 0: list[i] = None
            elif len(val) == 1: list[i] = val[0]
            else: list[i] = tuple(val)
        return list
    except:
        return []

def parseiptc(app):
    iptc = {}
    if app[:14] == "Photoshop 3.0\x00":
       app = app[14:]
    if 1:
       # parse the image resource block
       offset = 0
       data = None
       while app[offset:offset+4] == "8BIM":
          offset = offset + 4
          # resource code
          code = unpack("<H", app[offset:offset+2])[0]
          offset = offset + 2
          # resource name (usually empty)
          name_len = ord(app[offset])
          name = app[offset+1:offset+1+name_len]
          offset = 1 + offset + name_len
          if offset & 1:
              offset = offset + 1
          # resource data block
          size = unpack("<L", app[offset:offset+4])[0]
          offset = offset + 4
          if code == 0x0404:
              # 0x0404 contains IPTC/NAA data
              data = app[offset:offset+size]
              break
          offset = offset + size
          if offset & 1:
              offset = offset + 1
       if not data:
          return None
       offset = 0
       iptc = {}
       while 1:
           try:
               intro = ord(data[offset])
           except IndexError:
               return ''
           if intro != 0x1c:
               return iptc
           (key,len) = unpack('>HH',data[offset+1:offset+5])
           val = data[offset+5:offset+len+5]
           if iptc.has_key(key):
               iptc[key].append(val)
           else:
               iptc[key] = [val]
           offset += len + 5
    return iptc
    
    
