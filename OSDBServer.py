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
import base64, StringIO, gzip, httplib, re
import logging

from subdownloader import APP_TITLE, APP_VERSION
import subdownloader.videofile as videofile
import subdownloader.subtitlefile as subtitle

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
        self.log = logging.getLogger("subdownloader.OSDBServer.ProxiedTransport")
        self._use_datetime = True
        #self.user_agent = USER_AGENT
    def set_proxy(self, proxy):
        self.proxy = proxy
        self.log.debug("Proxy set to: %s"% proxy)
    def make_connection(self, host):
        self.log.debug("Connecting to %s through %s"% (host, self.proxy))
        self.realhost = host
        h = httplib.HTTP(self.proxy)
        return h
    def send_request(self, connection, handler, request_body):
        connection.putrequest("POST", 'http://%s%s' % (self.realhost, handler))
    def send_host(self, connection, host):
        connection.putheader('Host', self.realhost)

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
            
#            
#        try:
#            self.log.debug("Trying direct connection...")
##            # test connection to our server
##            self.log.debug("settings request var")
##            req = urllib2.Request(server)
##            self.log.debug("opening url request")
##            f = urllib2.urlopen(req)
##            self.log.debug("reading webpage to buffer")
##            notes= f.readlines()
##            self.log.debug("closing buffer")
##            f.close()
##            # end of test
#            self.log.debug("creating xmlrpc server")
#            self.xmlrpc_server = ServerProxy(server)
#            #self.xmlrpc_server.ServerInfo() # this would be the connection tester
#            self.log.debug("...connected")
#            return True
#        #except IOError, r:
#        except:
##            p = str(r)
##            if re.search(r'urlopen error timed out',p):
#            self.log.debug("...timeout")
#            if self.proxy:
#                self.log.debug("Trying proxied connection...")
#                p = ProxiedTransport()
#                p.set_proxy(self.proxy)
#                self.xmlrpc_server = ServerProxy(server, transport=p)
#                self.xmlrpc_server.ServerInfo() # this would be the connection tester
#                self.log.debug("...connected")
#                return True
#            else:
#                self.log.error("No proxy was set. Unable to connect.")
#                return False
##        except:
##            error = "Error creating XMLRPC server connection to: %s"% server
##            self.log.error(error)
##            return False
        
        
    @classmethod
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
    def GetSubLanguages(self,language=None):
        """Return all suported subtitles languages in a dictionary
        If language var is set, returns SubLanguageID for it
        """
        self.log.debug("----------------")
        self.log.debug("GetSubLanguages RPC method starting...")
        info = self.xmlrpc_server.GetSubLanguages(language)
        self.log.debug("GetSubLanguages complete in %s"% info['seconds'])

        if language:
            for lang in info['data']:
                if lang['ISO639'] == language: return lang['SubLanguageID']
                
        return result['data']
            
    def CheckSubHash(self,hashes):
        """
        @hashes = list of subtitle hashes
        returns: dictionary like { hash: subID }
        This method returns !IDSubtitleFile, if Subtitle Hash exists. If not exists, it returns '0'.
        """
        info = self.xmlrpc_server.CheckSubHash(self._token,hashes)
        self.log.debug("CheckSubHash ended in %s with status: %s"% (info['seconds'], info['status']))
        result = {}
        for hash in hashes:
            result[hash] = data['data'][hash]
