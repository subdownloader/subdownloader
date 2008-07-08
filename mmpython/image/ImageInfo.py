#if 0
# -----------------------------------------------------------------------
# $Id: ImageInfo.py,v 1.2 2005/04/16 15:01:53 dischi Exp $
# -----------------------------------------------------------------------
# $Log: ImageInfo.py,v $
# Revision 1.2  2005/04/16 15:01:53  dischi
# read gthumb comment files
#
# Revision 1.1  2004/05/20 15:56:31  dischi
# use Python Imaging for more info and gif/bmp support
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

import mmpython
from mmpython import mediainfo

import os
import gzip
from xml.utils import qp_xml

DEBUG = mediainfo.DEBUG

try:
    import Image
except:
    if DEBUG:
        print 'Python Imaging not found'

import bins

def add(filename, object):
    if os.path.isfile(filename + '.xml'):
        try:
            binsinfo = bins.get_bins_desc(filename)
            # get needed keys from exif infos
            for key in mediainfo.IMAGECORE + mediainfo.MEDIACORE:
                if not object[key] and binsinfo['exif'].has_key(key):
                    object[key] = binsinfo['exif'][key]
            # get _all_ infos from description
            for key in binsinfo['desc']:
                object[key] = binsinfo['desc'][key]
                if not key in mediainfo.IMAGECORE + mediainfo.MEDIACORE:
                    # if it's in desc it must be important
                    object.keys.append(key)
        except Exception, e:
            if DEBUG:
                print e
            pass

    comment_file = os.path.join(os.path.dirname(filename),
                                '.comments',
                                os.path.basename(filename) + '.xml')
    if os.path.isfile(comment_file):
        try:
            f = gzip.open(comment_file)
            p = qp_xml.Parser()
            tree = p.parse(f)
            f.close()
            for c in tree.children:
                if c.name == 'Place':
                    object.location = c.textof()
                if c.name == 'Note':
                    object.description = c.textof()
        except:
            pass
    try:
        i = Image.open(filename)
    except:
        return 0

    if not object.mime:
        object.mime = 'image/%s' % i.format.lower()
        
    object.type = i.format_description

    if i.info.has_key('dpi'):
        object['dpi'] = '%sx%s' % i.info['dpi']

    if DEBUG:
        for info in i.info:
            if not info == 'exif':
                print '%s: %s' % (info, i.info[info])

    object.mode = i.mode
    if not object.height:
        object.width, object.height = i.size

    return 1





class ImageInfo(mediainfo.ImageInfo):

    def __init__(self,file):
        mediainfo.ImageInfo.__init__(self)
        self.mime  = ''
        self.type  = ''
        self.valid = add(file.name, self)
        
mmpython.registertype( 'image/gif', ('gif',), mediainfo.TYPE_IMAGE, ImageInfo )
mmpython.registertype( 'image/bmp', ('bmp',), mediainfo.TYPE_IMAGE, ImageInfo )
