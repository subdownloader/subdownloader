#if 0
# -----------------------------------------------------------------------
# $Id: eyed3info.py,v 1.16 2005/01/01 14:18:11 dischi Exp $
# -----------------------------------------------------------------------
# $Log: eyed3info.py,v $
# Revision 1.16  2005/01/01 14:18:11  dischi
# add samplerate, bitrate and mode
#
# Revision 1.15  2004/09/09 02:45:58  outlyer
# Add the TPOS tag for multiple disc sets.
#
# Revision 1.14  2004/07/21 18:54:36  outlyer
# Big bugfix.
#
# If a mp3 lacks a genre, then nothing after the genre parsing works. This breaks
# calculating the length, among other things because it's all in a try except, so
# self.length takes on a random value. I was getting track lengths like 20000 seconds
# until I made this change.
#
# Revision 1.13  2004/07/11 12:06:03  dischi
# add genre parsing
#
# Revision 1.12  2004/07/07 09:35:50  dischi
# remove guessing of tracknum in TCON
#
# Revision 1.11  2004/05/29 12:31:36  dischi
# try to find trackof in TCON or trackno
#
# Revision 1.10  2004/02/08 17:42:56  dischi
# reduce debug
#
# Revision 1.9  2003/08/30 09:36:22  dischi
# turn off some debug based on DEBUG
#
# Revision 1.8  2003/07/10 13:05:05  the_krow
# o id3v2 tabled added to eyed3
# o type changed to MUSIC
#
# Revision 1.7  2003/07/02 20:15:42  dischi
# return nothing, not 0
#
# Revision 1.6  2003/06/30 13:17:18  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
#
# Revision 1.5  2003/06/30 11:38:22  dischi
# bugfix
#
# Revision 1.4  2003/06/29 18:30:14  dischi
# many many fixes
#
# Revision 1.3  2003/06/29 12:03:41  dischi
# fixed it to be _real_ eyed3 info
#
# Revision 1.2  2003/06/20 19:17:22  dischi
# remove filename again and use file.name
#
# Revision 1.1  2003/06/09 23:13:21  the_krow
# bugfix: unknown files are now resetted before trying if they are valid
# first rudimentary eyed3 mp3 parser added
#
#
# -----------------------------------------------------------------------
# MMPython - Media Metadata for Python
# Copyright (C) 2003 Thomas Schueppel, et. al
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#
# Most of the code of this module was taken from Vivake Guptas mp3info
# code. Below is his copyright notice. All credit to him.
#
# Copyright (c) 2002 Vivake Gupta (vivakeATomniscia.org).  All rights reserved.
# This software is maintained by Vivake (vivakeATomniscia.org) and is available at:
#     http://www.omniscia.org/~vivake/python/MP3Info.py
#
#


from mmpython import mediainfo
import mmpython

from eyeD3 import tag as eyeD3_tag
from eyeD3 import frames as eyeD3_frames

import os
import struct
import traceback
import id3 as id3info

MP3_INFO_TABLE = { "APIC": "picture",
                   "LINK": "link",
                   "TALB": "album",
                   "TCOM": "composer",
                   "TCOP": "copyright",
                   "TDOR": "release",
                   "TYER": "date",
                   "TEXT": "text",
                   "TIT2": "title",
                   "TLAN": "language",
                   "TLEN": "length",
                   "TMED": "media_type",
                   "TPE1": "artist",
                   "TPE2": "artist",
                   "TRCK": "trackno",
                   "TPOS": "discs"}

_bitrates = [
    [ # MPEG-2 & 2.5
        [0,32,48,56, 64, 80, 96,112,128,144,160,176,192,224,256,None], # Layer 1
        [0, 8,16,24, 32, 40, 48, 56, 64, 80, 96,112,128,144,160,None], # Layer 2
        [0, 8,16,24, 32, 40, 48, 56, 64, 80, 96,112,128,144,160,None]  # Layer 3
    ],

    [ # MPEG-1
        [0,32,64,96,128,160,192,224,256,288,320,352,384,416,448,None], # Layer 1
        [0,32,48,56, 64, 80, 96,112,128,160,192,224,256,320,384,None], # Layer 2
        [0,32,40,48, 56, 64, 80, 96,112,128,160,192,224,256,320,None]  # Layer 3
    ]
]

_samplerates = [
    [ 11025, 12000,  8000, None], # MPEG-2.5
    [  None,  None,  None, None], # reserved
    [ 22050, 24000, 16000, None], # MPEG-2
    [ 44100, 48000, 32000, None], # MPEG-1
]

_modes = [ "stereo", "joint stereo", "dual channel", "mono" ]

_MP3_HEADER_SEEK_LIMIT = 4096

