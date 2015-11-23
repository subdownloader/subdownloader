#!/usr/bin/env python
# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3
# PYTHON_ARGCOMPLETE_OK

import sys, os, platform

#calculating the folder of SubDownloader src (or .exe)
if os.path.isfile(sys.path[0]):
        subdownloader_folder = os.path.dirname(sys.path[0])
else:
        subdownloader_folder = sys.path[0]

import logging
import argparse

sys.path.append(os.path.join(sys.path[0], 'modules') )

import modules.configuration as conf

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
        #The EXE file in windows will think that outputs here are errors,
        #and it will show annoying mesage about run.exe.log
    except:
        pass
        #Cannot write message into subdownloader.log,
        #that happens for example in Vista,
        #where SD does not have writer permission on its ProgramFiles folder.

logging.basicConfig(level=options.logging,
                    format=conf.Logging.log_format,
                    datefmt='%H:%M',
                    filename=options.logfile,
                    filemode=conf.Logging.log_mode,
                    )

if options.mode == 'gui':
    import gui.main
elif options.mode == 'cli':
    import cli.main

"""
# add a console logging handler if verbosity is turned on
if not options.verbose:
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(options.logging)
    # set a format which is simpler for console use
    if options.output == "nerd":
        formatter = logging.Formatter("%(levelname)s::%(name)s # %(message)s")
    elif options.output == "human":
        formatter = logging.Formatter("%(message)s")
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
"""
# create a logger named 'subdownloader.run'
log = logging.getLogger("run")

if __name__ == "__main__":

    if options.mode == 'gui':
        gui.main.main(options)
    elif options.mode == 'cli':
        cli = cli.main.Main(options)
        cli.start_session()

