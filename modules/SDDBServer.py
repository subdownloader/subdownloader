import base64, urllib2
import platform
from subdownloader import APP_TITLE, APP_VERSION

class SDDBServer(object):
    def sendLogin(self, username):
        args = str({'username': username, 'platform': platform.platform(),'sd_version': APP_VERSION})
        enc = base64.b64encode(args)
        url = "http://dbserver.subdownloader.net/OSDBServer?function=store_login&args=%s" %enc
        urllib2.urlopen(url).read()
    
    def sendHash(self, hash_list,movienames ,  filesizes ):
        args = str({'hash_list': hash_list, 'movie_list': movienames,'size_list': filesizes , 'sd_version': APP_VERSION})
        print args
        enc = base64.b64encode(args)
        #print enc
        url = "http://dbserver.subdownloader.net/OSDBServer?function=store_hash&args=%s" %enc
        urllib2.urlopen(url).read()
