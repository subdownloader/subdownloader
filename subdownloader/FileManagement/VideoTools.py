# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

import logging

import subdownloader.FileManagement.videofile as videofile
from subdownloader.FileManagement import get_extension

log = logging.getLogger("subdownloader.FileManagement.Video")


def isVideofile(filepath):
    if get_extension(filepath).lower() in videofile.VIDEOS_EXT:
        return True
    return False
