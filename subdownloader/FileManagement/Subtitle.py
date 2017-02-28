# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
import re

import subdownloader.FileManagement.subtitlefile as subtitlefile

import subdownloader.FileManagement.videofile as videofile
from subdownloader.FileManagement import get_extension, clear_string, without_extension
from subdownloader.languages import autodetect_lang, language

log = logging.getLogger("subdownloader.FileManagement.Subtitle")


def AutoDetectSubtitle(pathvideofile, sub_list=None):
    """ will try to guess the subtitle for the given filepath video """
    log.debug("----------------")
    log.debug("AutoDetectSubtitle started with: %r, %r" %
              (pathvideofile, sub_list))

    if os.path.isfile(pathvideofile):
        videofolder = os.path.dirname(pathvideofile)
        filename1_noextension = without_extension(
            os.path.basename(pathvideofile))
    else:
        log.debug("AutoDetectSubtitle argument must be a complete video path")
        return ""

    # 1st METHOD , EXACT FILENAME THAN THE VIDEO WITHOUT EXTENSION
    log.debug("1st method starting...")
    for ext in subtitlefile.SUBTITLES_EXT:
        possiblefilenamesrt = filename1_noextension + "." + ext
        if sub_list:
            # print sub_list
            try:
                # check if subtitle is in our list
                if isinstance(sub_list, list):
                    sub_list.index(possiblefilenamesrt)
                    return possiblefilenamesrt
            except ValueError as e:
                log.debug(e)
            except AttributeError as e:
                log.debug(e)
        elif os.path.exists(os.path.join(videofolder, possiblefilenamesrt)):
            return os.path.join(videofolder, possiblefilenamesrt)

    # 2nd METHOD FIND THE AVI NAME MERGED INTO THE SUB NAME
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
                if filename.lower().endswith("." + ext):
                    filesfound.append(filename)  # To be used in the 4th method
                    cleaned_found = clear_string(
                        without_extension(filename.lower()))
                    if "srt" in subtitlefile.SUBTITLES_EXT and cleaned_found.find(cleaned_file) != -1:
                        if sub_list:
                            return filename
                        else:
                            return os.path.join(videofolder, filename)
                    elif cleaned_file.find(cleaned_found) != -1:
                        if sub_list:
                            return filename
                        else:
                            return os.path.join(videofolder, filename)
            except AttributeError as e:
                log.error(e)

    # 3rd METHOD SCORE EVERY SUBTITLE (this needs the sub_list) (by searching
    # the filename of the video in the content of the subtitle)
    if sub_list:
        log.debug("3rd method starting...")
        sub_scores = score_subtitles(pathvideofile, sub_list)
        best_sub = None
        best_sub_score = -1
        for sub in sub_scores:
            if sub_scores[sub] > best_sub_score:
                best_sub = sub
                best_sub_score = sub_scores[sub]
        if best_sub is not None:
            return best_sub
    else:
        log.debug("3rd was skipped")

    # 4th METHOD WE TAKE THE SUB IF THERE IS ONLY ONE
    log.debug("4th method starting...")
    if len(filesfound) == 1:
        if sub_list:
            return filesfound[0]
        else:
            return os.path.join(videofolder, filesfound[0])

    return ""


def score_subtitles(video, subtitle_list):
    """Will to a pseudo scoring on the subtitle list
    @video: video file name
    @subtitle_list: list of subtitle file names

    returns dictionary like {'subtitle_file_name': score}
    """
    log.debug("Subtitle scoring started with: %r, %r" % (video, subtitle_list))
    video_name = os.path.basename(video)
    # set initial scores to 0
    if isinstance(subtitle_list, list):
        sub_dict = dict(zip(subtitle_list, [0] * len(subtitle_list)))
    elif isinstance(subtitle_list, dict):
        sub_dict = dict(zip(subtitle_list.keys(), [0] * len(subtitle_list)))
    for sub in sub_dict:
        sub_name = subtitle_list[sub].get_filepath()
        # fetch the seperating character
        if re.search("\W", sub_name):
            sep_ch = re.search("\W", sub_name).group(0)
            splited_sub = sub_name.split(sep_ch)
            # iterate over each word and serch for it in the video file name
            for w in splited_sub:
                if w in video_name:
                    sub_dict[sub] += 1
        else:
            continue
        log.debug("scoring for %s is %i" % (sub_name, sub_dict[sub]))

    # return scored subtitles
    return sub_dict


def GetLangFromFilename(filepath):
    filepath = os.path.basename(filepath)
    if filepath.count('.') >= 2:
        return get_extension(without_extension(filepath))
    else:
        return ""

# FIXME: when language is 'Brazlian' wrong value is returned: 'Bra'
# instead of 'pob')


def AutoDetectLang(filepath):
    if isSubtitle(filepath):
        subtitle_content = open(filepath, mode='rb').read()
        language.CleanTagsFile(subtitle_content)
        # Initializing the Language Detector
        n = autodetect_lang._NGram()
        l = autodetect_lang.NGram()
        percentage, lang = l.classify(subtitle_content)
        # for example belarus-windows1251.lm we only need belarus
        pos = lang.rfind("-")
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
       # video_filename = video_filename.lower()
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
    if get_extension(filepath).lower() in subtitlefile.SUBTITLES_EXT:
        return True
    return False
