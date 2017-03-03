# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import hashlib
import logging
import os

log = logging.getLogger('subdownloader.FileManagement.subtitlefile')

"""
List of known subtitle extensions.
"""
SUBTITLES_EXT = ["srt", "sub", "txt", "ssa", "smi", "ass", "mpl"]


class SubtitleFile(object):

    """Contains the class that represents a SubtitleFile (SRT,SUB,etc)
    and provides easy methods to retrieve its attributes (Sizebytes, HASH, Validation,etc)
    """

    def __init__(self, online, id=None):
        self._language = None
        self._video = None
        self._online = online
        self._path = ""
        self._onlineId = ""
        self._onlineFileId = ""
        self._id_file_online = ""
        self._extraInfo = {}
        self._filename = ""

        log.debug("is online %s" % online)
        if online:
            log.debug("OnlineId is %s" % id)
            self._onlineId = id
        else:
            self._path = id
            self.setFileName(os.path.basename(self._path))
        self._uploader = None
        self.rating = 0.0
        self._size = 0
        self._hash = None
        if not online:
            self._size = os.path.getsize(self._path)
            self._hash = hashlib.md5(open(self._path, mode='rb').read()).hexdigest()
        self._languageXX = None
        self._languageXXX = None
        self._languageName = None

    def __repr__(self):
        xxx = self._language.xxx() if self._language else 'UNKNOWN'
        return "<SubtitleFile online: %s, local: %s, path: %s, file: %s, size: # %s," \
               " uploader: %s, onlineId: %s, hash: %s, language: %s, rating: %s>" % (
            self.isOnline(), self.isLocal(), self.getFilePath(),
            self.get_filepath(), self.getSize(), self.getUploader(),
            self.getIdOnline(), self.get_hash(), xxx,
            self.getRating())

    def setFileName(self, filename):
        self._filename = filename

    def get_filepath(self):
        return self._filename

    def setVideo(self, _video):
        self._video = _video

    def getVideo(self):
        return self._video

    def setUploader(self, uploader):
        self._uploader = uploader

    def getUploader(self):
        return self._uploader

    def setIdOnline(self, _id_online):
        self._onlineId = _id_online

    def getIdOnline(self):
        return self._onlineId

    def setIdFileOnline(self, _id_file_online):
        self._onlineFileId = _id_file_online

    def getIdFileOnline(self):
        return self._onlineFileId

    def getFilePath(self):
        return self._path

    # It could be the case when isLocal and isOnline are both true
    def isOnline(self):
        return self._onlineId != None and len(self._onlineId)

    def isLocal(self):
        return self._path != None and len(self._path)

    def getSize(self):
        return self._size

    def setHash(self, hash):
        self._hash = hash

    def get_hash(self):
        return self._hash

    def setLanguage(self, language):
        self._language = language

    def getLanguage(self):
        # FIXME: return
        return self._language

    def setRating(self, rating):
        self.rating = rating

    def getRating(self):
        return self.rating

    def setDownloadLink(self, link):
        self.download_link = link

    def getDownloadLink(self):
        return self.download_link

    def setExtraInfo(self, info, data):
        self._extraInfo[info] = data

    def getExtraInfo(self, info):
        return self._extraInfo[info]
