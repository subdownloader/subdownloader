#if 0
# -----------------------------------------------------------------------
# ogminfo.py - Ogg Streaming Video Files
# -----------------------------------------------------------------------
# $Id: ogminfo.py,v 1.16 2004/05/20 19:54:52 dischi Exp $
#
# $Log: ogminfo.py,v $
# Revision 1.16  2004/05/20 19:54:52  dischi
# more ogm fixes
#
# Revision 1.15  2004/05/20 08:49:29  dischi
# more ogm fixes, better length calc (again)
#
# Revision 1.14  2004/05/18 21:55:52  dischi
# o get correct length for ogm files
# o set metadat for the different streams
# o chapter support
#
# Revision 1.13  2003/09/22 16:21:54  the_krow
# utf-8 comment parsing
#
# Revision 1.12  2003/09/09 19:57:08  dischi
# bad hack to make length oggs work
#
# Revision 1.11  2003/09/09 19:32:26  dischi
# bugfix for finding oggs
#
# Revision 1.10  2003/08/04 08:44:51  the_krow
# Maximum iterations field added as suggested by Magnus in the
# freevo list.
#
# Revision 1.9  2003/07/13 15:20:53  dischi
# make the module quiet
#
# Revision 1.8  2003/07/10 11:16:31  the_krow
# o Added length calculation for audio only files.
# o In the future we will use this as a general parser for ogm/ogg
#
# Revision 1.7  2003/06/30 13:17:20  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
#
# Revision 1.6  2003/06/29 12:11:16  dischi
# changed print to _print
#
# Revision 1.5  2003/06/23 20:48:11  the_krow
# width + height fixes for OGM files
#
# Revision 1.4  2003/06/23 13:20:51  the_krow
# basic parsing should now work.
#
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


from mmpython import mediainfo
import mmpython
import struct
import re
import stat
import os

import fourcc

PACKET_TYPE_HEADER   = 0x01
PACKED_TYPE_METADATA = 0x03
PACKED_TYPE_SETUP    = 0x05
PACKET_TYPE_BITS     = 0x07
PACKET_IS_SYNCPOINT  = 0x08

#VORBIS_VIDEO_PACKET_INFO = 'video'

STREAM_HEADER_VIDEO = '<4sIQQIIHII'
STREAM_HEADER_AUDIO = '<4sIQQIIHHHI'

_print = mediainfo._debug

VORBISCOMMENT_tags = { 'title': 'TITLE',
                       'album': 'ALBUM',
                       'artist': 'ARTIST',
                       'comment': 'COMMENT',
                       'date': 'DATE',
                       'encoder': 'ENCODER',
                       'trackno': 'TRACKNUMBER',
                       'language': 'LANGUAGE',
                       'genre': 'GENRE',
                     }

MAXITERATIONS = 10

