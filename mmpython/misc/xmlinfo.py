#if 0
# -----------------------------------------------------------------------
# $Id: xmlinfo.py,v 1.2 2004/05/24 10:50:48 dischi Exp $
# -----------------------------------------------------------------------
# $Log: xmlinfo.py,v $
# Revision 1.2  2004/05/24 10:50:48  dischi
# bugfix
#
# Revision 1.1  2004/05/20 15:55:09  dischi
# add xml file detection
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

import os
import mmpython
from mmpython import mediainfo

DEBUG = mediainfo.DEBUG

try:
    # XML support
    from xml.utils import qp_xml
except:
    if DEBUG:
        print 'Python XML not found'


XML_TAG_INFO = {
    'image':  'Bins Image Description',
    'freevo': 'Freevo XML Definition'
    }
    
class XMLInfo(mediainfo.MediaInfo):

    def __init__(self,file):
        mediainfo.MediaInfo.__init__(self)
        self.valid = 0
        if not file.name.endswith('.xml') and not file.name.endswith('.fxd'):
            return

        self.mime  = 'text/xml'
        self.type  = ''

        try:
            parser = qp_xml.Parser()
            tree = parser.parse(file)
        except:
            return 0

        if tree.name in XML_TAG_INFO:
            self.type = XML_TAG_INFO[tree.name]
        else:
            self.type = 'XML file'
        self.valid = 1
        

mmpython.registertype( 'text/xml', ('xml', 'fxd'), mediainfo.TYPE_MISC, XMLInfo )
