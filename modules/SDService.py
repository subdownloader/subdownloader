#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) 2007 Ivan Garcia capiscuas@gmail.com
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    see <http://www.gnu.org/licenses/>.

from xmlrpclib import Transport,ServerProxy,ProtocolError
import base64, httplib, os
import StringIO, gzip, zlib
import logging
import threading, thread
log = logging.getLogger("subdownloader.WebService")
    
from modules import APP_TITLE, APP_VERSION
import modules.videofile as videofile
import modules.subtitlefile as subtitlefile
from FileManagement import Subtitle

DEFAULT_OSDB_SERVER = "http://api.opensubtitles.org/xml-rpc"
DEFAULT_SDDB_SERVER = "http://sddb.subdownloader.net/xmlrpc/"
DEFAULT_PROXY = 'http://w2.hidemyass.com/'
USER_AGENT = "%s %s"% (APP_TITLE, APP_VERSION)

def test_connection(url, timeout=15):
    import socket, urllib2
    defTimeOut=socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    connectable=True
    try:
        urllib2.urlopen(url)
    except (urllib2.HTTPError, urllib2.URLError, socket.error, socket.sslerror):
        connectable=False
    socket.setdefaulttimeout(defTimeOut)
    return connectable

class TimeoutFunctionException(Exception): 
    """Exception to raise on a timeout""" 
    pass 

class TimeoutFunction: 

    def __init__(self, function, timeout=30): 
        self.timeout = timeout 
        self.function = function 

    def handle_timeout(self): 
        raise TimeoutFunctionException()

    def __call__(self, *args): 
        #old = signal.alarm(signal.SIGALRM, self.handle_timeout) 
        #signal.alarm(self.timeout) 
        t = threading.Timer(self.timeout, self.handle_timeout)
        try: 
            t.start()
            result = self.function(*args)
        finally: 
            #signal.signal(signal.SIGALRM, old)
            t.cancel()
            pass
        #signal.alarm(0)
        del t
        return result 
    
"""The XMLRPC can use a Proxy, this class is need for that."""
class ProxiedTransport(Transport):
    """ Used for proxied connections to the XMLRPC server
    """
    def __init__(self):
        #self.log = logging.getLogger("subdownloader.OSDBServer.ProxiedTransport")
        self._use_datetime = True # annoying -> AttributeError: Main instance has no attribute '_use_datetime'
    def set_proxy(self, proxy):
        self.proxy = proxy
        #self.log.debug("Proxy set to: %s"% proxy)
    def make_connection(self, host):
        #self.log.debug("Connecting to %s through %s"% (host, self.proxy))
        self.realhost = host
        h = httplib.HTTP(self.proxy)
        return h
    def send_request(self, connection, handler, request_body):
        connection.putrequest("POST", 'http://%s%s' % (self.realhost, handler))
    def send_host(self, connection, host):
        connection.putheader('Host', self.realhost)


