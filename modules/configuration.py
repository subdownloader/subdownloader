#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Copyright (C) 2007 Ivan Garcia <contact@ivangarcia.org>
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

from optparse import make_option
import logging
import os.path
import user
from modules import progressbar
from modules import APP_TITLE
from modules import APP_VERSION

"""
Logging levels:
CRITICAL    50
ERROR        40
WARNING    30
INFO            20
DEBUG       10
NOTSET       0
"""
    
class Terminal(object):
    option_list = [
        # internal application options
        make_option("-g", "--gui", dest="mode", action="store_const", const="gui",  #default="cli", 
                                help="Run applicatin in GUI mode. This is the default"),
        make_option("-c", "--cli", dest="mode", action="store_const", const="cli",  default="gui",
                                help="Run applicatin in CLI mode"),
        make_option("-d", "--debug", dest="logging", default=logging.INFO,  
                                action="store_const", const=logging.DEBUG, 
                                help="Print debug messages to stout and logfile"),
        make_option("-q", "--quiet", dest="verbose", 
                                action="store_false", default=True, 
                                help="Don't print status messages to stdout"), 
        make_option("-T", "--test", dest="test", 
                                action="store_true", default=False, 
                                help="Used by developers for testing"), 
        make_option("-H", "--human", dest="output", action="store_const", const="human", 
                                help="Print human readable messages. Default for CLI mode"), 
        make_option("-n", "--nerd", dest="output", action="store_const", const="nerd", 
                                default="human", help="Print messages with more details"), 
        # user application options
        make_option("-D", "--download", dest="operation", action="store_const", const="download", 
                                help="Download a subtitle. Default for CLI mode"), 
        make_option("-U", "--upload", dest="operation", action="store_const", const="upload", 
                                default="download", help="Upload a subtitle"), 
        make_option("-L", "--list", dest="operation", action="store_const", const="list", 
                                default="download", help="List available subtitles without downloading"), 
        make_option("-V", "--video", dest="videofile", metavar="FILE/DIR", default=None, 
                                help="Full path to your video(s). Don't use '~'"), 
        make_option("-l", "--lang", dest="language", default='all', 
                                help="Used in subtitle download and upload preferences"), 
        make_option("-i","--interactive", dest="interactive", action="store_true", default=False, 
                                help="Prompt user when decisions need to be done"), 
        make_option("--rename-subs", dest="renaming", action="store_true", 
                                help="Rename subtitles to match movie file name"), 
        make_option("--keep-names", dest="renaming", action="store_false", default=False, 
                                help="Keep original subtitle names"), 
        make_option("--sol", dest="overwrite_local", action="store_true", #default=False, 
                                help="'Server Over Local' overwrites local subtitle with one from server. This is in cases when local subtitle isn't found on server, but server has subtitles for the movie."), 
        make_option("--los", dest="overwrite_local", action="store_false", default=False, 
                                help="'Local Over Server' keeps local subtitles, even if another is found on server. This is the default"), 
                                
        make_option("-u", "--user", dest="username", default='', 
                                help="Opensubtitles.com username. Must be set in upload mode. Default is blank (anonymous)"), 
        make_option("-p", "--password", dest="password", default='', 
                                help="Opensubtitles.com password. Must be set in upload mode. Default is blank (anonymous)"), 
        # misc options
        make_option("-s", "--server", dest="server", default=None,
                                help="Server address of Opensubtitles API"), 
        make_option("-P", "--proxy", dest="proxy", default=None, 
                                help="Proxy to use on internet connections")
        ]
        
    progress_bar_style= [progressbar.Bar(), progressbar.Percentage(), ' ', progressbar.ETA()]
    
class Graphical(object):
    pass
    
class General(object):
    name = APP_TITLE
    description = "%s is a Free Open-Source tool written in PYTHON for automatic download/upload subtitles for videofiles (DIVX,MPEG,AVI,etc) and DVD's using fast hashing."% name
    version = "%s v%s"% (APP_TITLE, APP_VERSION)
    rpc_server = "http://www.opensubtitles.org/xml-rpc"
    search_url = "http://www.opensubtitles.com/en/search2/sublanguageid-%s/moviename-%s/xml"
    
class Logging(object):
    log_level = logging.DEBUG
    log_format = "[%(asctime)s] %(levelname)s::%(name)s # %(message)s"
    log_dir = user.home # leave blank to use current path
    log_name = "%s.log"% General.name.lower()
    log_path = os.path.join(log_dir, log_name)
    log_mode = "a"
