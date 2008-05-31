#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import re, os, logging
import subdownloader.videofile as videofile
import subdownloader.subtitlefile as subtitlefile
from subdownloader.FileManagement import get_extension, clear_string, without_extension
from subdownloader.languages import Languages, autodetect_lang

log = logging.getLogger("subdownloader.FileManagement.Subtitle")

def AutoDetectSubtitle(pathvideofile, sub_list=None):
    """ will try to guess the subtitle for the given filepath video """
    log.debug("----------------")
    log.debug("AutoDetectSubtitle started with: %r, %r"% (pathvideofile, sub_list))
    
    if os.path.isfile(pathvideofile):
        videofolder = os.path.dirname(pathvideofile)
        filename1_noextension = without_extension(pathvideofile)
    else:
        log.debug("AutoDetectSubtitle argument must be a complete video path")
        return ""
 
    #1st METHOD
    log.debug("1st method starting...")
    for ext in subtitlefile.SUBTITLES_EXT:
        possiblefilenamesrt = filename1_noextension + "." + ext
        if sub_list:
            try:
                # check if subtitle is in our list
                sub_list.index(possiblefilenamesrt)
                return possiblefilenamesrt
            except ValueError, e:
                log.debug(e)
            except AttributeError, e:
                log.debug(e)
        elif os.path.exists(possiblefilenamesrt):
            return possiblefilenamesrt
 
    #2nd METHOD FIND THE AVI NAME MERGED INTO THE SUB NAME
    log.debug("2nd method starting...")
    cleaned_file = clear_string(filename1_noextension.lower())
    filesfound = []
    if sub_list:
        search_list = sub_list
    else:
        search_list = os.listdir(videofolder)
    for filename in search_list:
        for ext in subtitlefile.SUBTITLES_EXT:
            try:
                if filename.endswith("."+ext):
                    filesfound.append(filename)
                    cleaned_found = clear_string(without_extension(filename.lower()))
                    if "srt" in subtitlefile.SUBTITLES_EXT and cleaned_found.find(cleaned_file) != -1:
                        if sub_list:
                            return filename
                        else:
                            return os.path.join(videofolder,filename)
                    elif cleaned_file.find(cleaned_found) != -1:
                        if sub_list:
                            return filename
                        else:
                            return os.path.join(videofolder,filename)
            except AttributeError, e:
                log.error(e)
    
    #3rd METHOD SCORE EVERY SUBTITLE (this needs the sub_list)
    if sub_list:
        log.debug("3rd method starting...")
        sub_scores = score_subtitles(pathvideofile, sub_list)
        best_scored_sub = sub_scores.keys()[0]
        for sub in sub_scores:
            if sub_scores[sub] > sub_scores[best_scored_sub]:
                best_scored_sub = sub
        if sub_scores[best_scored_sub] > 0:
            return best_scored_sub
    else:
        log.debug("3rd was skipped")
    
 
    #4th METHOD WE TAKE THE SUB IF THERE IS ONLY ONE
    log.debug("4th method starting...")
    if len(filesfound) == 1:
        if sub_list:
            return filesfound[0]
        else:
            return os.path.join(videofolder,filesfound[0])
    
    return ""
    
def score_subtitles(video, subtitle_list):
    """Will to a pseudo scoring on the subtitle list
    @video: video file name
    @subtitle_list: list of subtitle file names
    
    returns dictionary like {'subtitle_file_name': score}
    """
    log.debug("Subtitle scoring started with: %r, %r"% (video, subtitle_list))
    video_name = os.path.basename(video)
    # set initial scores to 0
    if isinstance(subtitle_list, list):
        sub_dict = dict(zip(subtitle_list, [0]*len(subtitle_list)))
    elif isinstance(subtitle_list, dict):
        sub_dict = dict(zip(subtitle_list.keys(), [0]*len(subtitle_list)))
    for sub in sub_dict:
        sub_name = subtitle_list[sub].getFileName()
        #fetch the seperating character
        if re.search("\W",sub_name):
            sep_ch = re.search("\W",sub_name).group(0)
            splited_sub = sub_name.split(sep_ch)
            # iterate over each word and serch for it in the video file name
            for w in splited_sub:
                if w in video_name:
                    sub_dict[sub] += 1
        else:
            continue
        log.debug("scoring for %s is %i"% (sub_name, sub_dict[sub]))
            
    # return scored subtitles
    return sub_dict

#FIXME: when language is 'Brazlian' wrong value is returned: 'Bra' instead of 'pob')
def AutoDetectLang(filepath):
    if isSubtitle(filepath):
        subtitle_content = file(filepath,mode='rb').read()
        Languages.CleanTagsFile(subtitle_content)
        n = autodetect_lang._NGram()
        l = autodetect_lang.NGram(os.path.join(os.getcwd(),'languages','lm'))
        percentage, lang = l.classify(subtitle_content)
        pos = lang.rfind("-") #for example belarus-windows1251.lm we only need belarus
        if pos != -1:
            return lang[:pos]
        else:
            return lang
    else:
        return ""
        
def subtitle_name_gen(video_filename, extension=".srt"):
    """Generates a subtitle file name given the video file name
    """
    video_name = ""
    sub_name = ""
    if isinstance(video_filename, str):
        if get_extension(video_filename) in videofile.VIDEOS_EXT:
            video_name = without_extension(video_filename)
    elif isinstance(video_filename, videofile):
        if get_extension(video_filename.getFileName()) in videofile.VIDEOS_EXT:
            video_name = without_extension(video_filename.getFileName())
            
    if video_name:
        sub_name = video_name + extension
        return sub_name
    else:
        log.debug("No video name to generate subtitle file name")
        return ""
        
def isSubtitle(filepath):
    if get_extension(filepath) in subtitlefile.SUBTITLES_EXT:
        return True
    return False
