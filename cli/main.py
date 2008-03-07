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
from subdownloader.FileManagement import FileScan, Subtitle
import videofile, subtitlefile

class Main(OSDBServer.OSDBServer):
    
    def __init__(self, cli_options):
        self.options = cli_options
        self.log = logging.getLogger("subdownloader.cli.main")
        
    def start_session(self):
        check_result = self.check_directory()
        continue_ = 'y'
        if check_result == 2:
            continue_ = raw_input("Do you still want to search for missing subtitles? (Y/n)\n: ")
            if continue_.lower() != 'y':
                return
        if check_result == 0:
            return
        if continue_ == 'y':
            self.log.info("Starting subtitle search...")
            self.build_matrix(self.videos, self.subs)
            result = "\n"
            for video in self.videos_matrix:
                if video: video_name = video.getFileName()
                else: video_name = "NO MATCH"
                if self.videos_matrix[video]: sub_name = self.videos_matrix[video].getFileName()
                else: sub_name = "NO MATCH"
                result += "%s -> %s\n"% (video_name, sub_name)
            self.log.info(result)
            
        self.log.debug("Starting XMLRPC session...")
        OSDB = OSDBServer.OSDBServer(self.options)
        
    def check_directory(self):
        """ search for videos and subtitles in the given path """
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
        elif len(self.subs):
            self.log.debug("No videos were found")
            self.log.debug("Subtitles found: %i"% len(self.subs))
            self.log.info("Although some subtitles exist, no videos were found. No subtitles would be needed for this case :(")
            return 0
        else:
            self.log.info("Nothing to do here")
            return 0
            
    def build_matrix(self, videos, subtitles):
        """ construct a dictionary contaning existing videos and possible subtitle match """
        self.videos_matrix = {}
        for video in self.videos:
            self.log.debug("Processing %s..."% video.getFileName())
            possible_subtitle = Subtitle.AutoDetectSubtitle(video.getFilePath())
            self.log.debug("possible subtitle is: %s"% possible_subtitle)
            sub_match = None
            for subtitle in self.subs:
                sub_match = None
                if possible_subtitle == subtitle.getFilePath():
                    sub_match = subtitle
                    self.log.debug("Match found: %s"% sub_match.getFileName())
                    break
            self.videos_matrix[video] = sub_match
            
        return self.videos_matrix
        
