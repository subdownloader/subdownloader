# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import datetime
import logging
import xml.parsers.expat
from xml.dom import minidom

try:
    from urllib.parse import quote
    from urllib.request import HTTPError, urlopen, URLError
except ImportError:
    from urllib2 import HTTPError, urlopen, URLError, quote

from subdownloader.provider.SDService import OpenSubtitles_SubtitleFile

from subdownloader.languages.language import NotALanguageException, Language, UnknownLanguage
from subdownloader.FileManagement import subtitlefile

log = logging.getLogger("subdownloader.FileManagement.search")


class Movie(object):

    def __init__(self, movie_name, movie_year, provider_link, provider_id, imdb_link, imdb_id, imdb_rating, subtitles_nb_total):
        # movieInfo is a dict
        self._movie_name = movie_name
        self._movie_year = movie_year

        self._provider_link = provider_link
        self._provider_id = provider_id
        self._imdb_link = imdb_link
        self._imdb_id = imdb_id
        self._imdb_rating = imdb_rating

        self._subtitles_local = []
        self._subtitles_nb_total = subtitles_nb_total

    def get_nb_subs_total(self):
        return self._subtitles_nb_total

    def get_nb_subs_available(self):
        return len(self._subtitles_local)

    def get_provider_link(self):
        return self._provider_link

    def add_subtitles(self, subtitles):
        self._subtitles_local.extend(subtitles)

    def get_subtitles(self):
        return self._subtitles_local

    def get_name(self):
        return self._movie_name

    def get_year(self):
        return self._movie_year

    def get_imdb_id(self):
        return self._imdb_id

    def get_imdb_rating(self):
        return self._imdb_rating

    def __repr__(self):
        return '<{clsname} movie_name: {movie_name}, movie_year: {movie_year}, ' \
               'nb_subs_total={nb_subs_total}, nb_subs_available={nb_subs_available}, ' \
               'provider_link: {provider_link}, provider_id: {provider_id}, ' \
               'imdb_link: {imdb_link}, imdb_id: {imdb_id}, imdb_rating: {imdb_rating}'.format(
            clsname = type(self).__name__,
            movie_name=self._movie_name, movie_year=self._movie_year,
            nb_subs_total=self.get_nb_subs_total(), nb_subs_available=self.get_nb_subs_available(),
            provider_link=self._provider_link, provider_id=self._provider_id,
            imdb_link=self._imdb_link, imdb_id=self._imdb_id, imdb_rating=self._imdb_rating)


class MovieOriginal(object):

    def __init__(self, movieInfo):
        # movieInfo is a dict
        self.MovieName = movieInfo.get("MovieName", None)
        try:
            self.MovieSiteLink = str(movieInfo["MovieID"]["Link"])
        except KeyError:
            self.MovieSiteLink = None
        try:
            self.IMDBLink = str(movieInfo["MovieID"]["LinkImdb"])
        except KeyError:
            self.IMDBLink = None
        self.IMDBId = movieInfo.get("MovieImdbID", None)
        self.IMDBRating = movieInfo.get("MovieImdbRating", None)
        self.MovieYear = movieInfo.get("MovieYear", None)
        # this ID will be used when calling the 2nd step function to get the
        # Subtitle Details
        try:
            self.MovieId = int(movieInfo["MovieID"]["MovieID"])
        except (KeyError, ValueError):
            self.MovieId = None
        self.subtitles = []  # this is a list of Subtitle objects
        try:
            # Sometimes we get the TotalSubs in the 1st step before we get the
            # details of the subtitles
            self.totalSubs = int(movieInfo["TotalSubs"])
        except KeyError:
            self.totalSubs = self.get_total_subs()

    def get_total_subs(self):
        return len(self.subtitles)

    def get_subtitles(self):
        return self.subtitles

    def __repr__(self):
        return "<Movie MovieName: %s, MovieSiteLink: %s, IMDBLink: %s, IMDBRating: %s, MovieYear: %s, MovieId: %s, totalSubs: %s, subtitles: %r>" % (self.MovieName, self.MovieSiteLink, self.IMDBLink, self.IMDBRating, self.MovieYear, self.MovieId, self.totalSubs, self.subtitles)


