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
import os.path
from subdownloader.FileManagement import Subtitle

class Filter(object):
    """Filter object to returned filtered information on given videos
        Example:
            filter = Filter(list_of_video_objects)
            subs = filter.subtitles_to_download()
    """
    def __init__(self, videos):
        self.log = logging.getLogger("subdownloader.cli.filter")
        self.log.debug("Creating Filter object for %i videos", len(videos))
        self.videos = videos
        
    def subtitles_to_download(self):
        subtitles_to_download ={}
        self.log.debug("Building subtitle matrix...")
        for video in self.videos:
            if video.getTotalSubtitles() == 1 and video.getTotalOnlineSubtitles():
                subtitle = video.getOneSubtitle()
                self.log.debug("- adding: %s: %s"% (subtitle.getIdOnline(), subtitle.getFileName()))
                subtitles_to_download[subtitle.getIdOnline()] = {'subtitle_path': os.path.join(video.getFolderPath(), subtitle.getFileName()), 'video': video}
            elif video.getTotalSubtitles() > 1 and video.getTotalOnlineSubtitles():
                #TODO: give user the list of subtitles to choose from
                # set a starting point to compare scores
                best_rated_sub = video.getOnlineSubtitles()[0]
                # iterate over all subtitles
                subpath_list = {}
                for sub in video.getOnlineSubtitles():
                    subpath_list[sub.getIdOnline()] = sub
                    if sub.getRating() > best_rated_sub.getRating():
                        best_rated_sub = sub
                #compare video name with subtitles name to find best match
                sub_match = Subtitle.AutoDetectSubtitle(video.getFilePath(), sub_list=subpath_list)
                if sub_match:
                    self.log.debug("Subtitle choosen by match")
                    sub_choice = subpath_list[sub_match]
                else:
                    self.log.debug("Subtitle choosen by rating")
                    sub_choice = best_rated_sub
                self.log.debug("- adding: %s"% (sub_choice.getFileName()))
                #subtitles_to_download[sub_choice.getIdOnline()] = {'subtitle_path': os.path.join(video.getFolderPath(), sub_choice.getFileName()), 'video': video}
                subtitle_filename = Subtitle.subtitle_name_gen(video.getFileName())
                #subtitles_to_download[sub_choice.getIdOnline()] = {'subtitle_path': os.path.join(video.getFolderPath(), subtitle_filename), 'video': video}
                subtitles_to_download[sub_choice.getIdOnline()] = os.path.join(video.getFolderPath(), subtitle_filename)
            
        return subtitles_to_download
