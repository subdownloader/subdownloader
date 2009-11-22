# -*- coding: utf-8 -*-
# Written 2007 by j@v2v.cc

import os
from os.path import *
import urllib

import Crypto.Hash.MD4
import sha
import base32

"""
 	    generates and returns ed2klink for filename
 	    based on donkeyhash.pl translated to python
 	    depends on Crypto.Hash function needs to be installed
 	    source: http://www.amk.ca/python/code/crypto.html
 	    debian: apt-get install python-crypto
"""
def ed2kLink(filename):
 	  donkeychunk = 9728000
 	  digests = []
 	  filesize=getsize(filename)
 	  file=open(filename)
 	  if filesize < donkeychunk:
            md4 = Crypto.Hash.MD4.new()
            buffer=file.read(4096)
            while buffer:
                  md4.update(buffer)
                  buffer=file.read(4096)
            file.close()
            donkeyhash=md4.hexdigest()
 	  else:
            if (filesize % donkeychunk == 0):
                  md4 = Crypto.Hash.MD4.new()
                  md4.update('')
                  digests.append(md4.digest())
            buffer = file.read(donkeychunk)
            while buffer:
                  md4 = Crypto.Hash.MD4.new()
                  md4.update(buffer)
                  digests.append(md4.digest())
                  buffer = file.read(donkeychunk)
            md4 = Crypto.Hash.MD4.new()
            for d in digests:
                md4.update(d)
            donkeyhash=md4.hexdigest()
 	  return"ed2k://|file|%s|%s|%s|"  % (basename(filename), filesize,donkeyhash)
 	
'''
 	    returns magnet link for filename
'''
def calculateSha1Hash(filename):
 	    sha1 = sha.new()
 	    file=open(filename)
 	    buffer=file.read(4096)
 	    while buffer:
              sha1.update(buffer)
              buffer=file.read(4096)
 	    file.close()
 	    return base32.b2a(sha1.digest())

def magnetLink(filename, sha1Hash = ''):
    if not sha1Hash:
        sha1Hash = calculateSha1Hash(filename)
    filename = basename(filename)
    link="magnet:?%s" % urllib.urlencode({'dn':filename,'xt':"urn:sha1:%s" % sha1Hash})
    return link

      
