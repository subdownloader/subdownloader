#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
##    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.Warning

""" Create and launch the GUI """
import sys, re, os, traceback, tempfile
import time, thread
import webbrowser
import base64, zlib
#sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QVariant, QSize, QEventLoop, QString, \
                         QBuffer, QIODevice, QModelIndex,QDir, QFileInfo
from PyQt4.QtGui import QPixmap, QSplashScreen, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel, QItemSelectionModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical, QApplication, QMainWindow

from subdownloader.gui.SplashScreen import SplashScreen, NoneSplashScreen
from subdownloader.FileManagement import get_extension, clear_string, without_extension

# create splash screen and show messages to the user
app = QApplication(sys.argv)
splash = SplashScreen()
splash.showMessage(QApplication.translate("subdownloader", "Loading modules..."))

from subdownloader import * 
from subdownloader.OSDBServer import OSDBServer
from subdownloader.gui import installErrorHandler, Error, _Warning, extension

from subdownloader.gui.uploadlistview import UploadListModel, UploadListView
from subdownloader.gui.videotreeview import VideoTreeModel

from subdownloader.gui.main_ui import Ui_MainWindow
from subdownloader.gui.imdbSearch import imdbSearchDialog
from subdownloader.FileManagement import FileScan, Subtitle
from subdownloader.videofile import  *
from subdownloader.subtitlefile import *

import subdownloader.languages.Languages as languages

import logging
log = logging.getLogger("subdownloader.gui.main")

splash.showMessage(QApplication.translate("subdownloader", "Building main dialog..."))


