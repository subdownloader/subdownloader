# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
import struct

from subdownloader import metadata
from subdownloader.identification import IdentityCollection
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
    def __init__(self, filepath):
        self._filepath = filepath

    def __str__(self):
        return '"{filepath}" is not a video.'.format(filepath=self._filepath)


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

        self._filepath = filepath
        if not self._filepath.exists():
            raise NotAVideoException(self._filepath)

        # calculate hash and size on request
        self._size = None
        self._osdb_hash = None

        # Initialize metadata on request.
        self._fps = None
        self._time_ms = None
        self._framecount = None

        self._subtitles = SubtitleFileCollection(parent=self)
        self._identities = IdentityCollection()

    def __repr__(self):
        if self._is_metadata_init():
            meta = '{fps={fps},time_ms={time_ms},framecount={framecount}'.format(
                fps=self._fps, time_ms=self._time_ms, framecount=self._framecount)
        else:
            meta = '<unavailable>'
        return '<Video:path="{path}",size={size},osdb_hash={osdb_hash},metadata={metadata},' \
               '#identities={identities}'.format(
                    path=self._filepath, size=self._size, osdb_hash=self._osdb_hash, metadata=meta,
                    identities=len(self._identities))

    def _is_metadata_init(self):
        return self._fps is not None

    def _read_metadata(self):
        """
        Private function to read (if not read already) and store the metadata of the local VideoFile.
        """
        if self._is_metadata_init():
            return
        try:
            log.debug('Reading metadata of "{path}" ...'.format(path=self._filepath))
            data = metadata.parse(self._filepath)
            videotracks = data.get_videotracks()
            if len(videotracks) > 0:
                self._fps = videotracks[0].get_framerate()
                self._time_ms = videotracks[0].get_duration_ms()
                self._framecount = videotracks[0].get_framecount()
        except:
            # FIXME: find out what type the metadata parser can throw
            log.debug('... FAIL')
            log.exception('Exception was thrown.')
            # Two possibilities: the parser failed or the file is no video

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
        return self._filepath.parent

    def get_filename(self):
        """
        Get filename of this VideoFile
        :return: file name as string
        """
        return self._filepath.name

    def get_size(self):
        """
        Get size of this VideoFile in bytes
        :return: size as integer
        """
        if self._size is None:
            self._size = self._filepath.stat().st_size
        return self._size

    def get_osdb_hash(self):
        """
        Get the hash of this local videofile
        :return: hash as string
        """
        if self._osdb_hash is None:
            self._osdb_hash = self._calculate_osdb_hash()
        return self._osdb_hash

    def get_fps(self):
        """
        Get the fps (frames per second) of this VideoFile
        :return: fps as integer/float
        """
        self._read_metadata()
        return self._fps

    def get_framecount(self):
        """
        Get the number of frames of this VideoFile
        :return: frame countt as integer
        """
        self._read_metadata()
        return self._framecount

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

    def get_identities(self):
        """
        Get the identifications of this video in a list
        :return: list of Identifications
        """
        return self._identities

    def add_identity(self, identity):
        """
        Add a identity to this Video
        :param identity: identity to add
        """
        self._identities.add_identity(identity)

    def _calculate_osdb_hash(self):
        """
        Calculate OSDB (OpenSubtitleDataBase) hash of this VideoFile
        :return: hash as string
        """
        log.debug('_calculate_OSDB_hash() of "{path}" ...'.format(path=self._filepath))
        f = self._filepath.open(mode='rb')

        file_size = self.get_size()

        longlong_format = 'Q'  # unsigned long long little endian
        size_longlong = struct.calcsize(longlong_format)

        block_size = min(file_size, 64 << 10)  # 64kiB
        block_size = block_size & ~(size_longlong - 1)  # lower round on multiple of longlong

        nb_longlong = block_size // size_longlong
        fmt = '<{nbll}{member_format}'.format(
            nbll=nb_longlong,
            member_format=longlong_format)

        hash_int = file_size

        buffer = f.read(block_size)
        list_longlong = struct.unpack(fmt, buffer)
        hash_int += sum(list_longlong)

        f.seek(-block_size, os.SEEK_END)
        buffer = f.read(block_size)
        list_longlong = struct.unpack(fmt, buffer)
        hash_int += sum(list_longlong)

        f.close()
        hash_str = '{:016x}'.format(hash_int)[-16:]
        log.debug('hash("{}")={}'.format(self.get_filepath(), hash_str))
        return hash_str
