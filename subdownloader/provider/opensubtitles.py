# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import base64
import datetime
from http.client import CannotSendRequest
import io
import logging
import re
from socket import error as SocketError
import string
import time
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen
from xmlrpc.client import ProtocolError, ServerProxy
from xml.parsers.expat import ExpatError
import zlib

from subdownloader.languages.language import Language, NotALanguageException, UnknownLanguage
from subdownloader.identification import ImdbIdentity, ProviderIdentities, SeriesIdentity, VideoIdentity
from subdownloader.movie import RemoteMovie
from subdownloader.provider.imdb import ImdbMovieMatch
from subdownloader.provider import window_iterator
from subdownloader.provider.provider import ProviderConnectionError, ProviderNotConnectedError, \
    ProviderSettings, ProviderSettingsType, SubtitleProvider, SubtitleTextQuery, UploadResult
from subdownloader.subtitle2 import LocalSubtitleFile, RemoteSubtitleFile
from subdownloader.util import unzip_bytes, unzip_stream, write_stream


log = logging.getLogger('subdownloader.provider.opensubtitles')


class OpenSubtitlesProviderConnectionError(ProviderConnectionError):
    CODE_MAP = {
        200: _('OK'),
        206: _('Partial content; message'),
        301: _('Moved (host)'),
        401: _('Unauthorized'),
        402: _('Subtitle(s) have invalid format'),
        403: _('Subtitle hashes (content and sent subhash) are not same!'),
        404: _('Subtitles have invalid language!'),
        405: _('Not all mandatory parameters were specified'),
        406: _('No session'),
        407: _('Download limit reached'),
        408: _('Invalid parameters'),
        409: _('Method not found'),
        410: _('Other or unknown error'),
        411: _('Empty or invalid useragent'),
        412: _('%s has invalid format (reason)'),
        413: _('Invalid IMDb ID'),
        414: _('Unknown User Agent'),
        415: _('Disabled user agent'),
        416: _('Internal subtitle validation failed'),
        429: _('Too many requests'),
        503: _('Service unavailable'),
        506: _('Server under maintenance'),
    }

    def __init__(self, code, message, extra_data=None):
        self._code = code
        if self._code:
            try:
                msg = '{} {}'.format(self._code, self.CODE_MAP[self._code])
            except TypeError:
                self._code = None
                msg = '{} {}'.format(self._code, message)
        else:
            msg = message
        ProviderConnectionError.__init__(self, msg, extra_data=extra_data)

    def get_code(self):
        return self._code


