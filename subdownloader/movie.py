# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from subdownloader.identification import MovieMatch
from subdownloader.languages.language import UnknownLanguage
from subdownloader.subtitle2 import SubtitleFileCollection


class VideoSubtitle(object):
    def __init__(self, video=None, subtitle=None):
        self.video = video
        self.subtitle = subtitle

    def check(self):
        if not self.video or not self.video.exists():
            return False
        if not self.subtitle or not self.subtitle.exists():
            return False
        return True


class LocalMovie(object):
    def __init__(self):
        self._movie_name = None
        self._imdb_id = None
        self._language = UnknownLanguage.create_generic()
        self._release_name = None
        self._comments = None
        self._author = None

        self._hearing_impaired = None
        self._high_definition = None
        self._foreign_only = None
        self._automatic_translation = None

        self._data = []

    def add_video_subtitle(self, video, subtitle):
        self._data.append(VideoSubtitle(video, subtitle))

    def check(self):
        video_paths = set()
        subtitle_paths = set()
        for data in self._data:
            if not data.check():
                return False
            vfp = str(data.video.get_filepath().resolve())
            if vfp in video_paths:
                return False
            video_paths.add(vfp)

            sfp = str(data.subtitle.get_filepath().resolve())
            if sfp in subtitle_paths:
                return False
        if self._language.is_generic():
            return False
        return True

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def iter_video_subtitles(self):
        for d in self._data:
            yield d.video, d.subtitle

    def set_movie_name(self, movie_name):
        self._movie_name = movie_name

    def get_movie_name(self):
        return self._movie_name

    def set_imdb_id(self, imdb_id):
        self._imdb_id = imdb_id

    def get_imdb_id(self):
        return self._imdb_id

    def set_language(self, language):
        self._language = language

    def get_language(self):
        return self._language

    def set_release_name(self, release_name):
        self._release_name = release_name

    def get_release_name(self):
        return self._release_name

    def set_comments(self, comments):
        self._comments = comments

    def get_comments(self):
        return self._comments

    def set_author(self, author):
        self._author = author

    def get_author(self):
        return self._author

    def set_hearing_impaired(self, hearing_impaired):
        self._hearing_impaired = hearing_impaired

    def is_hearing_impaired(self):
        return self._hearing_impaired

    def set_high_definition(self, high_definition):
        self._high_definition = high_definition

    def is_high_definition(self):
        return self._high_definition

    def set_foreign_only(self, foreign_only):
        self._foreign_only = foreign_only

    def is_foreign_only(self):
        return self._foreign_only

    def set_automatic_translation(self, automatic_translation):
        self._automatic_translation = automatic_translation

    def is_automatic_translation(self):
        return self._automatic_translation


class RemoteMovie(object):
    def __init__(self, provider_id, provider_link, subtitles_nb_total, identities):
        self._provider_id = provider_id
        self._provider_link = provider_link

        self._subtitles_local = []
        self._subtitles_nb_total = subtitles_nb_total

        self._identities = identities

    def get_nb_subs_total(self):
        return self._subtitles_nb_total

    def get_nb_subs_available(self):
        return len(self._subtitles_local)

    def more_subtitles_available(self):
        return self.get_nb_subs_available() < self.get_nb_subs_total()

    def get_provider_id(self):
        return self._provider_id

    def get_provider_link(self):
        return self._provider_link

    def add_subtitles(self, subtitles):
        self._subtitles_local.extend(subtitles)

    def get_subtitles(self):
        return self._subtitles_local

    def get_identities(self):
        return self._identities

    def __repr__(self):
        return '<{clsname} identification: {identification}, ' \
               'nb_subs_total={nb_subs_total}, nb_subs_available={nb_subs_available}, ' \
               'provider_link: {provider_link}, provider_id: {provider_id}>'.format(
                    clsname=type(self).__name__, identification=self._identities,
                    nb_subs_total=self.get_nb_subs_total(), nb_subs_available=self.get_nb_subs_available(),
                    provider_link=self._provider_link, provider_id=self._provider_id)


class RemoteMovieNetwork(object):
    def __init__(self, movie, query):
        self._movies = []
        self._queries = []

        self._subtitles = SubtitleFileCollection(parent=self)

        self.add_movie(movie, query)

    def add_movie(self, movie, query):
        self._movies.append(movie)
        self._queries.append(query)

    def more_subtitles_available(self):
        return any(m.more_subtitles_available() for m in self._movies)

    def get_nb_subs_total(self):
        return sum(m.get_nb_subs_total() for m in self.movies())

    def get_nb_subs_available(self):
        return sum(m.get_nb_subs_available() for m in self.movies())

    def get_identities(self):
        from subdownloader.identification import Identities
        identity = Identities()
        for movie in self.movies():
            identity.merge(movie.get_identities())
        return identity

    def movies(self):
        return self._movies

    def get_subtitles(self):
        return self._subtitles

    def search_more_subtitles(self):
        found_new = False
        for movie, query in zip(self._movies, self._queries):
            new_subs = query.search_more_subtitles(movie)
            for new_sub in new_subs:
                self._subtitles.add_subtitle(new_sub)
            if new_subs:
                found_new = True
        return found_new


class RemoteMovieCollection(object):
    def __init__(self):
        self._movie_networks = []

    def add_movie(self, movie, query):
        m_identities = movie.get_identities()
        for movie_network in self._movie_networks:
            match_identity = m_identities.matches_identity(movie_network.get_identities())
            if match_identity == MovieMatch.Equal:
                movie_network.add_movie(movie, query)
        else:
            self._movie_networks.append(RemoteMovieNetwork(movie, query))

    def __len__(self):
        return len(self._movie_networks)

    def __getitem__(self, item):
        return self._movie_networks[item]