class OgmInfo(mediainfo.AVInfo):
    def __init__(self, file):
        mediainfo.AVInfo.__init__(self)
        self.samplerate  = 1
        self.all_streams = []           # used to add meta data to streams
        self.all_header  = []

        for i in range(MAXITERATIONS):
            granule, nextlen = self._parseOGGS(file)
            if granule == None:
                break
            elif granule > 0:
                # ok, file started
                break

        # seek to the end of the stream, to avoid scanning the whole file
        if (os.stat(file.name)[stat.ST_SIZE] > 50000):
            file.seek(os.stat(file.name)[stat.ST_SIZE]-49000)

        # read the rest of the file into a buffer
        h = file.read()

        # find last OggS to get length info
        if len(h) > 200:
            idx = h.find('OggS')
            pos = -49000 + idx
            if idx:
                file.seek(os.stat(file.name)[stat.ST_SIZE] + pos)
            while 1:
                granule, nextlen = self._parseOGGS(file)
                if not nextlen:
                    break

        # Copy metadata to the streams
        if len(self.all_header) == len(self.all_streams):
            for i in range(len(self.all_header)):
                # set length
                self.length = max(self.all_streams[i].length, self.length)

                # get meta info
                for key in self.all_streams[i].keys:
                    if self.all_header[i].has_key(key):
                        self.all_streams[i][key] = self.all_header[i][key]
                        del self.all_header[i][key]
                    if self.all_header[i].has_key(key.upper()):
                        self.all_streams[i][key] = self.all_header[i][key.upper()]
                        del self.all_header[i][key.upper()]

                # Extract subtitles:
                if hasattr(self.all_streams[i], 'type') and \
                   self.all_streams[i].type == 'subtitle':
                    self.subtitles.append(self.all_streams[i].language)

                # Chapter parser
                if self.all_header[i].has_key('CHAPTER01') and not self.chapters:
                    while 1:
                        s = 'CHAPTER0%s' % (len(self.chapters) + 1)
                        if len(s) < 9:
                            s = '0' + s
                        if self.all_header[i].has_key(s) and \
                               self.all_header[i].has_key(s + 'NAME'):
                            pos = self.all_header[i][s]
                            try:
                                pos = int(pos)
                            except ValueError:
                                new_pos = 0
                                for v in pos.split(':'):
                                    new_pos = new_pos * 60 + float(v)
                                pos = int(new_pos)
                                
                            c = mediainfo.ChapterInfo(self.all_header[i][s + 'NAME'], pos)
                            del self.all_header[i][s + 'NAME']
                            del self.all_header[i][s]
                            self.chapters.append(c)
                        else:
                            break

        for stream in self.all_streams:
            if not stream.length:
                stream.length = self.length
                
        # Copy Metadata from tables into the main set of attributes        
        for header in self.all_header:
            self.appendtable('VORBISCOMMENT', header)

        self.tag_map = { ('VORBISCOMMENT', 'en') : VORBISCOMMENT_tags }
        for k in self.tag_map.keys():
            _print(k)
            map(lambda x:self.setitem(x,self.gettable(k[0],k[1]),
                                      self.tag_map[k][x]), self.tag_map[k].keys())

        
    def _parseOGGS(self,file):
        h = file.read(27)
        if len(h) == 0:
            # Regular File end
            return None, None
        elif len(h) < 27:
            _print("%d Bytes of Garbage found after End." % len(h))
            return None, None
        if h[:4] != "OggS":        
            self.valid = 0
            _print("Invalid Ogg")
            return None, None

        self.valid = 1
        version = ord(h[4])
        if version != 0:
            _print("Unsupported OGG/OGM Version %d." % version)
            return None, None
        head = struct.unpack('<BQIIIB', h[5:])
        headertype, granulepos, serial, pageseqno, checksum, pageSegCount = head

        self.valid = 1
        self.mime = 'application/ogm'
        self.type = 'OGG Media'
        tab = file.read(pageSegCount)
        nextlen = 0
        for i in range(len(tab)):
            nextlen += ord(tab[i])
        else:
            h = file.read(1)
            packettype = ord(h[0]) & PACKET_TYPE_BITS 
            if packettype == PACKET_TYPE_HEADER:
                h += file.read(nextlen-1)
                self._parseHeader(h, granulepos)
            elif packettype == PACKED_TYPE_METADATA:
                h += file.read(nextlen-1)
                self._parseMeta(h)
            else:
                file.seek(nextlen-1,1)
        if len(self.all_streams) > serial:
            stream = self.all_streams[serial]
            if hasattr(stream, 'samplerate') and \
                   stream.samplerate:
                stream.length = granulepos / stream.samplerate
            elif hasattr(stream, 'bitrate') and \
                     stream.bitrate:
                stream.length = granulepos / stream.bitrate

        return granulepos, nextlen + 27 + pageSegCount

        
    def _parseMeta(self,h):
        flags = ord(h[0])
        headerlen = len(h)
        if headerlen >= 7 and h[1:7] == 'vorbis':
            header = {}
            nextlen, self.encoder = self._extractHeaderString(h[7:])
            numItems = struct.unpack('<I',h[7+nextlen:7+nextlen+4])[0]
            start = 7+4+nextlen
            for i in range(numItems):
                (nextlen, s) = self._extractHeaderString(h[start:])
                start += nextlen
                if s:
                    a = re.split('=',s)
                    header[(a[0]).upper()]=a[1]
            # Put Header fields into info fields
            self.type = 'OGG Vorbis'
            self.subtype = ''
            self.all_header.append(header)

            
    def _parseHeader(self,header,granule):
        headerlen = len(header)
        flags = ord(header[0])

        if headerlen >= 30 and header[1:7] == 'vorbis':
            #print("Vorbis Audio Header")
            ai = mediainfo.AudioInfo()
            ai.version, ai.channels, ai.samplerate, bitrate_max, ai.bitrate, \
                        bitrate_min, blocksize, framing = \
                        struct.unpack('<IBIiiiBB',header[7:7+23])
            ai.codec = 'Vorbis'
            #ai.granule = granule
            #ai.length = granule / ai.samplerate
            self.audio.append(ai)
            self.all_streams.append(ai)
            
        elif headerlen >= 7 and header[1:7] == 'theora':
            #print "Theora Header"
            # Theora Header
            # XXX Finish Me
            vi = mediainfo.VideoInfo()
            vi.codec = 'theora'
            self.video.append(vi)
            self.all_streams.append(vi)

        elif headerlen >= 142 and header[1:36] == 'Direct Show Samples embedded in Ogg':
            #print 'Direct Show Samples embedded in Ogg'
            # Old Directshow format
            # XXX Finish Me
            vi = mediainfo.VideoInfo()
            vi.codec = 'dshow'
            self.video.append(vi)
            self.all_streams.append(vi)

        elif flags & PACKET_TYPE_BITS == PACKET_TYPE_HEADER and headerlen >= struct.calcsize(STREAM_HEADER_VIDEO)+1:
            #print "New Directshow Format"
            # New Directshow Format
            htype = header[1:9]

            if htype[:5] == 'video':
                streamheader = struct.unpack( STREAM_HEADER_VIDEO, header[9:struct.calcsize(STREAM_HEADER_VIDEO)+9] )
                vi = mediainfo.VideoInfo()
                (type, ssize, timeunit, samplerate, vi.length, buffersize, \
                 vi.bitrate, vi.width, vi.height) = streamheader

                vi.width /= 65536
                vi.height /= 65536
                # XXX length, bitrate are very wrong
                try:
                    vi.codec = fourcc.RIFFCODEC[type]
                except:
                    vi.codec = 'Unknown (%s)' % type
                vi.fps = 10000000 / timeunit
                self.video.append(vi)
                self.all_streams.append(vi)

            elif htype[:5] == 'audio':
                streamheader = struct.unpack( STREAM_HEADER_AUDIO, header[9:struct.calcsize(STREAM_HEADER_AUDIO)+9] )
                ai = mediainfo.AudioInfo()
                (type, ssize, timeunit, ai.samplerate, ai.length, buffersize, ai.bitrate, ai.channels, bloc, ai.bitrate) = streamheader
                self.samplerate = ai.samplerate
                _print("Samplerate %d" % self.samplerate)
                self.audio.append(ai)
                self.all_streams.append(ai)

            elif htype[:4] == 'text':
                subtitle = mediainfo.MediaInfo()
                subtitle.keys.append('language')
                subtitle.type   = 'subtitle'
                subtitle.length = 0
                self.all_streams.append(subtitle)
                
        else:
            _print("Unknown Header")
              

    def _extractHeaderString(self,header):
        len = struct.unpack( '<I', header[:4] )[0]
        try:
            return (len+4,unicode(header[4:4+len], 'utf-8'))
        except:
            return (len+4,None)


mmpython.registertype( 'application/ogg', ('ogm', 'ogg',), mediainfo.TYPE_AV, OgmInfo )
