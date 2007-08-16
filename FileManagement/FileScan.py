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
from subdownloader import *
import RecursiveParser
import subdownloader.videofile as videofile
import subdownloader.subtitlefile as subtitlefile

def FakeProgress(count,msg):
    pass

"""Scanning all the Video and Subtitle files inside a Folder/Recursive Folders"""
def ScanFolder(folderpath,recursively = True,report_progress=None):    
    #Let's reset the progress bar to 0%
    if report_progress == None:
        report_progress = FakeProgress
    
    #Let's reset the progress bar to 0%
    report_progress(0)
    parser = RecursiveParser.RecursiveParser()
    #Scanning VIDEOS
    files_found = parser.getRecursiveFileList(folderpath, videofile.VIDEOS_EXT)
    videos_found = []
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
    percentage = 100 / len(files_found)
    count = 0
    for filepath in files_found:
        subs_found.append(subtitlefile.SubtitleFile(online = False,address = filepath))
        count += percentage
        report_progress(count,"Hashing sub: " + os.path.basename(filepath))
        
    report_progress(100,"Finished hashing")
        
        
    return videos_found,subs_found
    