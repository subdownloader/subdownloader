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
import base64, zlib
import thread
from modules import SDService
from FileManagement import FileScan, Subtitle
from modules import filter, progressbar
import modules.configuration as conf
import languages.Languages as Languages

class Main(SDService.SDService):
    
    def __init__(self, cli_options):
        self.options = cli_options
        self.log = logging.getLogger("subdownloader.cli.main")
        
    def start_session(self):
        if not self.minimum_parameters():
            return
            
        check_result = self.check_directory()
        continue_ = 'y'
        if check_result == 2 and self.options.operation == "download" and self.options.interactive:
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
        SDService.SDService.__init__(self, 'osdb', proxy=self.options.proxy) 
        try:
            self.login(self.options.username, self.options.password)
        except Exception, e:
            self.log.error(e)
            return
        
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
                
            videoSearchResults = self.SearchSubtitles(language=lang_id, videos=self.videos)
            if self.options.test:
                for (i, video) in enumerate(self.videos):
                    #details = check_result['data'][0]
                    if video.getHash():
                        cd = 'cd%i'% (i+1)
                        curr_video = video
                        curr_sub = curr_video.getSubtitles()[0]
                        user_choices = {'moviereleasename': 'NA', 
                                        'movieaka': 'NA', 
                                        'moviefilename': curr_video.getFileName(), 
                                        'subfilename': curr_sub.getFileName(), 
                                        'sublanguageid': curr_sub.getLanguage(), 
                                        }
                        # interactive mode
                        if self.usermode == 'cli' and self.interactive:
                            self.log.info("Upload the following information:")
                            for (i, choice) in enumerate(user_choices):
                                self.log.info("[%i] %s: %s"% (i, choice, user_choices[choice]))
                            change = raw_input("Change any of the details? [y/N] ").lower() or 'n'
                            while change == 'y':
                                change_what = int(raw_input("What detail? "))
                                if change_what in range(len(user_choices.keys())):
                                    choice = user_choices.keys()[change_what]
                                    new_value = raw_input("%s: [%s] "% (choice, user_choices[choice])) or user_choices[choice]
                                    user_choices[choice] = new_value
                                change = raw_input("Change any more details? [y/N] ").lower() or 'n'
                            
            else:
                self.handle_operation(self.options.operation)
                
            video_hashes = [video.calculateOSDBHash() for video in videoSearchResults]
            video_filesizes =  [video.getSize() for video in videoSearchResults]
            video_movienames = [video.getMovieName() for video in videoSearchResults]
            #thread.start_new_thread(self.SDDBServer.sendHash, (video_hashes,video_movienames,  video_filesizes,  ))
            
            self.logout()
                
    def minimum_parameters(self):
        """Check for minimum parameters integrity"""
        # check if user set a video file name
        self.log.debug("Checking video file parameter...")
        if not self.options.videofile:  #in GUI this value needs to empty, but for CLI we replace by currentDir
            self.options.videofile = os.path.abspath(os.path.curdir)
            
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
            self.do_upload(self.videos)
            
        elif operation == "list":
            _filter = filter.Filter(self.videos, interactive=self.options.interactive)
            print _filter.subtitles_to_download()
            
        
    def check_directory(self):
        """ search for videos and subtitles in the given path """
        self.log.info("Scanning %s ..."% self.options.videofile)
        if self.options.logging == logging.DEBUG or not self.options.verbose:
            report_progress = progress_end = None
        elif self.options.verbose:
            #for cli progressbar
            progress = progressbar.ProgressBar(widgets=conf.Terminal.progress_bar_style).start()
            report_progress = progress.update
            progress_end = progress.finish
#        else:
#            report_progress = progress_end = None
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
                sub_match.setLanguage(Languages.name2xxx(sub_lang))
                video.addSubtitle(sub_match)
        if self.options.logging > logging.DEBUG and self.options.verbose:
            progress.finish()
            
    def do_upload(self, videos):
        self.log.debug("----------------")
        self.log.debug("UploadSubtitles RPC method starting...")
        check_result = self.TryUploadSubtitles(videos)
        if isinstance(check_result, bool) and not check_result:
            self.log.info("One or more videos don't have subtitles associated. Stopping upload.")
            return False
        elif check_result['alreadyindb']:
            self.log.info("Subtitle already exists in server database. Stopping upload.")
            return False
        elif check_result['data']:
            #TODO: make this to work with non-hashed subtitles (no 'data' to handle)
            # quick check to see if all video/subtitles are from same movie
            for movie_sub in check_result['data']:
                if not locals().has_key('IDMovie'):
                    IDMovie = {}
                if IDMovie.has_key(movie_sub['IDMovie']):
                    IDMovie[movie_sub['IDMovie']] += 1
                else:
                    IDMovie[movie_sub['IDMovie']] = 1
#                    if IDMovie != movie_sub['IDMovie']:
#                        self.log.error("All videos must have same ID. Stopping upload.")
#                        return False
#                else:
#                    IDMovie = movie_sub['IDMovie']
            #
            movie_info = {}
            for (i, video) in enumerate(videos):
#                for details in check_result['data']:
                details = check_result['data'][0]
                if video.getHash() == details['MovieHash']:
                    cd = 'cd%i'% (i+1)
                    curr_video = video
                    curr_sub = curr_video.getSubtitles()[0]
                    user_choices = {'moviereleasename': details['MovieName'], 
                                    'movieaka': details['MovieNameEng'], 
                                    'moviefilename': curr_video.getFileName(), 
                                    'subfilename': curr_sub.getFileName(), 
                                    'sublanguageid': curr_sub.getLanguage(), 
                                    }
                    # interactive mode
                    if self.usermode == 'cli' and self.interactive:
                        self.log.info("Upload the following information:")
                        for (i, choice) in enumerate(user_choices):
                            self.log.info("[%i] %s: %s"% (i, choice, user_choices[choice]))
                        change = raw_input("Change any of the details? [y/N] ").lower() or 'n'
                        while change == 'y':
                            change_what = int(raw_input("What detail? "))
                            if change_what in range(len(user_choices.keys())):
                                choice = user_choices.keys()[change_what]
                                new_value = raw_input("%s: [%s] "% (choice, user_choices[choice])) or user_choices[choice]
                                user_choices[choice] = new_value
                            change = raw_input("Change any more details? [y/N] ").lower() or 'n'
                        
                    # cook subtitle content
                    self.log.debug("Compressing subtitle...")
                    buf = open(curr_sub.getFilePath(), mode='rb').read()
                    curr_sub_content = base64.encodestring(zlib.compress(buf))
                    
                    # transfer info
                    movie_info[cd] = {'subhash': curr_sub.getHash(), 'subfilename': user_choices['subfilename'], 'moviehash': details['MovieHash'], 'moviebytesize': details['MovieByteSize'], 'movietimems': details['MovieTimeMS'], 'moviefps': curr_video.getFPS(), 'moviefilename': user_choices['moviefilename'], 'subcontent': curr_sub_content}
                    break
                        
            movie_info['baseinfo'] = {'idmovieimdb': details['IDMovieImdb'], 'moviereleasename': user_choices['moviereleasename'], 'movieaka': user_choices['movieaka'], 'sublanguageid': user_choices['sublanguageid'], 'subauthorcomment': "Upload by SubDownloader2.0 - www.subdownloader.net"} #details['SubAuthorComment']}
            
            return self.UploadSubtitles(movie_info)
