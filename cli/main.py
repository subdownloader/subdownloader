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

import logging, os.path
from subdownloader import OSDBServer
from subdownloader.FileManagement import FileScan, Subtitle
from subdownloader.modules import filter, progressbar
import subdownloader.modules.configuration as conf

class Main(OSDBServer.OSDBServer):
    
    def __init__(self, cli_options):
        self.options = cli_options
        self.log = logging.getLogger("subdownloader.cli.main")
        
    def start_session(self):
        if not self.minimum_parameters():
            return
            
        check_result = self.check_directory()
        continue_ = 'y'
        if check_result == 2 and self.options.interactive:
            continue_ = raw_input("Do you still want to search for missing subtitles? [Y/n] ").lower() or 'y'
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
                
    def minimum_parameters(self):
        """Check for minimum parameters integrity"""
        # check if user set a video file name
        self.log.debug("Checking video file parameter...")
        if self.options.videofile == os.path.abspath(os.path.curdir) and self.options.interactive:
            # confirm with user if he wants to use default directory
            self.options.videofile = raw_input("Enter your video(s) directory [%s]: "% self.options.videofile) or self.options.videofile
        if os.path.exists(self.options.videofile):
            self.log.debug("...passed")
        elif self.options.interactive:
            choice = raw_input("Enter your video(s) directory: ") or ""
            self.options.videofile = choice
            if os.path.exists(self.options.videofile):
                self.log.debug("...passed")
            else:
                self.log.debug("...failed")
                self.log.info("--video parameter looks bad")
                return False
        else:
            self.log.debug("...failed")
            self.log.info("--video parameter must be set")
            return False
           
        # check if user set language to use on subtitles
        self.log.debug("Checking language parameter...")
        if self.options.language:
            self.log.debug("...passed")
        else:
            self.log.debug("...failed")
            self.log.info("--lang parameter must be set")
            return False
        # everything is good
        return True
            
    def handle_operation(self, operation):
        if operation == "download":
            _filter = filter.Filter(self.videos, interactive=self.options.interactive)
            self.DownloadSubtitles(_filter.subtitles_to_download())
            
        elif operation == "upload":
            self.UploadSubtitles(self.videos)
            
        else:
            pass
        
    def check_directory(self):
        """ search for videos and subtitles in the given path """
        self.log.info("Scanning %s ..."% self.options.videofile)
        if self.options.verbose:
            #for cli progressbar
            progress = progressbar.ProgressBar(widgets=conf.Terminal.progress_bar_style).start()
            report_progress = progress.update
            progress_end = progress.finish
        else:
            report_progress = progress_end = None
        (self.videos, self.subs) = FileScan.ScanFolder(self.options.videofile, report_progress=report_progress, progress_end=progress_end)
        self.log.info("Videos found: %i Subtitles found: %i"%(len(self.videos), len(self.subs)))
        if len(self.videos):
            if len(self.videos) == len(self.subs):
                self.log.info("Number of videos and subtitles are the same. I could guess you already have all subtitles.")
                return 2
            else:
                self.log.info("Looks like some of your videos might need subtitles :)")
                return 1
        elif len(self.subs):
            self.log.debug("No videos were found")
            self.log.info("Although some subtitles exist, no videos were found. No subtitles would be needed for this case :(")
            return -1
        else:
            self.log.info("Nothing to do here")
            return -1
            
    def do_matching(self, videos, subtitles):
        if self.options.logging > logging.DEBUG and self.options.verbose:
            progress = progressbar.ProgressBar(widgets=conf.Terminal.progress_bar_style, maxval=len(videos)).start()

        for i, video in enumerate(videos):
            if self.options.logging > logging.DEBUG and self.options.verbose:
                progress.update(i+1)
            self.log.debug("Processing %s..."% video.getFileName())
            
            possible_subtitle = Subtitle.AutoDetectSubtitle(video.getFilePath())
            #self.log.debug("possible subtitle is: %s"% possible_subtitle)
            sub_match = None
            for subtitle in subtitles:
                sub_match = None
                if possible_subtitle == subtitle.getFilePath():
                    sub_match = subtitle
                    self.log.debug("Match found: %s"% sub_match.getFileName())
                    break
            if sub_match:
                sub_lang = Subtitle.AutoDetectLang(sub_match.getFilePath())
                sub_match.setLanguage(sub_lang[:3])
                video.addSubtitle(sub_match)
        if self.options.logging > logging.DEBUG and self.options.verbose:
            progress.finish()
