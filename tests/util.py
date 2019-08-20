# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from collections import namedtuple
import os
from pathlib import Path
import shutil
import tempfile


class ChangeDirectoryScope:
    def __init__(self, directory):
        self.directory = directory
        self._old_directory = None

    def __enter__(self):
        self._old_directory = os.getcwd()
        os.chdir(str(self.directory))

    def __exit__(self, type, value, traceback):
        os.chdir(str(self._old_directory))


class TempFile(object):
    def __init__(self, text):
        fd, name = tempfile.mkstemp(text=text)
        file = os.fdopen(fd, mode='w' if text else 'wb')
        self.name = Path(name)
        self.file = file

    def __del__(self):
        self.delete()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.delete()

    def delete(self):
        if self.file is not None:
            self.file.close()
            os.unlink(self.name)
            assert self.file.closed
            self.name = None
            self.file = None


def create_temporary_file(text=True):
    return TempFile(text)


class TempDir(object):
    def __init__(self):
        self.path = Path(tempfile.mkdtemp())

    def __del__(self):
        self.delete()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__del__()

    def delete(self):
        if self.path is not None:
            shutil.rmtree(self.path)
            self.path = None


def create_temporary_directory():
    return TempDir()
