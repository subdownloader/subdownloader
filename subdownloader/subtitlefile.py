# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
import platform
from subdownloader import Languages

from hashlib import md5

SUBTITLES_EXT = ["srt", "sub", "txt", "ssa", "smi", "ass", "mpl"]
SELECT_SUBTITLES = "Subtitle Files (*.%s)" % " *.".join(SUBTITLES_EXT)


class SubtitleFile(object):

    """Contains the class that represents a SubtitleFile (SRT,SUB,etc)
    and provides easy methods to retrieve its attributes (Sizebytes, HASH, Validation,etc)
    """

    def __init__(self, online, id=None):
        self.log = logging.getLogger("subdownloader.modules.subtitlefile")
        self._language = None
        self._video = None
        self._online = online
        self._path = ""
        self._onlineId = ""
        self._onlineFileId = ""
        self._id_file_online = ""
        self._extraInfo = {}
        self._filename = ""

        self.log.debug("is online %s" % online)
        if online:
            self.log.debug("OnlineId is %s" % id)
            self._onlineId = id
        else:
            self._path = id
            self.setFileName(os.path.basename(self._path))
        self._uploader = None
        self._languageXX = None
        self._languageXXX = None
        self._languageName = None
        self.rating = 0.0
        self._size = 0
        self._hash = None
        if not online:
            self._size = os.path.getsize(self._path)
            self._hash = md5(open(self._path, mode='rb').read()).hexdigest()

    def __repr__(self):
        return "<SubtitleFile online: %s, local: %s, path: %s, file: %s, size: # %s, uploader: %s, onlineId: %s, hash: %s, language: %s, rating: %s>" % (self.isOnline(), self.isLocal(), self.getFilePath(),
         self.getFileName(), self.getSize(), self.getUploader(),
         self.getIdOnline(), self.getHash(), self.getLanguageXXX(),
         self.getRating())

    def setFileName(self, filename):
        self._filename = filename

    def getFileName(self):
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

    def getHash(self):
        return self._hash

    def setLanguage(self, language):
        self.setLanguageXXX(language)

    def getLanguage(self):
        return self.getLanguageXXX()

    def setLanguageXX(self, xx):
        # greek officially ISO639-1 is 'el'  , but opensubtitles is buggy
        if xx == 'gr':
            xx = 'el'
        self._languageXX = xx
        self._languageXXX = Languages.xx2xxx(xx)
        self._languageName = Languages.xx2name(xx)

    def getLanguageXX(self):
        if self._languageXX:
            return self._languageXX.lower()
        else:
            return None

    def setLanguageXXX(self, xxx):
        self._languageXXX = xxx
        self._languageXX = Languages.xxx2xx(xxx)
        self._languageName = Languages.xxx2name(xxx)

    def getLanguageXXX(self):
        if self._languageXXX:
            return self._languageXXX.lower()
        else:
            return None

    def getLanguageName(self):
        if self._languageName:
            return self._languageName
        else:
            return None

    def setLanguageName(self, language):
        self._languageName = language
        self._languageXX = Languages.name2xx(language)
        self._languageXXX = Languages.name2xxx(language)

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
