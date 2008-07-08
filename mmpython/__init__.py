#!/usr/bin/python
#if 0
# -----------------------------------------------------------------------
# $Id: __init__.py,v 1.35 2004/10/15 09:02:11 dischi Exp $
# -----------------------------------------------------------------------
# $Log: __init__.py,v $
# Revision 1.35  2004/10/15 09:02:11  dischi
# add ac3 parser
#
# Revision 1.34  2004/05/20 15:55:08  dischi
# add xml file detection
#
# Revision 1.33  2004/05/02 08:28:20  dischi
# dvd iso support
#
# Revision 1.32  2004/04/18 09:11:36  dischi
# improved lsdvd support
#
# Revision 1.31  2004/04/17 18:38:54  dischi
# add lsdvd parser to avoid problems with our own
#
# Revision 1.30  2004/01/31 12:24:39  dischi
# add basic matroska info
#
# Revision 1.29  2004/01/27 20:27:52  dischi
# remove cache, it does not belong in mmpython
#
# Revision 1.28  2004/01/03 17:44:04  dischi
# catch OSError in case the file is removed file scanning
#
# Revision 1.27  2003/11/24 20:30:17  dischi
# fix again, dvd may fail, but datadir may not
#
# Revision 1.26  2003/11/24 20:29:26  dischi
# resort to let dvd work again
#
# Revision 1.25  2003/11/07 13:58:52  dischi
# extra check for dvd
#
# Revision 1.24  2003/09/22 16:24:58  the_krow
# o added flac
# o try-except block around ioctl since it is not avaiable in all OS
#
# Revision 1.23  2003/09/14 13:50:42  dischi
# make it possible to scan extention based only
#
# Revision 1.22  2003/09/10 18:41:44  dischi
# add USE_NETWORK, maybe there is no network connection
#
# Revision 1.20  2003/08/26 13:16:41  outlyer
# Enabled m4a support
#
# Revision 1.19  2003/07/10 11:17:35  the_krow
# ogminfo is used to parse ogg files
#
# Revision 1.18  2003/07/01 21:07:42  dischi
# switch back to eyed3info
#
# Revision 1.17  2003/06/30 13:17:18  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
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

# Do this stuff before importing the info instances since they 
# depend on this function

import factory

from synchronizedobject import SynchronizedObject

_factory = None

def Factory():
    global _factory

    # One-time init
    if _factory == None:
        _factory = SynchronizedObject(factory.Factory())
        
    return _factory

def registertype(mimetype,extensions,type,c):
    f = Factory()
    f.register(mimetype,extensions,type,c)    

def gettype(mimetype,extensions):
    f = Factory()
    return f.get(mimetype,extensions)    
    

# Okay Regular imports and code follow

import sys
import os
import mediainfo
import audio.ogginfo
import audio.pcminfo
import audio.m4ainfo
import audio.ac3info
import video.riffinfo
import video.mpeginfo
import video.asfinfo
import video.movinfo
#import image.jpginfo
#import image.pnginfo
#import image.tiffinfo
#import image.ImageInfo
import video.vcdinfo
import video.realinfo
import video.ogminfo
import video.mkvinfo
import misc.xmlinfo

# import some disc modules (may fail)
try:
    #import disc.discinfo
    import disc.vcdinfo
    import disc.audioinfo
except ImportError:
    pass

# find the best working DVD module
try:
    import disc.lsdvd
except ImportError:
    pass

try:
    import disc.dvdinfo
except ImportError:
    pass

# use fallback disc module
try:
    import disc.datainfo
except ImportError:
    pass

import audio.eyed3info
import audio.mp3info
import audio.webradioinfo
import audio.flacinfo



USE_NETWORK     = 1


def parse(filename, ext_only = 0):
    """
    parse the file
    """
    return Factory().create(filename, ext_only)

