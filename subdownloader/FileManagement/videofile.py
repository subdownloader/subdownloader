# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
import os.path
import struct

from subdownloader import metadata

log = logging.getLogger('subdownloader.videofile')

"""
List of known video extensions.
"""
VIDEOS_EXT = ['3g2', '3gp', '3gp2', '3gpp', '60d', 'ajp', 'asf', 'asx',
              'avchd', 'avi', 'bik', 'bin', 'bix', 'box', 'cam', 'cue', 'dat', 'divx',
              'dmf', 'dv', 'dvr-ms', 'evo', 'flc', 'fli', 'flic', 'flv', 'flx', 'gvi',
              'gvp', 'h264', 'm1v', 'm2p', 'm2ts', 'm2v', 'm4e', 'm4v', 'mjp', 'mjpeg',
              'mjpg', 'mkv', 'moov', 'mov', 'movhd', 'movie', 'movx', 'mp4', 'mpe',
              'mpeg', 'mpg', 'mpv', 'mpv2', 'mxf', 'nsv', 'nut', 'ogm', 'ogv', 'omf',
              'ps', 'qt', 'ram', 'rm', 'rmvb', 'swf', 'ts', 'vfw', 'vid', 'video',
              'viv', 'vivo', 'vob', 'vro', 'webm', 'wm', 'wmv', 'wmx', 'wrap', 'wvx',
              'wx', 'x264', 'xvid']


class NotAVideoException(Exception):
    """
    Exception used to indicate a certain file is not a video.
    """
    def __init__(self, filePath, e):
        self._e = e
        self._filePath = filePath

    def __str__(self):
        return '{0} is not a video. Error is {1}.'.format(self._filePath, self._e)


class VideoFile(object):
    """
    Represents a local video file.
    """

    def __init__(self, filepath):
        """
        Initialize a new local VideoFile
        :param filepath: path of the videofile as string
        """
        log.debug('VideoFile.__init__("{}")'.format(filepath))
        # FIXME: calculate hash, fps, time at request time
        try:
            self._filepath = os.path.realpath(filepath)
            self._size = os.path.getsize(filepath)
            # FIXME: calculate hash on request?
            self._hash = self._calculate_OSDB_hash()
        except Exception as e:
            raise NotAVideoException(filepath, e)
        # Initialize metadata on request.
        self._metadata_init = False
        self._fps = 0
        self._time_ms = 0

        self._subs = []
        self.nos_subs = []
        self._osdb_info = {}
        self._movie_info = {}

    def _read_metadata(self):
        """
        Private function to read (if not read already) and store the metadata of the local VideoFile.
        """
        if self._metadata_init:
            return
        try:
            data = metadata.parse(self._filepath)
            videos = data.get_metadata()
            if len(videos) > 0:
                self._fps = videos[0].framerate
                self._time_ms = videos[0].duration_ms
        except:
            # Two possibilities: the parser failed or the file is no video
            # FIXME: log exception
            pass
        self._metadata_init = True

    def get_filepath(self):
        return self._filepath

    def get_folderpath(self):
        """
        Get the folder of this VideoFile
        :return: folder as string
        """
        return os.path.dirname(self._filepath)

    def get_filename(self):
        """
        Get filename of this VideoFile
        :return: file name as string
        """
        return os.path.basename(self._filepath)

    def get_size(self):
        """
        Get size of this VideoFile in bytes
        :return: size as integer
        """
        return self._size

    def get_hash(self):
        """
        Get the hash of this local videofile
        :return: hash as string
        """
        self._read_metadata()
        return self._hash

    def get_fps(self):
        """
        Get the fps (frames per second) of this VideoFile
        :return: fps as integer/float
        """
        self._read_metadata()
        return self._fps

    def get_time_ms(self):
        """
        Get the length of this VideoFile in milliseconds
        :return: time duration as integer/float
        """
        self._read_metadata()
        return self._time_ms

    def setOsdbInfo(self, info):
        self._osdb_info = info

    def getOsdbInfo(self):
        return self._osdb_info

    def hasOsdbInfo(self):
        return len(self._osdb_info) != 0

    def hasMovieName(self):
        try:
            return self._movie_info["MovieName"] != ""
        except:
            return False

    def getMovieName(self):
        try:
            return self._movie_info["MovieName"]
        except:
            return ""

    def hasMovieNameEng(self):
        try:
            return self._osdb_info["MovieNameEng"] != ""
        except NameError:
            return False

    def getMovieNameEng(self):
        return self._osdb_info["MovieNameEng"]

    def hasSubtitles(self):
        return len(self._subs) != 0

    def setSubtitles(self, subs):
        if len(self._subs):
            for sub in subs:
                self.addSubtitle(sub)
        else:
            self._subs = subs

    def addSubtitle(self, sub):
        if isinstance(sub, list):
            self._subs + sub
        else:
            for _sub in self._subs:
                if sub.get_hash() == _sub.get_hash():
                    return False
            self._subs.append(sub)
            return True

    def getSubtitle(self, hash):
        """returns the subtitle by its hash if any"""
        for sub in self.getSubtitles():
            if sub.get_hash() == hash:
                return sub
        return None

    def getSubtitles(self):
        """return only local subtitles"""
        return self._subs

    def getOneSubtitle(self):
        return self._subs[0]

    def getOnlineSubtitles(self):
        subs = []
        for sub in self.getSubtitles():
            if sub.isOnline():
                subs.append(sub)
        return subs

    def getTotalSubtitles(self):
        """return total number of subtitles, local and remote"""
        local = len(self._subs) + len(self.nos_subs)
        try:
            return len(self._osdb_info) + local
        except NameError:
            return local

    def getTotalOnlineSubtitles(self):
        return len(self.getOnlineSubtitles())

    def getTotalLocalSubtitles(self):
        return len(self.getSubtitles())

    def setNOSSubtitle(self, sub):
        """ transfer a subtitle from general list to 'not on server'
        """
        self.nos_subs.append(sub)
        self._subs.pop(self._subs.index(sub))

    def remNOSSubtitle(self, sub):
        """removes a subtitle from NOS list"""
        self.nos_subs.pop(self.nos_subs.index(sub))

    def getNOSSubtitles(self):
        return self.nos_subs

    def hasNOSSubtitles(self):
        return len(self.nos_subs) != 0

    def setMovieInfo(self, info):
        self._movie_info = info

    def getMovieInfo(self):
        return self._movie_info

    def _calculate_OSDB_hash(self):
        """
        Calculate OSDB (OpenSubtitleDataBase) hash of this VideoFile
        :return: hash as string
        """
        f = open(self._filepath, 'rb')

        filesize = os.fstat(f.fileno()).st_size

        blockSize = min(filesize, 64 << 10) # 64kiB

        longlongformat = 'Q'  # unsigned long long little endian
        bytesize = struct.calcsize(longlongformat)
        format = '<{nbll}{memberformat}'.format(
            nbll=blockSize // bytesize,
            memberformat=longlongformat)

        hash = filesize

        buffer = f.read(blockSize)
        longlongs = struct.unpack(format, buffer)
        hash += sum(longlongs)

        f.seek(-blockSize, os.SEEK_END)
        buffer = f.read(blockSize)
        longlongs = struct.unpack(format, buffer)
        hash += sum(longlongs)

        f.close()
        returnedhash = '{:016x}'.format(hash)[-16:]
        log.debug('hash("{}")={}'.format(self.get_filepath(), returnedhash))
        return returnedhash