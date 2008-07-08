#if 0
# $Id: movinfo.py,v 1.24 2004/07/14 13:42:57 dischi Exp $
# $Log: movinfo.py,v $
# Revision 1.24  2004/07/14 13:42:57  dischi
# small debug updates
#
# Revision 1.23  2004/05/24 12:54:35  dischi
# debug update
#
# Revision 1.22  2004/05/11 15:18:59  dischi
# o more stream infos (like codec)
# o better error handling for bad i18n tables
# o language detection
#
# Revision 1.21  2004/05/10 15:19:59  dischi
# o better stream detection
# o correct length calculation inside the track
# o support for compressed infos
#
# Revision 1.20  2004/03/07 10:27:58  dischi
# Oops
#
# Revision 1.19  2004/03/02 20:48:21  dischi
# fix gettable
#
# Revision 1.18  2003/08/30 09:36:22  dischi
# turn off some debug based on DEBUG
#
# Revision 1.17  2003/07/02 11:17:30  the_krow
# language is now part of the table key
#
# Revision 1.16  2003/06/30 13:17:20  the_krow
# o Refactored mediainfo into factory, synchronizedobject
# o Parsers now register directly at mmpython not at mmpython.mediainfo
# o use mmpython.Factory() instead of mmpython.mediainfo.get_singleton()
# o Bugfix in PNG parser
# o Renamed disc.AudioInfo into disc.AudioDiscInfo
# o Renamed disc.DataInfo into disc.DataDiscInfo
#
# Revision 1.15  2003/06/29 18:30:56  dischi
# length is broken, deactivated it until it is fixed
#
# Revision 1.14  2003/06/29 11:59:35  dischi
# make some debug silent
#
# Revision 1.13  2003/06/20 19:17:22  dischi
# remove filename again and use file.name
#
# Revision 1.12  2003/06/20 14:53:05  the_krow
# Metadata are copied from Quicktime Userdata to MediaInfo fields. This
#  may be broken since it assumes the Quicktime Comment language to be
#  set to 0.
#
# Revision 1.11  2003/06/19 17:31:12  dischi
# error handling (and nonsense data)
#
# Revision 1.10  2003/06/12 18:53:18  the_krow
# OGM detection added.
# .ram is a valid extension to real files
#
# Revision 1.9  2003/06/12 16:56:53  the_krow
# Some Quicktime should work.
#
# Revision 1.8  2003/06/12 15:58:05  the_krow
# QT parsing of i18n metadata
#
# Revision 1.7  2003/06/12 14:43:22  the_krow
# Realmedia file parsing. Title, Artist, Copyright work. Couldn't find
# many technical parameters to retrieve.
# Some initial QT parsing
# added Real to __init__.py
#
# Revision 1.6  2003/06/08 19:53:21  dischi
# also give the filename to init for additional data tests
#
# Revision 1.5  2003/06/08 15:40:26  dischi
# catch exception, raised for small text files
#
# Revision 1.4  2003/06/08 13:44:58  dischi
# Changed all imports to use the complete mmpython path for mediainfo
#
# Revision 1.3  2003/06/08 13:11:38  dischi
# removed print at the end and moved it into register
#
# Revision 1.2  2003/05/13 12:31:43  the_krow
# + Copyright Notice
#
#
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

import re
import struct
import string
import time
import zlib
import fourcc
import mmpython
from mmpython import mediainfo
from movlanguages import *

# http://developer.apple.com/documentation/QuickTime/QTFF/index.html

ATOM_DEBUG = 0

if mediainfo.DEBUG > 1:
    ATOM_DEBUG = 1
    
