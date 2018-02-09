# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import base64
import logging
import os.path
import zlib

import subdownloader.languages.language as language
from subdownloader.FileManagement import FileScan, Subtitle
from subdownloader.callback import ProgressCallback
from subdownloader.provider import SDService
from subdownloader.client.cli.callback import DEFAULT_WIDGETS, ProgressBarCallback
from subdownloader.client.cli.filter import Filter

try:
    input = raw_input
except NameError:
    pass

log = logging.getLogger("subdownloader.client.cli.main")


class Main(object):

    def __init__(self, cli_options):
        self.options = cli_options

    def start_session(self):
        if not self.minimum_parameters():
            return

        check_result = self.check_directory()
        continue_ = 'y'
        if check_result == 2 and self.options.operation == "download" and self.options.interactive:
            continue_ = input(
                "Do you still want to search for missing subtitles? [Y/n] ").lower() or 'y'
            if continue_ != 'y':
                return
        if check_result == -1:
            return
        if continue_ == 'y' or not self.options.interactive:
            log.info("Starting subtitle search, please wait...")
            self.do_matching(self.videos, self.subs)
            result = "\n"
            for video in self.videos:
                video_name = video.get_filepath()
                if video.hasSubtitles():
                    if video.getTotalLocalSubtitles() == 1:
                        sub_name = video.getSubtitles()[0].get_filepath()
                    elif video.getTotalLocalSubtitles() > 1:
                        sub_name = ""
                        for sub in video.getSubtitles():
                            sub_name += "%s, " % sub.get_filepath()
                else:
                    sub_name = "NO MATCH"
                result += "%s -> %s\n" % (video_name, sub_name)
            log.debug(result)

        log.debug("Starting XMLRPC session...")
        self.provider = SDService.SDService(proxy=self.options.proxy)
        try:
            self.provider.connect()
            self.provider.login(self.options.username, self.options.password)
        except:
            log.exception('exception in start_session()')
            return

        if self.provider.connected():
            # set language
            if len(self.options.language) == 2:
                lang_id = self.provider.GetSubLanguages(self.options.language)
            elif len(self.options.language) == 3:
                lang_id = self.options.language
            else:
                lang_id = 'all'
                log.debug(
                    "Wrong language code was set, using default: %r" % lang_id)
            # check if we will overwrite local subtitles
            if self.options.overwrite_local:
                log.debug(
                    "Overwriting local subtitles is set. Searching for victims...")
                for video in self.videos:
                    if video.hasSubtitles():
                        check_result = self.provider.CheckSubHash(video)
                        for hash in check_result:
                            if check_result[hash] == '0':
                                # we found a subtitle that's not on server
                                # (nos)
                                nos_sub = video.getSubtitle(hash)
                                log.debug(
                                    "Not on server - %s - jailing..." % nos_sub.get_filepath())
                                video.setNOSSubtitle(nos_sub)

            videoSearchResults = self.provider.SearchSubtitles(
                language=lang_id, videos=self.videos)
            if self.options.test:
                for (i, video) in enumerate(self.videos):
                    #details = check_result['data'][0]
                    if video.get_hash():
                        cd = 'cd%i' % (i + 1)
                        curr_video = video
                        curr_sub = curr_video.getSubtitles()[0]
                        user_choices = {'moviereleasename': 'NA',
                                        'movieaka': 'NA',
                                        'moviefilename': curr_video.get_filepath(),
                                        'subfilename': curr_sub.get_filepath(),
                                        'sublanguageid': curr_sub.getLanguage().xxx(),
                                        }
                        # interactive mode
                        if self.options.mode == 'cli' and self.options.interactive:
                            log.info("Upload the following information:")
                            for (i, choice) in enumerate(user_choices):
                                log.info(
                                    "[%i] %s: %s" % (i, choice, user_choices[choice]))
                            change = input(
                                "Change any of the details? [y/N] ").lower() or 'n'
                            while change == 'y':
                                change_what = int(input("What detail? "))
                                if change_what in range(len(user_choices.keys())):
                                    choice = user_choices.keys()[change_what]
                                    new_value = input(
                                        "%s: [%s] " % (choice, user_choices[choice])) or user_choices[choice]
                                    user_choices[choice] = new_value
                                change = input(
                                    "Change any more details? [y/N] ").lower() or 'n'

            else:
                self.handle_operation(self.options.operation)

            self.provider.logout()

    def minimum_parameters(self):
        """Check for minimum parameters integrity"""
        # check if user set a video file name
        log.debug("Checking video file parameter...")
        # in GUI this value needs to empty, but for CLI we replace by
        # currentDir
        if not self.options.videofile:
            self.options.videofile = os.path.abspath(os.path.curdir)

        if self.options.videofile == os.path.abspath(os.path.curdir) and self.options.interactive:
            # confirm with user if he wants to use default directory
            self.options.videofile = input(
                "Enter your video(s) directory [%s]: " % self.options.videofile) or self.options.videofile
        if os.path.exists(self.options.videofile):
            log.debug("...passed")
        elif self.options.interactive:
            choice = input("Enter your video(s) directory: ") or ""
            self.options.videofile = choice
            if os.path.exists(self.options.videofile):
                log.debug("...passed")
            else:
                log.debug("...failed")
                log.info("--video parameter looks bad")
                return False
        else:
            log.debug("...failed")
            log.info("--video parameter must be set")
            return False

        # check if user set language to use on subtitles
        log.debug("Checking language parameter...")
        if self.options.languages:
            log.debug("...passed")
        else:
            log.debug("...failed")
            log.info("--lang parameter must be set")
            return False
        # everything is good
        return True

    def handle_operation(self, operation):
        if operation == "download":
            _filter = Filter(
                self.videos, interactive=self.options.interactive, rename_subs=self.options.renaming)
            self.provider.DownloadSubtitles(_filter.subtitles_to_download())

        elif operation == "upload":
            self.do_upload(self.videos)

        elif operation == "list":
            _filter = Filter(
                self.videos, interactive=self.options.interactive)