#        for data in info['data']:
#            result[data.key()] = data.value()
        return results
    
    def DownloadSubtitle(self,sub_ids,dest = "temp.sub"):
        """
        Download subtitles by there id's
        
        @sub_ids: list of subtitle id's
        @dest: path to save subtitles in string format
        Returns: BASE64 encoded gzipped !IDSubtitleFile(s). You need to BASE64 decode and ungzip 'data' to get its contents.
        """
        try:
            subtitlefile = file(dest,'wb')
            subtitlefile.close()
        except:
            #self.LogMessage("Error saving " + dest)
            return
            
        #if globals.debugmode:
            #globals.Log("-------------Download parameters:")
            #globals.Log([sub_id])
            
        #try:
        answer = self.xmlrpc_server.DownloadSubtitles(self._token,[sub_id])
        #if globals.debugmode:
            #globals.Log("-------------Download Answer:")
            #globals.Log("disabled")
        
        if answer.has_key("data"):
            subtitle_compressed = answer["data"][0]["data"]
        else:
            #self.LogMessage("XMLRPC Error downloading result for idsubfile="+sub_id)
            return
            
        compressedstream = base64.decodestring(subtitle_compressed)
        #compressedstream = subtitle_compressed
        gzipper = gzip.GzipFile(fileobj=StringIO.StringIO(compressedstream))
        s=gzipper.read()
        gzipper.close()
        subtitlefile = file(dest,'wb')
        subtitlefile.write(s)
        subtitlefile.close()
        #self.LogMessage(dest + " saved",status="OK")
        #self.download_subs +=1
    #except: 
        #self.LogMessage("XMLRPC Error downloading id="+sub_id)
        
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
            self.log.debug("Build result: %s"% search_array)
        elif imdb_ids:
            self.log.debug("Building search array with IMDB id's")
            for id in imdb_ids:
                array = {'sublanguageid':language,'imdbid': id}
                self.log.debug(" - adding: %s"% array)
                search_array.append(array)
                
        self.log.debug("Communicating with server...")
        result = self.xmlrpc_server.SearchSubtitles(self._token, search_array)
        print result
        
        if result['data']:
            self.log.debug("Collecting downloaded data")
            
            self.log.debug("Movie hashes...")
            moviehashes = {}
            if result['data'] != False:
                for i in result['data']:
                    moviehash = i['MovieHash']
                    if not moviehashes.has_key(moviehash):
                        moviehashes[moviehash] = []
                    moviehashes[moviehash].append(i)
                 
            if videos:
                videos_result = []
                for video in videos:
                    if moviehashes.has_key(video.getHash()):
                        osdb_info = moviehashes[video.getHash()]
                        subtitles = []
                        for i in osdb_info:
                            sub = subtitle.SubtitleFile(online=True,id=i["IDSubtitleFile"])
                            sub.setFileName(i["SubFileName"])
                            sub.setLanguage(i["SubLanguageID"])
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

        
    def SearchToMail(self):
        pass
    def CheckMovieHash(self):
        pass
    def TryUploadSubtitles(self, videos=None):
        """Will (try) upload subtitle information for one or more videos
        @videos: video and its subtitle - dictionary
        """
        self.log.debug("----------------")
        self.log.debug("TryUploadSubtitles RPC method starting...")
        # will run this method if we have videos and subtitles associated
        if videos and video.getTotalSubtitles() > 0:
            array = {}
            self.log.debug("Building search array...")
            for i in range(1, len(videos)+1):
                cd = 'cd%i'% i
                subtitle = video.getSubtitles()[0]
                array_ = {'subhash': subtitle.getHash(), 'subfilename': subtitle.getFileName(), 'moviehash': video.getHash(), 'moviebytesize': video.getSize(), 'moviefps': video.getFPS(), 'moviefilename': video.getFileName()}
                self.log.debug(" - adding %s: %s"% (cd, array_))
                array[cd] = array_
                
            self.log.debug("Communicating with server...")
            result = self.xmlrpc_server.SearchSubtitles(self._token, search_array)
            self.log.debug("Search took %ss"% result['seconds'])
            if result['alreadyindb']:
                pass
            else:
                pass
        else:
            self.log.debug("No videos or subtitles were provided. Stoping method.")
            
        self.log.debug("----------------")
        
    def UploadSubtitles(self):
        pass
    def ReportWrongMovieHash(self):
        pass
    def GetAvailableTranslations(self):
        pass
    def GetTranslation(self):
        pass
    def SearchMoviesOnIMDB(self):
        pass
    def GetIMDBMovieDetails(self):
        pass
    def AutoUpdate(self):
        pass
    def NoOperation(self):
        pass
    