class eyeD3Info(mediainfo.MusicInfo):
   
   fileName       = str();
   fileSize       = int();
   
   def __init__(self, file, tagVersion = eyeD3_tag.ID3_ANY_VERSION):
      mediainfo.MusicInfo.__init__(self)
      self.fileName = file.name;
      self.valid = 1
      self.mime = 'audio/mp3'

      if not eyeD3_tag.isMp3File(file.name):
         self.valid = 0
         return

      id3 = None
      try:
         id3 = eyeD3_tag.Mp3AudioFile(file.name)
      except eyeD3_tag.TagException:
         try:
            id3 = eyeD3_tag.Mp3AudioFile(file.name)
         except eyeD3_tag.InvalidAudioFormatException:
            # File is not an MP3
            self.valid = 0
            return
         except:
            # The MP3 tag decoder crashed, assume the file is still
            # MP3 and try to play it anyway
            if mediainfo.DEBUG:
               print 'music: oops, mp3 tag parsing failed!'
               print 'music: filename = "%s"' % file.name
               traceback.print_exc()
      except:
         # The MP3 tag decoder crashed, assume the file is still
         # MP3 and try to play it anyway
         if mediainfo.DEBUG:
            print 'music: oops, mp3 tag parsing failed!'
            print 'music: filename = "%s"' % file.name
            traceback.print_exc()

      if not self.valid:
         return

      if mediainfo.DEBUG > 1:
         print id3.tag.frames
      try:
         if id3 and id3.tag:
            for k in MP3_INFO_TABLE:
               if id3.tag.frames[k]:
                  if k == 'APIC':
                     pass 
                  else:
                     setattr(self, MP3_INFO_TABLE[k], id3.tag.frames[k][0].text)
            if id3.tag.getYear():
               self.date = id3.tag.getYear()
            tab = {}
            for f in id3.tag.frames:
                if f.__class__ is eyeD3_frames.TextFrame:                
                    tab[f.header.id] = f.text
                elif f.__class__ is eyeD3_frames.UserTextFrame:
                    tab[f.header.id] = f.text
                elif f.__class__ is eyeD3_frames.DateFrame:
                    tab[f.header.id] = f.date_str
                elif f.__class__ is eyeD3_frames.CommentFrame:
                    tab[f.header.id] = f.comment
                elif f.__class__ is eyeD3_frames.URLFrame:
                    tab[f.header.id] = f.url
                elif f.__class__ is eyeD3_frames.UserURLFrame:
                    tab[f.header.id] = f.url
                elif mediainfo.DEBUG:
                   print f.__class__
            self.appendtable('id3v2', tab, 'en')

            if id3.tag.frames['TCON']:
               genre = None
               tcon = id3.tag.frames['TCON'][0].text
               try:
                  genre = int(tcon)
               except:
                  try:
                      genre = int(tcon[1:tcon.find(')')])
                  except ValueError:
                      pass
               if genre is not None:
                  try:
                     self.genre = id3info.GENRE_LIST[genre]
                  except:
                     pass
            # and some tools store it as trackno/trackof in TRCK
            if not self['trackof'] and self['trackno'] and self['trackno'].find('/') > 0:
                self['trackof'] = self['trackno'][self['trackno'].find('/')+1:]
                self['trackno'] = self['trackno'][:self['trackno'].find('/')]
         if id3:
            self.length = id3.getPlayTime()
      except:
         if mediainfo.DEBUG:
            traceback.print_exc()
      offset, header = self._find_header(file)
      if offset == -1 or header is None:
         return

      self._parse_header(header)
      

   def _find_header(self, file):
      file.seek(0, 0)
      amount_read = 0
      
      # see if we get lucky with the first four bytes
      amt = 4
      
      while amount_read < _MP3_HEADER_SEEK_LIMIT:
         header = file.read(amt)
         if len(header) < amt:
            # awfully short file. just give up.
            return -1, None

         amount_read = amount_read + len(header)
         
         # on the next read, grab a lot more
         amt = 500
         
         # look for the sync byte
         offset = header.find(chr(255))
         if offset == -1:
            continue
             
         # looks good, make sure we have the next 3 bytes after this
         # because the header is 4 bytes including sync
         if offset + 4 > len(header):
            more = file.read(4)
            if len(more) < 4:
               # end of file. can't find a header
               return -1, None
            amount_read = amount_read + 4
            header = header + more

         # the sync flag is also in the next byte, the first 3 bits
         # must also be set
         if ord(header[offset+1]) >> 5 != 7:
            continue

         # ok, that's it, looks like we have the header
         return amount_read - len(header) + offset, header[offset:offset+4]

      # couldn't find the header
      return -1, None


   def _parse_header(self, header):
      # http://mpgedit.org/mpgedit/mpeg_format/MP3Format.html
      bytes = struct.unpack('>i', header)[0]
      mpeg_version =    (bytes >> 19) & 3
      layer =           (bytes >> 17) & 3
      bitrate =         (bytes >> 12) & 15
      samplerate =      (bytes >> 10) & 3
      mode =            (bytes >> 6)  & 3

      if mpeg_version == 0:
         self.version = 2.5
      elif mpeg_version == 2:
         self.version = 2
      elif mpeg_version == 3:
         self.version = 1
      else:
         return

      if layer > 0:
         layer = 4 - layer
      else:
         return

      self.bitrate = _bitrates[mpeg_version & 1][layer - 1][bitrate]
      self.samplerate = _samplerates[mpeg_version][samplerate]

      if self.bitrate is None or self.samplerate is None:
         return

      self.mode = _modes[mode]
      self.keys.append('mode')


mmpython.registertype( 'audio/mp3', ('mp3',), mediainfo.TYPE_MUSIC, eyeD3Info )
