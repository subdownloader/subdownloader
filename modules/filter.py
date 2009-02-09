#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) 2007 Ivan Garcia <contact@ivangarcia.org>
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    see <http://www.gnu.org/licenses/>.

import logging
import os.path
from FileManagement import Subtitle

class Filter(object):
    """Filter object to returned filtered information on given videos
        Example:
            filter = Filter(list_of_video_objects)
            subs = filter.subtitles_to_download()
    """
    def __init__(self, videos, interactive=False, rename_subs=False):
        self.log = logging.getLogger("subdownloader.cli.filter")
        self.log.debug("Creating Filter object for %i videos", len(videos))
        self.videos = videos
        self.interactive = interactive
        self.rename_subs = rename_subs
        
    def subtitles_to_download(self):
        subtitles_to_download ={}
        self.log.debug("Building subtitle matrix ...")
        for video in self.videos:
            self.log.debug("(total: %i online: %i..."% (video.getTotalSubtitles(), video.getTotalOnlineSubtitles()))
            if video.getTotalOnlineSubtitles() == 1:
                subtitle = video.getOneSubtitle()
                choice = 'y'
                if self.interactive:
                    self.log.info("Only one subtitle was found for %s: %s"% (video.getFileName(), subtitle.getFileName()))
                    choice = raw_input("Is that correct? [Y/n]" ).lower() or 'y'
                if choice == 'y':
                    self.log.debug("- adding: %s: %s"% (subtitle.getIdFileOnline(), subtitle.getFileName()))
                    #subtitles_to_download[subtitle.getIdFileOnline()] = {'subtitle_path': os.path.join(video.getFolderPath(), subtitle.getFileName()), 'video': video}
                    if self.rename_subs:
                        subtitle_filename = Subtitle.subtitle_name_gen(video.getFileName())
                    else:
                        subtitle_filename = subtitle.getFileName()
                    subtitles_to_download[subtitle.getIdFileOnline()] = os.path.join(video.getFolderPath(), subtitle_filename)
            elif video.getTotalOnlineSubtitles() > 1:
                choice = 'auto_'
                if self.interactive:
                    self.log.info("Looks like \"%s\" has more than one subtitle candidate."% video.getFileName())
                    choices = ['auto']
                    for i, sub in enumerate(video.getOnlineSubtitles()):
                        self.log.info("[%i] %s (rate: %s)"% (i, sub.getFileName(), sub.getRating()))
                        choices += [str(i)]
                    self.log.info("[auto] Subdownloader will select one for you.")
                    while choice not in choices:
                        choice = raw_input("Please make you choice: [auto] ").lower() or 'auto'
                    if choice != 'auto':
                        sub_choice = video.getOnlineSubtitles()[int(choice)]
                        
                if choice == 'auto' or choice == 'auto_':
                    # set a starting point to compare scores
                    best_rated_sub = video.getOnlineSubtitles()[0]
                    # iterate over all subtitles
                    subpath_list = {}
                    for sub in video.getOnlineSubtitles():
                        subpath_list[sub.getIdOnline()] = sub
                        if sub.getRating() > best_rated_sub.getRating():
                            best_rated_sub = sub
                    #compare video name with subtitles name to find best match
                    sub_match = Subtitle.AutoDetectSubtitle(video.getFilePath(), sub_list=subpath_list) #FIXME: seems u sending a dictionary, but this function needs a list
                    if sub_match:
                        self.log.debug("Subtitle choosen by match")
                        sub_choice = subpath_list[sub_match]
                    else:
                        self.log.debug("Subtitle choosen by rating")
                        sub_choice = best_rated_sub
                    self.log.debug("- adding: %s"% (sub_choice.getFileName()))
                    
                #subtitles_to_download[sub_choice.getIdFileOnline()] = {'subtitle_path': os.path.join(video.getFolderPath(), sub_choice.getFileName()), 'video': video}
                if self.rename_subs:
                    subtitle_filename = Subtitle.subtitle_name_gen(video.getFileName())
                else:
                    subtitle_filename = subtitle.getFileName()

#                subtitle_filename = Subtitle.subtitle_name_gen(video.getFileName())
                #subtitles_to_download[sub_choice.getIdFileOnline()] = {'subtitle_path': os.path.join(video.getFolderPath(), subtitle_filename), 'video': video}
                subtitles_to_download[sub_choice.getIdFileOnline()] = os.path.join(video.getFolderPath(), subtitle_filename)
            else:
                self.log.info("No subtitle was downloaded \"%s\". Maybe you already have it?"% video.getFileName())
            
        print subtitles_to_download
        return subtitles_to_download