class SDService(object):
    """
    Contains the class that represents the OSDB and SDDB RPC Servers.
    Encapsules all the XMLRPC methods.
    
    Consult the OSDB API methods at http://trac.opensubtitles.org/projects/opensubtitles/wiki/XMLRPC
    Consult the SDDB API methods at https://sddb.subdownloader.net/xmlrpc/
    
    If it fails to connect directly to the XMLRPC server, it will try to do so through a default proxy.
    Default proxy uses a form to set which URL to open. We will try to change this in later stage.
    """
    def __init__(self, type, server = None, proxy = None ):
        self.log = logging.getLogger("subdownloader.SDService.SDService")
        self.log.debug("Creating Server with server = %s and proxy = %r" %(server, proxy))
        self.timeout = 30
        self.user_agent = USER_AGENT
        self.language = ''
        self.type = type

        if server: 
                self.server = server
        else:
                if self.type == 'osdb':
                    self.server = DEFAULT_OSDB_SERVER
                else:
                    self.server = DEFAULT_SDDB_SERVER
                
        self.proxy = proxy
        self.logged_as = None
        self.xmlrpc_server = None
        self._token = None
        #Let's connect with the server XMLRPC
        #OSConnection.__init__(self)
        try:
            self.create_xmlrpcserver(self.server, self.proxy)
        except Exception, e:
            raise e
            
    def create_xmlrpcserver(self, server, proxy):
        self.log.debug("Creating XMLRPC server connection...")
        try:
            return self.connect(server, proxy)
        except Exception, e:
            raise e
        
    def connect(self, server, proxy):
        try:
            self.log.debug("Connecting with parameters (%r, %r)" %(server, proxy))
            connect = TimeoutFunction(self._connect)
            return connect(server, proxy)
        except TimeoutFunctionException, e:
            self.log.error("Connection timed out. Maybe you need a proxy.")
            raise e
        #except Exception, e:
            #import sys
            #self.log.error("Unexpected error: %s", sys.exc_info())

    def _connect(self, server, proxy):
        try:
            if proxy:
                self.log.debug("Trying proxied connection... (%r)"% proxy)
                self.proxied_transport = ProxiedTransport()
                self.proxied_transport.set_proxy(proxy)
                self.xmlrpc_server = ServerProxy(server, transport=self.proxied_transport, allow_none=True)
                #self.ServerInfo()
                self.log.debug("...connected")
                return True
                
            elif test_connection(server):
                    self.log.debug("Trying direct connection...")
                    self.xmlrpc_server = ServerProxy(server, allow_none=True)
                    #self.ServerInfo()
                    self.log.debug("...connected")
                    return True
            else:
                self.log.debug("...failed")
                self.log.error("Unable to connect. Try setting a proxy.")
                return False
        except Exception,e:
                    self.log.debug("Connection to the server failed")
                    raise e
        
    def is_connected(self):
        """ 
        This method checks to see whether we are connected to the server. 
        It does not return any information about the validity of the 
        connection.
        """
        return self._token != None
        
    def ServerInfo(self):
        ServerInfo = TimeoutFunction(self._ServerInfo)
        try:
            a = ServerInfo()
            return a
        except TimeoutFunctionException:
            self.log.error("ServerInfo timed out")
            
        except Exception, e:
            #print type(e)     # the exception instance
            #print e.args      # arguments stored in .args
            #print e           # __str__ allows args to printed directly
            self.log.error("ServerInfo error connection.")
            raise e

    """This simple function returns basic server info, 
    it could be used for ping or telling server info to client"""    
    def _ServerInfo(self):
        try: 
            return self.xmlrpc_server.ServerInfo()
        except TimeoutFunctionException:
            raise
            
    def login(self, username="", password=""):
        login = TimeoutFunction(self._login)
        try:
            return login(username, password)
        except TimeoutFunctionException:
            self.log.error("login timed out")
        
    def _login(self, username="", password=""):
        """Login to the Server using username/password,
        empty parameters means an anonymously login
        Returns True if login sucessful, and False if not.
        """ 
        self.log.debug("----------------")
        self.log.debug("Logging in (username: %s)..."% username)
        info = self.xmlrpc_server.LogIn(username, password, self.language, self.user_agent)
        self.log.debug("Login ended in %s with status: %s"% (info['seconds'], info['status']))
        if info['status'] == "200 OK":
            self.log.debug("Session ID: %s"% info['token'])
            self.log.debug("----------------")
            self._token = info['token']
            return True
        else:
            # force token reset
            self.log.debug("----------------")
            self._token = None
            return False
        
    def logout(self):
        logout = TimeoutFunction(self._logout)
        try:
            return logout()
        except TimeoutFunctionException:
            self.log.error("logout timed out")
        
    def _logout(self):
        """Logout from current session(token)
        This functions doesn't return any boolean value, since it can 'fail' for anonymous logins
        """
        self.log.debug("Logging out from session ID: %s"% self._token)
        info = self.xmlrpc_server.LogOut(self._token)
        self.log.debug("Logout ended in %s with status: %s"% (info['seconds'], info['status']))
        # force token reset
        self._token = None
        
        
    #
    # SUBTITLE METHODS 
    #
    def GetSubLanguages(self, language):
        GetSubLanguages = TimeoutFunction(self._GetSubLanguages)
        try:
            return GetSubLanguages(language)
        except TimeoutFunctionException:
            self.log.error("GetSubLanguages timed out")
            
    def _GetSubLanguages(self, language):
        """Return all suported subtitles languages in a dictionary
        If language var is set, returns SubLanguageID for it
        """
        self.log.debug("----------------")
        self.log.debug("GetSubLanguages RPC method starting...")
        if language == "all":
            # return result right away if no 'translation' needed
            return "all"
        info = self.xmlrpc_server.GetSubLanguages(language)
        self.log.debug("GetSubLanguages complete in %s"% info['seconds'])
            
        if language:
            for lang in info['data']:
                if lang['ISO639'] == language: return lang['SubLanguageID']
                
        return info['data']
        
    def CheckSubHash(self, hashes):
        CheckSubHash = TimeoutFunction(self._CheckSubHash)
        try:
            return CheckSubHash(hashes)
        except TimeoutFunctionException:
            self.log.error("CheckSubHash timed out")
        
    def _CheckSubHash(self, hashes):
        """
        @hashes = list of subtitle hashes or video object
        returns: dictionary like { hash: subID }
        This method returns !IDSubtitleFile, if Subtitle Hash exists. If not exists, it returns '0'.
        """
        self.log.debug("----------------")
        self.log.debug("CheckSubHash RPC method starting...")
        if isinstance(hashes, videofile.VideoFile):
            self.log.debug("Video object parameter detected. Extracting hashes...")
            video = hashes
            hashes = []
            for sub in video.getSubtitles():
                hashes.append(sub.getHash())
            self.log.debug("...done")
        info = self.xmlrpc_server.CheckSubHash(self._token,hashes)
        self.log.debug("CheckSubHash ended in %s with status: %s"% (info['seconds'], info['status']))
        result = {}
        for hash in hashes:
            result[hash] = info['data'][hash]
