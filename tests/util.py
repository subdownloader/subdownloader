# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import os


class ChangeDirectoryScope:
    def __init__(self, directory):
        self.directory = directory
        self._old_directory = None

    def __enter__(self):
        self._old_directory = os.getcwd()
        os.chdir(str(self.directory))

    def __exit__(self, type, value, traceback):
        os.chdir(str(self._old_directory))