class OpenSubtitles(SubtitleProvider):
    URL = 'http://api.opensubtitles.org/xml-rpc'

    def __init__(self, settings=None):
        SubtitleProvider.__init__(self)
        self._xmlrpc = None
        self._token = None
        self._last_time = None

        if settings is None:
            settings = OpenSubtitlesSettings()
        self._settings = settings

    def get_settings(self):
        return self._settings

    def set_settings(self, settings):
        if self.connected():
            raise RuntimeError('Cannot set settings while connected')  # FIXME: change error
        self._settings = settings

    def connect(self):
        log.debug('connect()')
        if self.connected():
            return
        self._xmlrpc = ServerProxy(self.URL, allow_none=False)
        self._last_time = time.time()

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
            self.connect()

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
            # Do no check result of this call. Assume connection closed.
            self._safe_exec(logout_query, None)
        self._token = None

    def logged_in(self):
        return self._token is not None

    def reestablish(self):
        log.debug('reestablish()')
        connected = self.connected()
        logged_in = self.logged_in()
        self.disconnect()
        if connected:
            self.connect()
        if logged_in:
            self.login()

    _TIMEOUT_MS = 60000

    def _ensure_connection(self):
        now = time.time()
        if now - time.time() > self._TIMEOUT_MS:
            self.reestablish()
            self._last_time = now

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
                if video.get_osdb_hash() is None:
                    log.debug('osdb hash of "{}" is empty -> skip'.format(video.get_filepath()))
                    self._signal_connection_failed()  # FIXME: other name + general signaling
                    continue
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
                        date=remote_date,
                    )
                    movie_hash = '{:>016}'.format(rsub_raw['MovieHash'])
                    video = hash_video[movie_hash]

                    imdb_id = rsub_raw['IDMovieImdb']
                    try:
                        imdb_rating = float(rsub_raw['MovieImdbRating'])
                    except (ValueError, KeyError):
                        imdb_rating = None
                    imdb_identity = ImdbIdentity(imdb_id=imdb_id, imdb_rating=imdb_rating)

                    video_name = rsub_raw['MovieName']
                    try:
                        video_year = int(rsub_raw['MovieYear'])
                    except (ValueError, KeyError):
                        video_year = None
                    video_identity = VideoIdentity(name=video_name, year=video_year)

                    try:
                        series_season = int(rsub_raw['SeriesSeason'])
                    except (KeyError, ValueError):
                        series_season = None
                    try:
                        series_episode = int(rsub_raw['SeriesEpisode'])
                    except (KeyError, ValueError):
                        series_episode = None
                    series_identity = SeriesIdentity(season=series_season, episode=series_episode)

                    identity = ProviderIdentities(video_identity=video_identity, imdb_identity=imdb_identity,
                                                  episode_identity=series_identity, provider=self)
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

    def upload_subtitles(self, local_movie):
        log.debug('upload_subtitles()')
        if not self.logged_in():
            raise ProviderNotConnectedError()
        video_subtitles = list(local_movie.iter_video_subtitles())
        if not video_subtitles:
            return UploadResult(type=UploadResult.Type.MISSINGDATA, reason=_('Need at least one subtitle to upload'))

        query_try = dict()
        for sub_i, (video, subtitle) in enumerate(video_subtitles):
            if not video:
                return UploadResult(type=UploadResult.Type.MISSINGDATA, reason=_('Each subtitle needs an accompanying video'))
            query_try['cd{}'.format(sub_i+1)] = {
                'subhash': subtitle.get_md5_hash(),
                'subfilename': subtitle.get_filename(),
                'moviehash': video.get_osdb_hash(),
                'moviebytesize': str(video.get_size()),
                'moviefps': str(video.get_fps()) if video.get_fps() else None,
                'movieframes': str(video.get_framecount()) if video.get_framecount() else None,
                'moviefilename': video.get_filename(),
            }

        def run_query_try_upload():
            return self._xmlrpc.TryUploadSubtitles(self._token, query_try)
        try_result = self._safe_exec(run_query_try_upload, None)
        self.check_result(try_result)

        if int(try_result['alreadyindb']):
            return UploadResult(type=UploadResult.Type.DUPLICATE, reason=_('Subtitle is already in database'))

        if local_movie.get_imdb_id() is None:
            return UploadResult(type=UploadResult.Type.MISSINGDATA, reason=_('Need IMDb id'))
        upload_base_info = {
            'idmovieimdb': local_movie.get_imdb_id(),
        }

        if local_movie.get_comments() is not None:
            upload_base_info['subauthorcomment'] = local_movie.get_comments()
        if not local_movie.get_language().is_generic():
            upload_base_info['sublanguageid'] = local_movie.get_language().xxx()
        if local_movie.get_release_name() is not None:
            upload_base_info['moviereleasename'] = local_movie.get_release_name()
        if local_movie.get_movie_name() is not None:
            upload_base_info['movieaka'] = local_movie.get_movie_name()
        if local_movie.is_hearing_impaired() is not None:
            upload_base_info['hearingimpaired'] = local_movie.is_hearing_impaired()
        if local_movie.is_high_definition() is not None:
            upload_base_info['highdefinition'] = local_movie.is_high_definition()
        if local_movie.is_automatic_translation() is not None:
            upload_base_info['automatictranslation'] = local_movie.is_automatic_translation()
        if local_movie.get_author() is not None:
            upload_base_info['subtranslator'] = local_movie.get_author()
        if local_movie.is_foreign_only() is not None:
            upload_base_info['foreignpartsonly'] = local_movie.is_foreign_only()

        query_upload = {
            'baseinfo': upload_base_info,
        }
        for sub_i, (video, subtitle) in enumerate(video_subtitles):
            sub_bytes = subtitle.get_filepath().open(mode='rb').read()
            sub_tx_data = base64.b64encode(zlib.compress(sub_bytes)).decode()

            query_upload['cd{}'.format(sub_i+1)] = {
                'subhash': subtitle.get_md5_hash(),
                'subfilename': subtitle.get_filename(),
                'moviehash': video.get_osdb_hash(),
                'moviebytesize': str(video.get_size()),
                'movietimems': str(video.get_time_ms()) if video.get_time_ms() else None,
                'moviefps': str(video.get_fps()) if video.get_fps() else None,
                'movieframes': str(video.get_framecount()) if video.get_framecount() else None,
                'moviefilename': video.get_filename(),
                'subcontent': sub_tx_data,
            }

        def run_query_upload():
            return self._xmlrpc.UploadSubtitles(self._token, query_upload)

        result = self._safe_exec(run_query_upload, None)
        self.check_result(result)

        rsubs = []

        for sub_data in result['data']:
            filename = sub_data['SubFileName']
            file_size = sub_data['SubSize']
            md5_hash = sub_data['SubHash']
            id_online = sub_data['IDSubMOvieFile']
            download_link = sub_data['SubDownloadLink']
            link = None
            uploader = sub_data['UserNickName']
            language = Language.from_xxx(sub_data['SubLanguageID'])
            rating = float(sub_data['SubRating'])
            add_date = datetime.datetime.strptime(sub_data['SubAddDate'], '%Y-%m-%d %H:%M:%S')
            sub = OpenSubtitlesSubtitleFile(
                filename=filename, file_size=file_size, md5_hash=md5_hash, id_online=id_online,
                download_link=download_link, link=link, uploader=uploader, language=language,
                rating=rating, date=add_date)
            rsubs.append(sub)

        return UploadResult(type=UploadResult.Type.OK, rsubs=rsubs)

    def imdb_search_title(self, title):
        self._ensure_connection()

        def run_query():
            return self._xmlrpc.SearchMoviesOnIMDB(self._token, title.strip())

        result = self._safe_exec(run_query, default=None)
        self.check_result(result)

        imdbs = []
        re_title = re.compile(r'(?P<title>.*) \((?P<year>[0-9]+)\)')
        for imdb_data in result['data']:
            imdb_id = imdb_data['id']
            if all(c in string.digits for c in imdb_id):
                imdb_id = 'tt{}'.format(imdb_id)
            m = re_title.match(imdb_data['title'])
            if m:
                imdb_title = m['title']
                imdb_year = int(m['year'])
            else:
                imdb_title = imdb_data['title']
                imdb_year = None
            imdbs.append(ImdbMovieMatch(imdb_id=imdb_id, title=imdb_title, year=imdb_year))
        return imdbs

    def ping(self):
        log.debug('ping()')
        if not self.logged_in():
            raise ProviderNotConnectedError()

        def run_query():
            return self._xmlrpc.NoOperation(self._token)
        result = self._safe_exec(run_query, None)
        self.check_result(result)

    def provider_info(self):
        if self.connected():
            def run_query():
                return self._xmlrpc.ServerInfo()
            result = self._safe_exec(run_query, None)
            data = [
                (_('XML-RPC version'), result['xmlrpc_version']),
                (_('XML-RPC url'), result['xmlrpc_url']),
                (_('Application'), result['application']),
                (_('Contact'), result['contact']),
                (_('Website url'), result['website_url']),
                (_('Users online'), result['users_online_total']),
                (_('Programs online'), result['users_online_program']),
                (_('Users logged in'), result['users_loggedin']),
                (_('Max users online'), result['users_max_alltime']),
                (_('Users registered'), result['users_registered']),
                (_('Subtitles downloaded'), result['subs_downloads']),
                (_('Subtitles available'), result['subs_subtitle_files']),
                (_('Number movies'), result['movies_total']),
                (_('Number languages'), result['total_subtitles_languages']),
                (_('Client IP'), result['download_limits']['client_ip']),
                (_('24h global download limit'), result['download_limits']['global_24h_download_limit']),
                (_('24h client download limit'), result['download_limits']['client_24h_download_limit']),
                (_('24h client download count'), result['download_limits']['client_24h_download_count']),
                (_('Client download quota'), result['download_limits']['client_download_quota']),
            ]
        else:
            data = []
        return data

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

    @classmethod
    def get_icon(cls):
        return ':/images/sites/opensubtitles.png'

    def _signal_connection_failed(self):
        # FIXME: set flag/... to signal users that the connection has failed
        pass

    def _safe_exec(self, query, default):
        self._ensure_connection()
        try:
            result = query()
            return result
        except (ProtocolError, CannotSendRequest, SocketError, ExpatError) as e:
            self._signal_connection_failed()
            log.debug('Query failed: {} {}'.format(type(e), e.args))
            return default

    STATUS_CODE_RE = re.compile(r'(\d+) (.+)')

    @classmethod
    def check_result(cls, data):
        log.debug('check_result(<data>)')
        if data is None:
            log.warning('data is None ==> FAIL')
            raise OpenSubtitlesProviderConnectionError(None, _('No message'))
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
                raise OpenSubtitlesProviderConnectionError(
                    None,
                    _('Server returned status="{status}". Expected "200 OK".').format(status=data['status']),
                    data['status'])
            log.debug('... SUCCESS')
            code, message = 200, 'OK'
        log.debug('Checking code={code} ...'.format(code=code))
        if code != 200:
            log.debug('... FAIL. Raising ProviderConnectionError.')
            raise OpenSubtitlesProviderConnectionError(code, message)
        log.debug('... SUCCESS.')
        log.debug('check_result() finished (data is ok)')


