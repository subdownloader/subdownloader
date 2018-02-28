# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging
import socket
from ssl import SSLError

from urllib.error import HTTPError, URLError
from urllib.request import urlopen, urlretrieve


log = logging.getLogger('subdownloader.http')

DEFAULT_TIMEOUT = 300

# FIXME: allow download and unzip in one step?


def test_connection(url, timeout=DEFAULT_TIMEOUT):
    """
    Open a connection to the url.
    :param url: Url to test
    :param timeout: Timeout
    :return: True if connection could be made.
    """
    log.debug('testConnection: url={}, timeout={}'.format(url, timeout))
    # FIXME: For Python3 ==> use urlopen(timeout=...) and get rid of socket
    defTimeOut = socket.getdefaulttimeout()
    try:
        timeout = float(timeout)
    except ValueError:
        log.debug('Illegal timeout argument. {} ({})'.format(
            timeout, type(timeout)))
    socket.setdefaulttimeout(timeout)
    connectable = False
    log.debug('Test connection "{}", timeout={}'.format(url, timeout))
    try:
        urlopen(url)
        log.debug('urlopen succeeded')
        connectable = True
    except (HTTPError, URLError, SSLError, socket.error):
        log.exception('url failed')
    socket.setdefaulttimeout(defTimeOut)
    return connectable


def download_raw(url, local_path, callback):
    """
    Download an url to a local file.
    :param url: url of the file to download
    :param local_path: path where the downloaded file should be saved
    :param callback: instance of ProgressCallback
    :return: True is succeeded
    """
    log.debug('download_raw(url={url}, local_path={local_path})'.format(url=url, local_path=local_path))
    raw_progress = RawDownloadProgress(callback)
    reporthook = raw_progress.get_report_hook()
    try:
        log.debug('urlretrieve(url={url}, local_path={local_path}) ...'.format(url=url, local_path=local_path))
        urlretrieve(url=url, filename=local_path, reporthook=reporthook)
        log.debug('... SUCCEEDED')
        callback.finish(True)
        return True
    except URLError:
        log.exception('... FAILED')
        callback.finish(False)
        return False


class RawDownloadProgress(object):
    """
    Subclass of ProgressCallback purposed for reporting back download progress.
    """
    def __init__(self, callback):
        """
        Create a new RawDownloadProgress that encapsulates a ProgressCallback to record download progress.
        :param callback: ProgressCallback to encapsulate
        """
        self._callback = callback
        self._chunkNumber = 0
        self._total = 0

    def get_report_hook(self):
        """
        Return a callback function suitable for using reporthook argument of urllib(.request).urlretrieve
        :return: function object
        """
        def report_hook(chunkNumber, chunkSize, totalSize):
            if totalSize != -1 and not self._callback.range_initialized():
                log.debug('Initializing range: [{},{}]'.format(0, totalSize))
                self._callback.set_range(0, totalSize)
            self._chunkNumber = chunkNumber
            self._total += chunkSize
            if self._total > totalSize:
                # The chunk size can be bigger than the file
                self._total = totalSize
            self._callback.update(self._total)

        return report_hook
