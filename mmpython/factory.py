#if 0
# -----------------------------------------------------------------------
# $Id: factory.py,v 1.20.2.1 2005/05/07 11:37:08 dischi Exp $
# -----------------------------------------------------------------------
# $Log: factory.py,v $
# Revision 1.20.2.1  2005/05/07 11:37:08  dischi
# make sure all strings are unicode
#
# Revision 1.20  2004/05/29 12:30:36  dischi
# add function to correct data from the different mime modules
#
# Revision 1.19  2004/05/28 19:32:31  dischi
# remove old stuff
#
# Revision 1.18  2004/05/17 19:10:57  dischi
# better DEBUG handling
#
# Revision 1.17  2004/05/02 08:28:20  dischi
# dvd iso support
#
# Revision 1.16  2004/02/03 20:41:18  dischi
# add directory support
#
# Revision 1.15  2004/01/31 12:25:20  dischi
# better ext checking
#
# Revision 1.13  2003/09/22 16:24:58  the_krow
# o added flac
# o try-except block around ioctl since it is not avaiable in all OS
#
# Revision 1.12  2003/09/14 13:50:42  dischi
# make it possible to scan extention based only
#
# Revision 1.11  2003/09/01 19:23:23  dischi
# ignore case when searching the correct extention
#
# Revision 1.10  2003/08/30 12:16:24  dischi
# special handling for directories
#
# Revision 1.8  2003/08/26 18:01:26  outlyer
# Patch from Lars Eggert for FreeBSD support
#
# Revision 1.4  2003/07/04 15:34:45  outlyer
# Allow 'cdda' as well as 'cd' since we get that sometimes, and make sure
# we import urllib.
#
# Revision 1.3  2003/07/02 09:32:16  the_krow
# More Keys
# import traceback was missing in factory
#
# Revision 1.1  2003/06/30 13:17:18  the_krow
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

import mediainfo
import stat
import os
import urlparse
import traceback
import urllib

DEBUG = 0

try:
    DEBUG = int(os.environ['MMPYTHON_DEBUG'])
except:
    pass



def isurl(url):
    return url.find('://') > 0

class Factory:
    """
    Abstract Factory for the creation of MediaInfo instances. The different Methods
    create MediaInfo objects by parsing the given medium. 
    """
    def __init__(self):
        self.extmap = {}
        self.mimemap = {}
        self.types = []
        self.device_types = []
        self.directory_types = []
        self.stream_types = []
        
    def create_from_file(self, file, ext_only=0):
        """
        create based on the file stream 'file
        """
        # Check extension as a hint
        for e in self.extmap.keys():
            if DEBUG > 1: print "trying ext %s" % e
            if file.name.lower().endswith(e.lower()):
                if DEBUG == 1: print "trying ext %s" % e
                try:
                    file.seek(0,0)
                    t = self.extmap[e][3](file)
                    if t.valid: return t
                except:
                    if DEBUG:
                        traceback.print_exc()

        # no searching on all types
        if ext_only:
            return None

        if DEBUG:
            print "No Type found by Extension. Trying all"

        for e in self.types:
            if DEBUG: print "Trying %s" % e[0]
            try:
                file.seek(0,0)
                t = e[3](file)
                if t.valid:
                    if DEBUG: print 'found'
                    return t
            except:
                if DEBUG:
                    traceback.print_exc()
        if DEBUG: print 'not found'
        return None


    def create_from_url(self,url):
        """
        Create information for urls. This includes file:// and cd://
        """
        split  = urlparse.urlsplit(url)
        scheme = split[0]

        if scheme == 'file':
            (scheme, location, path, query, fragment) = split
            return self.create_from_filename(location+path)

        elif scheme == 'cdda':
            r = self.create_from_filename(split[4])
            if r:
                r.url = url
            return r
        
        elif scheme == 'http':
            # Quick Hack for webradio support
            # We will need some more soffisticated and generic construction
            # method for this. Perhaps move file.open stuff into __init__
            # instead of doing it here...
            for e in self.stream_types:
                if DEBUG: print 'Trying %s' % e[0]
                t = e[3](url)
                if t.valid:
                    t.url = url
                    return t
            
        else:
            (scheme, location, path, query, fragment) = split
            uhandle = urllib.urlopen(url)
            mime = uhandle.info().gettype()
            print "Trying %s" % mime
            if self.mimemap.has_key(mime):
                t = self.mimemap[mime][3](file)
                if t.valid: return t
            # XXX Todo: Try other types
        pass


    def create_from_filename(self, filename, ext_only=0):
        """
        Create information for the given filename
        """
        if os.path.isdir(filename):
            return None
        if os.path.isfile(filename):
            try:
                f = open(filename,'rb')
            except IOError:
                print 'IOError reading %s' % filename
                return None
            r = self.create_from_file(f, ext_only)
            f.close()
            if r:
                r.correct_data()
                r.url = 'file://%s' % os.path.abspath(filename)
                return r
        return None
    

    def create_from_device(self,devicename):
        """
        Create information from the device. Currently only rom drives
        are supported.
        """
        for e in self.device_types:
            if DEBUG: print 'Trying %s' % e[0]
            t = e[3](devicename)
            if t.valid:
                t.url = 'file://%s' % os.path.abspath(devicename)
                return t
        return None
            

    def create_from_directory(self, dirname):
        """
        Create information from the directory.
        """
        for e in self.directory_types:
            if DEBUG: print 'Trying %s' % e[0]
            t = e[3](dirname)
            if t.valid:
                return t
        return None
            

    def create(self, name, ext_only=0):
        """
        Global 'create' function. This function calls the different
        'create_from_'-functions.
        """
        try:
            if isurl(name):
                return self.create_from_url(name)
            if not os.path.exists(name):
                return None
            try:
                if (os.uname()[0] == 'FreeBSD' and \
                    stat.S_ISCHR(os.stat(name)[stat.ST_MODE])) \
                    or stat.S_ISBLK(os.stat(name)[stat.ST_MODE]):
                    return self.create_from_device(name)
            except AttributeError:
                pass            
            if os.path.isdir(name):
                return self.create_from_directory(name)
            return self.create_from_filename(name, ext_only)
        except:
            print 'mmpython.create error:'
            traceback.print_exc()
            print
            print 'Please report this bug to the Freevo mailing list'
            return None


        
    def register(self,mimetype,extensions,type,c):
        """
        register the parser to mmpython
        """
        if DEBUG > 0:
            print "%s registered" % mimetype
        tuple = (mimetype,extensions,type,c)

        if extensions == mediainfo.EXTENSION_DEVICE:
            self.device_types.append(tuple)
        elif extensions == mediainfo.EXTENSION_DIRECTORY:
            self.directory_types.append(tuple)
        elif extensions == mediainfo.EXTENSION_STREAM:
            self.stream_types.append(tuple)
        else:
            self.types.append(tuple)
            for e in extensions:
                self.extmap[e] = tuple
            self.mimemap[mimetype] = tuple


    def get(self, mimetype, extensions):
        """
        return the object for mimetype/extensions or None
        """
        if extensions == mediainfo.EXTENSION_DEVICE:
            l = self.device_types
        elif extensions == mediainfo.EXTENSION_DIRECTORY:
            l = self.directory_types
        elif extensions == mediainfo.EXTENSION_STREAM:
            l = self.stream_types
        else:
            l = self.types

        for info in l:
            if info[0] == mimetype and info[1] == extensions:
                return info[3]

        return None
