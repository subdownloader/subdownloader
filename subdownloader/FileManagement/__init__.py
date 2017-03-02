# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import os
import re


def get_extension(path):
    root, ext = os.path.splitext(path)
    if ext:
        return ext[1:]
    return ''


def clear_string(strng):
    return re.sub('[^a-zA-Z0-9]', '', strng)


def without_extension(path):
    root, ext = os.path.splitext(path)
    return root
