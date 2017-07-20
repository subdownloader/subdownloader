# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import sys

if sys.version_info < (3, 0):
    from httplib import HTTPConnection

    from commands import getstatusoutput

    from urllib import quote, urlretrieve
    from urllib2 import urlopen, HTTPError, URLError

    from xmlrpclib import Fault, ProtocolError, ServerProxy, Transport
else:
    from http.client import HTTPConnection

    from subprocess import getstatusoutput

    from urllib.error import HTTPError, URLError
    from urllib.parse import quote
    from urllib.request import urlopen, urlretrieve

    from xmlrpc.client import Fault, ProtocolError, ServerProxy, Transport
