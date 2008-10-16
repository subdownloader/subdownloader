#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Copyright (C) 2007 Ivan Garcia  capiscuas@gmail.com
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


import os.path
import re #To extract the imdb regexp from the NFO files
import logging
from FileManagement import get_extension
import RecursiveParser
import modules.videofile as videofile
import modules.subtitlefile as subtitlefile
import modules.metadata as metadata

log = logging.getLogger("subdownloader.FileManagement.FileScan")

class UserActionCanceled(Exception): 
    pass 
    
def FakeProgress(count=None,msg=""):
    if not count:
        return -1
    pass

def AutoDetectNFOfile(videofolder):
    if os.path.isdir(videofolder):
            for filename in os.listdir(videofolder):
                    if filename.endswith(".nfo"):
                            nfo_content = file(os.path.join(videofolder,filename)).read()
                            result = re.search('imdb\.\w+\/title\/tt(\d+)', nfo_content.lower())
                            if result:
                                    found_imdb_id = result.group(1)
                                    log.debug("Found Imdb from NFO file , IMDB = %s" % found_imdb_id)
                                    return found_imdb_id
    return None
        
def ScanFilesFolders(filepaths,recursively = True,report_progress=None, progress_end=None):
    all_videos_found = []
    all_subs_found = []
    for path in filepaths:
        log.debug("Scanning: %s"% path)
        if os.path.isdir(path):
            videos_found, subs_found = ScanFolder(path,recursively = True,report_progress=report_progress, progress_end=progress_end)
            all_videos_found += videos_found
            all_subs_found += subs_found
        else:
            if get_extension(path).lower() in videofile.VIDEOS_EXT:
                all_videos_found.append(videofile.VideoFile(path))
             #Interested to know which subtitles we have in the same folder
            all_subs_found += ScanSubtitlesFolder(os.path.dirname(path),recursively = False,report_progress=report_progress, progress_end=progress_end) 
    return all_videos_found, all_subs_found

"""Scanning all the Video and Subtitle files inside a Folder/Recursive Folders"""
def ScanFolder(folderpath,recursively = True,report_progress=None, progress_end=None):
    #Let's reset the progress bar to 0%
    log.debug("Scanning Folder %s" % folderpath)
    
    if report_progress == None:
        report_progress = FakeProgress
    
    #Let's reset the progress bar to 0%
    report_progress(0)

    parser = RecursiveParser.RecursiveParser()
    files_found = []
    try:
        # it's a file
        open(folderpath, 'r')
        if get_extension(folderpath).lower() in videofile.VIDEOS_EXT:
            files_found.append(folderpath)
        folderpath = os.path.dirname(folderpath)
    except IOError:
        # it's a directory
        #Scanning VIDEOS
        files_found = parser.getRecursiveFileList(folderpath, videofile.VIDEOS_EXT)

        
    videos_found = []
    # only work the video files if any were found
    if len(files_found):
        percentage = 100 / len(files_found)
        count = 0
        for i, filepath in enumerate(files_found):
            log.debug("Parsing %s ..."% filepath)
            if metadata.parse(filepath):
                videos_found.append(videofile.VideoFile(filepath))
            count += percentage

            if not report_progress(): #If it has been canceled
                raise UserActionCanceled()
            report_progress(count,_("Parsing video: %s")% os.path.basename(filepath))
    report_progress(0)
    
    #Scanning Subs
    files_found = parser.getRecursiveFileList(folderpath,subtitlefile.SUBTITLES_EXT)
    subs_found = []
    # only work the subtitles if any were found
    if len(files_found):
        percentage = 100 / len(files_found)
        count = 0
        for i, filepath in enumerate(files_found):
            subs_found.append(subtitlefile.SubtitleFile(online = False,id = filepath))
            count += percentage
            report_progress(count,_("Parsing sub: %s") % os.path.basename(filepath))
    report_progress(100,_("Finished hashing"))
    if progress_end:
        progress_end()
        
    return videos_found,subs_found
    

def ScanSubtitlesFolder(folderpath,recursively = True,report_progress=None, progress_end=None):
    if report_progress == None:
        report_progress = FakeProgress
    
    #Let's reset the progress bar to 0%
    report_progress(0)
    #Scanning Subs
    if recursively:
        files_found = parser.getRecursiveFileList(folderpath,subtitlefile.SUBTITLES_EXT)
    else:
        files_found =[]
        for filename in os.listdir(folderpath):
            if os.path.isfile(os.path.join(folderpath, filename)) and get_extension(filename).lower() in subtitlefile.SUBTITLES_EXT:
                files_found.append(os.path.join(folderpath, filename))
    
    subs_found = []
    # only work the subtitles if any were found
    if len(files_found):
        percentage = 100 / len(files_found)
        count = 0
        for i, filepath in enumerate(files_found):
            subs_found.append(subtitlefile.SubtitleFile(online = False,id = filepath))
            count += percentage
            report_progress(count,_("Parsing sub: %s") % os.path.basename(filepath))
    report_progress(100,_("Finished hashing"))
    if progress_end:
        progress_end()
        
    return subs_found
