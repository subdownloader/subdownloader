#!/usr/bin/env python
# Copyright (c) 2010 SubDownloader Developers - See COPYING - GPLv3

import logging

log = logging.getLogger("subdownloader.modules.metadata")
try:
    import kaa.metadata as metadata
except ImportError:
    try:
        import mmpython as metadata
    except ImportError:
        log.warning("Failed to import metadata module. This means you will be unable to upload your videos with all details.")

# expose metadata parsing method for global usage
def parse(filepath):
    return metadata.parse(filepath)
