#if 0
# -----------------------------------------------------------------------
# mkvinfo.py - Matroska Streaming Video Files
# -----------------------------------------------------------------------
# $Id: mkvinfo.py,v 1.3 2004/04/18 17:55:26 dischi Exp $
#
# $Log: mkvinfo.py,v $
# Revision 1.3  2004/04/18 17:55:26  dischi
# update, including subtitle support
#
# Revision 1.2  2004/03/21 08:57:31  dischi
# major bugfix
#
# Revision 1.1  2004/01/31 12:24:15  dischi
# add basic matroska info
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


from mmpython import mediainfo
import mmpython
import struct
import re
import stat
import os
import math
from types import *
from struct import *
from string import *

_print = mediainfo._debug

# Main IDs for the Matroska streams
MATROSKA_VIDEO_TRACK     = 0x01
MATROSKA_AUDIO_TRACK     = 0x02
MATROSKA_SUBTITLES_TRACK = 0x11

MATROSKA_HEADER_ID  = 0x1A45DFA3
MATROSKA_TRACKS_ID  = 0x1654AE6B
MATROSKA_SEGMENT_ID = 0x18538067
MATROSKA_SEGMENT_INFO_ID      = 0x1549A966
MATROSKA_CLUSTER_ID           = 0x1F43B675
MATROSKA_VOID_ID              = 0xEC
MATROSKA_CRC_ID               = 0xBF
MATROSKA_TIMECODESCALE_ID     = 0x2AD7B1
MATROSKA_DURATION_ID          = 0x4489
MATROSKA_CRC32_ID             = 0xBF
MATROSKA_TRACK_TYPE_ID        = 0x83
MATROSKA_TRACK_LANGUAGE_ID    = 0x22B59C
MATROSKA_TIMECODESCALE_ID     = 0x4489
MATROSKA_MUXING_APP_ID        = 0x4D80
MATROSKA_WRITING_APP_ID       = 0x5741
MATROSKA_CODEC_ID             = 0x86
MATROSKA_CODEC_NAME_ID        = 0x258688
MATROSKA_FRAME_DURATION_ID    = 0x23E383
MATROSKA_VIDEO_SETTINGS_ID    = 0xE0
MATROSKA_VID_WIDTH_ID         = 0xB0
MATROSKA_VID_HEIGHT_ID        = 0xBA
MATROSKA_AUDIO_SETTINGS_ID    = 0xE1
MATROSKA_AUDIO_SAMPLERATE_ID  = 0xB5
MATROSKA_AUDIO_CHANNELS_ID    = 0x9F
MATROSKA_TRACK_UID_ID         = 0x73C5
MATROSKA_TRACK_NUMBER_ID      = 0xD7

