# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import imdbpie
from typing import List, Optional, Sequence

from subdownloader.client.configuration import Settings

class ImdbMovieMatch:
    def __init__(self, imdb_id: str, title: str, year: Optional[int]):
        self.imdb_id = imdb_id
        self.title = title
        self.year = year

    @property
    def url(self) -> str:
        return 'https://www.imdb.com/title/{}'.format(self.imdb_id)

    @property
    def title_year(self) -> str:
        return '{}{}'.format(self.title, ' ({})'.format(self.year) if self.year is not None else '')

    def serialize(self) -> str:
        year_str = '' if self.year is None else str(self.year)
        return '{},{},{}'.format(self.imdb_id, year_str, self.title)

    @classmethod
    def deserialize(cls, data: str) -> Optional['ImdbMovieMatch']:
        try:
            [imdb_id, year_str, title] = data.split(',', 2)
            year = int(year_str) if year_str else None
            return cls(imdb_id, title, year)
        except ValueError:
            return None


class ImdbHistory(object):
    IMDB_HISTORY_KEY = ('upload', 'imdbHistory2',)

    def __init__(self):
        self.__data = []

    @property
    def _data(self) -> List[ImdbMovieMatch]:
        return self.__data

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, item: int) -> ImdbMovieMatch:
        return self._data[item]

    def insert_unique(self, index: int, item: ImdbMovieMatch) -> int:
        current_index = None
        for imdb_i, imdb in enumerate(self._data):
            if imdb.imdb_id == item.imdb_id:
                current_index = imdb_i
                break
        if current_index:
            del self._data[current_index]
        self._data.insert(index, item)
        return index

    def append(self, item: ImdbMovieMatch) -> None:
        self._data.append(item)

    def find_imdb_id(self, imdb_id: str) -> Optional[int]:
        for imdb_i, imdb in enumerate(self._data):
            if imdb.imdb_id == imdb_id:
                return imdb_i
        return None

    def sort_imdb_id(self) -> None:
        self._data.sort(key=lambda imdb: imdb.imdb_id)

    def limit(self, limit: int):
        self._data[:] = self._data[:limit]

    @classmethod
    def from_settings(cls, settings: Settings) -> 'ImdbHistory':
        imdb_str_list = settings.get_list(cls.IMDB_HISTORY_KEY, None)
        if imdb_str_list is None:
            return cls()
        result = cls()
        for imdb_str in imdb_str_list:
            imdb = ImdbMovieMatch.deserialize(imdb_str)
            if imdb is None:
                continue
            result.append(imdb)
        return result

    def save_settings(self, settings: Settings) -> None:
        imdb_str_list = list(imdb.serialize() for imdb in self._data)
        settings.set_list(self.IMDB_HISTORY_KEY, imdb_str_list)


class ImdbProvider(object):
    def __init__(self):
        pass

    def login(self) -> None:
        raise NotImplementedError()

    def search_title(self, title: str) -> Sequence[ImdbMovieMatch]:
        raise NotImplementedError()


class ImdbPieProvider(ImdbProvider):
    def __init__(self):
        ImdbProvider.__init__(self)
        self._imdb = imdbpie.ImdbFacade()

    def login(self) -> None:
        pass

    def search_title(self, title: str) -> Sequence[ImdbMovieMatch]:
        movies = self._imdb.search_for_title(title)
        results = []
        for movie in movies:
            results.append(ImdbMovieMatch(
                imdb_id=movie.imdb_id, title=movie.title, year=int(movie.year)))
        return results