#        for data in info['data']:
#            result[data.key()] = data.value()
        return result
    
    def DownloadSubtitles(self, subtitles):
        DownloadSubtitles = TimeoutFunction(self._DownloadSubtitles)
        try:
            return DownloadSubtitles(subtitles)
        except TimeoutFunctionException:
            self.log.error("DownloadSubtitles timed out")
    
    def _DownloadSubtitles(self, subtitles):
        #TODO: decide wheter this should save the subtitle (as it does atm) or just return the encoded data
        #Note ivan: in my GUI before I replace the file I'll show a confirmation code
        """
        Download subtitles by there id's
        
        @subtitles: dictionary with subtitle id's and their path - { id: "path_to_save", ...}
        Returns: BASE64 encoded gzipped !IDSubtitleFile(s). You need to BASE64 decode and ungzip 'data' to get its contents.
        """
        self.log.debug("----------------")
        self.log.debug("DownloadSubtitles RPC method starting...")
        
        subtitles_to_download = subtitles
        self.log.debug("Acting in: %r"% subtitles)
        
        if len(subtitles_to_download):
            self.log.debug("Communicating with server...")
            self.log.debug("xmlrpc_server.DownloadSubtitles(%s,%r)" %(self._token, subtitles_to_download.keys()))
            answer = self.xmlrpc_server.DownloadSubtitles(self._token, subtitles_to_download.keys())
            self.log.debug("DownloadSubtitles finished in %s with status %s."% (answer['seconds'], answer['status']))
            
            if answer.has_key("data"):
                if answer['data'] == False:  #TODO support passing the reason of the erorr to be shown in the GUI
                    self.log.info("Error downloading subtitle.")
                    return False
                self.log.debug("Got %i subtitles from server. Uncompressing data..."% len(answer['data']))
                for sub in answer['data']:
                    #self.log.info("%s -> %s"% (subtitles_to_download[sub['idsubtitlefile']]['subtitle_path'], subtitles_to_download[sub['idsubtitlefile']]['video'].getFileName()))
                    self.BaseToFile(sub['data'], subtitles_to_download[sub['idsubtitlefile']])
                return answer['data']
            else:
                self.log.info("Server sent no subtitles to me.")
                return False
        
    def SearchSubtitles(self, language="all", videos=None, imdb_ids=None):
        SearchSubtitles = TimeoutFunction(self._SearchSubtitles)
        try:
            return SearchSubtitles (language, videos, imdb_ids)
        except TimeoutFunctionException:
            self.log.error("SearchSubtitles timed out")
            return None
        except ProtocolError:
            self.log.error("Protocol Error on Opensubtitles.com")
            return None
        
    def _SearchSubtitles(self, language="all", videos=None, imdb_ids=None):
        """
        Search subtitles for the given video(s).
        
        @language: language code - string
        @videos: video objects - list
        @imdb_id: IMDB movie id's - list
        Note:Max results is 250. When nothing is found, 'data' is empty.
        """
        self.log.debug("----------------")
        self.log.debug("SearchSubtitles RPC method starting...")
        search_array = []
        if videos:
            self.log.debug("Building search array with video objects info")
            for video in videos:
                array = {'sublanguageid': language,'moviehash': video.getHash(),'moviebytesize': video.getSize()}
                self.log.debug(" - adding: %s"% array)
                search_array.append(array)
        elif imdb_ids:
            self.log.debug("Building search array with IMDB id's")
            for id in imdb_ids:
                array = {'sublanguageid':language,'imdbid': id}
                self.log.debug(" - adding: %s"% array)
                search_array.append(array)
                
        self.log.debug("Communicating with server...")
        if self.type == 'osdb':
            result = self.xmlrpc_server.SearchSubtitles(self._token, search_array)
        else:
            self.xmlrpc_server.SearchSubtitles(search_array)
            return
        
        if result['data'] != False:
            self.log.debug("Collecting downloaded data")
            moviehashes = {}
            for i in result['data']:
                moviehash = i['MovieHash']
                if not moviehashes.has_key(moviehash):
                    moviehashes[moviehash] = []
                moviehashes[moviehash].append(i)
            self.log.debug("Movie hashes: %i"% len(moviehashes.keys()))
            
            if videos:
                videos_result = []
                for video in videos:
                    if moviehashes.has_key(video.getHash()):
                        osdb_info = moviehashes[video.getHash()]
                        subtitles = []
                        self.log.debug("- %s (%s)"% (video.getFileName(), video.getHash()))
                        for i in osdb_info:
                            sub = subtitlefile.SubtitleFile(online=True,id=i["IDSubtitle"])
                            sub.setHash(i["SubHash"])
                            sub.setIdFileOnline(i["IDSubtitleFile"])
                            sub.setFileName(i["SubFileName"])
                            sub.setLanguageXXX(i["SubLanguageID"])  #This method will autogenerate the XX and the LanguageName 
                            #sub.setLanguageXX(i["ISO639"])  
                            #sub.setLanguageName(i["LanguageName"]) 
                            sub.setRating(i["SubRating"])
                            sub.setUploader(i["UserNickName"])
                            sub.setVideo(video)
                            
                            self.log.debug("  [%s] - %s"%  (sub.getLanguage(), sub.getFileName()))
                            subtitles.append(sub)
                            
                        #Let's get the IMDB info which is majority in the subtitles
                        video.setMovieInfo(self.getBestImdbInfo(osdb_info))
                        video.setOsdbInfo(osdb_info)
                        video.setSubtitles(subtitles)
                    videos_result.append(video)
                    
                return videos_result
                
            elif imdb_ids:
                #TODO: search with IMDB id's
                pass
            
        else:
            self.log.info("No subtitles were found on Opensubtitles.com")
            return []
        
        
    def TryUploadSubtitles(self, videos, no_update=False):
        TryUploadSubtitles = TimeoutFunction(self._TryUploadSubtitles)
        try:
            return TryUploadSubtitles(videos, no_update)
        except TimeoutFunctionException:
            self.log.error("TryUploadSubtitles timed out")
        
    def _TryUploadSubtitles(self, videos, no_update):
        """Check for subtitle existence in server database for one or more videos
        
        @videos: video objects - list
        Returns subtitle info in server if exists, and full info on movie if not.
        """
        self.log.debug("----------------")
        self.log.debug("TryUploadSubtitles RPC method starting...")
        # will run this method if we have videos and subtitles associated
        array = {}
        self.log.debug("Building search array...")
        for (i, video) in enumerate(videos):
            if video.getTotalLocalSubtitles() > 0:
                cd = 'cd%i'% (i+1)
                subtitle = video.getSubtitles()[0]
                array_ = {'subhash': subtitle.getHash(), 'subfilename': subtitle.getFileName(), 'moviehash': video.getHash(), 'moviebytesize': video.getSize(), 'moviefps': video.getFPS(), 'moviefilename': video.getFileName()}
                self.log.debug(" - adding %s: %s"% (cd, array_))
                array[cd] = array_
            else:
                if video.hasMovieName():
                    self.log.debug("'%s' has no subtitles. Stopping method."% video.getMovieName())
                else:
                    self.log.debug("'%s' has no subtitles. Stopping method."% video.getFileName())
                return False
            
        self.log.debug("Communicating with server...")
        #import pprint
        #print "parameters:"
        #pprint.pprint(array)
        
        #If no_update is 1, then the server won't try to update the hash of the movie for that subtitle, 
        #that is useful if we just want to get online info about the videos and the subtitles
        result = self.xmlrpc_server.TryUploadSubtitles(self._token, array, str(int(no_update)))
        self.log.debug("Search took %ss"% result['seconds'])
       
        #pprint.pprint(result)
