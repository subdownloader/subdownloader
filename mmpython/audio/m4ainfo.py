#!/usr/bin/env python
# Based on a sample implementation posted to daap-dev mailing list by
# Bob Ippolito <bob@redivi.com>
#
# Modifed by Aubin Paul <aubin@outlyer.org> for mmpython/Freevo
#

import struct
from mmpython import mediainfo
import mmpython

#_print = mediainfo._debug

class Mpeg4(mediainfo.MusicInfo):
    def __init__(self, file):
        self.containerTags = ('moov', 'udta', 'trak', 'mdia', 'minf', 'dinf', 'stbl',
                              'meta', 'ilst', '----')
        self.skipTags = {'meta':4 }

        mediainfo.MusicInfo.__init__(self)
        self.valid = 0
        returnval = 0
        while returnval == 0:
            try:
                self.readNextTag(file)
            except ValueError:
                returnval = 1
        if mediainfo.DEBUG and self.valid:
            print self.title
            print self.artist
            print self.album
            print self.year
            print self.encoder

    def readNextTag(self, file):
        length, name = self.readInt(file), self.read(4, file)
        length -= 8
        if length < 0 or length > 1000:
            raise ValueError, "Oops?"
        #print "%r" % str(name) # (%r bytes, starting at %r)" % \
        #  (name, length, file.tell() + 8)
        if name in self.containerTags:
            self.read(self.skipTags.get(name, 0), file)
            data = '[container tag]'
        else:
            data = self.read(length, file)
        if name == '\xa9nam':
            self.title = data[8:]
            self.valid = 1
        if name == '\xa9ART':
            self.artist = data[8:]
            self.valid = 1
        if name == '\xa9alb':
            self.album = data[8:]
            self.valid = 1
        if name == 'trkn':
            # Fix this
            self.trackno = data
            self.valid = 1
        if name == '\xa9day':
            self.year = data[8:]
            self.valid = 1
        if name == '\xa9too':
            self.encoder = data[8:]
            self.valid = 1
        return 0
        
    def read(self, b, file):
        data = file.read(b)
        if len(data) < b:
            raise ValueError, "EOF"
        return data

    def readInt(self, file):
        return struct.unpack('>I', self.read(4, file))[0]
        
mmpython.registertype( 'application/m4a', ('m4a',), mediainfo.TYPE_MUSIC, Mpeg4 )

