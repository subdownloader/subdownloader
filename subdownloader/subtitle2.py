# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import hashlib
import os
import logging
import re

from subdownloader.languages.language import Language, NotALanguageException, UnknownLanguage

log = logging.getLogger('subdownloader.subtitle2')

"""
List of known subtitle extensions.
"""
SUBTITLES_EXT = ['srt', 'sub', 'txt', 'ssa', 'smi', 'ass', 'mpl']


class SubtitleFile(object):
    def __init__(self, parent):
        self._parent = parent

    def get_parent(self):
        return self._parent

    def get_language(self):  # FIXME: abstractmethod
        raise NotImplementedError()

    def get_file_size(self):  # FIXME: abstractmethod
        raise NotImplementedError()

    def get_md5_hash(self):  # FIXME: abstractmethod
        raise NotImplementedError()

    def matches_videofile_filename(self, videofile):
        """
        Detect whether the filename of videofile matches with this SubtitleFile.
        :param videofile: VideoFile instance
        :return: True if match
        """

        vid_fn = videofile.get_filename()
        vid_base, _ = os.path.splitext(vid_fn)
        vid_base = vid_base.lower()

        sub_fn = self.get_filename()
        sub_base, _ = os.path.splitext(sub_fn)
        sub_base = sub_base.lower()

        log.debug('matches_filename(subtitle="{sub_filename}", video="{vid_filename}") ...'.format(
            sub_filename=sub_fn, vid_filename=vid_fn))

        matches = sub_base == vid_base

        lang = None
        if not matches:
            if sub_base.startswith(vid_base):
                sub_rest = sub_base[len(vid_base):]
                while len(sub_rest) > 0:
                    if sub_rest[0].isalnum():
                        break
                    sub_rest = sub_rest[1:]
                try:
                    lang = Language.from_unknown(sub_rest, locale=False, name=False)
                    matches = True
                except NotALanguageException:
                    matches = False

        if matches:
            log.debug('... matches (language={language})'.format(language=lang))
        else:
            log.debug('... does not match')
        return matches

    DETECT_LANGUAGE_REGEX = re.compile('.*(?:[^a-zA-Z])([a-zA-Z]+)$')

    @classmethod
    def detect_language_filename(cls, filename):
        """
        Detect the language of a subtitle filename
        :param filename: filename of a subtitle
        :return: Language object, None if language could not be detected.
        """
        log.debug('detect_language(filename="{}") ...'.format(filename))
        base, _ = os.path.splitext(filename)
        fn_lang = cls.DETECT_LANGUAGE_REGEX.findall(base)
        if fn_lang:
            language_part = fn_lang[0]
            try:
                lang = Language.from_unknown(language_part, locale=False, name=False)
                log.debug('... SUCCESS: detected from filename: {lang}'.format(lang=lang))
                return lang
            except NotALanguageException:
                pass
        else:
            log.debug('... FAIL: could not detect from filename')
        return UnknownLanguage.create_generic()

    def equals_SubtitleFile(self, other):
        return self.get_md5_hash() == other.get_md5_hash() and self.get_file_size() == other.get_file_size()


class SubtitleFileNetwork(SubtitleFile):
    def __init__(self, parent, subtitle_file):
        SubtitleFile.__init__(self, parent)
        self._subtitles = []
        self.add_subtitle(subtitle_file)

    def get_subtitles(self):
        return self._subtitles

    def add_subtitle(self, subtitle_file):
        subtitle_file.set_parent(self)
        self._subtitles.append(subtitle_file)

    def get_language(self):
        result_lang = UnknownLanguage.create_generic()
        for subtitle in self._subtitles:
            lang = subtitle.get_language()
            if isinstance(result_lang, UnknownLanguage):
                result_lang = lang
            elif isinstance(lang, UnknownLanguage):
                pass
            if result_lang != lang:
                return UnknownLanguage.create_generic()
        return result_lang

    def get_file_size(self):
        return self._subtitles[0].get_file_size()

    def get_md5_hash(self):
        return self._subtitles[0].get_md5_hash()

    def nb_providers(self):
        providers = {subtitle.get_provider() for subtitle in self._subtitles if isinstance(subtitle, RemoteSubtitleFile)}
        return len(providers)

    def equals_SubtitleFile(self, other):
        for subtitle in self._subtitles:
            if subtitle.equals_SubtitleFile(other):
                return True
        return False


class SubtitleFile_Storage(SubtitleFile):

    def __init__(self, parent, language, file_size, md5_hash):
        SubtitleFile.__init__(self, parent=parent)
        # Details of general Subtitle
        self._language = language
        self._file_size = file_size
        self._md5_hash = md5_hash

    def set_parent(self, parent):
        self._parent = parent

    def get_filename(self):  # FIXME: abstractmethod
        raise NotImplementedError()

    def get_language(self):
        return self._language

    def get_file_size(self):
        return self._file_size

    def get_md5_hash(self):
        return self._md5_hash


class LocalSubtitleFile(SubtitleFile_Storage):
    def __init__(self, filepath):
        filename = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)
        language = self.detect_language_filename(filename)
        md5_hash = hashlib.md5(open(filepath, mode='rb').read()).hexdigest()
        SubtitleFile_Storage.__init__(self, parent=None, file_size=file_size, language=language, md5_hash=md5_hash)
        self._filepath = filepath

    def get_filename(self):
        return os.path.basename(self._filepath)

    def get_filepath(self):
        return self._filepath


class RemoteSubtitleFile(SubtitleFile_Storage):
    def __init__(self, filename, language, file_size, md5_hash):
        SubtitleFile_Storage.__init__(self, parent=None, language=language, file_size=file_size, md5_hash=md5_hash)
        self._filename = filename

    def get_filename(self):
        return self._filename;

    def matches_videofile(self, videofile):
        raise NotImplementedError()

    def get_uploader(self):  # FIXME: abstractmethod
        raise NotImplementedError

    def get_rating(self):  # FIXME: abstractmethod
        raise NotImplementedError()

    def get_link(self):  # FIXME: abstractmethod
        raise NotImplementedError()

    def get_provider(self):  # FIXME: abstractmethod
        raise NotImplementedError

    def download(self, provider_instance, callback):  # FIXME: abstractmethod
        raise NotImplementedError()


class SubtitleFileCollection(object):
    def __init__(self, parent):
        self._parent = parent
        self._networks = []

    def get_parent(self):
        return self._parent

    def get_subtitle_networks(self):
        return self._networks

    def add_subtitle(self, subtitle):
        for network in self._networks:
            if network.equals_SubtitleFile(subtitle):
                network.add_subtitle(subtitle)
                return
        network = SubtitleFileNetwork(parent=self, subtitle_file=subtitle)
        self._networks.append(network)
