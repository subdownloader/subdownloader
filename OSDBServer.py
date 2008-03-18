##    Copyright (C) 2007 Ivan Garcia contact@ivangarcia.org
##    This program is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License along
##    with this program; if not, write to the Free Software Foundation, Inc.,
##    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xmlrpclib import Transport,ServerProxy
import base64, StringIO, gzip, httplib, os
import logging

from subdownloader import APP_TITLE, APP_VERSION
import subdownloader.videofile as videofile
import subdownloader.subtitlefile as subtitlefile
from subdownloader.FileManagement import Subtitle

#SERVER_ADDRESS = "http://dev.opensubtitles.org/xml-rpc"
DEFAULT_SERVER = "http://www.opensubtitles.org/xml-rpc"
DEFAULT_PROXY = 'http://w2.hidemyass.com/'
USER_AGENT = "%s %s"% (APP_TITLE, APP_VERSION)

#"""This class is useful to let the server know who we are, good for statistics,
#    so we can separate the traffic from normal Web visitors"""
#class GtkTransport (Transport):
#        user_agent = "Subdownloader " + APP_VERSION 
    

def test_connection(url, timeout=5):
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
    
"""The XMLRPC can use a Proxy, this class is need for that."""
class ProxiedTransport(Transport):
    """ Used for proxied connections to the XMLRPC server
        When
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
        
#class OSTransport(Transport):
#    """Main transport to use to connect to opensubtitles
#    """
    

class OSDBServer(ProxiedTransport):
    """
    Contains the class that represents the OSDB Server.
    Encapsules all the XMLRPC methods.
    
    Consult the API methods at http://code.google.com/p/subdownloader/wiki/XmlRpc_API
    
    If it fails to connect directly to the XMLRPC server, it will try to do so through a default proxy.
    Default proxy uses a form to set which URL to open. We will try to change this in later stage.
    """
    def __init__(self, options):
        self.log = logging.getLogger("subdownloader.OSDBServer.OSDBServer")
        self.log.debug("Creating OSDBServer with options= %s",  options)
        # for proxied connections
        ProxiedTransport.__init__(self)
        self.set_proxy(options.proxy)
        #self.timeout = options.timeout
        self.timeout = 30
        self.user_agent = USER_AGENT
        self.username = options.username
        self.passwd = options.password
        self.language = options.language
        if options.server: 
            self.server = options.server
        else:
            self.server = DEFAULT_SERVER
        self.logged_as = None
        self.xmlrpc_server = None
        self._token = None
        #Let's connect with the server XMLRPC
        if self.create_xmlrpcserver(self.server):
            self.login(self.username, self.passwd)
            #self.logout()
            
    def create_xmlrpcserver(self, server):
        #transport = GtkTransport()
        self.log.debug("Creating XMLRPC server connection...")
