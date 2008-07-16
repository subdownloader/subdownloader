import base64,  simplejson, urllib2
class SDDBServer(object):
    def sendLogin(self):
        pass
    
    def sendHash(self, hash_list, filename):
        args = simplejson.dumps({'hash_list': hash_list, 'sd_version': filename})
        enc = base64.b64encode(args)
        #print enc
        url = "http://dbserver.subdownloader.net/OSDBServer?function=store_hash&args=%s" %enc
        print urllib2.urlopen(url).read()