class OpenSubtitlesTextQuery(SubtitleTextQuery):
    def get_movies(self):
        return self._movies

    def get_nb_movies_online(self):
        return self._total

    def more_movies_available(self):
        if self._total is None:
            return True
        return len(self._movies) < self._total

    def __init__(self, query):
        SubtitleTextQuery.__init__(self, query)
        self._movies = []
        self._total = None

    def search_online(self):
        raise NotImplementedError()

    @staticmethod
    def _safe_exec(query, default):
        try:
            result = query()
            return result
        except HTTPError as e:
            log.debug('Query failed: {} {}'.format(type(e), e.args))
            return default

    def search_more_movies(self):
        if not self.more_movies_available():
            return []

        xml_url = 'http://www.opensubtitles.org/en/search2/moviename-{text_quoted}/offset-{offset}/xml'.format(
            offset=len(self._movies),
            text_quoted=quote(self.query))

        xml_page = self._fetch_url(xml_url)
        if xml_page is None:
            raise OpenSubtitlesProviderConnectionError(None, 'Failed to fetch XML page at {!r}'.format(xml_url))

        movies, nb_so_far, nb_provider = self._xml_to_movies(xml_page)
        if movies is None:
            raise OpenSubtitlesProviderConnectionError(None, 'Failed to extract movies from data at {!r}'.format(xml_url))

        self._total = nb_provider
        self._movies.extend(movies)

        if len(self._movies) != nb_so_far:
            log.warning('Provider told us it returned {nb_so_far} movies. '
                        'Yet we only extracted {nb_local} movies.'.format(
                nb_so_far=nb_so_far, nb_local=len(movies)))

        return movies

    def search_more_subtitles(self, movie):
        if movie.get_nb_subs_available() == movie.get_nb_subs_total():
            return None
        xml_url = 'http://www.opensubtitles.org{provider_link}/offset-{offset}/xml'.format(
            provider_link=movie.get_provider_link(),
            offset=movie.get_nb_subs_available())

        xml_contents = self._fetch_url(xml_url)
        if xml_contents is None:
            raise OpenSubtitlesProviderConnectionError(None, 'Failed to fetch url {url}'.format(url=xml_url))

        subtitles, nb_so_far, nb_provider = self._xml_to_subtitles(xml_contents)
        if subtitles is None:
            raise OpenSubtitlesProviderConnectionError(None, 'Failed to load subtitles from xml at {!r}'.format(xml_url))

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
            except (AttributeError, IndexError, ValueError) as e:
                log.warning('subtitle_entry={}'.format(subtitle_entry.toxml()))
                log.warning('XML entry has invalid format: {} {}'.format(type(e), e.args))

        return movies, nb_so_far, nb_provider

    @staticmethod
    def cleanup_string(name, alt='_'):
        valid = string.ascii_letters + string.digits
        name = name.strip()
        return ''.join(c if c in valid else alt for c in name)

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
                # subtitle_id = subtitle_id_entry.firstChild.data
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
                subtitle_file_size = int(subtitle_entry.getElementsByTagName('SubSize')[0].firstChild.data)

                # download_count = int(try_get_first_child_data('SubDownloadsCnt', -1))
                # subtitle_movie_aka = try_get_first_child_data('SubMovieAka', None)

                # subtitle_comments = int(try_get_first_child_data('SubComments', -1))
                # subtitle_total = int(try_get_first_child_data('TotalSubs', -1)) #PRESENT?
                # subtitle_newest = try_get_first_child_data('Newest', None) #PRESENT?

                language = Language.from_xx(language_iso639)

                movie_release_name = try_get_first_child_data('MovieReleaseName', None)
                if movie_release_name is None:
                    movie_release_name = try_get_first_child_data('MovieName', None)

                if movie_release_name is None:
                    log.warning('Skipping subtitle: no movie release name or movie name')
                    continue

                movie_release_name = self.cleanup_string(movie_release_name)

                filename = '{}.{}'.format(movie_release_name, subtitle_format)

                download_link = None  # 'https://www.opensubtitles.org/en/subtitleserve/sub/{}'.format(subtitle_id)
                if user_nickname:
                    uploader = user_nickname
                elif user_id != 0:
                    uploader = str(user_id)
                else:
                    uploader = None
                subtitle = OpenSubtitlesSubtitleFile(filename=filename, file_size=subtitle_file_size,
                                                     md5_hash=subtitle_uuid, id_online=subtitlefile_id,
                                                     download_link=download_link, link=subtitle_link, uploader=uploader,
                                                     language=language, rating=subtitle_rating, date=subtitle_add_date)
                subtitles.append(subtitle)
            except (AttributeError, IndexError, ValueError) as e:
                log.warning('subtitle_entry={}'.format(subtitle_entry.toxml()))
                log.warning('XML entry has invalid format: {} {}'.format(type(e), e.args))

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
        except (AttributeError, ValueError, xml.parsers.expat.ExpatError) as e:
            log.debug('... extraction FAILED (xml error): {} {}'.format(type(e), e.args))
            nb_so_far = None
            entries = None
        return entries, nb_so_far, nb_total

    @staticmethod
    def _fetch_url(url):
        try:
            log.debug('Fetching data from {}...'.format(url))
            page = urlopen(url).read()
            log.debug('... SUCCESS')
        except HTTPError as e:
            log.debug('... FAILED: {} {}'.format(type(e), e.args))
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

    @staticmethod
    def key_types():
        return {
            'username': ProviderSettingsType.String,
            'password': ProviderSettingsType.Password,
        }

    def get_user_agent(self):
        return self._user_agent


class OpenSubtitlesSubtitleFile(RemoteSubtitleFile):
    def __init__(self, filename, file_size, md5_hash, id_online, download_link,
                 link, uploader, language, rating, date):
        RemoteSubtitleFile.__init__(self, filename=filename, file_size=file_size, language=language, md5_hash=md5_hash)
        self._id_online = id_online
        self._download_link = download_link
        self._link = link
        self._uploader = uploader
        self._rating = rating
        self._date = date

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
        if self._download_link is None:
            stream = self._download_service(provider_instance)
        else:
            stream = unzip_stream(self._download_http())
        write_stream(src_file=stream, destination_path=target_path)
        local_sub = LocalSubtitleFile(filepath=target_path)
        return local_sub

    def _download_service(self, provider_instance):
        subs = provider_instance.download_subtitles([self])
        return io.BytesIO(subs[0])

    def _download_http(self):
        sub_stream = urlopen(self._download_link)
        return sub_stream


providers = OpenSubtitles,
