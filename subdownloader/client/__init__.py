# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import os
import platform
from subdownloader.project import TITLE


def get_project_description():
    """
    Get description of the project.
    :return: description as a string
    """
    return _('%s is a Free Open-Source tool written in PYTHON ' \
        'for automatic download/upload subtitles for videofiles ' \
        '(DIVX,MPEG,AVI,etc) and DVD\'s using fast hashing.') % TITLE


def get_client_path():
    """
    Get path to the client modules.
    :return: path as a string
    """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)))


def get_i18n_path():
    """
    Get path to the internationalization data.
    :return: path as a string
    """
    local_locale_path = os.path.join(get_client_path(), 'locale')
    if platform.system() == "Linux":
        if os.path.exists(local_locale_path):
            return local_locale_path
        else:
            return '/usr/share/locale/'
    else:
        return local_locale_path
