import globals
from xmlrpclib import Transport,Server
import os
import pickle
import time
import __builtin__

class Connection:
    
    def Create(self):
			#version = "SubDownloader " +globals.version
			#self.SetTitle(version + " : " +_("Connecting, please wait..."))
			if globals.preferences_list["proxyserver"]:
				transport = globals.ProxiedTransport()
				if not globals.preferences_list["proxyport"]:
					globals.preferences_list["proxyport"] = "8080"  
				userpass = ""
				if globals.preferences_list["proxyuser"]:
					userpass = globals.preferences_list["proxyuser"]+ ":" + globals.preferences_list["proxypass"] +"@"
	
				proxy_address =  userpass +  globals.preferences_list["proxyserver"] + ":" + globals.preferences_list["proxyport"]
				#print proxy_address
				transport.set_proxy(proxy_address)
			else:
				transport = globals.GtkTransport()
			
			self.httpheaders = {'User-Agent' : "Subdownloader " + globals.version }
			
			
			#CREATING CONNECTION WITH XMLRPC
			try:
				#wx.BusyInfo("Login into "+ globals.preferences_list["server_osdb"])
				if globals.debugmode:
					globals.Log("-------------xmlrpclib.Server-----")
					globals.Log("Connecting to server="+globals.preferences_list["server_osdb"])
					globals.Log("Login username="+globals.preferences_list["username"]+"  password="+"X"*len(globals.preferences_list["password"]))
				globals.xmlrpc_server = Server(globals.preferences_list["server_osdb"],transport)
			except:
				error = _("Error XMLRPC creating server connection to : %s") % globals.preferences_list["server_osdb"]
				wx.MessageBox(error)
				globals.Log(error)
				globals.disable_osdb = True
				self.SetTitle(version + " : "+ _("Not Connected"))
				return
			
    def Login(self,usecookie=True):		
			
	    #LOGGING IN FROM COOKIE
	    cookie = ""
	    cookie_details = True
	    thereis_cookie = os.path.exists(os.path.join(globals.sourcefolder,globals.cookiefile))
	    if usecookie and thereis_cookie:
		    cookie_details = pickle.load(file(os.path.join(globals.sourcefolder,globals.cookiefile),"rb"))
		    time_17min = 1020

		    if time.time() < cookie_details["time"] + time_17min:
			    globals.osdb_token = cookie_details["token"]
			    globals.logged_as = cookie_details["username"]
			    globals.disable_osdb = False
			    
			    message = "Succesful Connection from cookie. "
			    self.UpdateCurrentTranslation()
			    return True,message
		    

	    #LOGGING IN WITH XMLRPC
	    try:
		    login = globals.xmlrpc_server.LogIn(globals.preferences_list["username"],globals.preferences_list["password"],"","SubDownloader "+globals.version)
		    globals.osdb_token = login["token"]
		    if globals.debugmode:
			    globals.Log("-------------Receiving parameters:")
			    globals.Log("Login Result" + str(login))
		    
			    
    
		    if login["status"].startswith("4"):
			    error = _("I cannot login to server. Status: %s") % login["status"]
			    
			    globals.disable_osdb = True
			    
			    return False,error
		    else:
			    if globals.preferences_list["username"]:
				    globals.logged_as = globals.preferences_list["username"]
			    else: 
				    globals.logged_as = ""
				    
			    globals.disable_osdb = False
			    message = "Succesful Connection from XMLRPC, username = %s" % globals.preferences_list["username"]
			    
			    cookie = {"token": login["token"],"time": time.time(),"username": globals.logged_as}
			    pickle.dump(cookie,file(os.path.join(globals.sourcefolder,globals.cookiefile),"wb"))
			    return True,message
			    
	    except:
		    error = "Error XMLRPC loggin in at " + globals.preferences_list["server_osdb"]
		    globals.disable_osdb = True
		    return False,error
		
	    time_1hour = 3600

	    if not usecookie:
		if not thereis_cookie or (cookie_details and time.time() > cookie_details["time"] + time_1hour): 
		    self.GetSubLanguages()
				
    def GetSubLanguages(self):
	    try:
		    globals.Log("-----XMLRPC SERVERINFO----\n")
		    server_details = globals.xmlrpc_server.ServerInfo()
		    
		    globals.Log(server_details)
	    except:
		    globals.Log("Error globals.xmlrpc_server.ServerInfo()")
		    
	    try:
		    if int(server_details["total_subtitles_languages"]) > globals.sublanguages["total_subtitles_languages"]:
			    globals.Log("-----XMLRPC GetSubLanguages----\n")
			    list_languages = globals.xmlrpc_server.GetSubLanguages('')["data"]
			    globals.Log(list_languages)
			    languages_id_xxx = {}
			    for lang in list_languages:
				    languages_id_xxx[lang["SubLanguageID"]] =  [lang["ISO639"],lang["LanguageName"]]
				    
			    languages_name2xxx = {}
			    for xxx,[xx,name] in languages_id_xxx.items():
				    languages_name2xxx[name] = xxx
			      
			    languages_xx2xxx = {}
			    for xxx,[xx,name] in languages_id_xxx.items():
				    languages_xx2xxx[xx] = xxx
			      
			    globals.sublanguages["languages_id_xxx"] = languages_id_xxx
			    globals.sublanguages["languages_name2xxx"] = languages_name2xxx
			    globals.sublanguages["languages_xx2xxx"] = languages_xx2xxx
			    globals.sublanguages["total_subtitles_languages"] = int(server_details["total_subtitles_languages"])
			    pickle.dump(globals.sublanguages,file(os.path.join(globals.sourcefolder,"conf/.sublanguages"),"wb"))
	    except:
		    globals.Log("Error globals.xmlrpc_server.GetSubLanguages")
    def UpdateCurrentTranslation(self):
		lang_app_xx = globals.preferences_list["app_language"]
				
		globals.Log("-----XMLRPC GetAvailableTranslations----\n")
		list_translations = globals.xmlrpc_server.GetAvailableTranslations(globals.osdb_token)["data"]
		globals.Log(list_translations)
		globals.new_translations_dates = {}
		for lang,array in list_translations.items():
			globals.new_translations_dates[lang] =  time.mktime(time.strptime(array["LastCreated"],"%Y-%m-%d %H:%M:%S"))
		
		if globals.current_translations_dates.has_key(lang_app_xx):
			globals.Log("time current lang["+lang_app_xx + "] = " + str(globals.current_translations_dates[lang_app_xx]))
			globals.Log("time new lang[" +lang_app_xx + "] = "+ str(globals.new_translations_dates[lang_app_xx]))
		
		if not globals.current_translations_dates.has_key(lang_app_xx) and globals.new_translations_dates.has_key(lang_app_xx):
			globals.DownloadNewTranslations(lang_app_xx)
			globals.Log("Downloaded new translations for lang["+lang_app_xx + "] = " + str(globals.current_translations_dates[lang_app_xx]))
		elif globals.current_translations_dates[lang_app_xx] < globals.new_translations_dates[lang_app_xx]:
			globals.DownloadNewTranslations(lang_app_xx)
			globals.Log("Downloaded new translations for lang["+lang_app_xx + "] = " + str(globals.current_translations_dates[lang_app_xx]))
