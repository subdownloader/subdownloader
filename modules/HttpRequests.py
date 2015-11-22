#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

#Excample usage
# d = HttpRequests()
# d.download('http://www.opensubtitles.org/en/download/file/1951690122.gz',
#     '/home/myuser/Night.Watch.2004.CD1.DVDRiP.XViD-FiCO.srt')

try:
    from urllib import urlopen, urlretrieve
except ImportError:
    from urllib.request import urlopen, urlretrieve
import os
import gzip
import xml.dom.minidom as xml
import logging
import shutil

class HttpRequests:

    def __init__ (self):
        self.log = logging.getLogger('subdownloader.HttpRequests.HttpRequests')

    def download_subtitle(self, url=None, local_path=None, progress_callback=None):
        """
         Simple method to download a url to a local file.
        """
        if not url or not local_path:
            self.log.warning('Illegal argument to download_subtitle:')
            self.log.warning('url={}'.format(url))
            self.log.warning('local_path="{}"'.format(local_path))
            return
        urlretrieve(url=url, filename=local_path, reporthook=progress_callback)

    def unpack_subtitle(self, gz_path, destination_path):
        with gzip.open(gz_path, 'rb') as fin,\
                open(destination_path, 'wb') as fout:
          shutil.copyfileobj(fsrc=fin, fdst=fout)

    def download(self, url=None, local_path=None, progress_callback=None):
        """
        example of usage:
         d = HttpRequests()
         d.download('http://www.opensubtitles.org/en/download/file/1951690122.gz', '/home/myuser/Night.Watch.2004.CD1.DVDRiP.XViD-FiCO.srt')
        """
        if url and local_path:
           gz_path = "%s.gz" % local_path
           self.log.debug('Downloading subtitle from url: %s' % url)
           self.download_subtitle(url, gz_path, progress_callback)

           # unpack the gzipped subtitle
           self.log.debug('Unpacking and savinng to: %s' % local_path)
           self.unpack_subtitle(gz_path, local_path)

           # remove the gzipped subtitle
           os.remove(gz_path)

