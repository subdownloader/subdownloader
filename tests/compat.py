# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import sys

PY2 = sys.version_info < (3, 0)

if PY2:
    from urllib import urlretrieve
    from pathlib2 import Path

else:
    from urllib.request import urlretrieve
    from pathlib import Path
