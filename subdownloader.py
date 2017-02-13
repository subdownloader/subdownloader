#!/usr/bin/env python
# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3
# PYTHON_ARGCOMPLETE_OK

import os
import platform
import sys

# calculating the folder of SubDownloader src (or .exe)
if os.path.isfile(sys.path[0]):
    subdownloader_folder = os.path.dirname(sys.path[0])
else:
    subdownloader_folder = sys.path[0]

import logging
import argparse

sys.path.append(os.path.join(sys.path[0], 'modules'))

import subdownloader.client.configuration as conf

parser = argparse.ArgumentParser(description=conf.General.description)
conf.Terminal.populate_parser(parser)

try:
    import argcomplete
    argcomplete.autocomplete(parser)
except ImportError:
    pass

options = parser.parse_args()

if platform.system() == "Windows":
    try:
        sys.stderr = open(os.path.join(subdownloader_folder,
                                       "subdownloader.log"), "w")
        # The EXE file in windows will think that outputs here are errors,
        # and it will show annoying mesage about run.exe.log
    except:
        pass
        # Cannot write message into subdownloader.log,
        # that happens for example in Vista,
        # where SD does not have writer permission on its ProgramFiles folder.

logging.basicConfig(level=options.logging,
                    format=conf.Logging.log_format,
                    datefmt='%H:%M',
                    filename=options.logfile,
                    filemode=conf.Logging.log_mode,
                    )

if options.mode == 'gui':
    import subdownloader.client.gui.main
    subdownloader.client.gui.main.main(options)
elif options.mode == 'cli':
    import subdownloader.client.cli.main
    cli = subdownloader.client.cli.main.Main(options)
    cli.start_session()