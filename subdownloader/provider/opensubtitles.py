# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import base64
import datetime
from http.client import CannotSendRequest
import logging
import re
from socket import error as SocketError
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen
from xmlrpc.client import ProtocolError, ServerProxy

from subdownloader.languages.language import Language, NotALanguageException, UnknownLanguage
from subdownloader.identification import ImdbIdentity, ProviderIdentities, VideoIdentity
from subdownloader.movie import RemoteMovie
from subdownloader.provider import window_iterator
from subdownloader.provider.provider import ProviderConnectionError, ProviderNotConnectedError, \
    ProviderSettings, SubtitleProvider, SubtitleTextQuery
from subdownloader.subtitle2 import LocalSubtitleFile, RemoteSubtitleFile
from subdownloader.util import unzip_bytes, unzip_stream, write_stream


log = logging.getLogger('subdownloader.provider.opensubtitles')


class OpenSubtitles(SubtitleProvider):
    URL = 'http://api.opensubtitles.org/xml-rpc'

    def __init__(self):
        SubtitleProvider.__init__(self)
        self._xmlrpc = None
        self._token = None

        self._settings = OpenSubtitlesSettings()

    def get_settings(self):
        return self._settings

    def set_settings(self, settings):
        self._settings = settings

    def connect(self):
        log.debug('connect()')
        if self.connected():
            return
        self._xmlrpc = ServerProxy(self.URL, allow_none=False)

    def disconnect(self):
        log.debug('disconnect()')
        if self.logged_in():
            self.logout()
        if self.connected():
            self._xmlrpc = None

    def connected(self):
        return self._xmlrpc is not None

    def login(self):
        log.debug('login()')
        if self.logged_in():
            return
        if not self.connected():
            raise ProviderNotConnectedError()

        def login_query():
            # FIXME: 'en' language ok??? or '' as in the original
            return self._xmlrpc.LogIn(str(self._settings.username), str(self._settings.password),
                                      'en', str(self._settings.get_user_agent()))
        result = self._safe_exec(login_query, None)
        self.check_result(result)
        self._token = result['token']

    def logout(self):
        log.debug('logout()')
        if self.logged_in():
            def logout_query():
                return self._xmlrpc.LogOut(self._token)
            result = self._safe_exec(logout_query, None)
            self.check_result(result)
        self._token = None

    def logged_in(self):
        return self._token is not None

    SEARCH_LIMIT = 500

    def search_videos(self, videos, callback, languages=None):
        log.debug('search_videos(#videos={})'.format(len(videos)))
        if not self.logged_in():
            raise ProviderNotConnectedError()

        lang_str = self._languages_to_str(languages)

        window_size = 5
        callback.set_range(0, (len(videos) + (window_size - 1)) // window_size)

        remote_subtitles = []
        for window_i, video_window in enumerate(window_iterator(videos, window_size)):
            callback.update(window_i)
            if callback.canceled():
                break

            queries = []
            hash_video = {}
            for video in video_window:
                query = {
                    'sublanguageid': lang_str,
                    'moviehash': video.get_osdb_hash(),
                    'moviebytesize': str(video.get_size()),
                }
                queries.append(query)
                hash_video[video.get_osdb_hash()] = video

            def run_query():
                return self._xmlrpc.SearchSubtitles(self._token, queries, {'limit': self.SEARCH_LIMIT})
            result = self._safe_exec(run_query, None)
            self.check_result(result)
            if result is None:
                continue

            for rsub_raw in result['data']:
                try:
                    remote_filename = rsub_raw['SubFileName']
                    remote_file_size = int(rsub_raw['SubSize'])
                    remote_id = rsub_raw['IDSubtitleFile']
                    remote_md5_hash = rsub_raw['SubHash']
                    remote_download_link = rsub_raw['SubDownloadLink']
                    remote_link = rsub_raw['SubtitlesLink']
                    remote_uploader = rsub_raw['UserNickName'].strip()
                    remote_language_raw = rsub_raw['SubLanguageID']
                    try:
                        remote_language = Language.from_unknown(remote_language_raw,
                                                                xx=True, xxx=True)
                    except NotALanguageException:
                        remote_language = UnknownLanguage(remote_language_raw)
                    remote_rating = float(rsub_raw['SubRating'])
                    remote_date = datetime.datetime.strptime(rsub_raw['SubAddDate'], '%Y-%m-%d %H:%M:%S')
                    remote_subtitle = OpenSubtitlesSubtitleFile(
                        filename=remote_filename,
                        file_size=remote_file_size,
                        md5_hash=remote_md5_hash,
                        id_online=remote_id,
                        download_link=remote_download_link,
                        link=remote_link,
                        uploader=remote_uploader,
                        language=remote_language,
                        rating=remote_rating,
                        age=remote_date,
                    )
                    movie_hash = '{:>016}'.format(rsub_raw['MovieHash'])
                    video = hash_video[movie_hash]

                    imdb_id = rsub_raw['IDMovieImdb']
                    imdb_identity = ImdbIdentity(imdb_id=imdb_id, imdb_rating=None)
                    identity = ProviderIdentities(imdb_identity=imdb_identity, provider=self)

                    video.add_subtitle(remote_subtitle)
                    video.add_identity(identity)

                    remote_subtitles.append(remote_subtitle)
                except (KeyError, ValueError):
                    log.exception('Error parsing result of SearchSubtitles(...)')
                    log.error('Offending query is: {queries}'.format(queries=queries))
                    log.error('Offending result is: {remote_sub}'.format(remote_sub=rsub_raw))

        callback.finish()
        return remote_subtitles

    def query_text(self, query):
        return OpenSubtitlesTextQuery(query=query)

    def download_subtitles(self, os_rsubs):
        log.debug('download_subtitles()')
        if not self.logged_in():
            raise ProviderNotConnectedError()

        window_size = 20
        map_id_data = {}
        for window_i, os_rsub_window in enumerate(window_iterator(os_rsubs, window_size)):
            query = [subtitle.get_id_online() for subtitle in os_rsub_window]

            def run_query():
                return self._xmlrpc.DownloadSubtitles(self._token, query)
            result = self._safe_exec(run_query, None)

            self.check_result(result)
            map_id_data.update({item['idsubtitlefile']: item['data'] for item in result['data']})
        subtitles = [unzip_bytes(base64.b64decode(map_id_data[os_rsub.get_id_online()])).read() for os_rsub in os_rsubs]
        return subtitles

    def ping(self):
        log.debug('ping()')
        if not self.logged_in():
            raise ProviderNotConnectedError()

        def run_query():
            return self._xmlrpc.NoOperation(self._token)
        result = self._safe_exec(run_query, None)
        self.check_result(result)

    @staticmethod
    def _languages_to_str(languages):
        if languages:
            lang_str = ','.join([language.xxx() for language in languages])
        else:
            lang_str = 'all'

        return lang_str

    @classmethod
    def get_name(cls):
        return 'opensubtitles'

    @classmethod
    def get_short_name(cls):
        return 'os'

    def _signal_connection_failed(self):
        # FIXME: set flag/... to signal users that the connection has failed
        pass

    def _safe_exec(self, query, default):
        try:
            result = query()
            return result
        except (ProtocolError, CannotSendRequest, SocketError):
            self._signal_connection_failed()
            log.warning('Query failed', exc_info=True)
            return default

    STATUS_CODE_RE = re.compile('(\d+) (.+)')

    @classmethod
    def check_result(cls, data):
        log.debug('check_result(<data>)')
        if data is None:
            log.warning('data is None ==> FAIL')
            raise ProviderConnectionError(_('No message'))
        log.debug('checking presence of "status" in result ...')
        if 'status' not in data:
            log.debug('... no "status" in result ==> assuming SUCCESS')
            return
        log.debug('... FOUND')
        status = data['status']
        log.debug('result["status"]="{status}"'.format(status=status))
        log.debug('applying regex to status ...')
        try:
            code, message = cls.STATUS_CODE_RE.match(status).groups()
            log.debug('... regex SUCCEEDED')
            code = int(code)
        except (AttributeError, ValueError):
            log.debug('... regex FAILED')
            log.warning('Got unexpected status="{status}" from server.'.format(status=status))
            log.debug('Checking for presence of "200" ...')
            if '200' not in data['status']:
                log.debug('... FAIL. Raising ProviderConnectionError.')
                raise ProviderConnectionError(
                    _('Server returned status="{status}". Expected "200 OK".').format(status=data['status']),
                    data['status'])
            log.debug('... SUCCESS')
            code, message = 200, 'OK'
        log.debug('Checking code={code} ...'.format(code=code))
        if code != 200:
            log.debug('... FAIL. Raising ProviderConnectionError.')
            raise ProviderConnectionError(message, code)
        log.debug('... SUCCESS.')
        log.debug('check_result() finished (data is ok)')


class OpenSubtitlesTextQuery(SubtitleTextQuery):
    def __init__(self, query):
        SubtitleTextQuery.__init__(self, query)
        self._movies = []
        self._total = None

    def get_movies(self):
        return self._movies

    def get_nb_movies_online(self):
        return self._total

    def more_movies_available(self):
        if self._total is None:
            return True
        return len(self._movies) < self._total

    def search_online(self):
        raise NotImplementedError()

    @staticmethod
    def _safe_exec(query, default):
        try:
            result = query()
            return result
        except HTTPError:
            log.warning('Query failed', exc_info=True)
            return default

    def search_more_movies(self):
        if not self.more_movies_available():
            return []

        xml_url = 'http://www.opensubtitles.org/en/search2/moviename-{text_quoted}/offset-{offset}/xml'.format(
            offset=len(self._movies),
            text_quoted=quote(self._query))

        xml_page = self._fetch_url(xml_url)
        if xml_page is None:
            raise ProviderConnectionError()

        movies, nb_so_far, nb_provider = self._xml_to_movies(xml_page)
        if movies is None:
            raise ProviderConnectionError()

        self._total = nb_provider
        self._movies.extend(movies)

        if len(self._movies) != nb_so_far:
            log.warning('Provider told us it returned {nb_so_far} movies. '
                        'Yet we only extracted {nb_local} movies.'.format(
                nb_so_far=nb_so_far, nb_local=len(movies)))

        return movies

    def search_more_subtitles(self, movie):
        print('avail:', movie.get_nb_subs_available(), 'total:', movie.get_nb_subs_total())
        if movie.get_nb_subs_available() == movie.get_nb_subs_total():
            return None
        xml_url = 'http://www.opensubtitles.org{provider_link}/offset-{offset}/xml'.format(
            provider_link=movie.get_provider_link(),
            offset=movie.get_nb_subs_available())

        xml_contents = self._fetch_url(xml_url)
        if xml_contents is None:
            raise ProviderConnectionError('Failed to fetch url {url}'.format(url=xml_url))

        open('/tmp/sub', 'wb').write(xml_contents)

        subtitles, nb_so_far, nb_provider = self._xml_to_subtitles(xml_contents)
        if subtitles is None:
            raise ProviderConnectionError()

        # if movie.get_nb_subs_available() != nb_so_far:
        #     log.warning('Data mismatch: we know movie has {local_nb_so_far} subtitles available. '
        #                 'Server says it has so far returned {nb_so_far} subtitles.'.format(
        #         local_nb_so_far=movie.get_nb_subs_total(), nb_so_far=nb_so_far))
        #     return None  # Detect series
        movie.add_subtitles(subtitles)

        return subtitles

    def _xml_to_movies(self, xml):
        subtitle_entries, nb_so_far, nb_provider = self._extract_subtitle_entries(xml)
        if subtitle_entries is None:
            return None, None, None

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
                    movie_imdb_rating = float(
                        subtitle_entry.getElementsByTagName('MovieImdbRating')[0].getAttribute('Percent')) / 10
                except AttributeError:
                    movie_imdb_rating = None
                # try:
                #     movie_imdb_link = movie_id_entries[0].getAttribute('LinkImdb')
                # except AttributeError:
                #     movie_imdb_link = None
                movie_imdb_id = try_get_firstchild_data('MovieImdbID', None)
                subs_total = int(subtitle_entry.getElementsByTagName('TotalSubs')[0].firstChild.data)
                # newest = subtitle_entry.getElementsByTagName('Newest')[0].firstChild.data

                imdb_identity = ImdbIdentity(imdb_id=movie_imdb_id, imdb_rating=movie_imdb_rating)
                video_identity = VideoIdentity(name=movie_name, year=movie_year)
                identity = ProviderIdentities(video_identity=video_identity, imdb_identity=imdb_identity, provider=self)

                movie = RemoteMovie(
                    subtitles_nb_total=subs_total, provider_link=movie_id_link, provider_id=movie_id,
                    identities=identity
                )

                movies.append(movie)
            except (AttributeError, IndexError, ValueError):
                log.warning('subtitle_entry={}'.format(subtitle_entry.toxml()))
                log.warning('XML entry has invalid format.', exc_info=True)

        return movies, nb_so_far, nb_provider

    def _xml_to_subtitles(self, xml):
        subtitle_entries, nb_so_far, nb_provider = self._extract_subtitle_entries(xml)
        if subtitle_entries is None:
            return None, None, None

        subtitles = []
        for subtitle_entry in subtitle_entries:
            try:
                ads_entries = subtitle_entry.getElementsByTagName('ads1') or subtitle_entry.getElementsByTagName('ads2')
                if ads_entries:
                    continue

                def try_get_first_child_data(key, default):
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
                # user_link = 'http://www.opensubtitles.org' + user_entry.getAttribute('Link')
                user_nickname = try_get_first_child_data('UserNickName', None)

                # comment = try_get_first_child_data(''SubAuthorComment', None)

                language_entry = subtitle_entry.getElementsByTagName('ISO639')[0]
                language_iso639 = language_entry.firstChild.data
                # language_link_search = 'http://www.opensubtitles.org' + language_entry.getAttribute('LinkSearch')
                # language_flag = 'http:' + language_entry.getAttribute('flag')

                # language_name = try_get_first_child_data('LanguageName', None)

                subtitle_format = try_get_first_child_data('SubFormat', 'srt')
                # subtitle_nbcds = int(try_get_first_child_data('SubSumCD', -1))
                subtitle_add_date_locale = subtitle_entry.getElementsByTagName('SubAddDate')[0].getAttribute('locale')
                subtitle_add_date = datetime.datetime.strptime(subtitle_add_date_locale, '%d/%m/%Y %H:%M:%S')
                # subtitle_bad = int(subtitle_entry.getElementsByTagName('SubBad')[0].firstChild.data)
                subtitle_rating = float(subtitle_entry.getElementsByTagName('SubRating')[0].firstChild.data)

                # download_count = int(try_get_first_child_data('SubDownloadsCnt', -1))
                # subtitle_movie_aka = try_get_first_child_data('SubMovieAka', None)

                # subtitle_comments = int(try_get_first_child_data('SubComments', -1))
                # subtitle_total = int(try_get_first_child_data('TotalSubs', -1)) #PRESENT?
                # subtitle_newest = try_get_first_child_data('Newest', None) #PRESENT?

                language = Language.from_xx(language_iso639)

                movie_release_name = subtitle_entry.getElementsByTagName('MovieReleaseName')[0].firstChild.data
                filename = '{}.{}'.format(movie_release_name, subtitle_format)

                download_link = 'http://www.opensubtitles.org/download/sub/{}'.format(subtitle_id)
                if user_nickname:
                    uploader = user_nickname
                elif user_id != 0:
                    uploader = str(user_id)
                else:
                    uploader = None
                subtitle = OpenSubtitlesSubtitleFile(filename=filename, file_size=None, md5_hash=subtitle_uuid,
                                                     id_online=subtitlefile_id, download_link=download_link,
                                                     link=subtitle_link, uploader=uploader,
                                                     language=language, rating=subtitle_rating, age=subtitle_add_date)
                subtitles.append(subtitle)
            except (AttributeError, IndexError, ValueError):
                log.warning('subtitle_entry={}'.format(subtitle_entry.toxml()))
                log.warning('XML entry has invalid format.', exc_info=True)

        return subtitles, nb_so_far, nb_provider

    @staticmethod
    def _extract_subtitle_entries(raw_xml):
        entries = []
        nb_so_far = 0
        nb_total = 0
        from xml.dom import minidom
        import xml.parsers.expat
        log.debug('extract_subtitle_entries() ...')
        try:
            # FIXME: use xpath
            dom = minidom.parseString(raw_xml)
            opensubtitles_entries = dom.getElementsByTagName('opensubtitles')
            for opensubtitles_entry in opensubtitles_entries:
                results_entries = opensubtitles_entry.getElementsByTagName('results')
                for results_entry in results_entries:
                    try:
                        nb_so_far = int(results_entry.getAttribute('items'))
                        nb_total = int(results_entry.getAttribute('itemsfound'))
                        entries = results_entry.getElementsByTagName('subtitle')
                        break
                    except ValueError:
                        continue
            if entries is None:
                log.debug('... extraction FAILED: no entries found, maybe no subtitles on page!')
            else:
                log.debug('... extraction SUCCESS')
        except (AttributeError, ValueError, xml.parsers.expat.ExpatError):
            log.debug('... extraction FAILED (xml error)', exc_info=True)
            nb_so_far = None
            entries = None
        return entries, nb_so_far, nb_total

    @staticmethod
    def _fetch_url(url):
        try:
            log.debug('Fetching data from {}...'.format(url))
            page = urlopen(url).read()
            log.debug('... SUCCESS')
        except HTTPError:
            log.warning('... FAILED', exc_info=True)
            return None
        return page


DEFAULT_USER_AGENT = ''


def set_default_user_agent(user_agent):
    global DEFAULT_USER_AGENT
    DEFAULT_USER_AGENT = user_agent


class OpenSubtitlesSettings(ProviderSettings):
    def __init__(self, username='', password='', user_agent=None):
        ProviderSettings.__init__(self)
        self._username = username
        self._password = password
        self._user_agent = DEFAULT_USER_AGENT if user_agent is None else user_agent

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @classmethod
    def load(cls, username, password):
        return cls(username=str(username), password=str(password))

    def as_dict(self):
        return {
            'username': self._username,
            'password': self._password,
        }

    def get_user_agent(self):
        return self._user_agent


class OpenSubtitlesSubtitleFile(RemoteSubtitleFile):
    def __init__(self, filename, file_size, md5_hash, id_online, download_link,
                 link, uploader, language, rating, age):
        RemoteSubtitleFile.__init__(self, filename=filename, file_size=file_size, language=language, md5_hash=md5_hash)
        self._id_online = id_online
        self._download_link = download_link
        self._link = link
        self._uploader = uploader
        self._rating = rating
        self._age = age

    def get_id_online(self):
        return self._id_online

    def get_uploader(self):
        return self._uploader

    def get_rating(self):
        return self._rating

    def get_link(self):
        return self._link

    def get_age(self):
        return self._age

    def get_provider(self):
        return OpenSubtitles

    def download(self, target_path, provider_instance, callback):
        stream = self._download_web()
        write_stream(src_file=stream, destination_path=target_path)
        local_sub = LocalSubtitleFile(filepath=target_path)
        super_parent = self.get_super_parent()
        if super_parent:
            super_parent.add_subtitle(local_sub)
        return tuple((local_sub, ))

    # def _download(self, provider_instance, callback):
    #     # method 1:
    #     subs = provider_instance.download_subtitles([self])
    #     return BytesIO(subs[0])

    def _download_web(self):
        # method 2:
        sub_stream = urlopen(self._download_link)
        return sub_stream

providers = (OpenSubtitles, )
