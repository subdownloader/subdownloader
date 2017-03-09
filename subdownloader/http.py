# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

# Example usage
# d = Http()
# ok = d.downloadRaw('http://www.opensubtitles.org/en/download/file/1951690122.gz', '/tmp/zip.gz')
# if (ok):
#     d.unpackZip('/tmp/zip.gz', '/home/myuser/Night.Watch.2004.CD1.DVDRiP.XViD-FiCO.srt')

# FIXME: allow download and unzip in one step?

try:
    from urllib2 import urlopen, HTTPError, URLError
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlopen, urlretrieve
    from urllib.error import HTTPError, URLError
import logging
import socket
from ssl import SSLError

from subdownloader.callback import ProgressCallback

log = logging.getLogger('subdownloader.http')

DEFAULT_TIMEOUT = 300


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
    except HTTPError as e:
        log.debug('urlopen failed (HTTPError). code: {}'.format(e.code))
    except URLError as e:
        log.debug('urlopen failed (URLError). Reason: {}'.format(e.reason))
    except SSLError as e:
        log.debug('urlopen failed  (ssl.SSLError). library={}, reason={}'.format(
            e.library, e.reason))
    except socket.error as e:
        (value, message) = e.args
        log.debug('urlopen failed (socket.error): {}'.format(message))
    except:
        log.debug('Connection failed. (Unknown reason)')
    socket.setdefaulttimeout(defTimeOut)
    return connectable


def url_stream(url):
    return urlopen(url=url)


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
    except:
        log.debug('... FAILED')
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
