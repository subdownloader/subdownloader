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

import logging
from subdownloader import OSDBServer
from subdownloader.FileManagement import FileScan, Subtitle
from subdownloader.modules import terminal, filter
import videofile, subtitlefile

class Main(OSDBServer.OSDBServer):
    
    def __init__(self, cli_options):
        self.options = cli_options
        self.log = logging.getLogger("subdownloader.cli.main")
        
    def start_session(self):
        check_result = self.check_directory()
        continue_ = 'y'
        if check_result == 2 and self.options.interactive:
            continue_ = raw_input("Do you still want to search for missing subtitles? (Y/N)\n: ").lower() or 'y'
            if continue_ != 'y':
                return
        if check_result == -1:
            return
        if continue_ == 'y' or not self.options.interactive:
            self.log.info("Starting subtitle search, please wait...")
            self.do_matching(self.videos, self.subs)
            result = "\n"
            for video in self.videos:
                video_name = video.getFileName()
                if video.hasSubtitles():
                    if video.getTotalLocalSubtitles() == 1:
                        sub_name = video.getSubtitles()[0].getFileName()
                    elif video.getTotalLocalSubtitles() > 1:
                        sub_name = ""
                        for sub in video.getSubtitles():
                            sub_name += "%s, "% sub.getFileName()
                else: sub_name = "NO MATCH"
                result += "%s -> %s\n"% (video_name, sub_name)
            self.log.debug(result)
            
        self.log.debug("Starting XMLRPC session...")
        OSDBServer.OSDBServer.__init__(self, self.options)
        
        if self.is_connected():
            # set language
            if len(self.options.language) == 2:
                lang_id = self.GetSubLanguages(self.options.language)
            elif len(self.options.language) == 3:
                lang_id = self.options.language
            else:
                lang_id = 'all'
                self.log.debug("Wrong language code was set, using default: %r"% lang_id)
            # check if we will overwrite local subtitles
            if self.options.overwrite_local:
                self.log.debug("Overwriting local subtitles is set. Searching for victims...")
                for video in self.videos:
                    if video.hasSubtitles():
                        check_result = self.CheckSubHash(video)
                        for hash in check_result:
                            if check_result[hash] == '0':
                                # we found a subtitle that's not on server (nos)
                                nos_sub = video.getSubtitle(hash)
                                self.log.debug("Not on server - %s - jailing..."% nos_sub.getFileName())
                                video.setNOSSubtitle(nos_sub)
                
            self.SearchSubtitles(language=lang_id, videos=self.videos)
            self.handle_operation(self.options.operation)
            
            self.logout()
                
    def handle_operation(self, operation):
        if operation == "download":
            _filter = filter.Filter(self.videos)
            self.DownloadSubtitles(_filter.subtitles_to_download())
            
        elif operation == "upload":
            self.UploadSubtitles(self.videos)
            
        else:
            pass
        
    def check_directory(self):
        """ search for videos and subtitles in the given path """
        self.log.debug("Checking given directory")
        (self.videos, self.subs) = FileScan.ScanFolder(self.options.videofile)
        self.log.info("Videos found: %i Subtitles found: %i"%(len(self.videos), len(self.subs)))
        if len(self.videos):
#            self.log.info("Videos found: %i"% len(self.videos))
#            if len(self.subs):
#                self.log.info("Subtitles found: %i"% len(self.subs))
            if len(self.videos) == len(self.subs):
                self.log.info("Number of videos and subtitles are the same. I could guess you already have all subtitles.")
                return 2
            else:
                self.log.info("Looks like some of your videos might need subtitles :)")
                return 1
        elif len(self.subs):
            self.log.debug("No videos were found")
#            self.log.info("Subtitles found: %i"% len(self.subs))
            self.log.info("Although some subtitles exist, no videos were found. No subtitles would be needed for this case :(")
            return -1
        else:
            self.log.info("Nothing to do here")
            return -1
            
    def do_matching(self, videos, subtitles):
        if self.options.logging > logging.DEBUG:
                term = terminal.TerminalController()
                progress = terminal.ProgressBar(term, 'Matching %i videos with %i subtitles'% (len(videos), len(subtitles)))

        for i, video in enumerate(videos):
            if self.options.logging > logging.DEBUG:
                progress.update(float(i+1)/len(videos), "Processing %s..."% video.getFileName())
            self.log.debug("Processing %s..."% video.getFileName())
            
            possible_subtitle = Subtitle.AutoDetectSubtitle(video.getFilePath())
            #self.log.debug("possible subtitle is: %s"% possible_subtitle)
            sub_match = None
            for subtitle in subtitles:
                sub_match = None
                if possible_subtitle == subtitle.getFilePath():
                    sub_match = subtitle
                    if self.options.logging > logging.DEBUG:
                        progress.update(float(i+1)/len(videos), "Match found: %s"% sub_match.getFileName())
                    self.log.debug("Match found: %s"% sub_match.getFileName())
                    break
            if sub_match:
                if self.options.logging > logging.DEBUG:
                    progress.update(float(i+1)/len(videos), "Auto-detecting language of %s..."% sub_match.getFileName())
                sub_lang = Subtitle.AutoDetectLang(sub_match.getFilePath())
                if self.options.logging > logging.DEBUG:
                    progress.update(float(i+1)/len(videos), "Setting language to %s..."% sub_lang[:3])
                sub_match.setLanguage(sub_lang[:3])
                video.addSubtitle(sub_match)
        if self.options.logging > logging.DEBUG:
            progress.end()
