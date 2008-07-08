#if 0 /*
# -----------------------------------------------------------------------
# dvdinfo.py - parse dvd title structure
# -----------------------------------------------------------------------
# $Id: dvdinfo.py,v 1.18 2005/01/13 20:20:20 dischi Exp $
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


import os
import ifoparser
from mmpython import mediainfo
import mmpython
from discinfo import DiscInfo

class DVDAudio(mediainfo.AudioInfo):
    def __init__(self, title, number):
        mediainfo.AudioInfo.__init__(self)
        self.number = number
        self.title  = title
        self.id, self.language, self.codec, self.channels, self.samplerate = \
                 ifoparser.audio(title, number)


class DVDTitle(mediainfo.AVInfo):
    def __init__(self, number):
        mediainfo.AVInfo.__init__(self)
        self.number = number
        self.chapters, self.angles, self.length, audio_num, \
                       subtitles_num = ifoparser.title(number)

        self.keys.append('chapters')
        self.keys.append('subtitles')
        
        self.mime = 'video/mpeg'
        for a in range(1, audio_num+1):
            self.audio.append(DVDAudio(number, a))
            
        for s in range(1, subtitles_num+1):
            self.subtitles.append(ifoparser.subtitle(number, s)[0])

            
class DVDInfo(DiscInfo):
    def __init__(self, device):
        DiscInfo.__init__(self)
        self.context = 'video'
        self.offset = 0

        if mediainfo.DEBUG > 1:
            print 'trying buggy dvd detection'

        if isinstance(device, file):
            self.valid = self.isDVDiso(device)
        elif os.path.isdir(device):
            self.valid = self.isDVDdir(device)
        else:
            self.valid = self.isDisc(device)

        if self.valid and self.tracks:
            self.keys.append('length')
            self.length = 0
            first       = 0

            for t in self.tracks:
                self.length += t.length
                if not first:
                    first = t.length
            
            if self.length/len(self.tracks) == first:
                # badly mastered dvd
                self.length = first

        self.mime    = 'video/dvd'
        self.type    = 'DVD'
        self.subtype = 'video'


    def isDVDdir(self, dirname):
        if not (os.path.isdir(dirname+'/VIDEO_TS') or \
                os.path.isdir(dirname+'/video_ts') or \
                os.path.isdir(dirname+'/Video_ts')):
            return 0

        # OK, try libdvdread
        title_num = ifoparser.open(dirname)
        if not title_num:
            return 0

        for title in range(1, title_num+1):
            ti = DVDTitle(title)
            ti.trackno = title
            ti.trackof = title_num
            self.appendtrack(ti)

        ifoparser.close()
        return 1

    
    def isDisc(self, device):
        if DiscInfo.isDisc(self, device) != 2:
            return 0

        # brute force reading of the device to find out if it is a DVD
        f = open(device,'rb')
        f.seek(32768, 0)
        buffer = f.read(60000)

        if buffer.find('UDF') == -1:
            f.close()
            return 0

        # seems to be a DVD, read a little bit more
        buffer += f.read(550000)
        f.close()

        if buffer.find('VIDEO_TS') == -1 and buffer.find('VIDEO_TS.IFO') == -1 and \
               buffer.find('OSTA UDF Compliant') == -1:
            return 0

        # OK, try libdvdread
        title_num = ifoparser.open(device)

        if not title_num:
            return 0

        for title in range(1, title_num+1):
            ti = DVDTitle(title)
            ti.trackno = title
            ti.trackof = title_num
            self.appendtrack(ti)
        
        ifoparser.close()
        return 1


    def isDVDiso(self, f):
        # brute force reading of the device to find out if it is a DVD
        f.seek(32768, 0)
        buffer = f.read(60000)

        if buffer.find('UDF') == -1:
            return 0

        # seems to be a DVD, read a little bit more
        buffer += f.read(550000)

        if buffer.find('VIDEO_TS') == -1 and buffer.find('VIDEO_TS.IFO') == -1 and \
               buffer.find('OSTA UDF Compliant') == -1:
            return 0

        # OK, try libdvdread
        title_num = ifoparser.open(f.name)

        if not title_num:
            return 0

        for title in range(1, title_num+1):
            ti = DVDTitle(title)
            ti.trackno = title
            ti.trackof = title_num
            self.appendtrack(ti)
        
        ifoparser.close()
        return 1


if not mmpython.gettype('video/dvd', mediainfo.EXTENSION_DEVICE):
    mmpython.registertype( 'video/dvd', mediainfo.EXTENSION_DEVICE,
                           mediainfo.TYPE_AV, DVDInfo )

if not mmpython.gettype('video/dvd', mediainfo.EXTENSION_DIRECTORY):
    mmpython.registertype('video/dvd', mediainfo.EXTENSION_DIRECTORY,
                          mediainfo.TYPE_AV, DVDInfo)

mmpython.registertype('video/dvd', ['iso'], mediainfo.TYPE_AV, DVDInfo)