# This is class that is responsible to handle one Ebml entity as described in the Matroska/Ebml spec
class EbmlEntity:
    def __init__(self, inbuf):
        # Compute the EBML id
        # Set the CRC len to zero
        self.crc_len = 0
        # Now loop until we find an entity without CRC
        self.build_entity(inbuf)
        while self.get_id() == MATROSKA_CRC32_ID:
            self.crc_len += self.get_total_len()
            inbuf = inbuf[self.get_total_len():]
            self.build_entity(inbuf)

    def build_entity(self, inbuf):
        self.compute_id(inbuf)
        #_print("Entity id : %08X" % self.entity_id)
        if ( self.id_len == 0):
            self.valid = 0
            _print("EBML entity not found, bad file format")
            return
        self.valid = 1
        self.entity_len = self.compute_len(inbuf[self.id_len:])
        # Obviously, the segment can be very long (ie the whole file, so we truncate it at the read buffer size
        if (self.entity_len == -1):
            self.entity_data = inbuf[self.id_len+self.len_size:]
            self.entity_len = len(self.entity_data) # Set the remaining size
        else:
            self.entity_data = inbuf[self.id_len+self.len_size:self.id_len+self.len_size+self.entity_len]
        #_print("Entity len : %d" % self.entity_len)
        # if the size is 1, 2 3 or 4 it could be a numeric value, so do the job
        self.value = 0
        if self.entity_len == 1:
            self.value = ord(self.entity_data[0])
        if self.entity_len == 2:
            self.value = unpack('!H', self.entity_data)[0]
        if self.entity_len == 3:
            self.value = ord(self.entity_data[0])<<16 | ord(self.entity_data[1])<<8 | ord(self.entity_data[2])
        if self.entity_len == 4:
            self.value = unpack('!I', self.entity_data)[0]

    def compute_id(self, inbuf):
        first = ord(inbuf[0])
        self.id_len = 0
        if (first & 0x80):
            self.id_len = 1
            self.entity_id = first
        elif (first & 0x40):
            self.id_len = 2
            self.entity_id = ord(inbuf[0])<<8 | ord(inbuf[1])
        elif (first & 0x20):
            self.id_len = 3
            self.entity_id = (ord(inbuf[0])<<16) | (ord(inbuf[1])<<8) | (ord(inbuf[2]))
        elif (first & 0x10):
            self.id_len = 4
            self.entity_id = (ord(inbuf[0])<<24) | (ord(inbuf[1])<<16) | (ord(inbuf[2])<<8) | (ord(inbuf[3]))
        self.entity_str = inbuf[0:self.id_len]
        return

    def compute_len(self, inbuf):
        # Here we just handle the size up to 4 bytes
        # The size above will be truncated by the read buffer itself
        first = ord(inbuf[0])
        if (first & 0x80):
            self.len_size = 1
            return first - 0x80
        if (first & 0x40):
            self.len_size = 2
            (c1,c2) = unpack('BB',inbuf[:2])
            return ((c1-0x40)<<8) | (c2)
        if (first & 0x20):
            self.len_size = 3
            (c1, c2, c3) = unpack('BBB',inbuf[:3])
            return ((c1-0x20)<<16) | (c2<<8) | (c3)
        if (first & 0x10):
            self.len_size = 4
            (len) = unpack('!I',inbuf[:4])
            return len
        if (first & 0x08):
            self.len_size = 5
            return -1
        if (first & 0x04):
            self.len_size = 6
            return -1
        if (first & 0x02):
            self.len_size = 7
            return -1
        if (first & 0x01):
            self.len_size = 8
            return -1

    def get_crc_len(self):
        return self.crc_len

    def get_value(self):
        value = self.value
        return value

    def get_data(self):
        return self.entity_data

    def get_id(self):
        return self.entity_id

    def get_str_id(self):
        return self.entity_str

    def get_len(self):
        return self.entity_len

    def get_total_len(self):
        return self.entity_len+self.id_len+self.len_size