#            print _filter.subtitles_to_download()
            for video in self.videos:
                log.info("-" * 30)
                log.info("- %s (%s)" %
                              (video.get_filepath(), video.get_hash()))
                for sub in video.getSubtitles():
                    log.info("  [%s] - %s" %
                                  (sub.getLanguage().xxx(), sub.get_filepath()))

    def check_directory(self):
        """ search for videos and subtitles in the given path """
        log.info("Scanning %s ..." % self.options.videofile)
        callback = self._get_callback()
        (self.videos, self.subs) = FileScan.scan_folder(self.options.videofile, callback=callback) #report_progress=report_progress, progress_end=progress_end)
        log.info("Videos found: %i Subtitles found: %i" %
                      (len(self.videos), len(self.subs)))
        if len(self.videos):
            if len(self.videos) == len(self.subs):
                log.info(
                    "Number of videos and subtitles are the same. I could guess you already have all subtitles.")
                return 2
            else:
                log.info(
                    "Looks like some of your videos might need subtitles :)")
                return 1
        elif len(self.subs):
            log.debug("No videos were found")
            log.info(
                "Although some subtitles exist, no videos were found. No subtitles would be needed for this case :(")
            return -1
        else:
            log.info("Nothing to do here")
            return -1

    def do_matching(self, videos, subtitles):
        callback = self._get_callback()
        callback.set_range(0, len(videos))

        for i, video in enumerate(videos):
            callback.update(i + 1)
            log.debug("Processing %s..." % video.get_filepath())

            possible_subtitle = Subtitle.AutoDetectSubtitle(
                video.get_filepath())
            #log.debug("possible subtitle is: %s"% possible_subtitle)
            sub_match = None
            for subtitle in subtitles:
                sub_match = None
                if possible_subtitle == subtitle.get_filepath():
                    sub_match = subtitle
                    log.debug("Match found: %s" % sub_match.get_filepath())
                    break
            if sub_match:
                sub_lang = Subtitle.AutoDetectLang(sub_match.getFilePath())
                sub_match.setLanguage(language.name2xxx(sub_lang))
                video.addSubtitle(sub_match)
        callback.finish()

    def do_upload(self, videos):
        log.debug("----------------")
        log.debug("UploadSubtitles RPC method starting...")
        check_result = self.provider.TryUploadSubtitles(videos)
        if isinstance(check_result, bool) and not check_result:
            log.info(
                "One or more videos don't have subtitles associated. Stopping upload.")
            return False
        elif check_result['alreadyindb']:
            log.info(
                "Subtitle already exists in server database. Stopping upload.")
            return False
        elif check_result['data']:
            # TODO: make this to work with non-hashed subtitles (no 'data' to handle)
            # quick check to see if all video/subtitles are from same movie
            for movie_sub in check_result['data']:
                if 'IDMovie' not in locals():
                    IDMovie = {}
                if 'IDMovie' in IDMovie:
                    IDMovie[movie_sub['IDMovie']] += 1
                else:
                    IDMovie[movie_sub['IDMovie']] = 1
