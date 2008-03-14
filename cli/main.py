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
        
    def start_session(self, testing=False):
        check_result = self.check_directory()
        continue_ = 'y'
        if check_result == 2:
            continue_ = raw_input("Do you still want to search for missing subtitles? (Y/N)\n: ").lower() or 'y'
            if continue_ != 'y':
                return
        if check_result == 0:
            return
        if continue_ == 'y':
            self.log.info("Starting subtitle search...")
            self.do_matching(self.videos, self.subs)
            result = "\n"
            for video in self.videos:
                if video: video_name = video.getFileName()
                else: video_name = "NO MATCH"
                if len(video.getSubtitles()):
                    if len(video.getSubtitles()) == 1:
                        sub_name = video.getSubtitles()[0].getFileName()
                    elif len(video.getSubtitles()) > 1:
                        sub_name = ""
                        for sub in video.getSubtitles():
                            sub_name += "%s, "% sub.getFileName()
                else: sub_name = "NO MATCH"
                result += "%s -> %s\n"% (video_name, sub_name)
            self.log.info(result)
            
        self.log.debug("Starting XMLRPC session...")
        OSDBServer.OSDBServer.__init__(self, self.options)
        
        if testing:
            if self.is_connected():
#                print self.GetAvailableTranslations()
#                lang_id = self.GetSubLanguages(self.options.language)
                result = self.SearchSubtitles(videos=self.videos)
                self.UploadSubtitles(self.videos)
#                for r in result:
#                    print r in self.videos
#                    print r.getFileName(), r.getHash(), r.getSubtitles()
        else:
            if self.is_connected():
                if len(self.options.language) == 2:
                    lang_id = self.GetSubLanguages(self.options.language)
                else:
                    lang_id = self.options.language
                self.SearchSubtitles(language=lang_id, videos=self.videos)
                self.handle_operation(self.options.operation)
            
        self.logout()
                
    def handle_operation(self, operation):
        if operation == "download":
            self.DownloadSubtitles(self.videos)
            
        elif operation == "upload":
            pass
        else:
            pass
        
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
            
    def do_matching(self, videos, subtitles):
        for video in self.videos:
            self.log.debug("Processing %s..."% video.getFileName())
            possible_subtitle = Subtitle.AutoDetectSubtitle(video.getFilePath())
            #self.log.debug("possible subtitle is: %s"% possible_subtitle)
            sub_match = None
            for subtitle in self.subs:
                sub_match = None
                if possible_subtitle == subtitle.getFilePath():
                    sub_match = subtitle
                    self.log.debug("Match found: %s"% sub_match.getFileName())
                    break
            if sub_match:
                video.addSubtitle(sub_match)
