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

import logging
from subdownloader import OSDBServer
from subdownloader.FileManagement import FileScan
import videofile, subtitlefile

class Main(OSDBServer.OSDBServer):
    
    def __init__(self, cli_options):
        self.options = cli_options
        self.log = logging.getLogger("subdownloader.cli.main")
        
    def start_session(self):
        self.check_directory()
        #self.check_video()
        
    def check_directory(self):
        self.log.debug("Checking given directory")
        (self.videos, self.subs) = FileScan.ScanFolder(self.options.videofile)
        if len(self.videos):
            self.log.debug("Videos found: %i"% len(self.videos))
            if len(self.subs):
                self.log.debug("Subtitles found: %i"% len(self.subs))
            if len(self.videos) == len(self.subs):
                self.log.info("Number of videos and subtitles are the same. I could guess you already have all subtitles.")
                return 2
            else:
                self.log.info("Looks like some of your videos might need subtitles :)")
                return 1
        else:
            self.log.debug("No videos were found")
            self.log.info("Nothing to do here")
            return 0
    
