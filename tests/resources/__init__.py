# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from hashlib import md5
from pathlib import Path
from urllib.request import urlretrieve


RESOURCE_PATH = Path(__file__).absolute().with_name('files')

RESOURCE_AVI = RESOURCE_PATH / 'breakdance.avi'


def resources_init():
    RESOURCE_PATH.mkdir(exist_ok=True)

    if not RESOURCE_AVI.exists():
        URL = 'http://www.opensubtitles.org/addons/avi/{}'
        urlretrieve(url=URL.format('breakdance.avi'),
                    filename=str(RESOURCE_AVI))

    if not RESOURCE_AVI.exists():
        raise RuntimeError('Could not download resource')

    with RESOURCE_AVI.open('rb') as f:
        md5_hash = md5(f.read()).hexdigest()
    if md5_hash != 'dc6cc911a5f71b39918f9b24b73b8f26':
        raise RuntimeError('Resource corrupt: md5={}'.format(md5_hash))
