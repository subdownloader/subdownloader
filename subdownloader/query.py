# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3


from subdownloader.movie import RemoteMovieCollection


class SubtitlesTextQuery(object):
    def __init__(self, text):
        self._text = text
        self._queries = []
        self._movies = RemoteMovieCollection()

    @property
    def text(self):
        return self._text

    @property
    def movies(self):
        return self._movies

    def search_init(self, providers):
        self._queries = [provider.query_text(self.text) for provider in providers]

    def more_movies_available(self):
        return any(query.more_movies_available() for query in self._queries)

    def search_more_movies(self):
        for query in self._queries:
            movies = query.search_more_movies()
            for movie in movies:
                self.movies.add_movie(movie, query)
