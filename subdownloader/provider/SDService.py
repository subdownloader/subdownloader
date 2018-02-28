# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3
import xml.parsers
from xml.dom import minidom
import xml.parsers.expat

from subdownloader.movie import RemoteMovie
try:
    from base64 import b64encode
except ImportError:
    from base64 import encodebytes as b64encode

import base64
import datetime
import logging
import re
import threading
import zlib
from http.client import HTTPConnection
from io import BytesIO
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen
from xmlrpc.client import Fault, ProtocolError, ServerProxy, Transport

from subdownloader.languages.language import Language, NotALanguageException, UnknownLanguage
from subdownloader.project import PROJECT_TITLE, PROJECT_VERSION_STR
from subdownloader.provider import window_iterator
from subdownloader.subtitle2 import RemoteSubtitleFile
from subdownloader.util import unzip_stream, unzip_bytes
from subdownloader.identification import VideoIdentity, EpisodeIdentity, ImdbIdentity, ProviderIdentities


log = logging.getLogger("subdownloader.provider.SDService")

DEFAULT_OSDB_SERVER = "http://api.opensubtitles.org/xml-rpc"
TEST_URL = 'http://www.google.com'
USER_AGENT = "%s %s" % (PROJECT_TITLE, PROJECT_VERSION_STR)
CON_TIMEOUT = 300


def test_connection(url, timeout=CON_TIMEOUT):
    defTimeOut = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    connectable = False
    try:
        urlopen(url)
        log.debug("successfully tested connection")
        connectable = True
    except HTTPError as e:
        log.error(
            'The server couldn\'t fulfill the request. Error code: ' % e.code)
    except URLError as e:
        log.error('We failed to reach a server. Reason: %s ' % e.reason)
    except socket.error as e:
        (value, message) = e.args
        log.error("Could not open socket: %s" % message)
    except socket.sslerror as e:
        (value, message) = e.args
        log.error("Could not open ssl socket: %s" % message)
    socket.setdefaulttimeout(defTimeOut)
    return connectable


# FIXME: move to provider.
class ProviderConnectionError(Exception):
    def __init__(self, code, reason):
        Exception.__init__(self)
        self._code = code
        self._reason = reason

    def __str__(self):
        return 'code={code}; reason={reason}'.format(reason=self._reason, code=self._code)


class TimeoutFunctionException(Exception):

    """Exception to raise on a timeout"""
    pass


class TimeoutFunction:

    def __init__(self, function, timeout=CON_TIMEOUT):
        self.log = logging.getLogger("subdownloader.SDService.TimeoutFunction")
        self.timeout = timeout
        self.function = function

    def handle_timeout(self):
        self.log.debug("exception in timeouted function %s" % self.function)
        raise TimeoutFunctionException()

    def __call__(self, *args):
        #old = signal.alarm(signal.SIGALRM, self.handle_timeout)
        # signal.alarm(self.timeout)
        t = threading.Timer(self.timeout, self.handle_timeout)
        try:
            t.start()
            result = self.function(*args)
        except Exception as e:
            self.log.exception("exception in TimeoutFunction.__call__(*args)")
            raise
        finally:
            #signal.signal(signal.SIGALRM, old)
            t.cancel()
            pass
        # signal.alarm(0)
        del t
        return result

"""The XMLRPC can use a Proxy, this class is need for that."""


# FIXME: Proxied connection not working!
class ProxiedTransport(Transport):

    """ Used for proxied connections to the XMLRPC server
    """

    def __init__(self):
        self.log = logging.getLogger(
            "subdownloader.OSDBServer.ProxiedTransport")
        # annoying -> AttributeError: Main instance has no attribute
        # '_use_datetime'
        self._use_datetime = True

    def set_proxy(self, proxy):
        self.proxy = proxy
        self.log.debug("Proxy set to: {}".format(proxy))

    def make_connection(self, host):
        self.log.debug("Connecting to {} through {}".format(host, self.proxy))
        self.realhost = host
        h = HTTPConnection(self.proxy)
        return h

    def send_request(self, connection, handler, request_body, debug=False):
        connection.putrequest("POST", 'http://%s%s' % (self.realhost, handler))

    def send_host(self, connection, host):
        connection.putheader('Host', self.realhost)


