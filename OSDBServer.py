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
import base64, StringIO, gzip
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
    
"""The XMLRPC can use a Proxy, this class is need for that."""
class ProxiedTransport(Transport):
    """ Used for proxied connections to the XMLRPC server
        When
    """
    def __init__(self):
        self.log = logging.getLogger("subdownloader.OSDBServer.ProxiedTransport")
        self.user_agent = USER_AGENT
    def set_proxy(self, proxy):
        self.proxy = proxy
    def make_connection(self, host):
        self.realhost = host
        h = HTTP(self.proxy)
        return h
    def send_request(self, connection, handler, request_body):
        connection.putrequest("POST", 'http://%s%s' % (self.realhost, handler))
    def send_host(self, connection, host):
        connection.putheader('Host', self.realhost)

class OSDBServer(Transport):
    """
    Contains the class that represents the OSDB Server.
    Encapsules all the XMLRPC methods.
    
    Consult the API methods at http://code.google.com/p/subdownloader/wiki/XmlRpc_API
    
    If it fails to connect directly to the XMLRPC server, it will try to do so through a default proxy.
    Default proxy uses a form to set which URL to open. We will try to change this in later stage.
    """
    def __init__(self, options):
        self.log = logging.getLogger("subdownloader.OSDBServer.OSDBServer")
        Transport.__init__(self)
        self.user_agent = USER_AGENT
        self.username = options.username
        self.passwd = options.password
        self.language = options.language
        #TODO:Is there a way to simulate the ternary operator in Python for this?
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
        try:
            self.xmlrpc_server = ServerProxy(server,self)
            return True
        except:
            error = "Error creating XMLRPC server connection to: %s"% SERVER_ADDRESS
            self.log.error(error)
            return False

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
            print text
        except Exception,e:
            raise
        
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
    def GetSubLanguages(self,languages):
        """Return all suported subtitles languages in a dictionary"""
        return self.xmlrpc_server.GetSubLanguages(self._token, languages)["data"]
            
    def CheckSubHash(self,hashes):
        """
        @hashes = list of subtitle hashes
        returns: dictionary like { hash: subID }
        This method returns !IDSubtitleFile, if Subtitle Hash exists. If not exists, it returns '0'.
        """
        info = self.xmlrpc_server.CheckSubHash(self._token,hashes)
        self.log.debug("CheckSubHash ended in %s with status: %s"% (info['seconds'], info['status']))
        result = {}
        for data in info['data']:
            result[data.key()] = data.value()
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
        
    def SearchSubtitles(self, language="", videos=None, imdb_ids=None):
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
                search_array.append({'sublanguageid':language,'moviehash':video.getHash(),'moviebytesize':video.getSize()})
        elif imdb_ids:
            self.log.debug("Building search array with IMDB id's")
            for id in imdb_ids:
                search_array.append({'sublanguageid':language,'imdbid': id})
                
        self.log.debug("Doing actual server search...")
        result = self.xmlrpc_server.SearchSubtitles(self._token,search_array)
        print result
        
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
        
        
    #
    # VIDEO METHODS 
    #

        
    def SearchToMail(self):
        pass
    def CheckMovieHash(self):
        pass
    def TryUploadSubtitles(self):
        pass
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
    
