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

#
# SUBDOWNLOADER CONFIGURATION
#
from optparse import make_option
import logging
import os.path

"""
Logging levels:
CRITICAL    50
ERROR        40
WARNING    30
INFO            20
DEBUG       10
NOTSET       0
"""

# OPTPARSE #
# used in text mode
NAME = "Subdownloader"
DESCRIPTION = "%s is a Free Open-Source tool written in PYTHON for automatic download/upload subtitles for videofiles (DIVX,MPEG,AVI,etc) and DVD's using fast hashing."% NAME
VERSION = "%s v2.0"% NAME
OPTION_LIST = [
    # internal application options
    make_option("-g", "--gui", dest="mode", action="store_const", const="gui",  default="cli", 
                            help="Run applicatin in GUI mode. This is the default"),
    make_option("-c", "--cli", dest="mode", action="store_const", const="cli",  default="gui",
                            help="Run applicatin in CLI mode"),
    make_option("--debug", dest="logging", default=logging.INFO,  
                            action="store_const", const=logging.DEBUG, 
                            help="Print debug messages to stout and logfile"),
    make_option("--quiet", dest="verbose", 
                            action="store_false", default=True, 
                            help="Don't print status messages to stdout"), 
    # user application options
    make_option("--video", dest="videofile", metavar="FILE/DIR",  
                            help="Video file or a directory with videos"), 
    make_option("--lang", dest="language",
                            help="Subtitle language to download")
    ]

# MISC #
LOG_DIR = "" # leave blank to use current path
LOG_NAME = "%s.log"% NAME.lower()
LOG_PATH = os.path.join(LOG_DIR, LOG_NAME)
LOG_MODE = "a"