class Main(QObject, Ui_MainWindow): 
    def report_error(func):
        """ 
        Decorator to ensure that unhandled exceptions are displayed 
        to users via the GUI
        """
        def function(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception, e:
                Error("There was an error calling " + func.__name__, e)
                raise
        return function
        
    def read_settings(self):
        settings = QSettings()
        self.window.resize(settings.value("mainwindow/size", QVariant(QSize(1000, 700))).toSize())
        size = settings.beginReadArray("upload/imdbHistory")
        for i in range(size):
            settings.setArrayIndex(i)
            imdbId = settings.value("imdbId").toString()
            title = settings.value("title").toString()
            self.uploadIMDB.addItem("%s : %s" % (imdbId, title), QVariant(imdbId))
        settings.endArray()
        
        self.initializeVideoPlayers(settings)
        
        optionUploadLanguage = settings.value("options/uploadLanguage", QVariant("eng"))

        index = self.optionDefaultUploadLanguage.findData(optionUploadLanguage)
        if index != -1 :
            self.optionDefaultUploadLanguage.setCurrentIndex (index)
            
        self.readOptionsSettings(settings) #Initialized Settings for the OPTIONS tab
    
    def write_settings(self):
        settings = QSettings()
        settings.setValue("mainwindow/size", QVariant(self.window.size()))
    
    def close_event(self, e):
        self.write_settings()
        e.accept()
        
    def update_users(self, sleeptime=60):
        # WARNING: to be used by a thread
        while 1:
            self.status_label.setText("Users online: Updating...")
            try:
                data = self.OSDBServer._ServerInfo() # we cant use the timeout class inherited in OSDBServer
                self.status_label.setText("Users online: "+ str(data["users_online_program"]))
            except:
                self.status_label.setText("Users online: ERROR")
            time.sleep(sleeptime)

    def login_user(self, username, password):
        # WARNING: to be used by a thread
        self.status_label_login.setText("Trying to login...")
        try:
            if self.OSDBServer._login(username, password) :
                if not username: username = 'Anonymous'
                self.status_label_login.setText("Logged as: %s" % username)
            elif username: #We try anonymous login in case the normal user login has failed
                self.status_label_login.setText("Error logging as: %s. Logging anonymously..." % username)
                if self.OSDBServer._login("", "") :
                    self.status_label_login.setText("Logged as: Anonymous")
                else:
                    self.status_label_login.setText("Login: Cannot login.")
        except:
            self.status_label_login.setText("Login: ERROR")

            
    def __init__(self, window, log_packets, options):
        QObject.__init__(self)
        Ui_MainWindow.__init__(self)
        
        self.key = '-1'
        self.log_packets = log_packets
        self.options = options
        self.setupUi(window)
        self.card = None
        self.window = window
        window.closeEvent = self.close_event
        window.setWindowTitle(QtGui.QApplication.translate("MainWindow", "SubDownloader "+APP_VERSION, None, QtGui.QApplication.UnicodeUTF8))
        #Fill Out the Filters Language SelectBoxes
        self.InitializeFilterLanguages()
        self.read_settings()
        
        #self.treeView.reset()
        window.show()
        self.splitter.setSizes([400, 1000])

        #SETTING UP FOLDERVIEW
        model = QDirModel(window)        
        model.setFilter(QDir.AllDirs|QDir.NoDotAndDotDot)
        self.folderView.setModel(model)
        
        settings = QSettings()
        path = settings.value("mainwindow/workingDirectory", QVariant(QDir.rootPath()))
        self.folderView.setRootIndex(model.index(QDir.rootPath()))
        #index = model.index(QDir.rootPath())

        self.folderView.header().hide()
        self.folderView.hideColumn(3)
        self.folderView.hideColumn(2)
        self.folderView.hideColumn(1)
        self.folderView.show()
        
        #Loop to expand the current directory in the folderview.
        log.debug('Current directory: %s' % path.toString())
        path = QDir(path.toString())
        while True:
            self.folderView.expand(model.index(path.absolutePath()))
            if not path.cdUp(): break
                    
        QObject.connect(self.folderView, SIGNAL("activated(QModelIndex)"), \
                            self.onFolderTreeClicked)
        QObject.connect(self.folderView, SIGNAL("clicked(QModelIndex)"), \
                            self.onFolderTreeClicked)

        #SETTING UP SEARCH_VIDEO_VIEW
        self.videoModel = VideoTreeModel(window)
        self.videoView.setModel(self.videoModel)
        QObject.connect(self.videoView, SIGNAL("activated(QModelIndex)"), self.onClickVideoTreeView)
        QObject.connect(self.videoView, SIGNAL("clicked(QModelIndex)"), self.onClickVideoTreeView)
        QObject.connect(self.videoModel, SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.subtitlesCheckedChanged)
        
        QObject.connect(self.buttonDownload, SIGNAL("clicked(bool)"), self.onButtonDownload)
        QObject.connect(self.buttonPlay, SIGNAL("clicked(bool)"), self.onButtonPlay)
        QObject.connect(self.buttonIMDB, SIGNAL("clicked(bool)"), self.onButtonIMDB)
        
        #SETTING UP UPLOAD_VIEW
        self.uploadModel = UploadListModel(window)
        self.uploadView.setModel(self.uploadModel)
        self.uploadModel._main = self #FIXME: This connection should be cleaner.

        #Resizing the headers to take all the space(50/50) in the TableView
        header = self.uploadView.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.Stretch)
        
        QObject.connect(self.buttonUploadBrowseFolder, SIGNAL("clicked(bool)"), self.onUploadBrowseFolder)
        QObject.connect(self.uploadView, SIGNAL("activated(QModelIndex)"), self.onClickUploadViewCell)
        QObject.connect(self.uploadView, SIGNAL("clicked(QModelIndex)"), self.onClickUploadViewCell)
        
        QObject.connect(self.buttonUpload, SIGNAL("clicked(bool)"), self.onUploadButton)
        QObject.connect(self.buttonUploadUpRow, SIGNAL("clicked(bool)"), self.uploadModel.onUploadButtonUpRow)
        QObject.connect(self.buttonUploadDownRow, SIGNAL("clicked(bool)"), self.uploadModel.onUploadButtonDownRow)
        QObject.connect(self.buttonUploadPlusRow, SIGNAL("clicked(bool)"), self.uploadModel.onUploadButtonPlusRow)
        QObject.connect(self.buttonUploadMinusRow, SIGNAL("clicked(bool)"), self.uploadModel.onUploadButtonMinusRow)
        
        QObject.connect(self.buttonUploadFindIMDB, SIGNAL("clicked(bool)"), self.onButtonUploadFindIMDB)
        
        self.uploadSelectionModel = QItemSelectionModel(self.uploadModel)
        self.uploadView.setSelectionModel(self.uploadSelectionModel)
        QObject.connect(self.uploadSelectionModel, SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self.onUploadChangeSelection)
        QObject.connect(self, SIGNAL("imdbDetected(QString,QString)"), self.onUploadIMDBNewSelection)
        
        #OPTIONS events
        QObject.connect(self.optionsButtonApplyChanges, SIGNAL("clicked(bool)"), self.onOptionsButtonApplyChanges)
        QObject.connect(self.optionButtonChooseFolder, SIGNAL("clicked(bool)"), self.onOptionButtonChooseFolder)
        QObject.connect(self.optionDownloadFolderPredefined, SIGNAL("toggled(bool)"), self.onOptionDownloadFolderPredefined)
        QObject.connect(self.optionInterfaceLanguage, SIGNAL("currentIndexChanged(int)"), self.onOptionInterfaceLanguage)
        self.onOptionDownloadFolderPredefined()
            
        self.status_progress = QtGui.QProgressBar(self.statusbar)
        self.status_progress.setProperty("value",QVariant(0))
        
        self.status_progress.setOrientation(QtCore.Qt.Horizontal)
        self.status_label = QtGui.QLabel("v"+ APP_VERSION,self.statusbar)
        
        self.status_label_login = QtGui.QLabel("Not logged in",self.statusbar)
        
        self.statusbar.insertWidget(0,self.status_label)
        self.statusbar.insertWidget(1,self.status_label_login)
        self.statusbar.addPermanentWidget(self.status_progress,2)
        if not options.test:
            #print self.OSDBServer.xmlrpc_server.GetTranslation(self.OSDBServer._token, 'ar', 'po','subdownloader')
            self.window.setCursor(Qt.WaitCursor)
        
            if self.establish_connection():# and self.OSDBServer.is_connected():
                thread.start_new_thread(self.update_users, (60, ))
                settings = QSettings()
                settingsUsername = str(settings.value("options/LoginUsername", QVariant()).toString().toUtf8())
                settingsPassword = str(settings.value("options/LoginPassword", QVariant()).toString().toUtf8())
                thread.start_new_thread(self.login_user, (settingsUsername,settingsPassword,))
            else:
                QMessageBox.about(self.window,"Error","Cannot connect to server. Please try again later")
            self.window.setCursor(Qt.ArrowCursor)
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        
        
        #FOR TESTING
        if options.test:
            #self.SearchVideos('/media/xp/pelis/')
            self.tabs.setCurrentIndex(3)
            pass

    def InitializeFilterLanguages(self):
        self.filterLanguageForVideo.addItem(QtGui.QApplication.translate("MainWindow", "All", None, QtGui.QApplication.UnicodeUTF8))
        self.filterLanguageForTitle.addItem(QtGui.QApplication.translate("MainWindow", "All", None, QtGui.QApplication.UnicodeUTF8))
        for lang in languages.LANGUAGES:
            self.filterLanguageForVideo.addItem(QtGui.QApplication.translate("MainWindow", lang["LanguageName"], None, QtGui.QApplication.UnicodeUTF8), QVariant(lang["SubLanguageID"]))
            self.filterLanguageForTitle.addItem(QtGui.QApplication.translate("MainWindow", lang["LanguageName"], None, QtGui.QApplication.UnicodeUTF8), QVariant(lang["SubLanguageID"]))
            self.uploadLanguages.addItem(QtGui.QApplication.translate("MainWindow", lang["LanguageName"], None, QtGui.QApplication.UnicodeUTF8), QVariant(lang["SubLanguageID"]))
            self.optionDefaultUploadLanguage.addItem(QtGui.QApplication.translate("MainWindow", lang["LanguageName"], None, QtGui.QApplication.UnicodeUTF8), QVariant(lang["SubLanguageID"]))
            self.optionInterfaceLanguage.addItem(QtGui.QApplication.translate("MainWindow", lang["LanguageName"], None, QtGui.QApplication.UnicodeUTF8), QVariant(lang["SubLanguageID"]))
            
            
            
        self.filterLanguageForVideo.adjustSize()
        self.filterLanguageForTitle.adjustSize()
        self.uploadLanguages.adjustSize()
        self.optionDefaultUploadLanguage.adjustSize()
        self.optionInterfaceLanguage.adjustSize()
        
        QObject.connect(self.filterLanguageForVideo, SIGNAL("currentIndexChanged(int)"), self.onFilterLanguageVideo)
        QObject.connect(self.uploadLanguages, SIGNAL("language_updated(QString)"), self.onUploadLanguageDetection)
        
    
    def onFilterLanguageVideo(self, index):
        selectedLanguageName = self.filterLanguageForVideo.itemText(index)
        log.debug("Filtering subtitles by language : %s" % selectedLanguageName)
        self.videoModel.clearTree()
        self.videoView.expandAll()
        if selectedLanguageName != "All": #FIXME: Instead of using english words, we should use lang_codes
            selectedLanguageXX = languages.name2xx(selectedLanguageName)
            self.videoModel.setLanguageFilter(selectedLanguageXX)
        else:
            self.videoModel.setLanguageFilter(None)
        
        self.videoView.expandAll()
        
    def subtitlesCheckedChanged(self):
       subs = self.videoModel.getCheckedSubtitles()
       if subs:
           self.buttonDownload.setEnabled(True)
           self.buttonPlay.setEnabled(True)
       else:
           self.buttonDownload.setEnabled(False)
           self.buttonPlay.setEnabled(False)
           
    def videoSelectedChanged(self):
       subs = self.videoModel.getSelected()
       if subs:
           self.buttonIMDB.setEnabled(True)
       else:
           self.buttonDownload.setEnabled(False)
    
    def SearchVideos(self, path):
        #Scan recursively the selected directory finding subtitles and videos
        videos_found,subs_found = FileScan.ScanFolder(path,recursively = True,report_progress = self.progress)

        #Populating the items in the VideoListView
        self.videoModel.clearTree()
        self.videoView.expandAll()
        self.videoModel.setVideos(videos_found)
        self.videoView.setModel(self.videoModel)
        
        self.videoView.expandAll() #This was a solution found to refresh the treeView
        #Searching our videohashes in the OSDB database
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        if(videos_found):
            self.status("Asking Database...")
            self.window.setCursor(Qt.WaitCursor)
            videoSearchResults = self.OSDBServer.SearchSubtitles("",videos_found)
            if(videoSearchResults):
                self.videoModel.clearTree()
                self.videoModel.setVideos(videoSearchResults)
                self.videoView.expandAll() #This was a solution found to refresh the treeView
            elif videoSearchResults == None :
                QMessageBox.about(self.window,"Error","Server is not responding. Please try again later")
            self.progress(100)
            self.status_progress.setFormat("Search finished")
        else:
            self.progress(100)
            self.status_progress.setFormat("No videos found")
    
        self.window.setCursor(Qt.ArrowCursor)
        #TODO: check if the subtitle found is already in our folder.
        #self.OSDBServer.CheckSubHash(sub_hashes) 
        
    def onClickVideoTreeView(self, index):
        treeItem = self.videoModel.getSelectedItem(index)
        if type(treeItem.data) == VideoFile:
            video = treeItem.data
            if video.getMovieInfo():
                self.buttonIMDB.setEnabled(True)
        else:
            treeItem.checked = not(treeItem.checked)
            self.videoModel.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
            self.buttonIMDB.setEnabled(False)
        
    """What to do when a Folder in the tree is clicked"""
    def onFolderTreeClicked(self, index):
        if hasattr(self,"OSDBServer") and self.OSDBServer.is_connected():
            if index.isValid():
                settings = QSettings()
                data = self.folderView.model().filePath(index)
                folder_path = unicode(data, 'utf-8')
                settings.setValue("mainwindow/workingDirectory", QVariant(folder_path))
                self.SearchVideos(folder_path)
        else:
            QMessageBox.about(self.window,"Error","You are not logged in")
    
    def GetDefaultVideoPlayer(self):
        settings = QSettings()
        totalVideoPlayers = settings.beginReadArray("options/videoPlayers")
        settings.endArray()
        if totalVideoPlayers: 
            selectedVideoApp = settings.value("options/selectedVideoPlayer", QVariant()).toString()
            if selectedVideoApp == QString(): 
                return {}
            else:
                totalVideoPlayers = settings.beginReadArray("options/videoPlayers")
                for i in range(totalVideoPlayers):
                    settings.setArrayIndex(i)
                    programPath = settings.value("programPath").toString()
                    parameters = settings.value("parameters").toString()
                    name = settings.value("name").toString()
                    if name == selectedVideoApp:
                        return {'name': name, 'programPath': programPath,  'parameters': parameters}
                settings.endArray()
        return {}
        
    def onButtonPlay(self, checked):
        videoPlayer = self.GetDefaultVideoPlayer()
        if not videoPlayer.has_key("programPath"):
            QMessageBox.about(self.window,"Error","No default video player has been defined in Options")
            return
        else:
            subtitle = self.videoModel.getSelectedItem().data
            moviePath = subtitle.getVideo().getFilePath()
            subtitleID= subtitle.getIdOnline()
            tempSubFilePath = "/tmp/subdownloader.tmp.srt" #FIXME:  findout a temporary folder depending on the OS
            self.progress(0,"Downloading subtitle ... "+subtitle.getFileName())
            try:
                ok = self.OSDBServer.DownloadSubtitles({subtitleID:tempSubFilePath})
            except Exception, e: 
                traceback.print_exc(e)
                QMessageBox.about(self.window,"Error","Unable to download subtitle "+subtitle.getFileName())
            finally:
                self.progress(100)
            
            programPath = videoPlayer['programPath']
            parameters = videoPlayer['parameters']
            #Replace the {0} and {1} from parameteres
            parameters = parameters.replace('{0}', '"' + moviePath +'"' )
            parameters = parameters.replace('{1}', '"' + tempSubFilePath +'"')
            try:
                #TODO: launch a process for programPath + parameteres , take from codes 1.2.9
                print "Running this command:\n%s %s" % (programPath, parameters)
            except Exception, e: 
                traceback.print_exc(e)
                QMessageBox.about(self.window,"Error","Unable to launch videoplayer")
            
    def onButtonIMDB(self, checked):
        video = self.videoModel.getSelectedItem().data
        movie_info = video.getMovieInfo()
        if movie_info:
            #QMessageBox.about(self.window,"WWW","Open website: http://www.imdb.com/title/tt%s" % movie_info["IDMovieImdb"])
            webbrowser.open( "http://www.imdb.com/title/tt%s"% movie_info["IDMovieImdb"], new=2, autoraise=1)
            
    
    def getDownloadPath(self, video, subtitle):
        downloadFullPath = ""
        settings = QSettings()
        
        #Creating the Subtitle Filename
        optionSubtitleName = settings.value("options/subtitleName", QVariant("SAME_VIDEO"))
        sub_extension = get_extension(subtitle.getFileName().lower())
        if optionSubtitleName == QVariant("SAME_VIDEO"):
           subFileName = without_extension(video.getFileName()) +"." + sub_extension
        elif optionSubtitleName == QVariant("SAME_ONLINE"):
           subFileName = subtitle.getFileName()
        
        #Creating the Folder Destination
        optionWhereToDownload = settings.value("options/whereToDownload", QVariant("SAME_FOLDER"))
        if optionWhereToDownload == QVariant("ASK_FOLDER"):
            folderPath = video.getFolderPath()
            dir = QDir(QString(folderPath))
            downloadFullPath = dir.filePath(QString(subFileName))
            downloadFullPath = QFileDialog.getSaveFileName(None, "Save Subtitle", downloadFullPath, sub_extension)
        elif optionWhereToDownload == QVariant("SAME_FOLDER"):
            folderPath = video.getFolderPath()
            dir = QDir(QString(folderPath))
            downloadFullPath = dir.filePath(QString(subFileName))
        elif optionWhereToDownload == QVariant("PREDEFINED_FOLDER"):
            folderPath = settings.value("options/whereToDownloadFolder", QVariant("")).toString()
            dir = QDir(QString(folderPath)) 
            downloadFullPath = dir.filePath(QString(subFileName))

        return downloadFullPath
    def onButtonDownload(self, checked):
        #We download the subtitle in the same folder than the video
            subs = self.videoModel.getCheckedSubtitles()
            percentage = 100/len(subs)
            count = 0
            self.status("Connecting to download...")
            for sub in subs:
                self.progress(count,"Downloading subtitle ... "+sub.getFileName())
                count += percentage
                destinationPath = str(self.getDownloadPath(sub.getVideo(), sub).toUtf8())
                
                log.debug("Downloading subtitle '%s'" % destinationPath)
                try:
                   ok = self.OSDBServer.DownloadSubtitles({sub.getIdOnline():destinationPath})
                except Exception, e: 
                    traceback.print_exc(e)
                    QMessageBox.about(self.window,"Error","Unable to download subtitle "+sub.getFileName())
                
                if ok:
                     QMessageBox.about(self.window,"Error","Unable to download subtitle "+sub.getFileName())

            self.status("Subtitles downloaded succesfully.")
            self.progress(100)

    """Control the STATUS BAR PROGRESS"""
    def progress(self, val,msg = None):
        self.status_progress.setMaximum(100)
        self.status_progress.reset()
        if msg != None:
            self.status_progress.setFormat(msg + ": %p%")
        if val < 0:
            self.status_progress.setMaximum(0)
        else: 
            self.status_progress.setValue(val)
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
    
    def status(self, msg):
        self.status_progress.setMaximum(100)
        self.status_progress.reset()
        self.status_progress.setFormat(msg + ": %p%")
        self.progress(0)
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
    
    def establish_connection(self):
        settings = QSettings()
        settingsProxyHost = settings.value("options/ProxyHost", QVariant()).toString()
        settingsProxyPort = settings.value("options/ProxyPort", QVariant("8080")).toInt()[0]
        if not self.options.proxy:  #If we are not defining the proxy from command line 
            if settingsProxyHost: #Let's see if we have defined a proxy in our Settings
                self.options.proxy = str(settingsProxyHost + ":" + str(settingsProxyPort))
            else:
                self.status("Connecting to server") 
                
        if self.options.proxy:
            self.status("Connecting to server using proxy %s" % self.options.proxy) 
        
        try:
            self.OSDBServer = OSDBServer(self.options) 
            self.status_progress.setFormat("Connected succesfully")
            self.progress(100)
            return True
        except Exception, e: 
            #traceback.print_exc(e)
            self.status("Error connecting to server") 
            self.progress(0)
            return False
            #qFatal("Unable to connect to server. Please try again later")

        
    #UPLOAD METHODS
    
    def onButtonUploadFindIMDB(self):
        dialog = imdbSearchDialog(self)
        dialog.show()
        ok = dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        
    def onUploadBrowseFolder(self):
        settings = QSettings()
        path = settings.value("mainwindow/workingDirectory", QVariant())
        directory=QtGui.QFileDialog.getExistingDirectory(None,"Select a directory",path.toString())
        if directory:
            settings.setValue("mainwindow/workingDirectory", QVariant(directory))
            directory =  str(directory.toUtf8())
            videos_found,subs_found = FileScan.ScanFolder(directory,recursively = False,report_progress = self.progress)
            log.info("Videos found: %i Subtitles found: %i"%(len(videos_found), len(subs_found)))
            self.uploadModel.emit(SIGNAL("layoutAboutToBeChanged()"))
            for row, video in enumerate(videos_found):
                self.uploadModel.addVideos(row, [ video])
                subtitle = Subtitle.AutoDetectSubtitle(video.getFilePath())
                if subtitle:
                    sub = SubtitleFile(False,subtitle) 
                    self.uploadModel.addSubs(row, [sub])
            self.uploadView.resizeRowsToContents()
            self.uploadModel.update_lang_upload()
            self.uploadModel.emit(SIGNAL("layoutChanged()"))

    def onUploadButton(self, clicked):
        result = self.uploadModel.verify()
        if not result["ok"]:
            QMessageBox.about(self.window,"Error",result["error_msg"])
            return
        else:
            log.debug("Compressing subtitle...")
            details = {}
            imdb_id = self.uploadIMDB.itemData(self.uploadIMDB.currentIndex())
            if imdb_id == QVariant(): #No IMDB
                QMessageBox.about(self.window,"Error","Please select an IMDB movie.")
                return
            else:
                details['IDMovieImdb'] = str(imdb_id.toString().toUtf8())
                lang_xxx = self.uploadLanguages.itemData(self.uploadLanguages.currentIndex())
                details['sublanguageid'] = str(lang_xxx.toString().toUtf8()) 
                details['movieaka'] = ''
                details['moviereleasename'] = str(self.uploadReleaseText.text().toUtf8()) 
                details['subauthorcomment'] = str(self.uploadComments.toPlainText().toUtf8()) 
                
                movie_info = {}
                movie_info['baseinfo'] = {'idmovieimdb': details['IDMovieImdb'], 'moviereleasename': details['moviereleasename'], 'movieaka': details['movieaka'], 'sublanguageid': details['sublanguageid'], 'subauthorcomment': details['subauthorcomment']}
             
                for i in range(self.uploadModel.getTotalRows()):
                    curr_sub = self.uploadModel._subs[i]
                    curr_video = self.uploadModel._videos[i]
                    if curr_sub : #Make sure is not an empty row with None
                        buf = open(curr_sub.getFilePath()).read()
                        curr_sub_content = base64.encodestring(zlib.compress(buf))
                        cd = "cd" + str(i)
                        movie_info[cd] = {'subhash': curr_sub.getHash(), 'subfilename': curr_sub.getFileName(), 'moviehash': curr_video.calculateOSDBHash(), 'moviebytesize': curr_video.getSize(), 'movietimems': curr_video.getTimeMS(), 'moviefps': curr_video.getFPS(), 'moviefilename': curr_video.getFileName(), 'subcontent': curr_sub_content}

                if self.OSDBServer.UploadSubtitles(movie_info):
                    QMessageBox.about(self.window,"Success","Subtitles succesfully uploaded. Thanks.")
                else:
                    QMessageBox.about(self.window,"Error","Problem while uploading...")
    
    def onUploadIMDBNewSelection(self, id, title):
        id = str(id.toUtf8())
        
        #Let's select the item with that id.
        index = self.uploadIMDB.findData(QVariant(id))
        if index != -1 :
            self.uploadIMDB.setCurrentIndex (index)
        else:
            self.uploadIMDB.addItem("%s : %s" % (id, title), QVariant(id))
            index = self.uploadIMDB.findData(QVariant(id))
            self.uploadIMDB.setCurrentIndex (index)
            
            #Adding the new IMDB in our settings historial
            settings = QSettings()
            size = settings.beginReadArray("upload/imdbHistory")
            settings.endArray()
            settings.beginWriteArray("upload/imdbHistory")
            settings.setArrayIndex(size)
            settings.setValue("imdbId", QVariant(id))
            settings.setValue("title", QVariant(title))
            settings.endArray()



            #imdbHistoryList = settings.value("upload/imdbHistory", QVariant([])).toList()
            #print imdbHistoryList
            #imdbHistoryList.append({'id': id,  'title': title})
            #settings.setValue("upload/imdbHistory", imdbHistoryList)
            #print id
            #print title
            
    def onUploadLanguageDetection(self, lang_xxx):
        #Let's select the item with that id.
        index = self.uploadLanguages.findData(QVariant(lang_xxx))
        if index != -1:
            self.uploadLanguages.setCurrentIndex (index)
            return
            
    def updateButtonsUpload(self):
        self.uploadView.resizeRowsToContents()
        selected = self.uploadSelectionModel.selection()
        if selected.count():
            self.uploadModel.rowSelected = selected.last().bottomRight().row()
            self.buttonUploadMinusRow.setEnabled(True)
            if self.uploadModel.rowSelected != self.uploadModel.getTotalRows() -1:
                self.buttonUploadDownRow.setEnabled(True)
            else:
                self.buttonUploadDownRow.setEnabled(False)
                
            if self.uploadModel.rowSelected != 0:
                self.buttonUploadUpRow.setEnabled(True)
            else:
                self.buttonUploadUpRow.setEnabled(False)
        else:
            self.uploadModel.rowSelected = None
            self.buttonUploadDownRow.setEnabled(False)
            self.buttonUploadUpRow.setEnabled(False)
            self.buttonUploadMinusRow.setEnabled(False)
            
    def onUploadChangeSelection(self, selected, unselected):
        self.updateButtonsUpload()
        
    def onClickUploadViewCell(self, index):
        row, col = index.row(), index.column()
        settings = QSettings()
        currentDir = settings.value("mainwindow/workingDirectory", QVariant())
        
        if col == UploadListView.COL_VIDEO:
            fileName = QFileDialog.getOpenFileName(None, "Select Video", currentDir.toString(), videofile.SELECT_VIDEOS)
            if fileName:
                settings.setValue("mainwindow/workingDirectory", QVariant(QFileInfo(fileName).absolutePath()))
                video = VideoFile(str(fileName.toUtf8())) 
                self.uploadModel.emit(SIGNAL("layoutAboutToBeChanged()"))
                self.uploadModel.addVideos(row, [video])
                subtitle = Subtitle.AutoDetectSubtitle(video.getFilePath())
                if subtitle:
                    sub = SubtitleFile(False,subtitle) 
                    self.uploadModel.addSubs(row, [sub])
                    self.uploadModel.update_lang_upload()
                self.uploadView.resizeRowsToContents()
                self.uploadModel.emit(SIGNAL("layoutChanged()"))
        else:
            fileName = QFileDialog.getOpenFileName(None, "Select Subtitle", currentDir.toString(), subtitlefile.SELECT_SUBTITLES)
            if fileName:
                settings.setValue("mainwindow/workingDirectory", QVariant(QFileInfo(fileName).absolutePath()))
                sub = SubtitleFile(False, str(fileName.toUtf8())) 
                self.uploadModel.emit(SIGNAL("layoutAboutToBeChanged()"))
                self.uploadModel.addSubs(row, [sub])
                self.uploadView.resizeRowsToContents()
                self.uploadModel.emit(SIGNAL("layoutChanged()"))
                self.uploadModel.update_lang_upload()
    
    def onOptionButtonChooseFolder(self):
        directory=QtGui.QFileDialog.getExistingDirectory(None,"Select a directory",QString())
        if directory:
            self.optionPredefinedFolderText.setText(directory)
    def onOptionInterfaceLanguage(self, option):
        QMessageBox.about(self.window,"Alert","The new language will be displayed after restarting the application")
        
    def onOptionDownloadFolderPredefined(self):
        if self.optionDownloadFolderPredefined.isChecked():
            self.optionPredefinedFolderText.setEnabled(True)
            self.optionButtonChooseFolder.setEnabled(True)
        else:
            self.optionPredefinedFolderText.setEnabled(False)
            self.optionButtonChooseFolder.setEnabled(False)

    def onOptionsButtonApplyChanges(self):
        log.debug("Saving Options Settings")
        #Fields validation
        if self.optionDownloadFolderPredefined.isChecked() and self.optionPredefinedFolderText.text() == QString():
            QMessageBox.about(self.window,"Error","Predefined Folder cannot be empty")
            return
        #Writting settings
        settings = QSettings()
        if self.optionDownloadFolderAsk.isChecked():
            settings.setValue("options/whereToDownload", QVariant("ASK_FOLDER"))
        elif self.optionDownloadFolderSame.isChecked():
            settings.setValue("options/whereToDownload", QVariant("SAME_FOLDER"))
        elif self.optionDownloadFolderPredefined.isChecked():
            settings.setValue("options/whereToDownload", QVariant("PREDEFINED_FOLDER"))
            folder = self.optionPredefinedFolderText.text()
            settings.setValue("options/whereToDownloadFolder", QVariant(folder))
            
        if self.optionDownloadSameFilename.isChecked():
            settings.setValue("options/subtitleName", QVariant("SAME_VIDEO"))
        elif self.optionDownloadOnlineSubName.isChecked():
            settings.setValue("options/subtitleName", QVariant("SAME_ONLINE"))
        
        optionUploadLanguage = self.optionDefaultUploadLanguage.itemData(self.optionDefaultUploadLanguage.currentIndex())
        settings.setValue("options/uploadLanguage", optionUploadLanguage)
        
        optionInterfaceLanguage = self.optionInterfaceLanguage.itemData(self.optionInterfaceLanguage.currentIndex())
        settings.setValue("options/interfaceLanguage", optionInterfaceLanguage)
        
        IEoldValue = settings.value("options/IntegrationExplorer", QVariant(False)).toBool()
        IEnewValue = self.optionIntegrationExplorer.isChecked()
        if  IEoldValue != IEnewValue:
           settings.setValue("options/IntegrationExplorer", QVariant(IEnewValue))
           if IEnewValue:
               log.debug('Installing the Integration Explorer feature') 
               #TODO: install and uninstall
           else:
               log.debug('Uninstalling the Integration Explorer feature')
        
        newUsername =  self.optionLoginUsername.text()
        newPassword = self.optionLoginPassword.text()
        oldUsername = settings.value("options/LoginUsername", QVariant())
        oldPassword = settings.value("options/LoginPassword", QVariant())
        if newUsername != oldUsername.toString() or newPassword != oldPassword.toString():
            settings.setValue("options/LoginUsername",QVariant(newUsername))
            settings.setValue("options/LoginPassword", QVariant(newPassword))
            log.debug('Login credentials has changed. Trying to login.')
            thread.start_new_thread(self.login_user, (str(newUsername.toUtf8()),str(newPassword.toUtf8()),))
            
        newProxyHost =  self.optionProxyHost.text()
        newProxyPort = self.optionProxyPort.value()
        oldProxyHost = settings.value("options/ProxyHost", QVariant()).toString()
        oldProxyPort = settings.value("options/ProxyPort", QVariant("8080")).toInt()[0]
        if newProxyHost != oldProxyHost or newProxyPort != oldProxyPort:
            settings.setValue("options/ProxyHost",QVariant(newProxyHost))
            settings.setValue("options/ProxyPort", QVariant(newProxyPort))
            QMessageBox.about(self.window,"Alert","Modified proxy settings will take effect after restarting the program")

    def readOptionsSettings(self, settings):
        log.debug("Reading Options Settings")
        optionWhereToDownload = settings.value("options/whereToDownload", QVariant("SAME_FOLDER"))
        if optionWhereToDownload == QVariant("ASK_FOLDER"):
            self.optionDownloadFolderAsk.setChecked(True)
        elif optionWhereToDownload == QVariant("SAME_FOLDER"):
            self.optionDownloadFolderSame.setChecked(True)
        elif optionWhereToDownload == QVariant("PREDEFINED_FOLDER"):
            self.optionDownloadFolderPredefined.setChecked(True)
        
        folder = settings.value("options/whereToDownloadFolder", QVariant("")).toString()
        self.optionPredefinedFolderText.setText(folder)
            
            
        optionSubtitleName = settings.value("options/subtitleName", QVariant("SAME_VIDEO"))
        if optionSubtitleName == QVariant("SAME_VIDEO"):
            self.optionDownloadSameFilename.setChecked(True)
        elif optionSubtitleName == QVariant("SAME_ONLINE"):
            self.optionDownloadOnlineSubName.setChecked(True)
        
        optionUploadLanguage = settings.value("options/uploadLanguage", QVariant("eng"))
        index = self.uploadLanguages.findData(optionUploadLanguage)
        if index != -1 :
            self.uploadLanguages.setCurrentIndex (index)
            
        optionInterfaceLanguage = settings.value("options/interfaceLanguage", QVariant("eng"))
        index = self.optionInterfaceLanguage.findData(optionInterfaceLanguage)
        if index != -1 :
            self.optionInterfaceLanguage.setCurrentIndex (index)
            
        optionIntegrationExplorer = settings.value("options/IntegrationExplorer", QVariant(False))
        self.optionIntegrationExplorer.setChecked(optionIntegrationExplorer.toBool())
        
        self.optionLoginUsername.setText(settings.value("options/LoginUsername", QVariant()).toString())
        self.optionLoginPassword.setText(settings.value("options/LoginPassword", QVariant()).toString())
        
        self.optionProxyHost.setText(settings.value("options/ProxyHost", QVariant()).toString())
        self.optionProxyPort.setValue(settings.value("options/ProxyPort", QVariant(8080)).toInt()[0])
        
        totalVideoPlayers = settings.beginReadArray("options/videoPlayers")
        for i in range(totalVideoPlayers):
            settings.setArrayIndex(i)
            programPath = settings.value("programPath").toString()
            parameters = settings.value("parameters").toString()
            name = settings.value("name").toString()
            self.optionVideoAppCombo.addItem("%s" % (name), QVariant(name))
        settings.endArray()
        
        if totalVideoPlayers: 
            QObject.connect(self.optionVideoAppCombo, SIGNAL("currentIndexChanged(int)"), self.onOptionVideoAppCombo)
        selectedVideoApp = settings.value("options/selectedVideoPlayer", QVariant()).toString()
        if selectedVideoApp != QString():
            index = self.optionVideoAppCombo.findData(QVariant(selectedVideoApp))
            if index != -1 : 
                self.optionVideoAppCombo.setCurrentIndex (index)
                self.onOptionVideoAppCombo(index)
        
    def onOptionVideoAppCombo(self, index):
        settings = QSettings()
        totalVideoPlayers = settings.beginReadArray("options/videoPlayers")
        settings.setArrayIndex(index)
        programPath = settings.value("programPath").toString()
        parameters = settings.value("parameters").toString()
        name = settings.value("name").toString()
        self.optionVideoAppLocation.setText(programPath)
        self.optionVideoAppParams.setText(parameters)
        settings.endArray()
        
    def initializeVideoPlayers(self, settings):
        predefinedVIdeosPlayers = [{'name': 'MPLAYER', 'programPath': '/usr/bin/mplayer',  'parameters': '{0} -sub {1}'}, 
                                                    {'name': 'VLC','programPath': '/usr/bin/vlc',  'parameters': '{0} -subtitle {1}'}]
                                                    
        settings.beginWriteArray("options/videoPlayers")
        for i, videoapp in enumerate(predefinedVIdeosPlayers):
            settings.setArrayIndex(i)
            settings.setValue("programPath",  QVariant(videoapp['programPath']))
            settings.setValue("parameters", QVariant( videoapp['parameters']))
            settings.setValue("name", QVariant( videoapp['name']))
        settings.endArray()
        
        defaultVideoApp = predefinedVIdeosPlayers[0]
        settings.setValue("options/selectedVideoPlayer", QVariant(defaultVideoApp['name']))
        
def main(options):
    log.debug("Building main dialog")
#    app = QApplication(sys.argv)
#    splash = SplashScreen()
#    splash.showMessage(QApplication.translate("subdownloader", "Building main dialog..."))
    window = QMainWindow()
    window.setWindowTitle(APP_TITLE)
    window.setWindowIcon(QIcon(":/icon"))
    installErrorHandler(QErrorMessage(window))
    QCoreApplication.setOrganizationName("IvanGarcia")
    QCoreApplication.setApplicationName(APP_TITLE)
    
    splash.finish(window)
    log.debug("Showing main dialog")
    Main(window,"", options)    
    
    return app.exec_()

#if __name__ == "__main__": 
#    sys.exit(main())
