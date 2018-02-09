# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from enum import Enum
import logging
import os
import re

log = logging.getLogger('subdownloader.identification')


class MovieMatch(Enum):
    Equal = True
    NonEqual = False
    Unknown = None

    def __and__(self, other):
        if type(self) != type(other):
            return MovieMatch.Unknown

        sv = self.value
        ov = other.value

        if sv == MovieMatch.NonEqual or ov == MovieMatch.NonEqual:
            return MovieMatch.NonEqual

        if sv == MovieMatch.Equal or ov == MovieMatch.Equal:
            return MovieMatch.Equal

        return MovieMatch.Unknown


class VideoIdentity(object):
    def __init__(self, name, year):
        self._name = name
        self._year = year

    def get_name(self):
        return self._name

    def get_year(self):
        return self._year

    def merge(self, video_identity):
        name = video_identity.get_name()
        if self.get_name() is None:
            self._name = name

        year = video_identity.get_year()
        if self.get_year() is None:
            self._year = year

    def matches_identity(self, other):
        if type(self) != type(other):
            return MovieMatch.Unknown

        if self.get_name() is None or other.get_name() is None:
            return MovieMatch.Unknown
        if self.get_name().lower() == other.get_name().lower():
            return MovieMatch.Equal

        return MovieMatch.Unknown


class ImdbIdentity(object):
    def __init__(self, imdb_id, imdb_rating):
        self._imdb_id = imdb_id
        self._imdb_rating = imdb_rating

    def get_imdb_id(self):
        return self._imdb_id

    def get_imdb_rating(self):
        return self._imdb_rating

    def get_imdb_url(self):
        try:
            imdb_id = '{:07d}'.format(int(self.get_imdb_id()))
        except ValueError:
            imdb_id = self.get_imdb_id()
        return 'http://www.imdb.com/title/tt{imdb_id}/'.format(imdb_id=imdb_id)

    def merge(self, imdb_identity):
        imdb_id = imdb_identity.get_imdb_id()
        if imdb_id is not None:
            self._imdb_id = imdb_id

        imdb_rating = imdb_identity.get_imdb_rating()
        if imdb_rating is not None:
            self._imdb_rating = imdb_rating

    def matches_identity(self, other):
        if type(self) != type(other):
            return MovieMatch.Unknown

        if self.get_imdb_id() is None or other.get_imdb_id() is None:
            return MovieMatch.Unknown
        if self.get_imdb_id() == other.get_imdb_id():
            return MovieMatch.Equal

        return MovieMatch.NonEqual


class EpisodeIdentity(object):
    def __init__(self, season, episode):
        self._season = season
        self._episode = episode

    def get_season(self):
        return self._season

    def get_episode(self):
        return self._episode

    def merge(self, episode_identity):
        season = episode_identity.get_season()
        if season is not None:
            self._season = season

        episode = episode_identity.get_episode()
        if episode is not None:
            self._episode = episode

    def matches_identity(self, other):
        if type(self) != type(other):
            return MovieMatch.Unknown

        if self.get_season() is None or other.get_season is None:
            return MovieMatch.Unknown
        if self.get_season() != other.get_season():
            return MovieMatch.NonEqual

        if self.get_episode() is None or other.get_episode is None:
            return MovieMatch.Unknown
        if self.get_episode() != other.get_episode:
            return MovieMatch.NonEqual

        return MovieMatch.Equal


class Identities(object):
    def __init__(self, video_identity=None, episode_identity=None, imdb_identity=None):
        self._video_identity = video_identity
        self._episode_identity = episode_identity
        self._imdb_identity = imdb_identity

    @property
    def video_identity(self):
        return self._video_identity

    @property
    def episode_identity(self):
        return self._episode_identity

    @property
    def imdb_identity(self):
        return self._imdb_identity

    def merge(self, identities):
        if self.video_identity is not None:
            self.video_identity.merge(identities.video_identity)
        else:
            self._video_identity = identities.video_identity

        if self.episode_identity is not None:
            self.episode_identity.merge(identities.episode_identity)
        else:
            self._episode_identity = identities.episode_identity

        if self.imdb_identity is not None:
            self.imdb_identity.merge(identities.imdb_identity)
        else:
            self._imdb_identity = identities.imdb_identity

    def matches_identity(self, other):
        imdb_match = self.imdb_identity.matches_identity(other.imdb_identity)
        if imdb_match in (MovieMatch.Equal, MovieMatch.NonEqual):
            return imdb_match

        video_match = self.video_identity.matches_identity(other.video_identity)
        if video_match in (MovieMatch.Equal, MovieMatch.NonEqual):
            return video_match

        return MovieMatch.Unknown


