# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import importlib
import sys


PY2 = sys.version_info < (3, 0)

if PY2:
    from httplib import HTTPConnection, CannotSendRequest

    from commands import getstatusoutput

    from pathlib2 import Path

    from socket import error as SocketError

    from urllib import quote, urlretrieve
    from urllib2 import urlopen, HTTPError, URLError

    from xmlrpclib import Fault, ProtocolError, ServerProxy, Transport

    configparser = importlib.import_module('ConfigParser')
else:
    from http.client import HTTPConnection, CannotSendRequest

    from pathlib import Path

    from socket import error as SocketError

    from subprocess import getstatusoutput

    from urllib.error import HTTPError, URLError
    from urllib.parse import quote
    from urllib.request import urlopen, urlretrieve

    from xmlrpc.client import Fault, ProtocolError, ServerProxy, Transport

    configparser = importlib.import_module('configparser')