class SearchByName(object):

    def __init__(self, query):
        self._query = query
        self._movies = []
        self._total = None

    def _safe_exec(self, query, default):
        try:
            result = query()
            return result
        except HTTPError:
            log.debug("Query failed", exc_info=True)
            return default

    def get_movies(self):
        return self._movies

    def get_nb_movies_online(self):
        return self._total

    def more_movies_available(self):
        if self._total is None:
            return True
        return len(self._movies) < self._total

    def search_movies(self):
        if not self.more_movies_available():
            return False

        xml_url = 'http://www.opensubtitles.org/en/search2/moviename-{text_quoted}/offset-{offset}/xml'.format(
            offset=len(self._movies),
            text_quoted=quote(self._query))

        xml_page = self.fetch_url(xml_url)
        if xml_page is None:
            return False

        movies, nb_total = self.parse_movie(xml_page)
        self._total = nb_total
        self._movies.extend(movies)

        return True

    def search_more_subtitles(self, movie):
        if movie.get_nb_subs_available() == movie.get_nb_subs_total():
            return None
        xml_url = 'http://www.opensubtitles.org{provider_link}/offset-{offset}/xml'.format(
            provider_link=movie.get_provider_link(),
            offset=movie.get_nb_subs_available())

        xml_page = self.fetch_url(xml_url)
        if xml_page is None:
            return None

        subtitles, nb_total = self.parse_subtitles(xml_page)
        if subtitles is None:
            return None

        if movie.get_nb_subs_total() != nb_total:
            log.warning('Data mismatch: Partial search of subtitles told us movie has {nb_partial} subtitles '
                        'but index told us it has {nb_index} subtitles.'.format(
                nb_partial=nb_total, nb_index=movie.get_nb_subs_total()))
        movie.add_subtitles(subtitles)

        return subtitles

    def fetch_url(self, url):
        try:
            log.debug('Fetching data from {}...'.format(url))
            page = urlopen(url).read()
            log.debug('... SUCCESS')
        except HTTPError:
            log.debug('... FAILED (HTTPError)', exc_info=True)
            return None
        return page

    def search_url(self, xml_url):
        try:
            log.debug('Fetching data from {url}...'.format(url=xml_url))
            xml_page = urlopen(xml_url).read()
            log.debug('... SUCCESS')
        except HTTPError:
            log.debug('... FAILED (HTTPError)', exc_info=True)
            return None

        log.debug('Parsing xml...')
        movies = self.parse_results(xml_page)
        log.debug('... Parsing finished (is_none? {})'.format(movies is None))

        return movies

    def parse_movie(self, raw_xml):
        subtitle_entries, nb_provider, nb_provider_total = self.extract_subtitle_entries(raw_xml)
        if subtitle_entries is None:
            return None, None

        movies = []
        for subtitle_entry in subtitle_entries:
            try:
                ads_entries = subtitle_entry.getElementsByTagName('ads1')
                if ads_entries:
                    continue
                def try_get_firstchild_data(key, default):
                    try:
                        return subtitle_entry.getElementsByTagName(key)[0].firstChild.data
                    except (AttributeError, IndexError):
                        return default
                movie_id_entries = subtitle_entry.getElementsByTagName('MovieID')
                movie_id = movie_id_entries[0].firstChild.data
                movie_id_link = movie_id_entries[0].getAttribute('Link')
                # movie_thumb = subtitle_entry.getElementsByTagName('MovieThumb')[0].firstChild.data
                # link_use_next = subtitle_entry.getElementsByTagName('LinkUseNext')[0].firstChild.data
                # link_zoozle = subtitle_entry.getElementsByTagName('LinkZoozle')[0].firstChild.data
                # link_boardreader = subtitle_entry.getElementsByTagName('LinkBoardreader')[0].firstChild.data
                movie_name = try_get_firstchild_data('MovieName', None)
                movie_year = try_get_firstchild_data('MovieYear', None)
                try:
                    movie_imdb_rating = float(subtitle_entry.getElementsByTagName('MovieImdbRating')[0].getAttribute('Percent')) / 10
                except AttributeError:
                    movie_imdb_rating = None
                try:
                    movie_imdb_link = movie_id_entries[0].getAttribute('LinkImdb')
                except AttributeError:
                    movie_imdb_link = None
                movie_imdb_id = try_get_firstchild_data('MovieImdbID', None)
                subs_total = int(subtitle_entry.getElementsByTagName('TotalSubs')[0].firstChild.data)
                # newest = subtitle_entry.getElementsByTagName('Newest')[0].firstChild.data
                movie = Movie(
                    movie_name=movie_name, movie_year=movie_year, subtitles_nb_total=subs_total,
                    provider_link=movie_id_link, provider_id=movie_id,
                    imdb_link=movie_imdb_link, imdb_id=movie_imdb_id, imdb_rating=movie_imdb_rating)
                movies.append(movie)
            except (AttributeError, IndexError, ValueError):
                log.warning('subtitle_entry={}'.format(subtitle_entry.toxml()))
                log.warning('XML entry has invalid format.', exc_info=True)

        if len(movies) != nb_provider:
            log.warning('Provider told us it returned {nb_provider} movies. '
                        'Yet we only extracted {nb_local} movies.'.format(
                nb_provider=nb_provider, nb_local=len(movies)))
        return movies, nb_provider_total

    def extract_subtitle_entries(self, raw_xml):
        nb = None
        nb_total = None
        entries = None
        log.debug('extract_subtitle_entries() ...')
        try:
            dom = minidom.parseString(raw_xml)
            entries = None
            opensubtitles_entries = dom.getElementsByTagName('opensubtitles')
            for opensubtitles_entry in opensubtitles_entries:
                results_entries = opensubtitles_entry.getElementsByTagName('results')
                for results_entry in results_entries:
                    nb = int(results_entry.getAttribute('items'))
                    nb_total = int(results_entry.getAttribute('itemsfound'))
                    entries = results_entry.getElementsByTagName('subtitle')
                    if entries:
                        break
            if entries is None:
                log.debug('... extraction FAILED (xml has unknown format)')
            else:
                log.debug('... extraction SUCCESS')
        except (AttributeError, ValueError, xml.parsers.expat.ExpatError):
            log.debug('... extraction FAILED (xml error)', exc_info=True)
        return entries, nb, nb_total

    def parse_subtitles(self, raw_xml):
        subtitle_entries, nb_provider, nb_provider_total = self.extract_subtitle_entries(raw_xml)
        if subtitle_entries is None:
            return None, None

        subtitles = []
        for subtitle_entry in subtitle_entries:
            try:
                ads_entries = subtitle_entry.getElementsByTagName('ads1') or subtitle_entry.getElementsByTagName('ads2')
                if ads_entries:
                    continue
                def try_get_firstchild_data(key, default):
                    try:
                        return subtitle_entry.getElementsByTagName(key)[0].firstChild.data
                    except (AttributeError, IndexError):
                        return default
                subtitle_id_entry = subtitle_entry.getElementsByTagName('IDSubtitle')[0]
                subtitle_id = subtitle_id_entry.firstChild.data
                subtitle_link = 'http://www.opensubtitles.org' + subtitle_id_entry.getAttribute('Link')
                subtitle_uuid = subtitle_id_entry.getAttribute('uuid')

                subtitlefile_id = subtitle_entry.getElementsByTagName('IDSubtitleFile')[0].firstChild.data

                user_entry = subtitle_entry.getElementsByTagName('UserID')[0]
                user_id = int(user_entry.firstChild.data)
                user_link = 'http://www.opensubtitles.org' + user_entry.getAttribute('Link')
                user_nickname = try_get_firstchild_data('UserNickName', None)

                comment = subtitle_entry.getElementsByTagName('SubAuthorComment')[0].firstChild

                language_entry = subtitle_entry.getElementsByTagName('ISO639')[0]
                language_iso639 = language_entry.firstChild.data
                language_link_search = 'http://www.opensubtitles.org' + language_entry.getAttribute('LinkSearch')
                language_flag = 'http:' + language_entry.getAttribute('flag')

                language_name = subtitle_entry.getElementsByTagName('LanguageName')[0].firstChild.data

                subtitle_format = subtitle_entry.getElementsByTagName('SubFormat')[0].firstChild.data
                subtitle_nbcds = int(subtitle_entry.getElementsByTagName('SubSumCD')[0].firstChild.data)
                subtitle_add_date_locale = subtitle_entry.getElementsByTagName('SubAddDate')[0].getAttribute('locale')
                subtitle_add_date = datetime.datetime.strptime(subtitle_add_date_locale, '%d/%m/%Y %H:%M:%S')
                subtitle_bad = int(subtitle_entry.getElementsByTagName('SubBad')[0].firstChild.data)
                subtitle_rating = float(subtitle_entry.getElementsByTagName('SubRating')[0].firstChild.data)

                download_count = int(subtitle_entry.getElementsByTagName('SubDownloadsCnt')[0].firstChild.data)
                subtitle_movie_aka = try_get_firstchild_data('SubMovieAka', None)

                subtitle_comments = int(subtitle_entry.getElementsByTagName('SubComments')[0].firstChild.data)
                # subtitle_total = subtitle_entry.getElementsByTagName('TotalSubs')[0].firstChild.data #PRESENT?
                # subtitle_newest = subtitle_entry.getElementsByTagName('Newest')[0].firstChild.data #PRESENT?

                language = Language.from_xx(language_iso639)

                download_link = 'http://www.opensubtitles.org/download/sub/{}'.format(subtitle_id)
                if user_nickname:
                    uploader = user_nickname
                elif user_id != 0:
                    uploader = str(user_id)
                else:
                    uploader = None
                subtitle = OpenSubtitles_SubtitleFile(filename=None, file_size=None, md5_hash=subtitle_uuid,
                                                      id_online=subtitlefile_id, download_link=download_link,
                                                      link=subtitle_link, uploader=uploader,
                                                      language=language, rating=subtitle_rating, age=subtitle_add_date)
                subtitles.append(subtitle)
            except (AttributeError, IndexError, ValueError):
                log.warning('subtitle_entry={}'.format(subtitle_entry.toxml()))
                log.warning('XML entry has invalid format.', exc_info=True)

        if len(subtitles) != nb_provider:
            log.warning('Provider told us it returned {nb_provider} subtitles. '
                        'Yet we only extracted {nb_local} subtitles.'.format(
                nb_provider=nb_provider, nb_local=len(subtitles)))
        return subtitles, nb_provider_total