# FIXME: throw ConnectionError if not connected
class SDService(object):

    """
    Contains the class that represents the OSDB RPC Server.
    Encapsules all the XMLRPC methods.

    Consult the OSDB API methods at http://trac.opensubtitles.org/projects/opensubtitles/wiki/XMLRPC

    If it fails to connect directly to the XMLRPC server, it will try to do so through a default proxy.
    Default proxy uses a form to set which URL to open. We will try to change this in later stage.
    """

    def __init__(self, server=None, proxy=None):
        self.log = logging.getLogger("subdownloader.SDService.SDService")
        self.log.debug(
            "Creating Server with server = %s and proxy = %r" % (server, proxy))
        self.timeout = 30
        self.user_agent = USER_AGENT
        self.language = ''

        if server:
            self.server = server
        else:
            self.server = DEFAULT_OSDB_SERVER

        self.proxy = proxy
        self.logged_as = None
        self._xmlrpc_server = None
        self._token = None

    def connected(self):
        return self._token is not None

    def connect(self):
        server = self.server
        proxy = self.proxy
        self.log.debug("connect()... to server %s with proxy %s" % (server, proxy))

        connect_res = False
        try:
            self.log.debug(
                "Connecting with parameters (%r, %r)" % (server, proxy))
            connect = TimeoutFunction(self._connect)
            connect_res = connect(server, proxy)
        except TimeoutFunctionException as e:
            self.log.error("Connection timed out. Maybe you need a proxy.")
            raise
        except:
            self.log.exception("connect: Unexpected error")
            raise
        finally:
            self.log.debug("connection connected %s" % connect_res)
            return connect_res

    def _connect(self, server, proxy):
        try:
            if proxy:
                self.log.debug("Trying proxied connection... ({})".format(proxy))
                self.proxied_transport = ProxiedTransport()
                self.proxied_transport.set_proxy(proxy)
                self._xmlrpc_server = ServerProxy(
                    server, transport=self.proxied_transport, allow_none=True)
                # self.ServerInfo()
                self.log.debug("...connected")
                return True

            elif test_connection(TEST_URL):
                self.log.debug("Trying direct connection...")
                self._xmlrpc_server = ServerProxy(
                    server, allow_none=True)
                # self.ServerInfo()
                self.log.debug("...connected")
                return True
            else:
                self.log.debug("...failed")
                self.log.error("Unable to connect. Try setting a proxy.")
                return False
        except ProtocolError as e:
            self._connection_failed()
            self.log.debug("error in HTTP/HTTPS transport layer")
            raise
        except Fault as e:
            self.log.debug("error in xml-rpc server")
            raise
        except:
            self.log.exception("Connection to the server failed/other error")
            raise

    def logged_in(self):
        return self._token is not None

    def login(self, username="", password=""):
        try:
            login = TimeoutFunction(self._login)
            return login(username, password)
        except TimeoutFunctionException:
            self.log.error("login timed out")
        except:
            self.log.exception("login: other issue")
            raise

    def _login(self, username="", password=""):
        """Login to the Server using username/password,
        empty parameters means an anonymously login
        Returns True if login sucessful, and False if not.
        """
        self.log.debug("----------------")
        self.log.debug("Logging in (username: %s)..." % username)

        def run_query():
            return self._xmlrpc_server.LogIn(
                username, password, self.language, self.user_agent)

        info = self._safe_exec(run_query, None)
        if info is None:
            self._token = None
            return False

        self.log.debug("Login ended in %s with status: %s" %
                       (info['seconds'], info['status']))

        if info['status'] == "200 OK":
            self.log.debug("Session ID: %s" % info['token'])
            self.log.debug("----------------")
            self._token = info['token']
            return True
        else:
            # force token reset
            self.log.debug("----------------")
            self._token = None
            return False

    def logout(self):
        try:
            logout = TimeoutFunction(self._logout)
            result = logout()
            self._token = None
            return result
        except TimeoutFunctionException:
            self.log.error("logout timed out")

    def _logout(self):
        """Logout from current session(token)
        This functions doesn't return any boolean value, since it can 'fail' for anonymous logins
        """
        self.log.debug("Logging out from session ID: %s" % self._token)
        try:
            info = self._xmlrpc_server.LogOut(self._token)
            self.log.debug("Logout ended in %s with status: %s" %
                           (info['seconds'], info['status']))
        except ProtocolError as e:
            self.log.debug("error in HTTP/HTTPS transport layer")
            raise
        except Fault as e:
            self.log.debug("error in xml-rpc server")
            raise
        except:
            self.log.exception("Connection to the server failed/other error")
            raise
        finally:
            # force token reset
            self._token = None

    STATUS_CODE_RE = re.compile('(\d+) (.+)')

    @classmethod
    def check_result(cls, data):
        log.debug('check_result(<data>)')
        if data is None:
            log.warning('data is None ==> FAIL')
            raise ProviderConnectionError(None, 'No message')
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
                raise ProviderConnectionError(None, 'Server returned status="{status}". Expected "200 OK".'.format(
                    status=data['status']))
            log.debug('... SUCCESS')
            code, message = 200, 'OK'
        log.debug('Checking code={code} ...'.format(code=code))
        if code != 200:
            log.debug('... FAIL. Raising ProviderConnectionError.')
            raise ProviderConnectionError(code, message)
        log.debug('... SUCCESS.')
        log.debug('check_result() finished (data is ok)')

    @classmethod
    def name(cls):
        return "opensubtitles"

    def _signal_connection_failed(self):
        # FIXME: set flag/... to signal users that the connection has failed
        pass

    def _safe_exec(self, query, default):
        try:
            result = query()
            return result
        except (ProtocolError, xml.parsers.expat.ExpatError):
            self._signal_connection_failed()
            log.debug("Query failed", exc_info=True)
            return default

    @staticmethod
    def _languages_to_str(languages):
        if languages:
            lang_str = ','.join([language.xxx() for language in languages])
        else:
            lang_str = 'all'

        return lang_str

    def imdb_query(self, query):
        if not self.connected():
            return None

        def run_query():
            return self._xmlrpc_server.SearchMoviesOnIMDB(self._token, query)

        result = self._safe_exec(run_query, None)
        if result is None:
            return None

        provider_identities = []
        for imdb_data in result['data']:
            imdb_identity = ImdbIdentity(imdb_id=imdb_data['id'], imdb_rating=None)
            video_identity = VideoIdentity(name=imdb_data['title'], year=None)
            provider_identities.append(ProviderIdentities(
                video_identity=video_identity, imdb_identity=imdb_identity,
                provider=self))

        return provider_identities

    SEARCH_LIMIT = 500

    def search_text(self, text, languages=None):
        lang_str = self._languages_to_str(languages)
        query = {
            'sublanguageid': lang_str,
            'query': str(text),
        }
        queries = [query]

        def run_query():
            return self._xmlrpc_server.SearchSubtitles(self._token, queries, {'limit': self.SEARCH_LIMIT})
        self._safe_exec(run_query, None)

    def search_videos(self, videos, callback, languages=None):
        if not self.connected():
            return None

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
                return self._xmlrpc_server.SearchSubtitles(self._token, queries, {'limit': self.SEARCH_LIMIT})
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
                    remote_subtitle = OpenSubtitles_SubtitleFile(
                        filename=remote_filename,
                        file_size=remote_file_size ,
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

    def _video_info_to_identification(self, video_info):
        name = video_info['MovieName']
        year = int(video_info['MovieYear'])
        imdb_id = video_info['MovieImdbID']

        video_identity = VideoIdentity(name=name, year=year)
        imdb_identity = ImdbIdentity(imdb_id=imdb_id, imdb_rating=None)
        episode_identity = None

        movie_kind = video_info['MovieKind']
        if movie_kind == 'episode':
            season = int(video_info['SeriesSeason'])
            episode = int(video_info['SeriesEpisode'])
            episode_identity = EpisodeIdentity(season=season, episode=episode)
        elif movie_kind == 'movie':
            pass
        else:
            log.warning('Unknown MoviesKind="{}"'.format(video_info['MovieKind']))

        return ProviderIdentities(video_identity=video_identity, episode_identity=episode_identity,
                                  imdb_identity=imdb_identity, provider=self)

    def identify_videos(self, videos):
        if not self.connected():
            return
        for part_videos in window_iterator(videos, 200):
            hashes = [video.get_osdb_hash() for video in part_videos]
            hash_video = {hash: video for hash, video in zip(hashes, part_videos)}

            def run_query():
                return self._xmlrpc_server.CheckMovieHash2(self._token, hashes)
            result = self._safe_exec(run_query, None)
            self.check_result(result)

            for video_hash, video_info in result['data'].items():
                identification = self._video_info_to_identification(video_info[0])
                video = hash_video[video_hash]
                video.add_identity(identification)

    def download_subtitles(self, os_rsubs):
        if not self.connected():
            return None

        window_size = 20
        map_id_data = {}
        for window_i, os_rsub_window in enumerate(window_iterator(os_rsubs, window_size)):
            query = [subtitle.get_id_online() for subtitle in os_rsub_window]

            def run_query():
                return self._xmlrpc_server.DownloadSubtitles(self._token, query)
            result = self._safe_exec(run_query, None)

            self.check_result(result)
            map_id_data.update({item['idsubtitlefile']: item['data'] for item in result['data']})
        subtitles = [unzip_bytes(base64.b64decode(map_id_data[os_rsub.get_id_online()])).read() for os_rsub in os_rsubs]
        return subtitles

    def can_upload_subtitles(self, local_movie):
        if not self.connected():
            return False

        query = {}

        for i, (video, subtitle) in enumerate(local_movie.iter_video_subtitle()):
            # sub_bytes = open(subtitle.get_filepath(), mode='rb').read()
            # sub_tx_data = b64encode(zlib.compress(sub_bytes))
            cd = "cd{i}".format(i=i+1)

            cd_data = {
                'subhash': subtitle.get_md5_hash(),
                'subfilename': subtitle.get_filename(),
                'moviehash': video.get_osdb_hash(),
                'moviebytesize': str(video.get_size()),
                'movietimems': str(video.get_time_ms()),
                'moviefps': video.get_fps(),
                'movieframes': str(video.get_framecount()),
                'moviefilename': video.get_filename(),
            }

            query[cd] = cd_data

        def run_query():
            return self._xmlrpc_server.TryUploadSubtitles(self._token, query)
        result = self._safe_exec(run_query, None)

        self.check_result(result)

        movie_already_in_db = int(result['alreadyindb']) != 0
        if movie_already_in_db:
            return False
        return True

    def upload_subtitles(self, local_movie):
        query = {
            'baseinfo': {
                'idmovieimdb': local_movie.get_imdb_id(),
                'moviereleasename': local_movie.get_release_name(),
                'movieaka': local_movie.get_movie_name(),
                'sublanguageid': local_movie.get_language().xxx(),
                'subauthorcomment': local_movie.get_comments(),
            },
        }
        if local_movie.is_hearing_impaired() is not None:
            query['hearingimpaired'] = local_movie.is_hearing_impaired()
        if local_movie.is_high_definition() is not None:
            query['highdefinition'] = local_movie.is_high_definition()
        if local_movie.is_automatic_translation() is not None:
            query['automatictranslation'] = local_movie.is_automatic_translation()
        if local_movie.get_subtitle_author() is not None:
            query['subtranslator'] = local_movie.get_subtitle_author()
        if local_movie.is_foreign_only() is not None:
            query['foreignpartsonly'] = local_movie.is_foreign_only()

        for i, (video, subtitle) in enumerate(local_movie.iter_video_subtitle()):
            sub_bytes = subtitle.get_filepath().open(mode='rb').read()
            sub_tx_data = b64encode(zlib.compress(sub_bytes))
            cd = "cd{i}".format(i=i+1)

            cd_data = {
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

            query[cd] = cd_data

        def run_query():
            return self._xmlrpc_server.UploadSubtitles(self._token, query)
        result = self._safe_exec(run_query, None)
        self.check_result(result)

        # absolute_url = result['data']


class OpenSubtitles_SubtitleFile(RemoteSubtitleFile):
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
        return SDService

    def download(self, provider_instance, callback):
        # method 1:
        subs = provider_instance.download_subtitles([self])
        return BytesIO(subs[0])

    def download_web(self):
        # method 2:
        zip_stream = urlopen(self._download_link)
        sub_stream = unzip_stream(zip_stream)
        return sub_stream


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
        if movies is None:
            return False

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
            # log.debug('Data mismatch: Partial search of subtitles told us movie has {nb_partial} subtitles '
            #             'but index told us it has {nb_index} subtitles.'.format(
            #     nb_partial=nb_total, nb_index=movie.get_nb_subs_total()))
            return None  # Detect series
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

                imdb_identity = ImdbIdentity(imdb_id=movie_imdb_id, imdb_rating=movie_imdb_rating)
                video_identity = VideoIdentity(name=movie_name, year=movie_year)
                identities = ProviderIdentities(video_identity=video_identity, imdb_identity=imdb_identity, provider=self)

                movie = RemoteMovie(
                    subtitles_nb_total=subs_total,
                    provider_link=movie_id_link, provider_id=movie_id,
                    identities = identities
                )

                movies.append(movie)
            except (AttributeError, IndexError, ValueError):
                log.warning('subtitle_entry={}'.format(subtitle_entry.toxml()))
                log.warning('XML entry has invalid format.', exc_info=True)

        # if len(movies) != nb_provider:
        #     log.warning('Provider told us it returned {nb_provider} movies. '
        #                 'Yet we only extracted {nb_local} movies.'.format(
        #         nb_provider=nb_provider, nb_local=len(movies)))
        return movies, nb_provider_total

    def extract_subtitle_entries(self, raw_xml):
        nb = 0
        nb_total = 0
        entries = []
        log.debug('extract_subtitle_entries() ...')
        try:
            dom = minidom.parseString(raw_xml)
            opensubtitles_entries = dom.getElementsByTagName('opensubtitles')
            for opensubtitles_entry in opensubtitles_entries:
                results_entries = opensubtitles_entry.getElementsByTagName('results')
                for results_entry in results_entries:
                    try:
                        nb = int(results_entry.getAttribute('items'))
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
            nb = None
            nb_total = None
            entries = None
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

        # if len(subtitles) != nb_provider:
        #     log.warning('Provider told us it returned {nb_provider} subtitles. '
        #                 'Yet we only extracted {nb_local} subtitles.'.format(
        #         nb_provider=nb_provider, nb_local=len(subtitles)))
        return subtitles, nb_provider_total


providers = (SDService, )
