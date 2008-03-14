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
    make_option("-g", "--gui", dest="mode", action="store_const", const="gui",  #default="cli", 
                            help="Run applicatin in GUI mode. This is the default"),
    make_option("-c", "--cli", dest="mode", action="store_const", const="cli",  default="gui",
                            help="Run applicatin in CLI mode"),
    make_option("--debug", dest="logging", default=logging.INFO,  
                            action="store_const", const=logging.DEBUG, 
                            help="Print debug messages to stout and logfile"),
    make_option("--quiet", dest="verbose", 
                            action="store_false", default=True, 
                            help="Don't print status messages to stdout"), 
    make_option("--human", dest="output", action="store_const", const="human", 
                            help="Print human readable messages. Default for CLI mode"), 
    make_option("--nerd", dest="output", action="store_const", const="nerd", 
                            default="human", help="Print messages with more details"), 
    # user application options
    make_option("-d", "--download", dest="operation", action="store_const", const="download", 
                            help="Download a subtitle. Default for CLI mode"), 
    make_option("-u", "--upload", dest="operation", action="store_const", const="upload", 
                            default="download", help="Upload a subtitle"), 
    make_option("--video", dest="videofile", metavar="FILE/DIR",  
                            help="Video file or a directory with videos"), 
    make_option("--lang", dest="language", default='all', 
                            help="Used in subtitle download and upload preferences"), 
    make_option("--best", dest="interactive", action="store_false", default=False, 
                            help="Download the best rated subtitle. Default for CLI mode"), 
    make_option("--select", dest="interactive",  action="store_true", default=False, 
                            help="Prompt user what subtitle to download"), 
                            
    make_option("--user", dest="username", default='', 
                            help="Opensubtitles.com username. Must be set in upload mode. Default is blank (anonymous)"), 
    make_option("--passwd", dest="password", default='', 
                            help="Opensubtitles.com password. Must be set in upload mode. Default is blank (anonymous)"), 
    # misc options
    make_option("--server", dest="server", default=None,
                            help="Proxy to use on internet connections"), 
    make_option("--proxy", dest="proxy", default=None, 
                            help="Proxy to use on internet connections")
    ]

# MISC #
LOG_DIR = "" # leave blank to use current path
LOG_NAME = "%s.log"% NAME.lower()
LOG_PATH = os.path.join(LOG_DIR, LOG_NAME)
LOG_MODE = "a"

