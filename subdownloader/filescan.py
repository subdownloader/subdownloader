# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
import os

from subdownloader.subtitle2 import LocalSubtitleFile, SubtitleFileNetwork, SUBTITLES_EXT
from subdownloader.video2 import NotAVideoException, VideoFile, VIDEOS_EXT

log = logging.getLogger('subdownloader.filescan')


def extract_extension(path):
    # FIXME: when refactoring has finished, remove duplicate extract_extension functions.
    root, ext = os.path.splitext(path)
    if ext:
        return ext[1:].lower()
    return ''


def scan_videopaths(videopaths, callback, recursive=False):
    callback.set_range(0, len(videopaths))
    all_videos = []
    all_subtitles = []
    for videopath_i, videopath in enumerate(videopaths):
        callback.update(videopath_i)
        subcallback = callback.get_child_progress(videopath_i, videopath_i + 1)
        videos, subtitles = scan_videopath(videopath, subcallback, recursive)
        all_videos.extend(videos)
        all_subtitles.extend(subtitles)
    callback.finish()
    return all_videos, all_subtitles


def scan_videopath(videopath, callback, recursive=False):
    """
    Scan the videopath string for video files.
    :param videopath: String of the path
    :param callback: Instance of ProgressCallback
    :param recursive: True if the scanning should happen recursive
    :return: tuple with List of VideoFile's and list of SubtitleFileNetwork's
    """
    log.debug('scan_videopath(videopath="{videopath}", recursive={recursive})'.format(
        videopath=videopath, recursive=recursive))
    if os.path.isdir(videopath):
        log.debug('"{videopath}" is a directory'.format(videopath=videopath))
        return __scan_folder(videopath, callback=callback, recursive=recursive)
    elif os.path.isfile(videopath):
        log.debug('"{videopath}" is a file'.format(videopath=videopath))
        [all_subs, _] = filter_files_extensions(os.path.dirname(videopath), [SUBTITLES_EXT, VIDEOS_EXT])
        [_, video] = filter_files_extensions([videopath], [SUBTITLES_EXT, VIDEOS_EXT])
        sub_videos = [all_subs, video]
        path_subvideos = {os.path.dirname(videopath): sub_videos}
        return merge_path_subvideo(path_subvideos, callback)
    else:
        log.debug('"{videopath}" is of unknown type'.format(videopath=videopath))
        return [], []


def __scan_folder(folder_path, callback, recursive=False):
    """
    Scan a folder for videos and subtitles
    :param folder_path: String of a directory
    :param callback: Instance of ProgressCallback
    :param recursive: True if the scanning should happen recursive
    :return: A SubVideoFolderTree object with all the videos and subtitles
    """
    log.debug('__scan_folder(folder_path="{folder_path}", recursive={recursive})'.format(folder_path=folder_path,
                                                                                         recursive=recursive))
    path_subvideos = {}
    if recursive:
        for dir_path, _, files in os.walk(folder_path):
            log.debug('walking current directory:"{}"'.format(dir_path))
            sub_videos = filter_files_extensions(files, [SUBTITLES_EXT, VIDEOS_EXT])
            path_subvideos[dir_path] = sub_videos
    else:
        files = filter(os.path.isfile, os.listdir(folder_path))
        sub_videos = filter_files_extensions(files, [SUBTITLES_EXT, VIDEOS_EXT])
        path_subvideos[folder_path] = sub_videos
    return merge_path_subvideo(path_subvideos, callback)


def merge_path_subvideo(path_subvideos, callback):
    """
    Merge subtitles into videos.
    :param path_subvideos: a dict with paths as key and a list of lists of videos and subtitles
    :param callback: Instance of ProgressCallback
    :return: tuple with List of videos and list of subtitles
    """
    log.debug('merge_path_subvideo(path_subvideos=<#paths={nb_paths}>)'.format(nb_paths=len(path_subvideos)))
    # FIXME: add logging
    nb_videos = sum([len(subvids[1]) for subvids in path_subvideos.values()])

    all_videos = []
    all_subtitles = []

    callback.set_range(0, nb_videos)

    vid_i = 0
    callback.update(vid_i)
    for path, subvideos in path_subvideos.items():
        [subs_str, vids_str] = subvideos
        subtitles = [LocalSubtitleFile(filepath=os.path.join(path, sub_str)) for sub_str in subs_str]
        all_subtitles.extend(subtitles)
        for vid_str in vids_str:
            try:
                video = VideoFile(os.path.join(path, vid_str))
            except NotAVideoException:
                continue
            all_videos.append(video)

            for subtitle in subtitles:
                if subtitle.matches_videofile_filename(video):
                    video.add_subtitle(subtitle)

            vid_i += 1
            callback.update(vid_i)
    callback.finish(True)
    return all_videos, all_subtitles


def filter_files_extensions(files, extension_lists):
    """
    Put the files in buckets according to extension_lists
    files=[movie.avi, movie.srt], extension_lists=[[avi],[srt]] ==> [[movie.avi],[movie.srt]]
    :param files: A list of files
    :param extension_lists: A list of list of extensions
    :return: The files filtered and sorted according to extension_lists
    """
    log.debug('filter_files_extensions: files="{}"'.format(files))
    result = [[] for _ in extension_lists]
    for file in files:
        root, ext = os.path.splitext(file)
        ext = ext[1:].lower()
        for ext_i, ext_list in enumerate(extension_lists):
            if ext in ext_list:
                result[ext_i].append(file)
    log.debug('filter_files_extensions result:{}'.format(result))
    return result
