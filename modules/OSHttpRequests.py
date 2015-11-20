#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010 SubDownloader Developers - See COPYING - GPLv3

#Excample usage
# d = OSHttpSearch()
# d.download('http://www.opensubtitles.org/en/download/file/1951690122.gz', '/home/myuser/Night.Watch.2004.CD1.DVDRiP.XViD-FiCO.srt')

import httplib, urllib, os
import gzip
import xml.dom.minidom as xml
import logging

OS_URL = "http://www.opensubtitles.org/pt/search22%s/simplexml"


class OSHttpRequests:

   def __init__ (self):
      self.log = logging.getLogger("subdownloader.httpsearch.OSHttpSearch")

   def search (self, lang=None, videohash=None, bytesize=None):
      arguments = ""
      if lang:
         lang = "/sublanguageid-%s" % lang
         arguments += lang
      if videohash:
         self.log.debug("Searching for hash: %s" % videohash)
         videohash = "/moviehash-%s" % videohash
         arguments += videohash
      if bytesize:
         bytesize = "/moviebytesize-%s" % bytesize
         arguments += bytesize

      url = OS_URL % arguments
      print(url)
      data = urllib.urlopen(url).read()
      print(data)


   def download_subtitle(self, url=None, local_path=None, progress_callback=None):
      """
         Simple method to download the gziped subtitle
      """
      if url and local_path:
         urllib.urlretrieve(url, local_path, progress_callback)

   def unpack_subtitle(self, gz_path, destination_path):
      # unpack the gz content
      fileObj = gzip.GzipFile(gz_path, 'rb');
      fileContent = fileObj.readlines();
      fileObj.close()

      # write the content to a file
      fileObjOut = open(destination_path, 'wb');
      fileObjOut.writelines(fileContent)
      fileObjOut.close()

   def download (self, url=None, local_path=None, progress_callback=None):
      """
      example of usage:
         d = OSHttpSearch()
         d.download('http://www.opensubtitles.org/en/download/file/1951690122.gz', '/home/myuser/Night.Watch.2004.CD1.DVDRiP.XViD-FiCO.srt')
      """
      if url and local_path:
         gz_path = "%s.gz" % local_path
         self.log.debug("Downloading subtitle from url: %s" % url)
         self.download_subtitle(url, gz_path, progress_callback)

         # unpack the gzipped subtitle
         self.log.debug("Unpacking and savinng to: %s" % local_path)
         self.unpack_subtitle(gz_path, local_path)

         # remove the gzipped subtitle
         os.remove(gz_path)

