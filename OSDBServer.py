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

from xmlrpclib import Transport,Server
from subdownloader import *

import subdownloader.videofile as videofile
import subdownloader.subtitlefile as subtitlefile

SERVER_ADDRESS = "http://www.opensubtitles.org/xml-rpc"

"""This class is useful to let the server know who we are, good for statistics,
    so we can separate the traffic from normal Web visitors"""
class GtkTransport (Transport):
        user_agent = "Subdownloader " + APP_VERSION 
    
"""The XMLRPC can use a Proxy, this class is need for that."""
class ProxiedTransport(Transport):
        user_agent = "Subdownloader " + APP_VERSION 
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

class OSDBServer:
    """Contains the class that represents the OSDB Server
    encapsules all the XMLRpc methods.
    Consult the methods Api at http://code.google.com/p/subdownloader/wiki/XmlRpc_API"""

    
       
    def __init__(self):
        self.logged_as = None
        self.xmlrpc_server = None
        self._token = "666"
        #Let's connect with the server XMLRPC
        self.create_xmlrpcserver()
        
    def GetSubLanguages(self,languages):
            print self.xmlrpc_server.GetSubLanguages(self._token,languages)["data"]
            
    def CheckSubHash(self,hashes):
            answer = self.xmlrpc_server.CheckSubHash(self._token,hashes)
            print answer
            #I need changes in the API to get more info about these subtitles
    
    def SearchSubtitles(self,lang,videos):
            search_array = []
            for video in videos:
                    search_array.append({'sublanguageid':lang,'moviehash':video.getHash(),'moviebytesize':video.getSize()})
            result = self.xmlrpc_server.SearchSubtitles(self._token,search_array)
            ###print result
            moviehashes = {}
            if result['data'] != False:
                    for i in result['data']:
                            moviehash = i['MovieHash']
                            if not moviehashes.has_key(moviehash):
                                    moviehashes[moviehash] = []
                        
                            moviehashes[moviehash].append(i)
                 
            videos_result = []
            for video in videos:
                if moviehashes.has_key(video.getHash()):
                      video.setOsdbInfo(moviehashes[video.getHash()])
                videos_result.append(video)
                            
            return videos_result
                            
            
    def create_xmlrpcserver(self):
        transport = GtkTransport()
        try:
                self.xmlrpc_server = Server(SERVER_ADDRESS,transport)
        except:
                error = ("Error XMLRPC creating server connection to : %s") % SERVER_ADDRESS
                wx.MessageBox(error)
                return
            
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
        empty parameters means an anonymously login""" 
        
    @classmethod
    def is_connected(self):
        """ 
        This method checks to see whether we are connected to the server. 
        It does not return any information about the validity of the 
        connection.
        """
        return self.logged_as != None