# This ithe main Matroska object
class MkvInfo(mediainfo.AVInfo):
    def __init__(self, file):
        mediainfo.AVInfo.__init__(self)
        self.samplerate = 1

        buffer = file.read(80000)
        if len(buffer) == 0:
            # Regular File end
            return None

        # Check the Matroska header
        header = EbmlEntity(buffer)
        if ( header.get_id() == MATROSKA_HEADER_ID ):
            _print("HEADER ID found %08X" % header.get_id() )
            self.valid = 1
            self.mime = 'application/mkv'
            self.type = 'Matroska'
            # Now get the segment
            segment = EbmlEntity(buffer[header.get_total_len():])
            if ( segment.get_id() == MATROSKA_SEGMENT_ID):
                _print("SEGMENT ID found %08X" % segment.get_id() )
                #MEDIACORE = ['title', 'caption', 'comment', 'artist', 'size', 'type', 'subtype',
                #'date', 'keywords', 'country', 'language', 'url']
                segtab = self.process_one_level(segment)
                seginfotab = self.process_one_level(segtab[MATROSKA_SEGMENT_INFO_ID])
                try:
                    # Express scalecode in ms instead of ns
                    # Rescale it to the second
                    scalecode = float(seginfotab[MATROSKA_TIMECODESCALE_ID].get_value() / (1000*1000))
                except:
                    scalecode = 1000
                try:
                    duration = float(unpack('!f', seginfotab[MATROSKA_DURATION_ID].get_data() )[0])
                    duration = float(duration / scalecode)
                    # Express the time in minutes
                    self.length = int(duration/60)
                except:
                    pass
                try:
                    _print ("Searching for id : %X" % MATROSKA_TRACKS_ID)
                    entity = segtab[MATROSKA_TRACKS_ID]
                    self.process_tracks(entity)
                except:
                    _print("TRACKS ID not found !!" )
            else:
                _print("SEGMENT ID not found %08X" % segment.get_id() )
        else:
            self.valid = 0

    def process_tracks(self, tracks):
        tracksbuf = tracks.get_data()
        indice = 0
        while indice < tracks.get_len():
            trackelem = EbmlEntity(tracksbuf[indice:])
            _print ("ELEMENT %X found" % trackelem.get_id())
            self.process_one_track(trackelem)
            indice += trackelem.get_total_len() + trackelem.get_crc_len()

    def process_one_level(self, item):
        buf = item.get_data()
        indice = 0
        tabelem = {}
        while indice < item.get_len():
            elem = EbmlEntity(buf[indice:])
            tabelem[elem.get_id()] = elem
            indice += elem.get_total_len() + elem.get_crc_len()
        return tabelem

    def process_one_track(self, track):
        # Process all the items at the track level
        tabelem = self.process_one_level(track)
        # We have the dict of track eleme, now build the MMPYTHON information
        type = tabelem[MATROSKA_TRACK_TYPE_ID]
        mytype = type.get_value()
        _print ("Track type found with UID %d" % mytype)
        if (mytype == MATROSKA_VIDEO_TRACK ):
            _print("VIDEO TRACK found !!" )
            #VIDEOCORE = ['length', 'encoder', 'bitrate', 'samplerate', 'codec', 'samplebits',
            #     'width', 'height', 'fps', 'aspect']
            vi = mediainfo.VideoInfo()
            try:
                elem = tabelem[MATROSKA_CODEC_ID]
                vi.codec = elem.get_data()
            except:
                vi.codec = 'Unknown'
            try:
                elem = tabelem[MATROSKA_FRAME_DURATION_ID]
                vi.fps = 1 / (pow(10, -9) * (elem.get_value()))
            except:
                vi.fps = 0
            try:
                vinfo = tabelem[MATROSKA_VIDEO_SETTINGS_ID]
                vidtab = self.process_one_level(vinfo)
                vi.width  = vidtab[MATROSKA_VID_WIDTH_ID].get_value()
                vi.height = vidtab[MATROSKA_VID_HEIGHT_ID].get_value()
            except:
                _print("No other info about video track !!!")
            self.video.append(vi)
        elif (mytype == MATROSKA_AUDIO_TRACK ):
            _print("AUDIO TRACK found !!" )
            #AUDIOCORE = ['channels', 'samplerate', 'length', 'encoder', 'codec', 'samplebits',
            #     'bitrate', 'language']
            ai = mediainfo.AudioInfo()
            try:
                elem = tabelem[MATROSKA_TRACK_LANGUAGE_ID]
                ai.language = elem.get_data()
                ai['language'] = elem.get_data()
            except:
                ai.language = 'en'
                ai['language'] = 'en'
            try:
                elem = tabelem[MATROSKA_CODEC_ID]
                ai.codec = elem.get_data()
            except:
                ai.codec = "Unknown"
            try:
                ainfo = tabelem[MATROSKA_AUDIO_SETTINGS_ID]
                audtab = self.process_one_level(vinfo)
                ai.samplerate  = unpack('!f', audtab[MATROSKA_AUDIO_SAMPLERATE_ID].get_value())[0]
                ai.channels = audtab[MATROSKA_AUDIO_CHANNELS_ID].get_value()
            except:
                _print("No other info about audio track !!!")
            self.audio.append(ai)
        elif (mytype == MATROSKA_SUBTITLES_TRACK):
            try:
                elem = tabelem[MATROSKA_TRACK_LANGUAGE_ID]
                language = elem.get_data()
                _print ("Subtitle language found : %s" % elem.get_data() )
            except:
                language = "en" # By default
            self.subtitles.append(language)

        #_print("Found %d elem for this track" % len(tabelem) )

mmpython.registertype( 'application/mkv', ('mkv', 'mka',), mediainfo.TYPE_AV, MkvInfo )