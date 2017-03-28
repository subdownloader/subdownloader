# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import os
from subdownloader.project import PROJECT_TITLE


def client_get_path():
    """
    Get path to the client modules.
    :return: path as a string
    """
    return os.path.dirname(os.path.realpath(__file__))
