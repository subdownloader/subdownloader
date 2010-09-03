#!/usr/bin/env python
# Copyright (c) 2010 SubDownloader Developers - See COPYING - GPLv3

import sys, os, platform

#calculating the folder of SubDownloader src (or .exe)
if os.path.isfile(sys.path[0]):
        subdownloader_folder = os.path.dirname(sys.path[0])
else:
        subdownloader_folder = sys.path[0]
        

import logging
from optparse import OptionParser
# this will allow logic imports
#sys.path.append(os.path.dirname(sys.path[0]))
#print sys.path[0]
sys.path.append(os.path.join(sys.path[0], 'modules') )
# simple aplication starter
import modules.configuration as conf
from modules import APP_VERSION

"""
CRITICAL    50
ERROR        40
WARNING    30
INFO            20
DEBUG       10
NOTSET       0
"""
#TODO: Check if APP_VERSION replace really works.
parser = OptionParser(description=conf.General.description, version=APP_VERSION, option_list=conf.Terminal.option_list)
(options, args) = parser.parse_args()

if platform.system() == "Windows":
    try:
        sys.stderr = open(os.path.join(subdownloader_folder,"subdownloader.log"), "w") #The EXE file in windows will think that outputs here are errors, and it will show annoying mesage about run.exe.log
    except:
        pass #Cannot write message into subdownloader.log, that happens for example in Vista, where SD does not have writer permission on its ProgramFiles folder
        
if options.mode == 'gui':
    import gui.main
elif options.mode == 'cli':
    import cli.main

logging.basicConfig(level=options.logging,
                    format=conf.Logging.log_format,
                    datefmt='%H:%M',
                    #uncomment next two lines if we want logging into a file
                    #filename=conf.Logging.log_path,
                    #filemode=conf.Logging.log_mode,
                    )

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
    
