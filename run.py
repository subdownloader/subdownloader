#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Copyright (C) 2007 Ivan Garcia contact@ivangarcia.org
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

import sys, os
import logging
from optparse import OptionParser
# this will allow logic imports
sys.path.append(os.path.dirname(os.getcwd()))
# simple aplication starter
from subdownloader.cli import conf

"""
CRITICAL    50
ERROR        40
WARNING    30
INFO            20
DEBUG       10
NOTSET       0
"""
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "[%(asctime)s] %(levelname)s::%(name)s # %(message)s"

#TODO: change conf.VERSION to subdownloader.APP_VERSION
parser = OptionParser(description=conf.DESCRIPTION,  version=conf.VERSION,  option_list=conf.OPTION_LIST)
(options, args) = parser.parse_args()

if options.mode == 'gui':
    import gui.main
elif options.mode == 'cli':
    import cli.main


logging.basicConfig(level=options.logging,
                    format=LOG_FORMAT,
                    datefmt='%y-%m-%d %H:%M',
                    #uncomment next two lines if we want logging into a file
                    filename=conf.LOG_PATH,
                    filemode=conf.LOG_MODE,
                    )
# add a console logging handler if verbosity is turned on
if options.verbose:
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
# create a logger named 'subdownloader.run' 
# consequent ones should follow its parent as. 'subdownloader.package.foo'
log = logging.getLogger("subdownloader.run")
    
if __name__ == "__main__": 
    log.info('Subdownloader started')
    if options.mode == 'gui':
        gui.main.main(options)
    elif options.mode == 'cli':
        # check if user set a video file name
        log.debug("Checking video file parameter...")
        if options.videofile:
            log.debug("...passed")
        else:
            log.debug("...failed")
            log.info("--video parameter must be set")
            exit()
        # check if user set language to use on subtitles
        log.debug("Checking language parameter...")
        if options.language:
            log.debug("...passed")
        else:
            log.debug("...failed")
            log.info("--lang parameter must be set")
            exit()
            
        # assume everything is good from here
        cli = cli.main.Main(options)
        cli.start_session()
        
    log.info('Subdownloader closed for mantainance.')
    #sys.stdout.write("stopped!\n"); sys.stdout.flush()
