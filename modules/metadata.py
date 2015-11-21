#!/usr/bin/env python
# Copyright (c) 2010 SubDownloader Developers - See COPYING - GPLv3

import logging

log = logging.getLogger("subdownloader.modules.metadata")
try:
    import kaa.metadata as metadata
except ImportError:
    log.error("Failed to import metadata module. This means you will be unable to automatically download your subtitles or upload your videos with all details.")
    class metadata:
        @classmethod
        def parse(cls, *args, **kwargs):
            log.warning("Using dummy metadata parser.")
            return None

# expose metadata parsing method for global usage
def parse(filepath):
    return metadata.parse(filepath)
