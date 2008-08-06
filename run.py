#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Copyright (C) 2007 Ivan Garcia capiscua@gmail.com
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

import sys, os, platform
if platform.system() == "Windows":
    sys.stderr = open(os.path.join(os.path.dirname(sys.path[0]),"stderr.log"), "w") #The EXE file in windows will think that outputs here are errors, and it will show annoying mesage about run.exe.log
import logging
from optparse import OptionParser
# this will allow logic imports
#sys.path.append(os.path.dirname(sys.path[0]))
#print sys.path[0]
sys.path.append(os.path.join(sys.path[0], 'modules') )
# simple aplication starter
import modules.configuration as conf

"""
CRITICAL    50
ERROR        40
WARNING    30
INFO            20
DEBUG       10
NOTSET       0
"""

#TODO: change conf.VERSION to subdownloader.APP_VERSION
parser = OptionParser(description=conf.General.description, version=conf.General.version, option_list=conf.Terminal.option_list)
(options, args) = parser.parse_args()

if options.mode == 'gui':
    import gui.main
elif options.mode == 'cli':
    import cli.main

logging.basicConfig(level=options.logging,
                    format=conf.Logging.log_format,
                    datefmt='%y-%m-%d %H:%M',
                    #uncomment next two lines if we want logging into a file
                    filename=conf.Logging.log_path,
                    filemode=conf.Logging.log_mode,
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
log = logging.getLogger("run")
    
if __name__ == "__main__": 
    log.info('Subdownloader started')
    
    if options.mode == 'gui':
        
        gui.main.main(options)
    elif options.mode == 'cli':
        cli = cli.main.Main(options)
        cli.start_session()
    
    log.info('Subdownloader closed for mantainance.')
