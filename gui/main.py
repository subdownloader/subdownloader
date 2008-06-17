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
import commands
import platform

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
                    
        QObject.connect(self.folderView, SIGNAL("clicked(QModelIndex)"),  self.onFolderTreeClicked)
        
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
        
        #Menu options
        QObject.connect(self.action_Quit, SIGNAL("triggered()"), self.onMenuQuit)
        QObject.connect(self.action_HelpHomepage, SIGNAL("triggered()"), self.onMenuHelpHomepage)
        QObject.connect(self.action_HelpAbout, SIGNAL("triggered()"), self.onMenuHelpAbout)
        QObject.connect(self.action_HelpBug, SIGNAL("triggered()"), self.onMenuHelpBug)
        QObject.connect(self.action_HelpDonation, SIGNAL("triggered()"), self.onMenuHelpDonation)
        QObject.connect(self.action_ShowPreferences, SIGNAL("triggered()"), self.onMenuPreferences)

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
        totalVideoPlayers = settings.beginReadArray("options/videoPlayers")
        settings.endArray()
        if not totalVideoPlayers:
            self.initializeVideoPlayers(settings)
        

        #self.readOptionsSettings(settings) #Initialized Settings for the OPTIONS tab
    
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

    def onMenuQuit(self):
        self.window.close()
    
    def onMenuHelpAbout(self):
        dialog = aboutDialog(self)
        dialog.show()
        ok = dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def onMenuHelpHomepage(self):
         webbrowser.open( "http://code.google.com/p/subdownloader/", new=2, autoraise=1)

    def onMenuHelpBug(self):
        webbrowser.open( "http://code.google.com/p/subdownloader/issues", new=2, autoraise=1)

    def onMenuHelpDonation(self):
        webbrowser.open( "https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=donations%40subdownloader%2enet&no_shipping=0&no_note=1&tax=0&currency_code=EUR&lc=PT&bn=PP%2dDonationsBF&charset=UTF%2d8", new=2, autoraise=1)
        
    def onMenuPreferences(self):
        dialog = preferencesDialog(self)
        dialog.show()
        ok = dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def InitializeFilterLanguages(self):
        self.filterLanguageForVideo.addItem(QtGui.QApplication.translate("MainWindow", "All", None, QtGui.QApplication.UnicodeUTF8))
        self.filterLanguageForTitle.addItem(QtGui.QApplication.translate("MainWindow", "All", None, QtGui.QApplication.UnicodeUTF8))
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
    
        self.window.setCursor(Qt.ArrowCursor)
        #TODO: CHECK if our local subtitles are already in the server.
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
            #This should work in all the OS, creating a temporary file 
            tempSubFilePath = str(QDir.temp().absoluteFilePath("subdownloader.tmp.srt"))
            log.debug("Temporary subtitle will be downloaded into: %s" % tempSubFilePath)
            self.progress(0,"Downloading subtitle ... "+subtitle.getFileName())
            try:
                ok = self.OSDBServer.DownloadSubtitles({subtitleID:tempSubFilePath})
            except Exception, e: 
                traceback.print_exc(e)
                QMessageBox.about(self.window,"Error","Unable to download subtitle "+subtitle.getFileName())
            finally:
                self.progress(100)
            
            params = []
            programPath = str(videoPlayer['programPath'].toUtf8()) 
            parameters = str(videoPlayer['parameters'].toUtf8()) 

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
            
    def onButtonIMDB(self, checked):
        video = self.videoModel.getSelectedItem().data
        movie_info = video.getMovieInfo()
        if movie_info:
            webbrowser.open( "http://www.imdb.com/title/tt%s"% movie_info["IDMovieImdb"], new=2, autoraise=1)
            
    
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
    def onButtonDownload(self, checked):
        #We download the subtitle in the same folder than the video
            subs = self.videoModel.getCheckedSubtitles()
            replace_all  = False
            total_subs = len(subs)
            percentage = 100/total_subs
            count = 20
            answer = None
            success_downloaded = 0
            self.status("Connecting to download...")
            for sub in subs:
                destinationPath = str(self.getDownloadPath(sub.getVideo(), sub).toUtf8())
                if not destinationPath:
                    continue
                log.debug("Trying to download subtitle '%s'" % destinationPath)
                self.progress(count,"Downloading subtitle ... "+QFileInfo(destinationPath).fileName())
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
                   if self.OSDBServer.DownloadSubtitles({sub.getIdOnline():destinationPath}):
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
    

        
    def initializeVideoPlayers(self, settings):
        predefinedVideoPlayers = []
        if platform.system() == "Linux":
            status, path = commands.getstatusoutput("which mplayer")
            if status == 0: 
                predefinedVideoPlayers.append({'name': 'MPLAYER', 'programPath': path,  'parameters': '{0} -sub {1}'})
            status, path = commands.getstatusoutput("which vlc")
            if status == 0:
                predefinedVideoPlayers.append({'name': 'VLC', 'programPath': path,  'parameters': '{0} --sub-file {1}'})
        elif platform.system() == "Windows":
            pass #TODO: Detect from Registry the path of the Mplayer and VLC programs.

        settings.beginWriteArray("options/videoPlayers")
        for i, videoapp in enumerate(predefinedVideoPlayers):
            settings.setArrayIndex(i)
            settings.setValue("programPath",  QVariant(videoapp['programPath']))
            settings.setValue("parameters", QVariant( videoapp['parameters']))
            settings.setValue("name", QVariant( videoapp['name']))
        settings.endArray()
        
        defaultVideoApp = predefinedVideoPlayers[0]
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
    QCoreApplication.setOrganizationName("SubDownloader")
    QCoreApplication.setApplicationName(APP_TITLE)
    
    splash.finish(window)
    log.debug("Showing main dialog")
    Main(window,"", options)    
    
    return app.exec_()

#if __name__ == "__main__": 
#    sys.exit(main())
