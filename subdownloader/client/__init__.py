# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import os
from subdownloader.project import PROJECT_TITLE


def project_get_description():
    """
    Get description of the project.
    :return: description as a string
    """
    return _('{project} is a Free Open-Source tool written in PYTHON '
             'for automatic download/upload subtitles for videofiles '
             '(DIVX,MPEG,AVI,etc) and DVD\'s using fast hashing.'.format(project=PROJECT_TITLE))


def client_get_path():
    """
    Get path to the client modules.
    :return: path as a string
    """
    return os.path.dirname(os.path.realpath(__file__))
