#!/usr/bin/env python
# Copyright (c) 2010 SubDownloader Developers - See COPYING - GPLv3

import re, os, logging
import modules.videofile as videofile
import modules.subtitlefile as subtitlefile
from FileManagement import get_extension, clear_string, without_extension
from languages import Languages, autodetect_lang

log = logging.getLogger("subdownloader.FileManagement.Video")

def isVideofile(filepath):
    if get_extension(filepath).lower() in videofile.VIDEOS_EXT:
        return True
    return False
