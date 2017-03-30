# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
import struct

from subdownloader import metadata
from subdownloader.subtitle2 import SubtitleFileCollection

log = logging.getLogger('subdownloader.video2')

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
        return '"{filePath}" is not a video. Error is "{e}".'.format(filePath=self._filePath, e=self._e)


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
            self._osdb_hash = self._calculate_OSDB_hash()
        except Exception as e:
            log.exception('Could not calculate filepath, size and/or osdb hash of "{path}"'.format(path=filepath))
            raise NotAVideoException(filepath, e)
        # Initialize metadata on request.
        self._metadata_init = False
        self._fps = 0
        self._time_ms = 0

        self._subtitles = SubtitleFileCollection(parent=self)

    def _read_metadata(self):
        """
        Private function to read (if not read already) and store the metadata of the local VideoFile.
        """
        if self._metadata_init:
            return
        try:
            log.debug('Reading metadata of "{path}" ...'.format(path=self._filepath))
            data = metadata.parse(self._filepath)
            videotracks = data.get_videotracks()
            if len(videotracks) > 0:
                self._fps = videotracks[0].get_framerate()
                self._time_ms = videotracks[0].get_duration_ms()
        except Exception:
            log.debug('... FAIL')
            log.exception('Exception was thrown.')
            # Two possibilities: the parser failed or the file is no video
        self._metadata_init = True

    def get_filepath(self):
        """
        Get the full file path of this VideoFile
        :return: file path as a string
        """
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

    def get_osdb_hash(self):
        """
        Get the hash of this local videofile
        :return: hash as string
        """
        return self._osdb_hash

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

    def get_subtitles(self):
        """
        Get the subtitles of this video in a SubtitleFileCollection
        :return: instance of SubtitleFileCollection
        """
        return self._subtitles

    def add_subtitle(self, subtitle):
        """
        Add subtitle to the the subtitle collection of this video.
        :param subtitle: subtitle to add
        """
        self._subtitles.add_subtitle(subtitle)

    def _calculate_OSDB_hash(self):
        """
        Calculate OSDB (OpenSubtitleDataBase) hash of this VideoFile
        :return: hash as string
        """
        log.debug('_calculate_OSDB_hash() of "{path}" ...'.format(path=self._filepath))
        f = open(self._filepath, 'rb')

        file_size = os.fstat(f.fileno()).st_size
        log.debug('... file_size ={file_size} bytes'.format(file_size=file_size))

        longlong_format = 'Q'  # unsigned long long little endian
        size_longlong = struct.calcsize(longlong_format)

        block_size = min(file_size , 64 << 10)  # 64kiB
        block_size = block_size & ~0x7  # Lower round on 8

        nb_longlong = block_size // size_longlong
        format = '<{nbll}{member_format}'.format(
            nbll=nb_longlong,
            member_format=longlong_format)

        hash_int = file_size

        buffer = f.read(block_size)
        list_longlong = struct.unpack(format, buffer)
        hash_int += sum(list_longlong)

        f.seek(-block_size, os.SEEK_END)
        buffer = f.read(block_size)
        list_longlong = struct.unpack(format, buffer)
        hash_int += sum(list_longlong)

        f.close()
        hash_str = '{:016x}'.format(hash_int)[-16:]
        log.debug('hash("{}")={}'.format(self.get_filepath(), hash_str))
        return hash_str