class ProviderIdentities(Identities):
    def __init__(self, provider, video_identity=None, episode_identity=None, imdb_identity=None):
        Identities.__init__(self, video_identity=video_identity, episode_identity=episode_identity,
                            imdb_identity=imdb_identity)
        self._provider = provider

    @property
    def provider(self):
        return self._provider


class IdentityCollection(object):
    def __init__(self):
        self._data = {}

    def add_identity(self, identity):
        provider = identity.provider
        try:
            identities = self._data[provider]
            identities.merge(identity)
        except KeyError:
            self._data[provider] = identity

    def __iter__(self):
        return iter(self._data.values())

    def __len__(self):
        return len(self._data)

    def __contains__(self, provider):
        return provider in self._data

    def iter_video_identity(self):
        for provider_identity in self:
            video_identity = provider_identity.video_identity
            if video_identity is not None:
                yield video_identity

    def iter_imdb_identity(self):
        for provider_identity in self:
            imdb_identity = provider_identity.imdb_identity
            if imdb_identity is not None:
                yield imdb_identity

    def get_merged_video_identity(self):
        res_video_identity = VideoIdentity(name=None, year=None)
        for video_identity in self.iter_video_identity():
            res_video_identity.merge(video_identity)
        return res_video_identity

    def get_merged_imdb_identity(self):
        res_imdb_identity = ImdbIdentity(imdb_id=None, imdb_rating=None)
        for imdb_identity in self.iter_imdb_identity():
            res_imdb_identity.merge(imdb_identity)
        return res_imdb_identity


class NFOIdentificator(object):
    def __init__(self):
        pass

    def identify_videos(self, videos):
        log.debug('NFOIdentificator.identify_videos(videos={videos})'.format(videos=videos))
        directory_identification = {}
        for video in videos:
            if video is None:
                continue
            directory = video.get_filepath().parent
            if directory in directory_identification:
                identity = directory_identification[directory]
                if identity:
                    video.add_identity(identity=identity)
                continue
            identity = None
            for directory_file in directory.iterdir():
                if directory_file.suffix != '.nfo':
                    continue
                try:
                    nfo_content = directory_file.open().read().lower()
                except IOError:
                    continue
                result = re.search('imdb\.\w+/title/tt(\d+)', nfo_content)
                if result:
                    imdb_id = result.group(1)
                    imdb_identity = ImdbIdentity(imdb_id=imdb_id, imdb_rating=None)
                    identity = ProviderIdentities(imdb_identity=imdb_identity, provider=self)

                    break
            if identity is None:
                identity = ProviderIdentities(provider=self)
            directory_identification[directory] = identity
            video.add_identity(identity=identity)


# class Identification(object):
#     def __init__(self):
#         self._videos = []
#
#     def set_videos(self, videos):
#         self._videos = [v for v in videos]
#
#     def detect_lang(self):
#         log.debug('Identification.detect_lang(videos={videos})'.format(videos=self._videos))
#         languages = {}
#         for v in self._videos:
#             if not v:
#                 continue
#             try:
#                 subtitle = next(v.get_subtitles().iter_local_subtitles())
#             except StopIteration:
#                 continue
#             language = subtitle.get_language()
#             if not language.is_generic():
#                 dict_increment_key(languages, language)
#                 continue
#
#             language = Language.from_file(subtitle.get_filepath())
#             if not language.is_generic():
#                 dict_increment_key(languages, language)
#
#             dict_increment_key(languages, UnknownLanguage.create_generic())
#
#         log.debug('Detected these languages: {languages}'.format(languages=languages))
#         return languages


_IDENTIFICATORS = set()


def identificators_get():
    return iter(_IDENTIFICATORS)


def identificator_add(identificator):
    _IDENTIFICATORS.add(identificator)


def identificator_remove(identificator):
    try:
        _IDENTIFICATORS.remove(identificator)
    except KeyError:
        pass

identificator_add(NFOIdentificator())