#        print result.keys()
        result.pop('seconds')
        
        if result['alreadyindb']:
            self.log.debug("Subtitle already exists in server database")
        else:
            self.log.debug("Subtitle doesn't exist in server database")
        self.log.debug("----------------")
        return result
        
    def UploadSubtitles(self, movie_info):
        UploadSubtitles = TimeoutFunction(self._UploadSubtitles)
        try:
            return UploadSubtitles(movie_info)
        except TimeoutFunctionException:
            self.log.error("UploadSubtitles timed out")
            raise
        
    def _UploadSubtitles(self, movie_info):
        self.log.debug("----------------")
        self.log.debug("UploadSubtitles RPC method starting...")
        self.log.info("Uploading subtitle...")
        self.log.debug("Sending info: %s"% movie_info)
        info = self.xmlrpc_server.UploadSubtitles(self._token, movie_info)
        self.log.debug("Upload finished in %s with status %s."% (info['seconds'], info['status']))
        return info
        self.log.debug("----------------")
        
    def getBestImdbInfo(self, subs ):
            movies_imdb = []
            for sub in subs:
                movies_imdb.append(sub["IDMovieImdb"])
            _best_imdb = {'imdb': None, 'count': 0}
            for imdb in movies_imdb:
                if movies_imdb.count(imdb) > _best_imdb['count']:
                    _best_imdb = {'imdb': imdb, 'count': movies_imdb.count(imdb)}
            best_imdb = _best_imdb['imdb']
            for sub in subs:
                if sub["IDMovieImdb"] == best_imdb:
                    self.log.debug("getBestImdbInfo = %s" % best_imdb)
                    return {"IDMovieImdb":sub["IDMovieImdb"], 
                                    "MovieName":sub["MovieName"], 
                                    "MovieNameEng":sub["MovieNameEng"], 
                                    "MovieYear":sub["MovieYear"], 
                                    "MovieImdbRating":sub["MovieImdbRating"],
                                    "MovieImdbRating":sub["MovieImdbRating"] }
            return {}
                    
        
    #
    # VIDEO METHODS 
    #
        
    def CheckMovieHash(self, hashes):
        CheckMovieHash = TimeoutFunction(self._CheckMovieHash)
        try:
            return CheckMovieHash(hashes)
        except TimeoutFunctionException:
            self.log.error("CheckMovieHash timed out")
        
    def _CheckMovieHash(self, hashes):
        """Return MovieImdbID, MovieName, MovieYear for each hash
        @hashes - movie hashes - list
        """
        self.log.debug("----------------")
        self.log.debug("CheckMovieHash RPC method starting...")
        info = self.xmlrpc_server.CheckMovieHash(self._token, hashes)
        self.log.debug("CheckMovieHash ended in %s. Processing data..."% info['seconds'])
        result = {}
        for hash in hashes:
            result[hash] = info['data'][hash]
        return result
        
    def ReportWrongMovieHash(self, subtitle_id):
        ReportWrongMovieHash = TimeoutFunction(self._ReportWrongMovieHash)
        try:
            return ReportWrongMovieHash(subtitle_id)
        except TimeoutFunctionException:
            self.log.error("ReportWrongMovieHash timed out")
        
    def _ReportWrongMovieHash(self, subtitle_id):
        """Report wrong subtitle for a movie
        @subtitle_id: subtitle id from a video (IDSubMovieFile) - string/int
        """
        self.log.debug("----------------")
        self.log.debug("ReportWrongMovieHash RPC method starting...")
        info = self.xmlrpc_server.ReportWrongMovieHash(self._token, subtitle_id)
        self.log.debug("ReportWrongMovieHash finished in %s with status %s."% (info['seconds'], info['status']))
        
    def GetAvailableTranslations(self, program=None):
        GetAvailableTranslations = TimeoutFunction(self._GetAvailableTranslations)
        try:
            return GetAvailableTranslations(program)
        except TimeoutFunctionException:
            self.log.error("GetAvailableTranslations timed out")
        
    def _GetAvailableTranslations(self, program=None):
        """Returns dictionary of available translations for the given program. 
        @program: program name - string
        return example: {'en': {'LastCreated': '2007-02-03 21:36:14', 'StringsNo': 438}, 'ar': ...}
        """
        self.log.debug("----------------")
        self.log.debug("GetAvailableTranslations RPC method starting...")
        if not program: program = APP_TITLE.lower()
        info = self.xmlrpc_server.GetAvailableTranslations(self._token, program)
        self.log.debug("GetAvailableTranslations finished in %s with status %s."% (info['seconds'], info['status']))
        if info.has_key('data'):
            return info['data']
        return False
        
    def GetTranslation(self, language, format):
        GetTranslation = TimeoutFunction(self._GetTranslation)
        try:
            return GetTranslation(language, format)
        except TimeoutFunctionException:
            self.log.error("GetTranslation timed out")
        
    def _GetTranslation(self, language, format):
        """Returns base64 encoded strings for language.
        @language: iso639 language code (2 chars)
        @format: format in which the result is returned (mo, po, txt, xml)
        """
        self.log.debug("----------------")
        self.log.debug("GetTranslation RPC method starting...")
        info = self.xmlrpc_server.GetTranslation(self._token, language, format, self.user_agent )
        self.log.debug("GetTranslation finished in %s with status %s."% (info['seconds'], info['status']))
        if info.has_key('data'):
            return info['data']
        return False
        
    def SearchMoviesOnIMDB(self, query):
        SearchMoviesOnIMDB = TimeoutFunction(self._SearchMoviesOnIMDB)
        try:
            return SearchMoviesOnIMDB(query)
        except TimeoutFunctionException,  e:
            self.log.error("SearchMoviesOnIMDB timed out")
            raise
        except Exception, e:
            traceback.print_exc(e)
            raise
        
    def _SearchMoviesOnIMDB(self, query):
        """Returns a list of found movies in IMDB
        @query - search string (ie: movie name)
        return example: [{'id': '0452623', 'title': 'Gone Baby Gone (2007)'}, { }, ...]
        """
        self.log.debug("----------------")
        self.log.debug("SearchMoviesOnIMDB RPC method starting...")
        info = self.xmlrpc_server.SearchMoviesOnIMDB(self._token, query)
        self.log.debug("SearchMoviesOnIMDB finished in %s with status %s."% (info['seconds'], info['status']))
        result = []
        for result_ in info['data']:
            result.append(result_)
        return result
        
    def GetIMDBMovieDetails(self, imdb_id):
        GetIMDBMovieDetails = TimeoutFunction(self._GetIMDBMovieDetails)
        try:
            return GetIMDBMovieDetails(imdb_id)
        except TimeoutFunctionException:
            self.log.error("GetIMDBMovieDetails timed out")
            return False
        except Exception, e:
            traceback.print_exc(e)
            return False
        
    def _GetIMDBMovieDetails(self, imdb_id):
        """Returns video details from IMDB if available
        @imdb_id - IMDB movie id - int/string
        """
        self.log.debug("----------------")
        self.log.debug("GetIMDBMovieDetails RPC method starting...")
        info = self.xmlrpc_server.GetIMDBMovieDetails(self._token, imdb_id)
        self.log.debug("GetIMDBMovieDetails finished in %s with status %s."% (info['seconds'], info['status']))
        return info['data']
        
    def CheckSoftwareUpdates(self, app=None):
        CheckSoftwareUpdates = TimeoutFunction(self._CheckSoftwareUpdates)
        try:
            return CheckSoftwareUpdates(app)
        except TimeoutFunctionException:
            self.log.error("CheckSoftwareUpdates timed out")
        
    def _CheckSoftwareUpdates(self, app=None):
        """Returns latest info on the given application if available
        """
        self.log.debug("----------------")
        self.log.debug("CheckSoftwareUpdates RPC method starting...")
        if not app: app = APP_TITLE.lower()
        info = self.xmlrpc_server.CheckSoftwareUpdates(app)

        # we have something to show
        self.log.debug("Latest SubDownloader Version Found: %s"% info['latest_version'])
        return info
        
    def NoOperation(self, token=None):
        NoOperation = TimeoutFunction(self._NoOperation)
        try:
            return NoOperation()
        except TimeoutFunctionException:
            self.log.error("NoOperation timed out")
        
    def _NoOperation(self):
        """This method should be called every 15 minutes after last request to xmlrpc. 
        It's used to keep current session alive.
        Returns True if current session token is valid and False if not.
        """
        self.log.debug("----------------")
        self.log.debug("NoOperation RPC method starting...")
        info = self.xmlrpc_server.NoOperation(self._token)
        self.log.debug("NoOperation finished in %s with status %s."% (info['seconds'], info['status']))
        self.log.debug("----------------")
        if info['status'] != "200 OK":
            return False
        return True
        
    def SearchToMail(self, videos, languages):
        SearchToMail = TimeoutFunction(self._SearchToMail)
        try:
            return SearchToMail(videos, languages)
        except TimeoutFunctionException:
            self.log.error("SearchToMail timed out")
        
    def _SearchToMail(self, videos, languages):
        """Register user email to be noticed when given video subtitles are available to download
        @videos: video objects - list
        @languages: language id codes - list
        """
        self.log.debug("----------------")
        self.log.debug("SearchToMail RPC method starting...")
        video_array = []
        for video in videos:
            array = {'moviehash': video.getHash(), 'moviesize': video.getSize()}
            video_array.append(array)
        info = self.xmlrpc_server.SearchToMail(self._token, languages, video_array)
        self.log.debug("SearchToMail finished in %s with status %s."% (info['seconds'], info['status']))
        
    def BaseToFile(self, base_data, path):
        """This will decode the base64 data and save it as a file with the given path
        """
        compressedstream = base64.decodestring(base_data)
        gzipper = gzip.GzipFile(fileobj=StringIO.StringIO(compressedstream))
        s=gzipper.read()
        gzipper.close()
        subtitle_file = file(path,'wb')
        subtitle_file.write(s)
        subtitle_file.close()