class MovInfo(mediainfo.AVInfo):
    def __init__(self,file):
        mediainfo.AVInfo.__init__(self)
        self.context = 'video'
        self.valid = 0
        self.mime = 'video/quicktime'
        self.type = 'Quicktime Video'
        h = file.read(8)                
        (size,type) = struct.unpack('>I4s',h)
        if type == 'moov':
            self.valid = 1
        elif type == 'wide':
            self.valid = 1
        else:
            return
        # Extended size
        if size == 1:
            #print "Extended Size"
            size = struct.unpack('>Q', file.read(8))                  
        while self._readatom(file):
            pass
        try:
            info = self.gettable('QTUDTA', 'en')
            self.setitem('title', info, 'nam')
            self.setitem('artist', info, 'aut')
            self.setitem('copyright', info, 'cpy')
        except:
            pass


    def _readatom(self, file):
        
        s = file.read(8)
        if len(s) < 8:
            return 0

        atomsize,atomtype = struct.unpack('>I4s', s)
        if not str(atomtype).decode('latin1').isalnum():
            # stop at nonsense data
            return 0

        if mediainfo.DEBUG or ATOM_DEBUG:
            print "%s [%X]" % (atomtype,atomsize)

        if atomtype == 'udta':
            # Userdata (Metadata)
            pos = 0
            tabl = {}
            i18ntabl = {}
            atomdata = file.read(atomsize-8)
            while pos < atomsize-12:
                (datasize,datatype) = struct.unpack('>I4s', atomdata[pos:pos+8])
                if ord(datatype[0]) == 169:
                    # i18n Metadata... 
                    mypos = 8+pos
                    while mypos < datasize+pos:
                        # first 4 Bytes are i18n header
                        (tlen,lang) = struct.unpack('>HH', atomdata[mypos:mypos+4])
                        i18ntabl[lang] = i18ntabl.get(lang, {})
                        i18ntabl[lang][datatype[1:]] = atomdata[mypos+4:mypos+tlen+4]
                        mypos += tlen+4
                elif datatype == 'WLOC':
                    # Drop Window Location
                    pass
                else:
                    if ord(atomdata[pos+8:pos+datasize][0]) > 1:
                        tabl[datatype] = atomdata[pos+8:pos+datasize]
                pos += datasize
            if len(i18ntabl.keys()) > 0:
                for k in i18ntabl.keys():                
                    if QTLANGUAGES.has_key(k):
                        self.appendtable('QTUDTA', i18ntabl[k], QTLANGUAGES[k])
                        self.appendtable('QTUDTA', tabl, QTLANGUAGES[k])
            else:
                #print "NO i18"
                self.appendtable('QTUDTA', tabl)
             
        elif atomtype == 'trak':
            atomdata = file.read(atomsize-8)
            pos   = 0
            vi    = None
            ai    = None
            info  = None
            while pos < atomsize-8:
                (datasize,datatype) = struct.unpack('>I4s', atomdata[pos:pos+8])
                if datatype == 'tkhd':
                    tkhd = struct.unpack('>6I8x4H36xII', atomdata[pos+8:pos+datasize])
                    vi = mediainfo.VideoInfo()
                    vi.width = tkhd[10] >> 16
                    vi.height = tkhd[11] >> 16
                    vi.id = tkhd[3]

                    ai = mediainfo.AudioInfo()
                    ai.id = tkhd[3]
                    
                    try:
                        # XXX Date number of Seconds is since January 1st 1904!!!
                        # XXX 2082844800 is the difference between Unix and Apple time
                        # XXX Fix me to work on Apple, too
                        self.date = int(tkhd[1]) - 2082844800
                        self.date = time.strftime('%y/%m/%d', time.gmtime(self.date))
                    except Exception, e:
                        print 'ex', e
                    
                elif datatype == 'mdia':
                    pos      += 8
                    datasize -= 8
                    if ATOM_DEBUG:
                        print '--> mdia information'

                    while datasize:
                        mdia = struct.unpack('>I4s', atomdata[pos:pos+8])
                        if mdia[1] == 'mdhd':
                            mdhd = struct.unpack('>IIIIIhh', atomdata[pos+8:pos+8+24])
                            # duration / time scale
                            if vi:
                                vi.length = mdhd[4] / mdhd[3]
                            if ai:
                                ai.length = mdhd[4] / mdhd[3]
                                if mdhd[5] in QTLANGUAGES:
                                    ai.language = QTLANGUAGES[mdhd[5]]
                            # mdhd[6] == quality 
                            self.length = max(self.length, mdhd[4] / mdhd[3])
                        elif mdia[1] == 'minf':
                            # minf has only atoms inside
                            pos -=      (mdia[0] - 8)
                            datasize += (mdia[0] - 8)
                        elif mdia[1] == 'stbl':
                            # stbl has only atoms inside
                            pos -=      (mdia[0] - 8)
                            datasize += (mdia[0] - 8)
                        elif mdia[1] == 'hdlr':
                            hdlr = struct.unpack('>I4s4s', atomdata[pos+8:pos+8+12])
                            if hdlr[1] == 'mhlr':
                                if hdlr[2] == 'vide' and not vi in self.video:
                                    self.video.append(vi)
                                    info = vi
                                if hdlr[2] == 'soun' and not ai in self.audio:
                                    self.audio.append(ai)
                                    info = ai
                        elif mdia[1] == 'stsd':
                            stsd = struct.unpack('>2I', atomdata[pos+8:pos+8+8])
                            if stsd[1] > 0 and info:
                                codec = struct.unpack('>I4s', atomdata[pos+16:pos+16+8])
                                info.codec = codec[1]
                                if info.codec == 'jpeg':
                                    # jpeg is no video, remove it from the list
                                    self.video.remove(vi)
                                    info = None

                        elif mdia[1] == 'dinf':
                            dref = struct.unpack('>I4s', atomdata[pos+8:pos+8+8])
                            if ATOM_DEBUG:
                                print '  --> %s, %s' % mdia
                                print '    --> %s, %s (reference)' % dref
                            
                        elif ATOM_DEBUG:
                            if mdia[1].startswith('st'):
                                print '  --> %s, %s (sample)' % mdia
                            elif mdia[1] in ('vmhd', 'smhd'):
                                print '  --> %s, %s (media information header)' % mdia
                            else:
                                print '  --> %s, %s (unknown)' % mdia

                        pos      += mdia[0]
                        datasize -= mdia[0]

                elif datatype == 'udta' and ATOM_DEBUG:
                    print struct.unpack('>I4s', atomdata[:8])
                elif ATOM_DEBUG:
                    if datatype == 'edts':
                        print "--> %s [%d] (edit list)" % (datatype, datasize)
                    else:
                        print "--> %s [%d] (unknown)" % (datatype, datasize)
                pos += datasize

        elif atomtype == 'mvhd':
            # movie header
            mvhd = struct.unpack('>6I2h', file.read(28))
            self.length = max(self.length, mvhd[4] / mvhd[3])
            self.volume = mvhd[6]
            file.seek(atomsize-8-28,1)

        elif atomtype == 'cmov':
            # compressed movie
            datasize, atomtype = struct.unpack('>I4s', file.read(8))
            if not atomtype == 'dcom':
                return atomsize

            method = struct.unpack('>4s', file.read(datasize-8))[0]

            datasize, atomtype = struct.unpack('>I4s', file.read(8))
            if not atomtype == 'cmvd':
                return atomsize

            if method == 'zlib':
                data = file.read(datasize-8)
                try:
                    decompressed = zlib.decompress(data)
                except Exception, e:
                    try:
                        decompressed = zlib.decompress(data[4:])
                    except Exception, e:
                        if mediainfo.DEBUG:
                            print 'unable to decompress atom'
                        return atomsize
                import StringIO
                decompressedIO = StringIO.StringIO(decompressed)
                while self._readatom(decompressedIO):
                    pass
                
            else:
                if mediainfo.DEBUG:
                    print 'unknown compression %s' % method
                # unknown compression method
                file.seek(datasize-8,1)
        
        elif atomtype == 'moov':
            # decompressed movie info
            while self._readatom(file):
                pass
            
        elif atomtype == 'mdat':
            pos = file.tell() + atomsize - 8
            # maybe there is data inside the mdat
            if ATOM_DEBUG:
                print 'parsing mdat'
            while self._readatom(file):
                pass
            if ATOM_DEBUG:
                print 'end of mdat'
            file.seek(pos, 0)
            
        
        else:
            if ATOM_DEBUG and not atomtype in ('wide', 'free'):
                print 'unhandled base atom %s' % atomtype

            # Skip unknown atoms
            try:
                file.seek(atomsize-8,1)
            except IOError:
                return 0

        return atomsize
        
mmpython.registertype( 'video/quicktime', ('mov', 'qt'), mediainfo.TYPE_AV, MovInfo )

# doc links:
# [1] http://developer.apple.com/documentation/QuickTime/QTFF/QTFFChap4/chapter_5_section_2.html#//apple_ref/doc/uid/TP40000939-CH206-BBCBIICE