#        timeout_transport = TimeoutTransport()
#        timeout_transport.timeout = self.timeout
#        try:
        self.log.debug("Trying direct connection...")
        if test_connection(server):
            self.xmlrpc_server = ServerProxy(server)
            self.log.debug("...connected")
            return True
        else:
            self.log.debug("...failed")
            if self.proxy:
                self.log.debug("Trying proxied connection...")
                #p = ProxiedTransport()
                #p.set_proxy(self.proxy)
                self.xmlrpc_server = ServerProxy(server, transport=self)
                #self.xmlrpc_server.ServerInfo() # this would be the connection tester
                self.log.debug("...connected")
                return True
            else:
                self.log.error("No proxy was set. Unable to connect.")
                return False
        
    def is_connected(self):
        """ 
        This method checks to see whether we are connected to the server. 
        It does not return any information about the validity of the 
        connection.
        """
        return self._token != None
        
    """This simple function returns basic server info, 
    it could be used for ping or telling server info to client"""    
    def ServerInfo(self):
        try: 
            serverinfo = self.xmlrpc_server.ServerInfo()
            text = ""
            for key,value in serverinfo.items():
                text += key + " : " + str(value) + "\n"
            return text
        except Exception,e:
            raise e
        
    def login(self, username="", password=""):
        """Login to the Server using username/password,
        empty parameters means an anonymously login
        Returns True if login sucessful, and False if not.
        """ 
        self.log.debug("----------------")
        self.log.debug("Logging in (username:%r, password:%r)..."% (username, password))
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
        """Return all suported subtitles languages in a dictionary
        If language var is set, returns SubLanguageID for it
        """
        self.log.debug("----------------")
        self.log.debug("GetSubLanguages RPC method starting...")
        if(language == "all"):
            # return result right away if no 'translation' needed
             return "all"
        info = self.xmlrpc_server.GetSubLanguages(language)
        self.log.debug("GetSubLanguages complete in %s"% info['seconds'])
            
        if language:
            for lang in info['data']:
                if lang['ISO639'] == language: return lang['SubLanguageID']
                
        return info['data']
            
    def CheckSubHash(self, hashes):
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
    
    def DownloadSubtitles(self, videos):
        """
        Download subtitles by there id's
        
        @sub_ids: list of subtitle id's
        @dest: path to save subtitles in string format
        Returns: BASE64 encoded gzipped !IDSubtitleFile(s). You need to BASE64 decode and ungzip 'data' to get its contents.
        """
        self.log.debug("----------------")
        self.log.debug("DownloadSubtitles RPC method starting...")
        subtitles_to_download ={}
        self.log.debug("Building subtitle matrix...")
        for video in videos:
            if video.getTotalSubtitles() == 1 and video.getTotalOnlineSubtitles():
                subtitle = video.getOneSubtitle()
                self.log.debug("- adding: %s: %s"% (subtitle.getIdOnline(), subtitle.getFileName()))
                subtitles_to_download[subtitle.getIdOnline()] = {'subtitle_path': os.path.join(video.getFolderPath(), subtitle.getFileName()), 'video': video}
            elif video.getTotalSubtitles() > 1 and video.getTotalOnlineSubtitles():
                #TODO: give user the list of subtitles to choose from
                # set a starting point to compare scores
                best_rated_sub = video.getOnlineSubtitles()[0]
                # iterate over all subtitles
                subpath_list = {}
                for sub in video.getOnlineSubtitles():
                    subpath_list[sub.getIdOnline()] = sub
                    if sub.getRating() > best_rated_sub.getRating():
                        best_rated_sub = sub
                #compare video name with subtitles name to find best match
                sub_match = Subtitle.AutoDetectSubtitle(video.getFilePath(), sub_list=subpath_list.keys())
                if len(sub_match):
                    self.log.debug("Subtitle choosen by match")
                    sub_choice = subpath_list[sub_match]
                else:
                    self.log.debug("Subtitle choosen by rating")
                    sub_choice = best_rated_sub
                self.log.debug("- adding: %s"% (sub_choice.getFileName()))
                subtitles_to_download[sub_choice.getIdOnline()] = {'subtitle_path': os.path.join(video.getFolderPath(), sub_choice.getFileName()), 'video': video}
            
        if len(subtitles_to_download):
            self.log.debug("Communicating with server...")
            answer = self.xmlrpc_server.DownloadSubtitles(self._token, subtitles_to_download.keys())
            self.log.debug("DownloadSubtitles finished in %s with status %s."% (answer['seconds'], answer['status']))
            if answer.has_key("data"):
                self.log.info("Got %i subtitles from server. Uncompressing data..."% len(answer['data']))
                for sub in answer['data']:
                    self.log.info("%s -> %s"% (subtitles_to_download[sub['idsubtitlefile']]['subtitle_path'], subtitles_to_download[sub['idsubtitlefile']]['video'].getFileName()))
                    subtitle_compressed = sub['data']
                    compressedstream = base64.decodestring(subtitle_compressed)
                    #compressedstream = subtitle_compressed
                    gzipper = gzip.GzipFile(fileobj=StringIO.StringIO(compressedstream))
                    s=gzipper.read()
                    gzipper.close()
                    subtitle_file = file(subtitles_to_download[sub['idsubtitlefile']]['subtitle_path'],'wb')
                    subtitle_file.write(s)
                    subtitle_file.close()
                    if subtitles_to_download[sub['idsubtitlefile']]['video'].hasNOSSubtitles():
                        self.log.info("Deleting old subtitle...")
                        for sub in subtitles_to_download[sub['idsubtitlefile']]['video'].getNOSSubtitles():
                            try:
                                os.remove(sub.getFilePath())
                                subtitles_to_download[sub['idsubtitlefile']]['video'].remNOSSubtitle(sub)
                            except Exception, e:
                                self.log.error(e)
                                self.log.error("Unable to delete %r"% sub.getFilePath())
                return True
            else:
                self.log.info("Server sent no subtitles to me.")
                return False
        
    def SearchSubtitles(self, language="all", videos=None, imdb_ids=None):
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
                array = {'sublanguageid': language,'moviehash': video.getHash(),'moviebytesize': str(video.getSize())}
                self.log.debug(" - adding: %s"% array)
                search_array.append(array)
        elif imdb_ids:
            self.log.debug("Building search array with IMDB id's")
            for id in imdb_ids:
                array = {'sublanguageid':language,'imdbid': id}
                self.log.debug(" - adding: %s"% array)
                search_array.append(array)
                
        self.log.debug("Communicating with server...")
        result = self.xmlrpc_server.SearchSubtitles(self._token, search_array)
        
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
                        for i in osdb_info:
                            sub = subtitlefile.SubtitleFile(online=True,id=i["IDSubtitleFile"])
                            sub.setHash(i["SubHash"])
                            sub.setFileName(i["SubFileName"])
                            sub.setLanguage(i["SubLanguageID"])
                            sub.setRating(i["SubRating"])
                            subtitles.append(sub)
                        video.setOsdbInfo(osdb_info)
                        video.setSubtitles(subtitles)
                    videos_result.append(video)
                                
                return videos_result
                
            elif imdb_ids:
                pass
            
        else:
            self.log.info("No subtitles were found on Opensubtitles.com")
            return []
        
    #
    # VIDEO METHODS 
    #
        
    def SearchToMail(self, videos, languages):
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
        
    def CheckMovieHash(self, hashes):
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
        
    def TryUploadSubtitles(self, videos):
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
        result = self.xmlrpc_server.TryUploadSubtitles(self._token, array)
        self.log.debug("Search took %ss"% result['seconds'])
        print result.keys()
        result.pop('seconds')
        import pprint
        pprint.pprint(result)
        if result['alreadyindb']:
            self.log.debug("Subtitle already exists in server database")
        else:
            self.log.debug("Subtitle doesn't exist in server database")
        self.log.debug("----------------")
        return result
        
    def UploadSubtitles(self, videos):
        self.log.debug("----------------")
        self.log.debug("UploadSubtitles RPC method starting...")
        
        check_result = self.TryUploadSubtitles(videos)
        if isinstance(check_result, bool) and not check_result:
            self.log.info("One or more videos don't have subtitles associated. Stopping upload.")
            return False
        elif check_result['alreadyindb']:
            self.log.info("Subtitle already exists in server database. Stopping upload.")
            return False
        else:
            # quick check to see if all video/subtitles are from same movie
            for movie_sub in check_result['data']:
                if locals().has_key('IDMovie'):
                    if IDMovie != movie_sub['IDMovie']:
                        self.log.error("All videos must have same ID. Stopping upload.")
                        return False
                else:
                    IDMovie = movie_sub['IDMovie']
            #
            movie_info = {}
            for details in check_result['data']:
                for (i, video) in enumerate(videos):
                    if video.getHash() == details['MovieHash']:
                        cd = 'cd%i'% (i+1)
                        curr_video = video
                        curr_sub = curr_video.getSubtitles()[0]
                        # cook subtitle content
                        f = open(curr_sub.getFilePath())
                        buf = f.read()
                        f.close()
                        compressed_buf = StringIO.StringIO()
                        gzipper = gzip.GzipFile(fileobj=compressed_buf, mode='wb')
                        gzipper.write(buf); gzipper.close()
                        encoded_buf = base64.encodestring(compressed_buf)
                        curr_sub_content = encoded_buf
                        #curr_cd = {'cd': 'cd%s'%i, 'content': {'subhash': curr_sub.getHash(), 'subfilename': curr_sub.getFileName(), 'moviehash': details['MovieHash'], 'moviebytesize': details['MovieByteSize'], 'movietimems': details['MovieTimeMS'], 'moviefps': curr_video.getFPS(), 'movieframes': details['MovieFrames'], 'moviefilename': curr_video.getFileName(), 'subcontent': None} }
                        # transfer info
                        movie_info[cd] = {'subhash': curr_sub.getHash(), 'subfilename': curr_sub.getFileName(), 'moviehash': details['MovieHash'], 'moviebytesize': details['MovieByteSize'], 'movietimems': details['MovieTimeMS'], 'moviefps': curr_video.getFPS(), 'movieframes': details['MovieFrames'], 'moviefilename': curr_video.getFileName(), 'subcontent': curr_sub_content}
                        
            movie_info['baseinfo'] = {'idmovieimdb': details['IDMovieImdb'], 'moviereleasename': details['MovieName'], 'movieaka': details['MovieNameEng'], 'sublanguageid': curr_sub.getLanguage(), 'subauthorcomment': details['SubAuthorComment']}
            
            print movie_info
            #info = self.xmlrpc_server.UploadSubtitles(self._token, movie_info)
        
    def ReportWrongMovieHash(self, subtitle_id):
        """Report wrong subtitle for a movie
        @subtitle_id: subtitle id from a video (IDSubMovieFile) - string/int
        """
        self.log.debug("----------------")
        self.log.debug("ReportWrongMovieHash RPC method starting...")
        info = self.xmlrpc_server.ReportWrongMovieHash(self._token, subtitle_id)
        self.log.debug("ReportWrongMovieHash finished in %s with status %s."% (info['seconds'], info['status']))
        
    def GetAvailableTranslations(self, program=None):
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
        """Returns video details from IMDB if available
        @imdb_id - IMDB movie id - int/string
        """
        self.log.debug("----------------")
        self.log.debug("GetIMDBMovieDetails RPC method starting...")
        info = self.xmlrpc_server.GetIMDBMovieDetails(self._token, imdb_id)
        self.log.debug("GetIMDBMovieDetails finished in %s with status %s."% (info['seconds'], info['status']))
        return info['data']
        
    def AutoUpdate(self, app=None):
        """Returns latest info on the given application if available
        """
        self.log.debug("----------------")
        self.log.debug("AutoUpdate RPC method starting...")
        if not app: app = APP_TITLE.lower()
        info = self.xmlrpc_server.AutoUpdate(app)
        self.log.debug("CheckMovieHash finished with status %s"% info['status'])
        # no info about this program
        if info['status'] != "200 OK":
            self.log.info("Invalid application name provided.")
            return False
        # we have something to show
        self.log.info("Last version details for %s:"% app)
        self.log.info("Version: %s"% info['version'])
        self.log.info("Linux url: %s"% info['url_linux'])
        self.log.info("Windows url: %s"% info['url_windows'])
        self.log.info("Comments: %s"% info['comments'])
        return info
        
    def NoOperation(self):
        """This method should be called every 15 minutes after last request to xmlrpc. 
        It's used to keep current session alive.
        Returns True if current session token is valid and False if not.
        """
        self.log.debug("----------------")
        self.log.debug("NoOperation RPC method starting...")
        info = self.xmlrpc_server.NoOperation(self._token)
        self.log.debug("NoOperation finished in %s with status %s."% (info['seconds'], info['status']))
        if info['status'] != "200 OK":
            return False
        return True
