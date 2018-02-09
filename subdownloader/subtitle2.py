# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

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

    def get_super_parent(self):
        parents = set()
        obj = self
        while True:
            parent = obj.get_parent()
            if parent is None:
                return None
            if not isinstance(parent, SubtitleFile):
                return parent
            if parent in parents:
                log.warning('Loop detected in parents of "{self}": parent {parent} already in {parents}'.format(
                    self=self, parent=parent, parents = parents))
                return None
            parents.add(parent)
            obj = parent

    def get_filename(self):  # FIXME: abstractmethod
        raise NotImplementedError()

    def get_language(self):  # FIXME: abstractmethod
        raise NotImplementedError()

    def get_file_size(self):  # FIXME: abstractmethod
        raise NotImplementedError()

    def get_md5_hash(self):  # FIXME: abstractmethod
        raise NotImplementedError()

    DETECT_LANGUAGE_REGEX = re.compile('.*(?:[^a-zA-Z])([a-zA-Z]+)$')

    @classmethod
    def detect_language_filename(cls, filename):
        """
        Detect the language of a subtitle filename
        :param filename: filename of a subtitle
        :return: Language object, None if language could not be detected.
        """
        log.debug('detect_language(filename="{}") ...'.format(filename))
        root, _ = os.path.splitext(filename)
        fn_lang = cls.DETECT_LANGUAGE_REGEX.findall(root)
        if fn_lang:
            language_part = fn_lang[0]
            try:
                lang = Language.from_unknown(language_part, xx=True, xxx=True)
                log.debug('... SUCCESS: detected from filename: {lang}'.format(lang=lang))
                return lang
            except NotALanguageException:
                pass
        else:
            log.debug('... FAIL: could not detect from filename')
        return UnknownLanguage.create_generic()

    def equals_subtitle_file(self, other):
        return self.get_md5_hash() == other.get_md5_hash() and self.get_file_size() == other.get_file_size()


class SubtitleFileNetwork(SubtitleFile):
    def __init__(self, parent, subtitle_file, reparent=True):
        SubtitleFile.__init__(self, parent)
        self._subtitles = []
        self.add_subtitle(subtitle_file, reparent=reparent)

    def get_subtitles(self):
        return self._subtitles

    def get_filename(self):
        return self._subtitles[0].get_filename()

    def add_subtitle(self, subtitle_file, reparent=True):
        if reparent:
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
        providers = {subtitle.get_provider() for subtitle in self._subtitles
                     if isinstance(subtitle, RemoteSubtitleFile)}
        return len(providers)

    def equals_subtitle_file(self, other):
        for subtitle in self._subtitles:
            if subtitle.equals_subtitle_file(other):
                return True
        return False

    def iter_local_subtitles(self):
        for subtitle in self._subtitles:
            if isinstance(subtitle, LocalSubtitleFile):
                yield subtitle

    def iter_remote_subtitles(self):
        for subtitle in self._subtitles:
            if isinstance(subtitle, RemoteSubtitleFile):
                yield subtitle

    def __len__(self):
        return len(self._subtitles)

    def __getitem__(self, item):
        return self._subtitles[item]


class SubtitleFileStorage(SubtitleFile):
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

    def matches_video_filename(self, video):
        """
        Detect whether the filename of videofile matches with this SubtitleFile.
        :param video: VideoFile instance
        :return: True if match
        """

        vid_fn = video.get_filename()
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
                    lang = Language.from_unknown(sub_rest, xx=True, xxx=True)
                    matches = True
                except NotALanguageException:
                    matches = False

        if matches:
            log.debug('... matches (language={language})'.format(language=lang))
        else:
            log.debug('... does not match')
        return matches

    def get_language(self):
        return self._language

    def get_file_size(self):
        return self._file_size

    def get_md5_hash(self):
        return self._md5_hash

    def is_remote(self):
        raise NotImplementedError()

    def is_local(self):
        raise NotImplementedError()


class LocalSubtitleFile(SubtitleFileStorage):
    def __init__(self, filepath, parent=None):
        filename = filepath.name
        file_size = filepath.stat().st_size
        language = self.detect_language_filename(filename)
        md5_hash = hashlib.md5(filepath.open(mode='rb').read()).hexdigest()
        SubtitleFileStorage.__init__(self, parent=None, file_size=file_size, language=language, md5_hash=md5_hash)
        self._filepath = filepath

    def get_filename(self):
        return self._filepath.name

    def get_filepath(self):
        return self._filepath

    def set_language(self, language):
        self._language = language

    def __repr__(self):
        return '<LocalSubtitleFile:filepath="{filepath}",size={size},language={language}>'.format(
            filepath=self.get_filepath(), size=self.get_file_size(), language=self.get_language()
        )

    def is_remote(self):
        return False

    def is_local(self):
        return True


class RemoteSubtitleFile(SubtitleFileStorage):
    def __init__(self, filename, language, file_size, md5_hash):
        SubtitleFileStorage.__init__(self, parent=None, language=language, file_size=file_size, md5_hash=md5_hash)
        self._filename = filename

    def get_filename(self):
        return self._filename

    def get_uploader(self):  # FIXME: abstractmethod
        raise NotImplementedError

    def get_rating(self):  # FIXME: abstractmethod
        raise NotImplementedError()

    def get_link(self):  # FIXME: abstractmethod
        raise NotImplementedError()

    def get_provider(self):  # FIXME: abstractmethod
        raise NotImplementedError

    def download(self, target_path, provider_instance, callback):  # FIXME: abstractmethod
        raise NotImplementedError()

    def is_remote(self):
        return True

    def is_local(self):
        return False


class SubtitleFileCollection(object):
    def __init__(self, parent):
        self._parent = parent
        self._networks = []
        self._candidates = []

    def get_parent(self):
        return self._parent

    def get_subtitle_networks(self):
        return self._networks

    def add_subtitle(self, subtitle):
        for network in self._networks:
            if network.equals_subtitle_file(subtitle):
                network.add_subtitle(subtitle)
                return
        for candidate in self._candidates:
            if candidate.equals_subtitle_file(subtitle):
                network = SubtitleFileNetwork(parent=self, subtitle_file=subtitle)
                network.add_subtitle(candidate.get_subtitles()[0])
                self._networks.append(network)
                self._candidates.remove(candidate)
                return
        network = SubtitleFileNetwork(parent=self, subtitle_file=subtitle)
        self._networks.append(network)

    def add_candidates(self, subtitles):
        for subtitle in subtitles:
            for candidate in self._candidates:
                if candidate.equals_subtitle_file(subtitle):
                    candidate.add_subtitle(subtitle, reparent=False)
                    break
            new_candidate = SubtitleFileNetwork(parent=self, subtitle_file=subtitle, reparent=False)
            self._candidates.append(new_candidate)

    def iter_local_subtitles(self):
        for network in self._networks:
            for subtitle in network.iter_local_subtitles():
                yield subtitle

    def get_nb_subtitles(self):
        return sum(len(network) for network in self._networks)

    def __len__(self):
        return len(self._networks)

    def __getitem__(self, item):
        return self._networks[item]
