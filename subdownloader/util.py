# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import gzip
import io
import shutil


class IllegalPathException(Exception):
    def __init__(self, path):
        self._path = path

    def path(self):
        return self._path


def asciify(data):
    """
    Limit the byte data string to only ascii characters and convert it to a string.
    Non-representable characters are dropped.
    :param data: byte data string to convert to ascii
    :return: string
    """
    return ''.join(map(chr, filter(lambda x : x < 128, data)))


def unzip_bytes(bytes):
    """
    Unpack bytes. Return file object
    :param bytes: bytes object
    """
    return gzip.GzipFile(fileobj=io.BytesIO(bytes))


def unzip_stream(src_stream):
    """
    Unpack src_file file object. Return file object
    :param src_stream: file like zip stream
    """
    return gzip.GzipFile(fileobj=src_stream)


def write_stream(src_file, destination_path):
    """
    Write the file-like src_file object to the string dest_path
    :param src_file: file-like data to be written
    :param destination_path: string of the destionation file
    """
    with open(destination_path, 'wb') as destination_file:
        shutil.copyfileobj(fsrc=src_file, fdst=destination_file)
