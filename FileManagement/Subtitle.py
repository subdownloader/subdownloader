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

import os
import subdownloader.subtitlefile as subtitlefile
from subdownloader.FileManagement import get_extension, clear_string, without_extension
from subdownloader.languages import Languages, autodetect_lang

def AutoDetectSubtitle(pathvideofile):
    """ will try to guess the subtitle for the given filepath video """
    
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
    
def AutoDetectLang(filepath):
    if isSubtitle(filepath):
        subtitle_content = file(filepath,mode='rb').read()
        Languages.CleanTagsFile(subtitle_content)
        n = autodetect_lang._NGram()
        l = autodetect_lang.NGram(os.path.join(os.getcwd(),'lm'))
        percentage, lang = l.classify(subtitle_content)
        pos = lang.rfind("-")
        if pos != -1:
            return lang[:pos]
        else:
            return lang
    else:
        return ""
        
def isSubtitle(filepath):
    if get_extension(filepath) in SUBTITLES_EXT:
        return True
    return False
