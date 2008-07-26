#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Copyright (C) 2007 Ivan Garcia  capiscuas@gmail.com
##    This program is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License along
##    with this program; if not, write to the Free Software Foundation, Inc.,
##    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
