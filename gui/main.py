#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Copyright (C) 2007 Ivan Garcia capiscuas@gmail.com
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
import urllib2
import base64, zlib
import commands
import platform
import os.path
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QVariant, QSize, QEventLoop, QString, \
                         QBuffer, QIODevice, QModelIndex,QDir, QFileInfo, QTime, QFile
from PyQt4.QtGui import QPixmap, QSplashScreen, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel, QItemSelectionModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical, QApplication, QMainWindow

from subdownloader.gui.SplashScreen import SplashScreen, NoneSplashScreen
from subdownloader.FileManagement import get_extension, clear_string, without_extension

# create splash screen and show messages to the user
app = QApplication(sys.argv)
splash = SplashScreen()
splash.showMessage(QApplication.translate("subdownloader", "Loading modules..."))
QCoreApplication.flush()
from subdownloader import * 
from subdownloader.OSDBServer import OSDBServer
from subdownloader.modules.SDDBServer import SDDBServer
from subdownloader.gui import installErrorHandler, Error, _Warning, extension

from subdownloader.gui.uploadlistview import UploadListModel, UploadListView
from subdownloader.gui.videotreeview import VideoTreeModel

from subdownloader.gui.main_ui import Ui_MainWindow
from subdownloader.gui.imdbSearch import imdbSearchDialog
from subdownloader.gui.preferences import preferencesDialog
from subdownloader.gui.about import aboutDialog
from subdownloader.FileManagement import FileScan, Subtitle
from subdownloader.videofile import  *
from subdownloader.subtitlefile import *
from subdownloader.modules.search import *

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
    
    def __init__(self, window, log_packets, options):
        QObject.__init__(self)
        Ui_MainWindow.__init__(self)
        self.timeLastSearch = QTime.currentTime();

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
        
        #self.folderView.setRootIndex(model.index(QDir.rootPath()))
        #index = model.index(QDir.rootPath())

        self.folderView.header().hide()
        self.folderView.hideColumn(3)
        self.folderView.hideColumn(2)
        self.folderView.hideColumn(1)
        self.folderView.show()
        
        #Loop to expand the current directory in the folderview.
        lastDir = settings.value("mainwindow/workingDirectory", QVariant(QDir.rootPath()))
        log.debug('Current directory: %s' % lastDir.toString())
        path = QDir(lastDir.toString())
        while True:
            self.folderView.expand(model.index(path.absolutePath()))
            if not path.cdUp(): break
        
        self.folderView.scrollTo(model.index(lastDir.toString()))
        QObject.connect(self.folderView, SIGNAL("clicked(QModelIndex)"),  self.onFolderTreeClicked)
        
        #SETTING UP SEARCH_VIDEO_VIEW
        self.videoModel = VideoTreeModel(window)
        self.videoView.setModel(self.videoModel)
        QObject.connect(self.videoView, SIGNAL("activated(QModelIndex)"), self.onClickVideoTreeView)
        QObject.connect(self.videoView, SIGNAL("clicked(QModelIndex)"), self.onClickVideoTreeView)
        QObject.connect(self.videoView, SIGNAL("customContextMenuRequested(QPoint)"), self.onContext)
        QObject.connect(self.videoModel, SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.subtitlesCheckedChanged)
        
        QObject.connect(self.buttonDownload, SIGNAL("clicked(bool)"), self.onButtonDownload)
        QObject.connect(self.buttonPlay, SIGNAL("clicked(bool)"), self.onButtonPlay)
        QObject.connect(self.buttonIMDB, SIGNAL("clicked(bool)"), self.onButtonIMDB)
        self.videoView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) 
        
        
        self.videoView.__class__.dragEnterEvent = self.dragEnterEvent
        self.videoView.__class__.dragMoveEvent = self.dragEnterEvent
        self.videoView.__class__.dropEvent = self.dropEvent
        self.videoView.setAcceptDrops(1)

        
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
        
        #Search by Name
        QObject.connect(self.buttonSearchByName, SIGNAL("clicked(bool)"), self.onButtonSearchByTitle)
        QObject.connect(self.movieNameText, SIGNAL("returnPressed()"), self.onButtonSearchByTitle)
        QObject.connect(self.buttonDownloadByTitle, SIGNAL("clicked(bool)"), self.onButtonDownloadByTitle)
        QObject.connect(self.buttonIMDBByTitle, SIGNAL("clicked(bool)"), self.onButtonIMDB)
        self.moviesModel = VideoTreeModel(window)
        self.moviesView.setModel(self.moviesModel)
        
        
        QObject.connect(self.moviesView, SIGNAL("clicked(QModelIndex)"), self.onClickMovieTreeView)
        QObject.connect(self.moviesModel, SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.subtitlesMovieCheckedChanged)
        QObject.connect(self.moviesView, SIGNAL("expanded(QModelIndex)"), self.onExpandMovie)
        self.moviesView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) 
        QObject.connect(self.moviesView, SIGNAL("customContextMenuRequested(QPoint)"), self.onContext)
        

        
        #Menu options
        QObject.connect(self.action_Quit, SIGNAL("triggered()"), self.onMenuQuit)
        QObject.connect(self.action_HelpHomepage, SIGNAL("triggered()"), self.onMenuHelpHomepage)
        QObject.connect(self.action_HelpAbout, SIGNAL("triggered()"), self.onMenuHelpAbout)
        QObject.connect(self.action_HelpBug, SIGNAL("triggered()"), self.onMenuHelpBug)
        QObject.connect(self.action_HelpDonation, SIGNAL("triggered()"), self.onMenuHelpDonation)
        QObject.connect(self.action_ShowPreferences, SIGNAL("triggered()"), self.onMenuPreferences)
        QObject.connect(self.window, SIGNAL("updateTitleApp(QString)"), self.onChangeTitleBarText)
        
        self.status_progress = QtGui.QProgressBar(self.statusbar)
        self.status_progress.setProperty("value",QVariant(0))
        
        self.status_progress.setOrientation(QtCore.Qt.Horizontal)
        self.status_label = QtGui.QLabel("v"+ APP_VERSION,self.statusbar)
        self.setTitleBarText("Connecting...")
        
        self.statusbar.insertWidget(0,self.status_label)
        self.statusbar.addPermanentWidget(self.status_progress,2)
        self.status("")
        if not options.test:
            #print self.OSDBServer.xmlrpc_server.GetTranslation(self.OSDBServer._token, 'ar', 'po','subdownloader')
            self.window.setCursor(Qt.WaitCursor)
        
            if self.establish_connection():# and self.OSDBServer.is_connected():
                thread.start_new_thread(self.update_users, (60, ))
                settings = QSettings()
                settingsUsername = str(settings.value("options/LoginUsername", QVariant()).toString().toUtf8())
                settingsPassword = str(settings.value("options/LoginPassword", QVariant()).toString().toUtf8())
                thread.start_new_thread(self.login_user, (settingsUsername,settingsPassword,window, ))
                thread.start_new_thread(self.SDDBServer.sendLogin, (settingsUsername,  ))
            else:
                QMessageBox.about(self.window,"Error","Cannot connect to server. Please try again later")
            self.window.setCursor(Qt.ArrowCursor)
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

        #FOR TESTING
        if options.test:
            #self.SearchVideos('/media/xp/pelis/')
            self.tabs.setCurrentIndex(3)
            pass
            
    def dragEnterEvent(self, event):
        #print event.mimeData().formats().join(" ")
        if event.mimeData().hasFormat("text/plain")  or event.mimeData().hasFormat("text/uri-list"):
                event.accept()
        else:
                event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            paths = [str(u.toLocalFile().toUtf8()) for u in event.mimeData().urls()]
            self.SearchVideos(paths)
            
    def onContext(self, point): # Create a menu 
            menu = QtGui.QMenu("Menu", self.window) 
            if self.tabs.currentIndex() == 0: #Tab for SearchByHash TODO:replace this 0 by an ENUM value
                listview = self.videoView
            else:
                listview = self.moviesView
            index = listview.currentIndex()
            treeItem = listview.model().getSelectedItem(index)
            if treeItem != None:
                if type(treeItem.data) == VideoFile:
                        video = treeItem.data
                        movie_info = video.getMovieInfo()
                        if movie_info:
                            subWebsiteAction = QtGui.QAction(QIcon(":/images/imdb.png"),"View IMDB info", self)
                            QObject.connect(subWebsiteAction, SIGNAL("triggered()"), self.onViewOnlineInfo)
                        else:
                            subWebsiteAction = QtGui.QAction(QIcon(":/images/imdb.png"),"Set IMDB info...", self)
                            QObject.connect(subWebsiteAction, SIGNAL("triggered()"), self.onSetIMDBInfo)
                        menu.addAction(subWebsiteAction) 
                elif type(treeItem.data) == SubtitleFile: #Subtitle
                    treeItem.checked = True
                    self.videoModel.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
                    downloadAction = QtGui.QAction(QIcon(":/images/download.png"), "Download", self)
                    if self.tabs.currentIndex() == 0: #Video tab, TODO:Replace me with a enum
                        QObject.connect(downloadAction, SIGNAL("triggered()"), self.onButtonDownload)
                        playAction = QtGui.QAction(QIcon(":/images/play.png"),"Play video + subtitle", self)
                        QObject.connect(playAction, SIGNAL("triggered()"), self.onButtonPlay)
                        menu.addAction(playAction) 
                    else:
                        QObject.connect(downloadAction, SIGNAL("triggered()"), self.onButtonDownloadByTitle)
                    subWebsiteAction = QtGui.QAction(QIcon(":/images/sites/opensubtitles.png"),"View online info", self)
                    
                    menu.addAction(downloadAction) 
                    QObject.connect(subWebsiteAction, SIGNAL("triggered()"), self.onViewOnlineInfo)
                    menu.addAction(subWebsiteAction) 
                elif type(treeItem.data) == Movie:
                    movie = treeItem.data
                    subWebsiteAction = QtGui.QAction(QIcon(":/images/imdb.png"),"View IMDB info", self)
                    QObject.connect(subWebsiteAction, SIGNAL("triggered()"), self.onViewOnlineInfo)
                    menu.addAction(subWebsiteAction) 

            # Show the context menu. 
            menu.exec_(listview.mapToGlobal(point)) 
    
    def onSetIMDBInfo(self):
        QMessageBox.about(self.window,"Info","Not implemented yet. Please donate.")
        
    def onViewOnlineInfo(self):
        if self.tabs.currentIndex() == 0: #Tab for SearchByHash TODO:replace this 0 by an ENUM value
                listview = self.videoView
        else:
                listview = self.moviesView
        index = listview.currentIndex()
        treeItem = listview.model().getSelectedItem(index)
        
        if type(treeItem.data) == VideoFile:
            self.onButtonIMDB()
        elif type(treeItem.data) == SubtitleFile: #Subtitle
            sub = treeItem.data
            print  sub.isOnline()
            if sub.isOnline():
                webbrowser.open( "http://www.opensubtitles.org/en/subtitles/%s/"% sub.getIdOnline(), new=2, autoraise=1)

        elif type(treeItem.data) == Movie:
                self.onButtonIMDB()
            
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
        programPath = settings.value("options/VideoPlayerPath", QVariant()).toString()
        if programPath == QVariant(): #If not found videoplayer
            self.initializeVideoPlayer(settings)
        
    
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

    def login_user(self, username, password, window):
        window.emit(SIGNAL('updateTitleApp(QString)'),"Trying to login...")
        try:
            if self.OSDBServer._login(username, password) :
                if not username: username = 'Anonymous'
                window.emit(SIGNAL('updateTitleApp(QString)'),"Logged as: %s" % username)
            elif username: #We try anonymous login in case the normal user login has failed
                window.emit(SIGNAL('updateTitleApp(QString)'),"Error logging as: %s. Logging anonymously..." % username)
                if self.OSDBServer._login("", "") :
                    window.emit(SIGNAL('updateTitleApp(QString)'),"Logged as: Anonymous")
                else:
                    window.emit(SIGNAL('updateTitleApp(QString)'),"Login: Cannot login.")
        except:
            window.emit(SIGNAL('updateTitleApp(QString)'),"Login: ERROR")

    def onMenuQuit(self):
        self.window.close()
    
    def setTitleBarText(self, text):
        self.window.setWindowTitle("SubDownloader "+APP_VERSION + " - %s" %text)
        
    def onChangeTitleBarText(self, title):
        self.setTitleBarText(title)
    
    def onMenuHelpAbout(self):
        dialog = aboutDialog(self)
        dialog.show()
        ok = dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def onMenuHelpHomepage(self):
         webbrowser.open( "http://www.subdownloader.net/", new=2, autoraise=1)

    def onMenuHelpBug(self):
        webbrowser.open( "https://bugs.launchpad.net/subdownloader", new=2, autoraise=1)

    def onMenuHelpDonation(self):
        webbrowser.open( "https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=donations%40subdownloader%2enet&no_shipping=0&no_note=1&tax=0&currency_code=EUR&lc=PT&bn=PP%2dDonationsBF&charset=UTF%2d8", new=2, autoraise=1)
        
    def onMenuPreferences(self):
        dialog = preferencesDialog(self)
        dialog.show()
        ok = dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def InitializeFilterLanguages(self):
        self.filterLanguageForVideo.addItem(QtGui.QApplication.translate("MainWindow", "All languages", None, QtGui.QApplication.UnicodeUTF8))
        self.filterLanguageForTitle.addItem(QtGui.QApplication.translate("MainWindow", "All languages", None, QtGui.QApplication.UnicodeUTF8))
        for lang in languages.LANGUAGES:
            self.filterLanguageForVideo.addItem(QtGui.QApplication.translate("MainWindow", lang["LanguageName"], None, QtGui.QApplication.UnicodeUTF8), QVariant(lang["SubLanguageID"]))
            self.filterLanguageForTitle.addItem(QtGui.QApplication.translate("MainWindow", lang["LanguageName"], None, QtGui.QApplication.UnicodeUTF8), QVariant(lang["SubLanguageID"]))
            self.uploadLanguages.addItem(QtGui.QApplication.translate("MainWindow", lang["LanguageName"], None, QtGui.QApplication.UnicodeUTF8), QVariant(lang["SubLanguageID"]))
        
        settings = QSettings()
        optionUploadLanguage = settings.value("options/uploadLanguage", QVariant("eng"))
        index = self.uploadLanguages.findData(optionUploadLanguage)
        if index != -1 :
            self.uploadLanguages.setCurrentIndex (index)    
        
        self.filterLanguageForVideo.adjustSize()
        self.filterLanguageForTitle.adjustSize()
        self.uploadLanguages.adjustSize()

       
        
        QObject.connect(self.filterLanguageForVideo, SIGNAL("currentIndexChanged(int)"), self.onFilterLanguageVideo)
        QObject.connect(self.filterLanguageForTitle, SIGNAL("currentIndexChanged(int)"), self.onFilterLanguageSearchName)
        QObject.connect(self.uploadLanguages, SIGNAL("language_updated(QString)"), self.onUploadLanguageDetection)

        

    def onFilterLanguageVideo(self, index):
        selectedLanguageXXX = str(self.filterLanguageForVideo.itemData(index).toString())
        log.debug("Filtering subtitles by language : %s" % selectedLanguageXXX)
        self.videoView.clearSelection()
        
       # self.videoModel.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.videoModel.clearTree()
       # self.videoModel.emit(SIGNAL("layoutChanged()"))
        #self.videoView.expandAll()
        if selectedLanguageXXX:
            self.videoModel.setLanguageFilter(selectedLanguageXXX)
            self.videoModel.selectMostRatedSubtitles() #Let's select by default the most rated subtitle for each video 
            self.subtitlesCheckedChanged()
        else:
            self.videoModel.setLanguageFilter(None)
            self.videoModel.unselectSubtitles() #Let's select by default the most rated subtitle for each video 
            self.subtitlesCheckedChanged()
        
        self.videoView.expandAll()
        
    def subtitlesCheckedChanged(self):
       subs = self.videoModel.getCheckedSubtitles()
       if subs:
           self.buttonDownload.setEnabled(True)
           self.buttonPlay.setEnabled(True)
       else:
           self.buttonDownload.setEnabled(False)
           self.buttonPlay.setEnabled(False)
           
    
    def SearchVideos(self, path):
        #Scan recursively the selected directory finding subtitles and videos
        if not type(path) == list:
            path = [path]
        videos_found,subs_found = FileScan.ScanFilesFolders(path,recursively = True,report_progress = self.progress)
        print videos_found
        print subs_found
        #Populating the items in the VideoListView
        self.videoModel.clearTree()
        self.videoView.expandAll()
        self.videoModel.setVideos(videos_found)
        self.videoView.setModel(self.videoModel)
        
        self.videoView.expandAll() #This was a solution found to refresh the treeView
        #Searching our videohashes in the OSDB database
        QCoreApplication.processEvents()
        if(videos_found):
            self.status("Asking Database...")
            self.progress(20)
            self.window.setCursor(Qt.WaitCursor)
            videoSearchResults = self.OSDBServer.SearchSubtitles("",videos_found)
                
            if(videoSearchResults and subs_found):
                hashes_subs_found = {}
                #Hashes of the local subtitles
                for sub in subs_found:
                    hashes_subs_found[sub.getHash()] = sub.getFilePath()
                    
                #are the online subtitles already in our folder?
                for video in videoSearchResults:
                   for sub in video._subs:
                       if sub.getHash() in hashes_subs_found:
                           sub._path = hashes_subs_found[sub.getHash()]
                           sub._online = False
                
            if(videoSearchResults):
                self.videoModel.clearTree()
                self.videoModel.setVideos(videoSearchResults)
                self.onFilterLanguageVideo(self.filterLanguageForVideo.currentIndex())
                self.videoView.expandAll() #This was a solution found to refresh the treeView
            elif videoSearchResults == None :
                QMessageBox.about(self.window,"Error","Server is not responding. Please try again later")
            self.progress(100)
            self.status_progress.setFormat("Search finished")
        else:
            self.progress(100)
            self.status_progress.setFormat("No videos found")
        
        video_hashes = [video.calculateOSDBHash() for video in videoSearchResults]
        video_filesizes =  [str(video.getSize()) for video in videoSearchResults]
        video_movienames = [video.getMovieName() for video in videoSearchResults]

        thread.start_new_thread(self.SDDBServer.sendHash, (video_hashes,video_movienames,  video_filesizes,  ))
    
        self.window.setCursor(Qt.ArrowCursor)
        #TODO: CHECK if our local subtitles are already in the server, otherwise suggest to upload
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
                #QObject.disconnect(self.folderView, SIGNAL("clicked(QModelIndex)"),  self.onFolderTreeClicked)
                now = QTime.currentTime()
                if now > self.timeLastSearch.addMSecs(500) :
                    settings = QSettings()
                    data = self.folderView.model().filePath(index)
                    folder_path = unicode(data, 'utf-8')
                    settings.setValue("mainwindow/workingDirectory", QVariant(folder_path))
                    self.SearchVideos(folder_path) 
                    self.timeLastSearch = QTime.currentTime()
                    #QCoreApplication.sendPostedEvents()
                    #QObject.connect(self.folderView, SIGNAL("clicked(QModelIndex)"),  self.onFolderTreeClicked)
        else:
            QMessageBox.about(self.window,"Error","You are not logged in")

    def onButtonPlay(self):
        settings = QSettings()
        programPath = settings.value("options/VideoPlayerPath", QVariant()).toString()
        parameters = settings.value("options/VideoPlayerParameters", QVariant()).toString()
        if programPath == QString(): 
            QMessageBox.about(self.window,"Error","No default video player has been defined in Main->Preferences")
            return
        else:
            subtitle = self.videoModel.getSelectedItem().data
            moviePath = subtitle.getVideo().getFilePath()
            subtitleFileID= subtitle.getIdFileOnline()
            #This should work in all the OS, creating a temporary file 
            tempSubFilePath = str(QDir.temp().absoluteFilePath("subdownloader.tmp.srt"))
            log.debug("Temporary subtitle will be downloaded into: %s" % tempSubFilePath)
            self.progress(0,"Downloading subtitle ... "+subtitle.getFileName())
            try:
                ok = self.OSDBServer.DownloadSubtitles({subtitleFileID:tempSubFilePath})
                if not ok:
                    QMessageBox.about(self.window,"Error","Unable to download subtitle "+subtitle.getFileName())
            except Exception, e: 
                traceback.print_exc(e)
                QMessageBox.about(self.window,"Error","Unable to download subtitle "+subtitle.getFileName())
            finally:
                self.progress(100)
            
            params = []
            programPath = str(programPath.toUtf8()) 
            parameters = str(parameters.toUtf8()) 

            for param in parameters.split(" "):
                param = param.replace('{0}', moviePath  )
                param = param.replace('{1}',  tempSubFilePath )
                params.append(param)
                
            params.insert(0,'"' + programPath+'"' )
            print params
            log.info("Running this command:\n%s %s" % (programPath, params))
            try:
                os.spawnve(os.P_NOWAIT, programPath,params, os.environ)
            except AttributeError:
                pid = os.fork()
                if not pid :
                    os.execvpe(os.P_NOWAIT, programPath,params, os.environ)
            except Exception, e: 
                traceback.print_exc(e)
                QMessageBox.about(self.window,"Error","Unable to launch videoplayer")
            
    def onButtonIMDB(self):
        imdb = ""
        if self.tabs.currentIndex() == 0: #Search by HASH tabs
            video = self.videoModel.getSelectedItem().data
            movie_info = video.getMovieInfo()
            if movie_info:
                imdb = movie_info["IDMovieImdb"]
        else:
            movie = self.moviesModel.getSelectedItem().data
            imdb = movie.IMDBId
        
        if imdb:
            webbrowser.open( "http://www.imdb.com/title/tt%s"% imdb , new=2, autoraise=1)
    
    def getDownloadPath(self, video, subtitle):
        downloadFullPath = ""
        settings = QSettings()
        
        #Creating the Subtitle Filename
        optionSubtitleName = settings.value("options/subtitleName", QVariant("SAME_VIDEO"))
        sub_extension = get_extension(subtitle.getFileName().lower())
        if optionSubtitleName == QVariant("SAME_VIDEO"):
           subFileName = without_extension(video.getFileName()) +"." + sub_extension
        elif optionSubtitleName == QVariant("SAME_VIDEOPLUSLANG"):
           subFileName = without_extension(video.getFileName()) +"." +subtitle.getLanguageXXX() +"." + sub_extension
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
    def onButtonDownload(self):
        #We download the subtitle in the same folder than the video
            subs = self.videoModel.getCheckedSubtitles()
            replace_all  = False
            if not subs:
                QMessageBox.about(self.window,"Error","No subtitles selected to be downloaded")
                return
            total_subs = len(subs)
            percentage = 100/total_subs
            count = 0
            answer = None
            success_downloaded = 0
            for i, sub in enumerate(subs):
                destinationPath = str(self.getDownloadPath(sub.getVideo(), sub).toUtf8())
                if not destinationPath:
                    break
                log.debug("Trying to download subtitle '%s'" % destinationPath)
                self.progress(count,"Downloading subtitle %s (%d/%d)" % (QFileInfo(destinationPath).fileName(), i + 1, total_subs))
                #Check if we have write permissions, otherwise show warning window
                while True: 
                    #If the file and the folder don't have writte access.
                    if not QFileInfo(destinationPath).isWritable() and not QFileInfo(QFileInfo(destinationPath).absoluteDir().path()).isWritable() :
                        warningBox = QMessageBox("Error write permission", 
                                                                    "%s cannot be saved.\nCheck that the folder exists and user has write-access permissions." %destinationPath , 
                                                                    QMessageBox.Warning, 
                                                                    QMessageBox.Retry | QMessageBox.Default ,
                                                                    QMessageBox.Discard | QMessageBox.Escape, 
                                                                    QMessageBox.NoButton, 
                                                                    self.window)

                        saveAsButton = warningBox.addButton(QString("Save as..."), QMessageBox.ActionRole)
                        answer = warningBox.exec_()
                        if answer == QMessageBox.Retry:
                            continue
                        elif answer == QMessageBox.Discard :
                            break #Let's get out from the While true
                        elif answer ==  QMessageBox.NoButton: #If we choose the SAVE AS
                            fileName = QFileDialog.getSaveFileName(None, "Save subtitle as...", destinationPath, 'All (*.*)')
                            if fileName:
                                destinationPath = fileName
                    else: #If we have write access we leave the while loop.
                        break 
                        
                #If we have chosen Discard subtitle button.
                if answer == QMessageBox.Discard:
                    count += percentage
                    continue #Continue the next subtitle
                    
                optionWhereToDownload =  QSettings().value("options/whereToDownload", QVariant("SAME_FOLDER"))
                #Check if doesn't exists already, otherwise show replace window
                if QFileInfo(destinationPath).exists() and not replace_all and optionWhereToDownload != QVariant("ASK_FOLDER"):
                    answer = QMessageBox.warning(self.window,"Replace subtitle","%s already exists.\nWould you like to replace it?" %destinationPath, QMessageBox.Yes | QMessageBox.Default, QMessageBox.YesAll, QMessageBox.No |QMessageBox.Escape)
                    if answer == QMessageBox.YesAll:
                        replace_all = True
                    elif answer == QMessageBox.No:
                        count += percentage
                        continue
                QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
                
                try:
                   log.debug("Downloading subtitle '%s'" % destinationPath)
                   if self.OSDBServer.DownloadSubtitles({sub.getIdFileOnline():destinationPath}):
                       success_downloaded += 1
                   else:
                     QMessageBox.about(self.window,"Error","Unable to download subtitle "+sub.getFileName())
                except Exception, e: 
                    traceback.print_exc(e)
                    QMessageBox.about(self.window,"Error","Unable to download subtitle "+sub.getFileName())
                finally:
                    count += percentage

            self.status("%d from %d subtitles downloaded succesfully" % (success_downloaded, total_subs))
            self.progress(100)

    """Control the STATUS BAR PROGRESS"""
    def progress(self, val,msg = None):
        self.status_progress.setMaximum(100)
        self.status_progress.reset()
        if msg != None:
            self.status_progress.setFormat(msg) # + ": %p%")
        if val < 0:
            self.status_progress.setMaximum(0)
        else: 
            self.status_progress.setValue(val)
        
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
    
    def status(self, msg):
        self.status_progress.setMaximum(100)
        self.status_progress.reset()
        self.status_progress.setFormat(msg) #+ ": %p%")
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
                self.setTitleBarText("Connecting to server") 
                
        if self.options.proxy:
            self.setTitleBarText("Connecting to server using proxy %s" % self.options.proxy) 
        
        try:
            self.OSDBServer = OSDBServer(self.options) 
            self.SDDBServer = SDDBServer()
            self.setTitleBarText("Connected succesfully")
            self.progress(100)
            return True
        except Exception, e: 
            #traceback.print_exc(e)
            self.setTitleBarText("Error connecting to server") 
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
        ok, error = self.uploadModel.validate()
        if not ok:
            QMessageBox.about(self.window,"Error",error)
            return
        else:
            imdb_id = self.uploadIMDB.itemData(self.uploadIMDB.currentIndex())
            if imdb_id == QVariant(): #No IMDB
                QMessageBox.about(self.window,"Error","Please select an IMDB movie.")
                return
            else:
                self.progress(0)
                self.window.setCursor(Qt.WaitCursor)
                log.debug("Compressing subtitle...")
                details = {}
                details['IDMovieImdb'] = str(imdb_id.toString().toUtf8())
                lang_xxx = self.uploadLanguages.itemData(self.uploadLanguages.currentIndex())
                details['sublanguageid'] = str(lang_xxx.toString().toUtf8()) 
                details['movieaka'] = ''
                details['moviereleasename'] = str(self.uploadReleaseText.text().toUtf8()) 
                comments = str(self.uploadComments.toPlainText().toUtf8()) 
                if comments:
                    comments += "<br>"
                comments += 'Uploaded with <a href="http://www.subdownloader.net/">Subdownloader2</a>' 
                details['subauthorcomment'] =  comments
                
                movie_info = {}
                movie_info['baseinfo'] = {'idmovieimdb': details['IDMovieImdb'], 'moviereleasename': details['moviereleasename'], 'movieaka': details['movieaka'], 'sublanguageid': details['sublanguageid'], 'subauthorcomment': details['subauthorcomment']}
             
                for i in range(self.uploadModel.getTotalRows()):
                    curr_sub = self.uploadModel._subs[i]
                    curr_video = self.uploadModel._videos[i]
                    if curr_sub : #Make sure is not an empty row with None
                        buf = open(curr_sub.getFilePath(), mode='rb').read()
                        curr_sub_content = base64.encodestring(zlib.compress(buf))
                        cd = "cd" + str(i)
                        movie_info[cd] = {'subhash': curr_sub.getHash(), 'subfilename': curr_sub.getFileName(), 'moviehash': curr_video.calculateOSDBHash(), 'moviebytesize': curr_video.getSize(), 'movietimems': curr_video.getTimeMS(), 'moviefps': curr_video.getFPS(), 'moviefilename': curr_video.getFileName(), 'subcontent': curr_sub_content}
                
                try:
                    info = self.OSDBServer.UploadSubtitles(movie_info)
                    if info['status'] == "200 OK":
                        successBox = QMessageBox("Success", 
                                                                        "Subtitles succesfully uploaded. \nMany Thanks!." , 
                                                                        QMessageBox.Information, 
                                                                        QMessageBox.Ok | QMessageBox.Default | QMessageBox.Escape,
                                                                        QMessageBox.NoButton,
                                                                        QMessageBox.NoButton, 
                                                                        self.window)

                        saveAsButton = successBox.addButton(QString("View Subtitle Info"), QMessageBox.ActionRole)
                        answer = successBox.exec_()
                        if answer ==  QMessageBox.NoButton:
                            webbrowser.open( info['data'], new=2, autoraise=1)
                        self.cleanUploadWindow()
                    else:
                        QMessageBox.about(self.window,"Error","Problem while uploading...\nError: %s" % info['status'])
                except:
                    QMessageBox.about(self.window,"Error","Error contacting with the server.\nPlease restart or try later.")
                self.progress(100)
                self.window.setCursor(Qt.ArrowCursor)
    
    def cleanUploadWindow(self):
        self.uploadReleaseText.setText("")
        self.uploadComments.setText("")
        self.progress(0)
        #Note: We don't reset the language
        self.uploadModel.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.uploadModel.removeAll()
        self.uploadModel.emit(SIGNAL("layoutChanged()"))
        index = self.uploadIMDB.findData(QVariant())
        if index != -1 :
            self.uploadIMDB.setCurrentIndex (index)
            
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

    def initializeVideoPlayer(self, settings):
        predefinedVideoPlayer = None
        if platform.system() == "Linux":
            linux_players = [{'executable': 'mplayer', 'parameters': '{0} -sub {1}'}, 
                                    {'executable': 'vlc', 'parameters': '{0} --sub-file {1}'},
                                    {'executable': 'xine', 'parameters': '{0}#subtitle:{1}'}] 
            for player in linux_players:
                status, path = commands.getstatusoutput("which %s" %player["executable"]) #1st video player to find
                if status == 0: 
                    predefinedVideoPlayer = {'programPath': path,  'parameters': player['parameters']}
                    break

        elif platform.system() == "Windows":
            import _winreg
            windows_players = [{'regRoot': _winreg.HKEY_LOCAL_MACHINE , 'regFolder': 'SOFTWARE\\VideoLan\\VLC', 'regKey':'','parameters': '{0} --sub-file {1}'}, 
                                            {'regRoot': _winreg.HKEY_LOCAL_MACHINE , 'regFolder': 'SOFTWARE\\Gabest\\Media Player Classic', 'regKey':'ExePath','parameters': '{0} /sub {1}'}]

            for player in windows_players:
                try:
                    registry = _winreg.OpenKey(player['regRoot'],  player["regFolder"])
                    path, type = _winreg.QueryValueEx(registry, player["regKey"])
                    print "Video Player found at: ", repr(path)
                    predefinedVideoPlayer = {'programPath': path,  'parameters': player['parameters']}
                    break
                except WindowsError:
                    print "Cannot find registry for %s" % player['regRoot']
        elif platform.system() == "Darwin": #MACOSX
            macos_players = [{'path': '/Applications/VLC.app/Contents/MacOS/VLC', 'parameters': '{0} --sub-file {1}'}, 
                                        {'path': '/Applications/MPlayer OSX.app/Contents/MacOS/MPlayer OSX', 'parameters': '{0} -sub {1}'}, 
                                        {'path': '/Applications/MPlayer OS X 2.app/Contents/MacOS/MPlayer OS X 2', 'parameters': '{0} -sub {1}'} ]
            for player in macos_players:
                if os.path.exists(player['path']):
                    predefinedVideoPlayer =  {'programPath': player['path'],  'parameters': player['parameters']}

        if predefinedVideoPlayer:
            settings.setValue("options/VideoPlayerPath",  QVariant(predefinedVideoPlayer['programPath']))
            settings.setValue("options/VideoPlayerParameters", QVariant( predefinedVideoPlayer['parameters']))

    
    def onClickMovieTreeView(self, index):
        treeItem = self.moviesModel.getSelectedItem(index)
        if type(treeItem.data) == Movie:
            movie = treeItem.data
            if movie.IMDBId:
                self.buttonIMDBByTitle.setEnabled(True)
        else:
            treeItem.checked = not(treeItem.checked)
            self.moviesModel.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
            self.buttonIMDBByTitle.setEnabled(False)
            
    def onButtonSearchByTitle(self):
        self.progress(0,"Searching movies")
        self.window.setCursor(Qt.WaitCursor)
        self.moviesModel.clearTree()
        self.moviesView.expandAll() #This was a solution found to refresh the treeView
        QCoreApplication.processEvents()
        s = SearchByName()
        selectedLanguageXXX = str(self.filterLanguageForTitle.itemData(self.filterLanguageForTitle.currentIndex()).toString())
        search_text = str(self.movieNameText.text().toUtf8())
        movies = s.search_movie(search_text,'all')
        self.moviesModel.setMovies(movies, selectedLanguageXXX)
        if len(movies) == 1:
            self.moviesView.expandAll() 
        else:
            self.moviesView.collapseAll() 
        QCoreApplication.processEvents()
        self.window.setCursor(Qt.ArrowCursor)
        self.progress(100)
        
    def onFilterLanguageSearchName(self, index):
        selectedLanguageXXX = str(self.filterLanguageForTitle.itemData(index).toString())
        log.debug("Filtering subtitles by language : %s" % selectedLanguageXXX)
        self.moviesView.clearSelection()
        self.moviesModel.clearTree()
        self.moviesModel.setLanguageFilter(selectedLanguageXXX)

        self.moviesView.expandAll()
        
    def subtitlesMovieCheckedChanged(self):
       subs = self.moviesModel.getCheckedSubtitles()
       if subs:
           self.buttonDownloadByTitle.setEnabled(True)
       else:
           self.buttonDownloadByTitle.setEnabled(False)
           
    def onButtonDownloadByTitle(self):
        subs = self.moviesModel.getCheckedSubtitles()
        total_subs = len(subs)
        if not subs:
                QMessageBox.about(self.window,"Error","No subtitles selected to be downloaded")
                return
        percentage = 100/total_subs
        count = 0
        answer = None
        success_downloaded = 0
        for i, sub in enumerate(subs):
            url = sub.getExtraInfo("downloadLink")
            webbrowser.open( url, new=2, autoraise=1)
            log.debug("Opening link %s" % (url))
            count += percentage
            self.progress(count,"Opening Link %s" % url)
        self.progress(100)

    def onExpandMovie(self, index):
        movie = index.internalPointer().data
        if not movie.subtitles and movie.totalSubs:
            self.progress(0,"Searching subtitles")
            self.window.setCursor(Qt.WaitCursor)
            s = SearchByName()
            selectedLanguageXXX = str(self.filterLanguageForTitle.itemData(self.filterLanguageForTitle.currentIndex()).toString())
            temp_movie = s.search_movie(None,'all',MovieID_link= movie.MovieSiteLink)
            #The internal results are not filtered by language, so in case we change the filter, we don't need to request again.
            movie.subtitles =  temp_movie[0].subtitles 
            self.moviesModel.updateMovie(index, selectedLanguageXXX) #The treeview is filtered by language
            self.moviesView.collapse(index)
            self.moviesView.expand(index)
            self.progress(100)
            QCoreApplication.processEvents()
            self.window.setCursor(Qt.ArrowCursor)
        
def main(options):
    log.debug("Building main dialog")
#    app = QApplication(sys.argv)
#    splash = SplashScreen()
#    splash.showMessage(QApplication.translate("subdownloader", "Building main dialog..."))
    window = QMainWindow()
    window.setWindowTitle(APP_TITLE)
    window.setWindowIcon(QIcon(":/icon"))
    installErrorHandler(QErrorMessage(window))
    QCoreApplication.setOrganizationName("SubDownloader")
    QCoreApplication.setApplicationName(APP_TITLE)
    
    splash.finish(window)
    log.debug("Showing main dialog")
    Main(window,"", options)    
    
    return app.exec_()

#if __name__ == "__main__": 
#    sys.exit(main())