#                    if IDMovie != movie_sub['IDMovie']:
#                        log.error("All videos must have same ID. Stopping upload.")
#                        return False
#                else:
#                    IDMovie = movie_sub['IDMovie']
            #
            movie_info = {}
            for (i, video) in enumerate(videos):
                # for details in check_result['data']:
                details = check_result['data'][0]
                if video.get_hash() == details['MovieHash']:
                    cd = 'cd%i' % (i + 1)
                    curr_video = video
                    curr_sub = curr_video.getSubtitles()[0]
                    user_choices = {'moviereleasename': details['MovieName'],
                                    'movieaka': details['MovieNameEng'],
                                    'moviefilename': curr_video.get_filepath(),
                                    'subfilename': curr_sub.get_filepath(),
                                    'sublanguageid': curr_sub.getLanguage().xxx(),
                                    }
                    # interactive mode
                    if self.options.mode == 'cli' and self.interactive:
                        log.info("Upload the following information:")
                        for (i, choice) in enumerate(user_choices):
                            log.info("[%i] %s: %s" %
                                          (i, choice, user_choices[choice]))
                        change = input(
                            "Change any of the details? [y/N] ").lower() or 'n'
                        while change == 'y':
                            change_what = int(input("What detail? "))
                            if change_what in range(len(user_choices.keys())):
                                choice = user_choices.keys()[change_what]
                                new_value = input(
                                    "%s: [%s] " % (choice, user_choices[choice])) or user_choices[choice]
                                user_choices[choice] = new_value
                            change = input(
                                "Change any more details? [y/N] ").lower() or 'n'

                    # cook subtitle content
                    log.debug("Compressing subtitle...")
                    buf = open(curr_sub.get_filepath(), mode='rb').read()
                    curr_sub_content = base64.encodestring(zlib.compress(buf))

                    # transfer info
                    movie_info[cd] = {'subhash': curr_sub.get_hash(), 'subfilename': user_choices['subfilename'], 'moviehash': details['MovieHash'], 'moviebytesize': details[
                        'MovieByteSize'], 'movietimems': details['MovieTimeMS'], 'moviefps': curr_video.get_fps(), 'moviefilename': user_choices['moviefilename'], 'subcontent': curr_sub_content}
                    break

            movie_info['baseinfo'] = {'idmovieimdb': details['IDMovieImdb'], 'moviereleasename': user_choices['moviereleasename'], 'movieaka': user_choices[
                'movieaka'], 'sublanguageid': user_choices['sublanguageid'], 'subauthorcomment': "Upload by SubDownloader2.0 - www.subdownloader.net"}  # details['SubAuthorComment']}

            return self.provider.UploadSubtitles(movie_info)

    def _get_callback(self):
        if self.options.loglevel > logging.DEBUG:
            callback = ProgressBarCallback(DEFAULT_WIDGETS)
        else:
            callback = ProgressCallback()
        return callback
