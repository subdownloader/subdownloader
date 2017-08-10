# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import base64
import datetime
from io import BytesIO
import logging
import re

from subdownloader.compat import CannotSendRequest, ProtocolError, ServerProxy, SocketError, urlopen
from subdownloader.languages.language import Language, NotALanguageException, UnknownLanguage
from subdownloader.identification import ImdbIdentity, ProviderIdentities
from subdownloader.provider import window_iterator
from subdownloader.provider.provider import ProviderConnectionError, ProviderNotConnectedError, \
    ProviderSettings, SubtitleProvider
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

    def _download(self, provider_instance, callback):
        # method 1:
        subs = provider_instance.download_subtitles([self])
        return BytesIO(subs[0])

    def _download_web(self):
        # method 2:
        # FIXME: try/except => throw ProviderConnectionError
        zip_stream = urlopen(self._download_link)
        sub_stream = unzip_stream(zip_stream)
        return sub_stream

providers = (OpenSubtitles, )
