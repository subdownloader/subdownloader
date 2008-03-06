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


import os.path
import logging
from subdownloader import *
from subdownloader.FileManagement import get_extension, clear_string, without_extension
import RecursiveParser
import subdownloader.videofile as videofile
import subdownloader.subtitlefile as subtitlefile

log = logging.getLogger("subdownloader.FileManagement.FileScan")

def FakeProgress(count,msg=""):
    pass

"""Scanning all the Video and Subtitle files inside a Folder/Recursive Folders"""
def ScanFolder(folderpath,recursively = True,report_progress=None):    
    #Let's reset the progress bar to 0%
    if report_progress == None:
        report_progress = FakeProgress
    
    #Let's reset the progress bar to 0%
    report_progress(0)
    parser = RecursiveParser.RecursiveParser()
    files_found = []
    try:
        # it's a file
        open(folderpath, 'r')
        if get_extension(folderpath) in videofile.VIDEOS_EXT:
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
        for filepath in files_found:
            videos_found.append(videofile.VideoFile(filepath))
            count += percentage
            report_progress(count,"Hashing video: " + os.path.basename(filepath))
    
    report_progress(0)
    
    #Scanning Subs
    files_found = parser.getRecursiveFileList(folderpath,subtitlefile.SUBTITLES_EXT)
    subs_found = []
    # only work the subtitles if any were found
    if len(files_found):
        percentage = 100 / len(files_found)
        count = 0
        for filepath in files_found:
            subs_found.append(subtitlefile.SubtitleFile(online = False,id = filepath))
            count += percentage
            report_progress(count,"Hashing sub: " + os.path.basename(filepath))
        
    report_progress(100,"Finished hashing")
        
        
    return videos_found,subs_found
    
def guessSubtitle(filepath):
    """ will try to guess the subtitle for the given filepath video """
    video = filepath

def AutoDetectSubtitle(pathvideofile):
 
    if os.path.isfile(pathvideofile):
        videofolder = os.path.dirname(pathvideofile)
        filename1_noextension = without_extension(pathvideofile)
    else:
        log.debug("AutoDetectSubtitle argument must be a complete video path")
        return ""
 
    #1st METHOD
    for ext in subtitlefile.SUBTITLES_EXT:
        possiblefilenamesrt = filename1_noextension + "." + ext
        if os.path.exists(possiblefilenamesrt):
            return possiblefilenamesrt
 
 
    #2nd METHOD FIND THE AVI NAME MERGED INTO THE SUB NAME
    cleaned_file = clear_string(filename1_noextension.lower())
    filesfound = []
    for filename in os.listdir(videofolder):
        for ext in subtitlefile.SUBTITLES_EXT:
            if filename.endswith("."+ext):
                filesfound.append(filename)
                cleaned_found = clear_string(without_extension(filename.lower()))
                if "srt" in subtitlefile.SUBTITLES_EXT:
                    if cleaned_found.find(cleaned_file) != -1:
                        return os.path.join(videofolder,filename)
                else:
                    if cleaned_file.find(cleaned_found) != -1:
                        return os.path.join(videofolder,filename)
 
 
    #3rd METHOD WE TAKE THE SUB IF THERE IS ONLY ONE
    if len(filesfound) == 1:
        return os.path.join(videofolder,filesfound[0])
    
    return ""
