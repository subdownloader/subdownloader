# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from enum import Enum
import os
from pathlib import Path
import sys


class ClientType(Enum):
    CLI = 'cli'
    GUI = 'gui'


def client_get_path():
    """
    Get path to the client modules.
    :return: path as a string
    """
    return Path(__file__).absolute().parent


def add_client_module_dependencies():
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules'))


class IllegalArgumentException(Exception):
    def __init__(self, msg):
        self.msg = msg
