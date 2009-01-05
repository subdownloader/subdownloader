#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) 2007 Ivan Garcia capiscuas@gmail.com
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    see <http://www.gnu.org/licenses/>.Warning

""" Create and launch the GUI """
import sys, re, os, traceback, tempfile
import time, thread
import webbrowser
import urllib2
import base64, zlib
import commands
import platform
import os.path
import zipfile


import __builtin__,gettext,locale

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QVariant, QSize, QEventLoop, QString, \
                         QBuffer, QIODevice, QModelIndex,QDir, QFileInfo, QTime, QFile
from PyQt4.QtGui import QProgressDialog, QPixmap, QSplashScreen, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel, QItemSelectionModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical, QApplication, QMainWindow


from gui.SplashScreen import SplashScreen, NoneSplashScreen
from FileManagement import get_extension, clear_string, without_extension


# create splash screen and show messages to the user
app = QApplication(sys.argv)
splash = SplashScreen()
splash.showMessage(_("Loading modules..."))
QCoreApplication.flush()
from modules import * 
from modules.SDService import SDService, TimeoutFunctionException

from gui import installErrorHandler, Error, _Warning, extension

from gui.uploadlistview import UploadListModel, UploadListView
from gui.videotreeview import VideoTreeModel

from gui.main_ui import Ui_MainWindow
from gui.imdbSearch import imdbSearchDialog
from gui.preferences import preferencesDialog
from gui.about import aboutDialog

from gui.chooseLanguage import chooseLanguageDialog
from gui.login import loginDialog
from FileManagement import FileScan, Subtitle
from modules.videofile import  *
from modules.subtitlefile import *
from modules.search import *
import modules.utils as utils
import languages.Languages as languages

if SHAREWARE:
    import gui.expiration as expiration
    
import logging
log = logging.getLogger("subdownloader.gui.main")
splash.showMessage(_("Building main dialog..."))

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

        self.log_packets = log_packets
        self.options = options
        self.upload_autodetected_lang = ""
        self.upload_autodetected_imdb = ""
        self.window = window
        
        self.calculateProgramFolder()
        self.SetupInterfaceLang()
        self.setupUi(window)
        window.closeEvent = self.close_event
        window.setWindowTitle(_("SubDownloader %s") % APP_VERSION)
        #Fill Out the Filters Language SelectBoxes
        QObject.connect(self, SIGNAL("filterLangChangedPermanent(QString)"), self.onFilterLangChangedPermanent)
        self.InitializeFilterLanguages()
        self.read_settings()
        #self.treeView.reset()
        window.show()
        self.splitter.setSizes([600, 1000])

        #SETTING UP FOLDERVIEW
        model = QDirModel(window)        
        model.setFilter(QDir.AllDirs|QDir.NoDotAndDotDot)
        self.folderView.setModel(model)
        
        settings = QSettings()
        
        #SHAREWARE PART
        if SHAREWARE:
            activation_email = settings.value('activation/email', QVariant())
            activation_licensekey = settings.value('activation/licensekey', QVariant())
            activation_fullname = settings.value('activation/fullname', QVariant())
            if activation_email != QVariant() and activation_licensekey != QVariant() and activation_fullname != QVariant():
                self.software_registered = True
            else:
                self.software_registered = False
                self.action_ActivateProgram = QtGui.QAction(self.window)
                daysLeft = expiration.calculateDaysLeft(time.time())
                self.action_ActivateProgram.setText(_("%d days to expire. Activate Program.") % daysLeft)
                QObject.connect(self.action_ActivateProgram, SIGNAL("triggered()"), self.onActivateMenu)
                self.menu_Help.addAction(self.action_ActivateProgram)
                QObject.connect(self, SIGNAL("ServerTime(float)"), self.decideExpiration)

        self.folderView.header().hide()
        self.folderView.hideColumn(3)
        self.folderView.hideColumn(2)
        self.folderView.hideColumn(1)
        self.folderView.show()
        
        self.showInstructions()
        
        #Loop to expand the current directory in the folderview.
        lastDir = settings.value("mainwindow/workingDirectory", QVariant(QDir.rootPath()))
        log.debug('Current directory: %s' % lastDir.toString())
        path = QDir(lastDir.toString())
        while True:
            self.folderView.expand(model.index(path.absolutePath()))
            if not path.cdUp(): break
        
        self.folderView.scrollTo(model.index(lastDir.toString()))
        QObject.connect(self.folderView, SIGNAL("clicked(QModelIndex)"),  self.onFolderTreeClicked)
        QObject.connect(self.buttonFind, SIGNAL("clicked(bool)"), self.onButtonFind)
        
        #SETTING UP SEARCH_VIDEO_VIEW
        self.videoModel = VideoTreeModel(window)
        self.videoView.setModel(self.videoModel)
        QObject.connect(self.videoView, SIGNAL("activated(QModelIndex)"), self.onClickVideoTreeView)
        QObject.connect(self.videoView, SIGNAL("clicked(QModelIndex)"), self.onClickVideoTreeView)
        QObject.connect(self.videoView, SIGNAL("customContextMenuRequested(QPoint)"), self.onContext)
        QObject.connect(self.videoModel, SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.subtitlesCheckedChanged)
        
        QObject.connect(self.buttonSearchSelectVideos, SIGNAL("clicked(bool)"), self.onButtonSearchSelectVideos)
        QObject.connect(self.buttonSearchSelectFolder, SIGNAL("clicked(bool)"), self.onButtonSearchSelectFolder)
        QObject.connect(self.buttonDownload, SIGNAL("clicked(bool)"), self.onButtonDownload)
        QObject.connect(self.buttonPlay, SIGNAL("clicked(bool)"), self.onButtonPlay)
        QObject.connect(self.buttonIMDB, SIGNAL("clicked(bool)"), self.onViewOnlineInfo)
        self.videoView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) 
        
        #Drag and Drop files to the videoView enabled
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
        QObject.connect(self.uploadView, SIGNAL("activated(QModelIndex)"), self.onUploadClickViewCell)
        QObject.connect(self.uploadView, SIGNAL("clicked(QModelIndex)"), self.onUploadClickViewCell)
        
        QObject.connect(self.buttonUpload, SIGNAL("clicked(bool)"), self.onUploadButton)
        
        QObject.connect(self.buttonUploadUpRow, SIGNAL("clicked(bool)"), self.uploadModel.onUploadButtonUpRow)
        QObject.connect(self.buttonUploadDownRow, SIGNAL("clicked(bool)"), self.uploadModel.onUploadButtonDownRow)
        QObject.connect(self.buttonUploadPlusRow, SIGNAL("clicked(bool)"), self.uploadModel.onUploadButtonPlusRow)
        QObject.connect(self.buttonUploadMinusRow, SIGNAL("clicked(bool)"), self.uploadModel.onUploadButtonMinusRow)
        QObject.connect(self.buttonUploadDeleteAllRow, SIGNAL("clicked(bool)"), self.uploadModel.onUploadButtonDeleteAllRow)
        
        QObject.connect(self.buttonUploadFindIMDB, SIGNAL("clicked(bool)"), self.onButtonUploadFindIMDB)
        QObject.connect(self.uploadIMDB, SIGNAL("activated(int)"), self.onUploadSelectImdb)
        
        self.uploadSelectionModel = QItemSelectionModel(self.uploadModel)
        self.uploadView.setSelectionModel(self.uploadSelectionModel)
        QObject.connect(self.uploadSelectionModel, SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self.onUploadChangeSelection)
        QObject.connect(self, SIGNAL("imdbDetected(QString,QString,QString)"), self.onUploadIMDBNewSelection)
        QObject.connect(self, SIGNAL("release_updated(QString)"), self.OnChangeReleaseName)
        
        QObject.connect(self, SIGNAL("SoftwareUpdateDetected(QString,QString)"), self.OnSoftwareUpdateDetected)
        
        self.label_autodetect_imdb.hide()
        self.label_autodetect_lang.hide()
        #print self.uploadView.sizeHint ()
        #self.uploadView.adjustSize()
        #self.groupBox_2.adjustSize()
        #self.uploadDetailsGroupBox.adjustSize()
        #self.window.adjustSize()
        
        #Search by Name
        QObject.connect(self.buttonSearchByName, SIGNAL("clicked(bool)"), self.onButtonSearchByTitle)
        QObject.connect(self.movieNameText, SIGNAL("returnPressed()"), self.onButtonSearchByTitle)
        QObject.connect(self.buttonDownloadByTitle, SIGNAL("clicked(bool)"), self.onButtonDownloadByTitle)
        QObject.connect(self.buttonIMDBByTitle, SIGNAL("clicked(bool)"), self.onViewOnlineInfo)
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
        QObject.connect(self.window, SIGNAL("setLoginStatus(QString)"), self.onChangeLoginStatus)
        
        self.status_progress = None #QtGui.QProgressBar(self.statusbar)
        #self.status_progress.setProperty("value",QVariant(0))
        self.login_button = QtGui.QPushButton(_("Not logged yet"))
        QObject.connect(self.action_Login, SIGNAL("triggered()"), self.onButtonLogin)
        QObject.connect(self.login_button, SIGNAL("clicked(bool)"), self.onButtonLogin)
        #self.status_progress.setOrientation(QtCore.Qt.Horizontal)
        self.status_label = QtGui.QLabel("v"+ APP_VERSION,self.statusbar)
        self.status_label.setIndent(10)
        
        self.donate_button = QtGui.QPushButton("   " + _("Help Us With 5 USD/EUR"))
        #self.donate_button.setIndent(10)
        
        iconpaypal = QtGui.QIcon()
        iconpaypal.addPixmap(QtGui.QPixmap(":/images/paypal.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        if platform.system() == "Windows":
            self.donate_button.setIcon(iconpaypal)
            self.donate_button.setIconSize(QtCore.QSize(50, 24))
            
        QObject.connect(self.donate_button, SIGNAL("clicked(bool)"), self.onMenuHelpDonation)
        
        self.statusbar.insertWidget(0,self.status_label)
        self.statusbar.insertWidget(1,self.login_button)
        self.statusbar.addPermanentWidget(self.donate_button, 0)
        #self.statusbar.addPermanentWidget(self.login_button,0)
        #self.statusbar.addPermanentItem(horizontalLayout_4,2)
        #self.status("")
        
        if not options.test:
            #print self.OSDBServer.xmlrpc_server.GetTranslation(self.OSDBServer._token, 'ar', 'po','subdownloader')
            self.window.setCursor(Qt.WaitCursor)
            if self.establishServerConnection():# and self.OSDBServer.is_connected():
                thread.start_new_thread(self.update_users, (300, )) #update the users counter every 5min
                thread.start_new_thread(self.detect_software_updates, ())
                if SHAREWARE:
                   if not self.software_registered:
                            thread.start_new_thread(self.getServerTime, ())
                   else:
                            activation_email = unicode(settings.value('activation/email', QVariant()).toString())
                            activation_licensekey = unicode(settings.value('activation/licensekey', QVariant()).toString())
                            activation_fullname = unicode(settings.value('activation/fullname', QVariant()).toString())
                            QObject.connect(self, SIGNAL("CheckedRegisteredLicense(QString,QString,QString,QString)"), self.onCheckedRegisteredLicense)
                            thread.start_new_thread(self.checkRegisteredLicense, (activation_email, activation_licensekey, activation_fullname))
                            
                settings = QSettings()
                if options.username:
                    loginUsername = options.username
                    loginPassword = options.password
                else:
                    loginUsername = str(settings.value("options/LoginUsername", QVariant()).toString().toUtf8())
                    loginPassword = str(settings.value("options/LoginPassword", QVariant()).toString().toUtf8())
                #thread.start_new_thread(self.login_user, (settingsUsername,settingsPassword,window, ))
                self.login_user(loginUsername,loginPassword,self.window)
            else:
                QMessageBox.about(self.window,_("Error"),_("Error contacting the server. Please try again later"))
            self.window.setCursor(Qt.ArrowCursor)
        QCoreApplication.processEvents()
        
        if options.videofile:
                if os.path.exists(options.videofile):
                        self.SearchVideos(options.videofile)
                else:
                        QMessageBox.about(self.window,_("Error"),_("Unable to find %s") % options.videofile)
            
    
    def SetupInterfaceLang(self):
        if platform.system() == "Linux":
                if self.programFolder == '/usr/share/subdownloader':
                        localedir = '/usr/share/locale/'
                else:
                        localedir = 'locale'
        else:
                localedir = 'locale'
                #Get the local directory since we are not installing anything
                #local_path = os.path.realpath(os.path.dirname(sys.argv[0]))
                #print local_path
            
        #localedir = 'locale' #remove
        
        log.debug('Scanning translation files .mo in folder: %s' %localedir)
        self.interface_langs = [] 
        for root, dirs, files in os.walk(localedir):
                if re.search(".*locale$", os.path.split(root)[0]):
                        _lang = os.path.split(root)[-1]
                
                if 'subdownloader.mo' in files:
                        self.interface_langs.append(_lang)
        
        log.debug('Found these translations languages: %r' % self.interface_langs)
                
        #Check the default locale
        lc, encoding = locale.getdefaultlocale()
        if not lc:
            user_locale = 'en' #english will be the default locale in case of not found
        else:
            if lc in languages.ListAll_locale():
                user_locale = lc
            else:
                user_locale = lc.split('_')[0]
        
        settings = QSettings()
        interface_lang = settings.value("options/interfaceLang", QVariant())
        if not len(self.interface_langs):
                interface_lang = 'en'
        else:
                if interface_lang == QVariant():
                        interface_lang = self.chooseInterfaceLanguage(user_locale)
                        settings.setValue("options/interfaceLang", QVariant(interface_lang))
                else:
                        interface_lang = str(interface_lang.toString().toUtf8())
        
        log.debug('Interface language: %s' % interface_lang)
        try:
            isTrans = gettext.translation(domain = "subdownloader",localedir = localedir ,languages=[interface_lang],fallback=True)
        except IOError:
            isTrans = False

        if isTrans:
                # needed for the _ in the __init__ plugin (menuentry traduction)
                __builtin__._ = lambda s : gettext.translation("subdownloader",localedir = localedir,languages=[interface_lang],fallback=True).ugettext(s)
        else:
                __builtin__._ = lambda x : x
                
    def chooseInterfaceLanguage(self, user_locale):
        self.choosenLanguage = 'en' #By default
        dialog = chooseLanguageDialog(self, user_locale)
        dialog.show()
        ok = dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        return self.choosenLanguage

    def calculateProgramFolder(self):
        if os.path.isdir(sys.path[0]): #for Linux is /program_folder/
            self.programFolder =  sys.path[0]
        else: #for Windows is the /program_folder/run.py
            self.programFolder =  os.path.dirname(sys.path[0])
            
    def showInstructions(self):
            introduction = '<p align="center"><h2>%s</h2></p>' \
                                    '<p><b>%s</b><br>%s</p>' \
                                    '<p><b>%s</b><br>%s</p>'\
                                    '<p><b>%s</b><br>%s</p>'  % (_("How To Use SubDownloader"), \
                                     _("1st Tab:"), _("Select, from the Folder Tree on the left, the folder which contains the videos that need subtitles. SubDownloader will then try to automatically find available subtitles."), \
                                     _("2nd Tab:"),_("If you don't have the videos in your machine, you can search subtitles by introducing the title/name of the video."), \
                                    _("3rd Tab:"),_("If you have found some subtitle somewhere else that it's not in SubDownloader database, please upload those subtitles so next users will be able to find them more easily."))
            introduction += '<p><b>%s</b><br>%s</p>' % (_("Quid Pro Quo:"),_("If you think this program is useful and has saved you plenty of time, please help us by making a donation."))
            
            self.introductionHelp.setHtml(introduction)
            self.videoView.hide()
            self.label_filterBy.hide()
            self.label_videosFound.hide()
            self.filterLanguageForVideo.hide()
            self.buttonDownload.hide()
            self.buttonIMDB.hide()
            self.buttonPlay.hide()
            
    def hideInstructions(self):
            self.videoView.show()
            self.label_filterBy.show()
            self.label_videosFound.show()
            self.filterLanguageForVideo.show()
            self.buttonDownload.show()
            self.buttonIMDB.show()
            self.buttonPlay.show()
            self.introductionHelp.hide()

    def openExternalUrl(self, url):
            webbrowser.open( unicode(url.toString()), new=2, autoraise=1)
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
                            subWebsiteAction = QtGui.QAction(QIcon(":/images/info.png"),_("View IMDB info"), self)
                            QObject.connect(subWebsiteAction, SIGNAL("triggered()"), self.onViewOnlineInfo)
                        else:
                            subWebsiteAction = QtGui.QAction(QIcon(":/images/info.png"),_("Set IMDB info..."), self)
                            QObject.connect(subWebsiteAction, SIGNAL("triggered()"), self.onSetIMDBInfo)
                        menu.addAction(subWebsiteAction) 
                elif type(treeItem.data) == SubtitleFile: #Subtitle
                    treeItem.checked = True
                    self.videoModel.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
                    downloadAction = QtGui.QAction(QIcon(":/images/download.png"), _("Download"), self)
                    if self.tabs.currentIndex() == 0: #Video tab, TODO:Replace me with a enum
                        QObject.connect(downloadAction, SIGNAL("triggered()"), self.onButtonDownload)
                        playAction = QtGui.QAction(QIcon(":/images/play.png"),_("Play video + subtitle"), self)
                        QObject.connect(playAction, SIGNAL("triggered()"), self.onButtonPlay)
                        menu.addAction(playAction) 
                    else:
                        QObject.connect(downloadAction, SIGNAL("triggered()"), self.onButtonDownloadByTitle)
                    subWebsiteAction = QtGui.QAction(QIcon(":/images/sites/opensubtitles.png"),_("View online info"), self)
                    
                    menu.addAction(downloadAction) 
                    QObject.connect(subWebsiteAction, SIGNAL("triggered()"), self.onViewOnlineInfo)
                    menu.addAction(subWebsiteAction) 
                elif type(treeItem.data) == Movie:
                    movie = treeItem.data
                    subWebsiteAction = QtGui.QAction(QIcon(":/images/info.png"),_("View IMDB info"), self)
                    QObject.connect(subWebsiteAction, SIGNAL("triggered()"), self.onViewOnlineInfo)
                    menu.addAction(subWebsiteAction) 

            # Show the context menu. 
            menu.exec_(listview.mapToGlobal(point)) 
    
    def onSetIMDBInfo(self):
        QMessageBox.about(self.window,_("Info"),"Not implemented yet. Please donate.")
        
    def onViewOnlineInfo(self):
        if self.tabs.currentIndex() == 0: #Tab for SearchByHash TODO:replace this 0 by an ENUM value
                listview = self.videoView
        else:
                listview = self.moviesView
        index = listview.currentIndex()
        treeItem = listview.model().getSelectedItem(index)
        
        if type(treeItem.data) == VideoFile:
            video = self.videoModel.getSelectedItem().data
            movie_info = video.getMovieInfo()
            if movie_info:
                imdb = movie_info["IDMovieImdb"]
                if imdb:
                    webbrowser.open( "http://www.imdb.com/title/tt%s"% imdb , new=2, autoraise=1)
        elif type(treeItem.data) == SubtitleFile: #Subtitle
            sub = treeItem.data
            #print  sub.isOnline()
            if sub.isOnline():
                webbrowser.open( "http://www.opensubtitles.org/en/subtitles/%s/"% sub.getIdOnline(), new=2, autoraise=1)

        elif type(treeItem.data) == Movie:
                movie = self.moviesModel.getSelectedItem().data
                imdb = movie.IMDBId
                if imdb:
                    webbrowser.open( "http://www.imdb.com/title/tt%s"% imdb , new=2, autoraise=1)
            
    def read_settings(self):
        settings = QSettings()
        self.window.resize(settings.value("mainwindow/size", QVariant(QSize(1000, 400))).toSize())
        pos = settings.value("mainwindow/pos", QVariant())
        if pos != QVariant():
                self.window.move(pos.toPoint())
            
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
        settings.setValue("mainwindow/pos", QVariant(self.window.pos()))
    
    def close_event(self, e):
        self.write_settings()
        e.accept()
    
    def OnSoftwareUpdateDetected(self, new_version, update_link):
        warningBox = QMessageBox(_("New Version Detected"), 
                                    _("A new version of SubDownloader has been released.\n\nNew Version: %s\nCurrent Version: %s\n\n" \
                                    "Would you like to download the new version now?") %(new_version, APP_VERSION) , 
                                    QMessageBox.Information, 
                                    QMessageBox.Yes | QMessageBox.Default ,
                                    QMessageBox.Cancel | QMessageBox.Escape, 
                                    QMessageBox.NoButton, 
                                    self.window)
        answer = warningBox.exec_()
        if answer == QMessageBox.Yes:
            webbrowser.open( update_link, new=2, autoraise=1)
        elif answer == QMessageBox.Cancel :
            return
            
    def detect_software_updates(self):
        # REMARK: to be used by a thread
        #try:
                result = self.SDDBServer.CheckSoftwareUpdates('SubDownloader')
                if utils.compVer(result['latest_version'], APP_VERSION) == 1:  #if APP_VERSION is < than latest_version 
                        self.emit(SIGNAL("SoftwareUpdateDetected(QString,QString)"),result['latest_version'], result['link'])
        #except:
           #     log.debug('Error while asking server CheckSoftwareUpdates()')
                
    def update_users(self, sleeptime=60):
        # REMARK: to be used by a thread
        while 1:
            self.status_label.setText(_("Users online: Updating..."))
            try:
                data = self.OSDBServer.ServerInfo() # we cant use the timeout class inherited in OSDBServer
                self.status_label.setText(_("Users online: %s" % str(data["users_online_program"])))
            except:
                self.status_label.setText(_("Users online: ERROR"))
            time.sleep(sleeptime)
    
    def onButtonLogin(self):
        dialog = loginDialog(self)
        dialog.show()
        ok = dialog.exec_()
        
    def login_user(self, username, password, window):
        #window.emit(SIGNAL('setLoginStatus(QString)'),"Trying to login...")
        self.status_progress = QProgressDialog(_("Logging in..."), _("&Cancel"), 0,0, window)
        self.status_progress.setWindowTitle(_("Logging in..."))
        self.status_progress.setCancelButton(None)
        self.status_progress.show()
        self.login_button.setText(_("Logging in..."))
        self.progress(0)
        
        QCoreApplication.processEvents()
        try:
            if self.OSDBServer._login(username, password):
                if not username: 
                    username = _('Anonymous')
                self.login_button.setText(_("Logged as %s") % username)
                self.status_progress.close()
                return True
            elif username: #We try anonymous login in case the normal user login has failed
                self.login_button.setText(_("Login as %s: ERROR") % username)
                self.status_progress.close()
                return False
        except Exception, e:
            self.login_button.setText(_("Login: ERROR"))
            traceback.print_exc(e)
            self.status_progress.close()
            return False

    def onMenuQuit(self):
        self.window.close()
    
    def setTitleBarText(self, text):
        self.window.setWindowTitle(_("SubDownloader %s - %s") % (APP_VERSION , text))
        
    def onChangeTitleBarText(self, title):
        self.setTitleBarText(title)
        
    def onChangeLoginStatus(self, statusMsg):
        self.login_button.setText(statusMsg)
        QCoreApplication.processEvents()
    
    def onActivateMenu(self):
        daysLeft = expiration.calculateDaysLeft(time.time())
        expirationDialog = expiration.expirationDialog(self, daysLeft)
        expirationDialog.show()
        ok = expirationDialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
    
    def onCheckedRegisteredLicense(self, result, email, licensekey, fullname):
        settings = QSettings()
        if result == "REGISTERED":
             self.setTitleBarText(_('Program Registered'))
        elif result == "DISABLED_TOO_MANY":
            QMessageBox.about(self.window,_("Error"),"Your License Key has been disabled because of too many suspicious registrations in a short period of time.\nIf you think this is a mistake contact us at licenses@subdownloader.net")
            settings.remove('activation/email')
            settings.remove('activation/licensekey')
            settings.remove('activation/fullname')
            self.window.close()
            sys.exit(1)
        else:
            QMessageBox.about(self.window,_("Error"),"Invalid License Key Registration.")
            settings.remove('activation/email')
            settings.remove('activation/licensekey')
            settings.remove('activation/fullname')
            self.window.close()
            sys.exit(1)
    def checkRegisteredLicense(self, email, licensekey, fullname):
            log.debug("Checking Registered License: %s - %s - %s" % (email, licensekey, fullname))
            result =  self.SDDBServer.xmlrpc_server.CheckSoftwareLicense(APP_VERSION,email, fullname, licensekey, False)
            log.debug("License Status : %s" % result)
            self.emit(SIGNAL("CheckedRegisteredLicense(QString,QString,QString,QString)"),result, email, licensekey, fullname)
            
    def getServerTime(self):
        try:
            time.sleep(5)
            log.debug("Getting time from Server...")
            server_time = self.SDDBServer.xmlrpc_server.GetTimeStamp()
            log.debug("Time: %r" % server_time)
            self.emit(SIGNAL("ServerTime(float)"),server_time)
        except:
            pass
        
    def decideExpiration(self, server_time):
        daysLeft = expiration.calculateDaysLeft(server_time)
        settings = QSettings()
        
        self.setTitleBarText(_("(Unregistered Program, %d days to expire)") % daysLeft)
        if daysLeft == 0:
                expirationDialog = expiration.expirationDialog(self, daysLeft)
                expirationDialog.show()
                ok = expirationDialog.exec_()
                QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
                if ok == QDialog.Rejected:
                    self.window.close()
                    sys.exit(1)
                    
        elif daysLeft <= 20 and daysLeft > 10 and not settings.value("expiration/reminder20", QVariant(False)).toBool():
                self.showExpirationWarning(daysLeft)
                settings.setValue("expiration/reminder20", QVariant(True))
        elif daysLeft <= 10  and not settings.value("expiration/reminder10", QVariant(False)).toBool():
                self.showExpirationWarning(daysLeft)
                settings.setValue("expiration/reminder10", QVariant(True))
        
    def showExpirationWarning(self, daysLeft):
        reminderBox = QMessageBox(_("Expiration Reminder"),_("The program will expire in %d days.\nWould you like to activate it now?") % daysLeft, QMessageBox.Warning, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton , QMessageBox.NoButton, self.window)
        activateButton = reminderBox.addButton(QString(_("Activate")), QMessageBox.ActionRole)
        reminderBox.exec_()
        answer = reminderBox.clickedButton()
        if answer == activateButton:
            expirationDialog = expiration.expirationDialog(self, daysLeft)
            expirationDialog.show()
            ok = expirationDialog.exec_()
            QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
            
    def onMenuHelpAbout(self):
        dialog = aboutDialog(self)
        dialog.ui.label_version.setText(APP_VERSION)
        dialog.show()
        ok = dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def onMenuHelpHomepage(self):
         webbrowser.open( "http://www.subdownloader.net/", new=2, autoraise=1)

    def onMenuHelpBug(self):
        webbrowser.open( "https://bugs.launchpad.net/subdownloader", new=2, autoraise=1)

    def onMenuHelpDonation(self):
        webbrowser.open( "http://www.subdownloader.net/donations.html", new=2, autoraise=1)
        
    def onMenuPreferences(self):
        dialog = preferencesDialog(self)
        dialog.show()
        ok = dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def InitializeFilterLanguages(self):
        self.filterLanguageForVideo.addItem(_("All languages"), QVariant(''))
        self.filterLanguageForTitle.addItem(_("All languages"), QVariant(''))
        for lang in languages.LANGUAGES:
            self.filterLanguageForVideo.addItem(_(lang["LanguageName"]),  QVariant(lang["SubLanguageID"]))
            self.filterLanguageForTitle.addItem(_(lang["LanguageName"]), QVariant(lang["SubLanguageID"]))
            self.uploadLanguages.addItem(_(lang["LanguageName"]), QVariant(lang["SubLanguageID"]))
        
        settings = QSettings()
        optionUploadLanguage = settings.value("options/uploadLanguage", QVariant("eng"))
        index = self.uploadLanguages.findData(optionUploadLanguage)
        if index != -1 :
            self.uploadLanguages.setCurrentIndex (index)    
        
        self.filterLanguageForVideo.adjustSize()
        self.filterLanguageForTitle.adjustSize()
        self.uploadLanguages.adjustSize()
        
        optionFilterLanguage = str(settings.value("options/filterSearchLang", QVariant("")).toString())
        
        self.emit(SIGNAL('filterLangChangedPermanent(QString)'),optionFilterLanguage)
        
        QObject.connect(self.filterLanguageForVideo, SIGNAL("currentIndexChanged(int)"), self.onFilterLanguageVideo)
        QObject.connect(self.filterLanguageForTitle, SIGNAL("currentIndexChanged(int)"), self.onFilterLanguageSearchName)
        QObject.connect(self.uploadLanguages, SIGNAL("activated(int)"), self.onUploadSelectLanguage)
        QObject.connect(self.uploadLanguages, SIGNAL("language_updated(QString,QString)"), self.onUploadLanguageDetection)

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
            self.videoModel.unselectSubtitles()
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
        if not hasattr(self, 'OSDBServer') or not self.OSDBServer.is_connected():
                QMessageBox.about(self.window,_("Error"),_("You are not connected to the server. Please reconnect first."))
        else:
                #Scan recursively the selected directory finding subtitles and videos
                if not type(path) == list:
                    path = [path]
                
                self.status_progress = QProgressDialog(_("Scanning files"), _("&Abort"), 0, 100, self.window)
                self.status_progress.setWindowTitle(("Scanning files"))
                self.status_progress.forceShow()
                self.progress(-1)
                try:
                    videos_found,subs_found = FileScan.ScanFilesFolders(path,recursively = True,report_progress = self.progress)
                    #progressWindow.destroy()
                except FileScan.UserActionCanceled:
                    print "user canceled"
                    return 
                log.debug("Videos found: %s"% videos_found)
                log.debug("Subtitles found: %s"% subs_found)
                self.status_progress.close()
                
                self.hideInstructions()
                
                self.window.setCursor(Qt.ArrowCursor)
                #Populating the items in the VideoListView
                self.videoModel.clearTree()
                self.videoView.expandAll()
                self.videoModel.setVideos(videos_found)
                self.videoView.setModel(self.videoModel)
                self.videoModel.videoResultsBackup = []
                
                self.videoView.expandAll() #This was a solution found to refresh the treeView
                #Searching our videohashes in the OSDB database
                QCoreApplication.processEvents()
                if not videos_found:
                    QMessageBox.about(self.window,_("Scan Results"),_("No video has been found"))
                else:
                    self.window.setCursor(Qt.WaitCursor)
                    self.status_progress = QProgressDialog(_("Searching subtitles..."), _("&Abort"), 0, 100, self.window)
                    self.status_progress.setWindowTitle(_("Asking Server..."))
                    self.status_progress.forceShow()
                    self.progress(1)
                    i = 0
                    total = len(videos_found)
                    if self.SDDBServer: #only sending those hashes bigger than 12MB
                        videos_sddb = [video for video in videos_found if int(video.getSize()) >  12000000]
                        if videos_sddb:
                                thread.start_new_thread(self.SDDBServer.SearchSubtitles, ('',videos_sddb, ))
                    while i < total :
                            next = min(i+10, total)
                            videos_piece = videos_found[i:next]
                            progress_percentage = int(i * 100/total )
                            self.progress(progress_percentage ,_("Searching subtitles ( %d / %d )") % (i, total))
                            if not self.progress():
                                print "canceled"
                                self.window.setCursor(Qt.ArrowCursor)
                                return
                            videoSearchResults = self.OSDBServer.SearchSubtitles("",videos_piece)
                            i += 10

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
                                #self.videoModel.clearTree()
                                self.videoModel.setVideos(videoSearchResults, filter=None, append=True)
                                self.onFilterLanguageVideo(self.filterLanguageForVideo.currentIndex())
                                self.videoView.expandAll() #This was a solution found to refresh the treeView
                            elif videoSearchResults == None :
                                QMessageBox.about(self.window,_("Error"),_("Error contacting the server. Please try again later"))
                                return
                        
                            if locals().has_key('videoSearchResults'):
                                video_osdb_hashes = [video.calculateOSDBHash() for video in videoSearchResults]
                                
                                video_filesizes =  [video.getSize() for video in videoSearchResults]
                                video_movienames = [video.getMovieName() for video in videoSearchResults]
                                
                                
#                                thread.start_new_thread(self.SDDBServer.sendHash, (video_hashes,video_movienames,  video_filesizes,  ))
                    
                    self.status_progress.setLabelText(_("Search finished"))
                    self.progress(-1)
                    self.status_progress.close()
                    self.window.setCursor(Qt.ArrowCursor)
                            
                #TODO: CHECK if our local subtitles are already in the server, otherwise suggest to upload
                #self.OSDBServer.CheckSubHash(sub_hashes)
    

    def onClickVideoTreeView(self, index):
        treeItem = self.videoModel.getSelectedItem(index)
        if type(treeItem.data) == VideoFile:
            video = treeItem.data
            if video.getMovieInfo():
                self.buttonIMDB.setEnabled(True)
                self.buttonIMDB.setIcon(QIcon(":/images/info.png"))
                self.buttonIMDB.setText(_("Movie Info"))
        else:
            treeItem.checked = not(treeItem.checked)
            self.videoModel.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
            self.buttonIMDB.setEnabled(True)
            self.buttonIMDB.setIcon(QIcon(":/images/sites/opensubtitles.png"))
            self.buttonIMDB.setText(_("Sub Info"))

    def onClickMovieTreeView(self, index):
        treeItem = self.moviesModel.getSelectedItem(index)
        if type(treeItem.data) == Movie:
            movie = treeItem.data
            if movie.IMDBId:
                self.buttonIMDBByTitle.setEnabled(True)
                self.buttonIMDBByTitle.setIcon(QIcon(":/images/info.png"))
                self.buttonIMDBByTitle.setText(_("Movie Info"))
        else:
            treeItem.checked = not(treeItem.checked)
            self.moviesModel.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
            self.buttonIMDBByTitle.setEnabled(True)
            self.buttonIMDBByTitle.setIcon(QIcon(":/images/sites/opensubtitles.png"))
            self.buttonIMDBByTitle.setText(_("Sub Info"))

    def onButtonFind(self):
        folder_path = None
        for index in self.folderView.selectedIndexes():
            folder_path = str(self.folderView.model().filePath(index).toUtf8())
        
        if not folder_path:
            QMessageBox.about(self.window,_("Info"),_("You must select a folder first"))
        else:
            settings = QSettings()
            settings.setValue("mainwindow/workingDirectory", QVariant(folder_path))
            self.SearchVideos(folder_path) 
            
    def onButtonSearchSelectVideos(self):
        if not hasattr(self, 'OSDBServer') or not self.OSDBServer.is_connected():
            QMessageBox.about(self.window,_("Error"),_("You are not connected to the server. Please reconnect first."))
        else:
            settings = QSettings()
            currentDir = settings.value("mainwindow/workingDirectory", QVariant())
            fileNames = QFileDialog.getOpenFileNames(None, _("Select the video(s) that need subtitles"), currentDir.toString(), videofile.SELECT_VIDEOS)
            fileNames = [str(file.toUtf8()) for file in fileNames]
            if fileNames:
                settings.setValue("mainwindow/workingDirectory", QVariant(QFileInfo(fileNames[0]).absolutePath()))
                self.SearchVideos(fileNames) 
    def onButtonSearchSelectFolder(self):
        if not hasattr(self, 'OSDBServer') or not self.OSDBServer.is_connected():
            QMessageBox.about(self.window,_("Error"),_("You are not connected to the server. Please reconnect first."))
        else:
            settings = QSettings()
            path = settings.value("mainwindow/workingDirectory", QVariant())
            directory=QtGui.QFileDialog.getExistingDirectory(None,_("Select the directory that contains your videos"),path.toString())
            if directory:
                settings.setValue("mainwindow/workingDirectory", QVariant(directory))
                folder_path =  str(directory.toUtf8())
                self.SearchVideos(folder_path) 
        
        
    """What to do when a Folder in the tree is clicked"""
    def onFolderTreeClicked(self, index):
            if index.isValid():
                now = QTime.currentTime()
                if now > self.timeLastSearch.addMSecs(500):
                        if not self.folderView.model().hasChildren(index):
                                settings = QSettings()
                                folder_path = unicode(self.folderView.model().filePath(index))
                                settings.setValue("mainwindow/workingDirectory", QVariant(folder_path))
                                self.SearchVideos(folder_path) 
                                self.timeLastSearch = QTime.currentTime()
                        self.buttonFind.setEnabled(True)


    def onButtonPlay(self):
        settings = QSettings()
        programPath = settings.value("options/VideoPlayerPath", QVariant()).toString()
        parameters = settings.value("options/VideoPlayerParameters", QVariant()).toString()
        if programPath == QString(): 
            QMessageBox.about(self.window,_("Error"),_("No default video player has been defined in Settings."))
            return
        else:
            subtitle = self.videoModel.getSelectedItem().data
            moviePath = subtitle.getVideo().getFilePath()
            subtitleFileID= subtitle.getIdFileOnline()
            #This should work in all the OS, creating a temporary file 
            tempSubFilePath = str(QDir.temp().absoluteFilePath("subdownloader.tmp.srt"))
            log.debug("Temporary subtitle will be downloaded into: %s" % tempSubFilePath)
            self.status_progress = QProgressDialog(_("Downloading files..."), _("&Abort"), 0, 0, self.window)
            self.status_progress.setWindowTitle(_("Playing video + sub"))
            self.window.setCursor(Qt.BusyCursor)
            self.status_progress.show()
            self.progress(-1)
            try:
                ok = self.OSDBServer.DownloadSubtitles({subtitleFileID:tempSubFilePath})
                if not ok:
                    QMessageBox.about(self.window,_("Error"),_("Unable to download subtitle %s") % subtitle.getFileName())
            except Exception, e: 
                traceback.print_exc(e)
                QMessageBox.about(self.window,_("Error"),_("Unable to download subtitle %s") % subtitle.getFileName())
            finally:
                self.status_progress.close()
                self.window.setCursor(Qt.ArrowCursor)
            
            params = []
            programPath = str(programPath.toUtf8()) 
            parameters = str(parameters.toUtf8()) 

            for param in parameters.split(" "):
                if platform.system() == "Windows":
                    param = param.replace('{0}', '"' + moviePath + '"'  )
                else:
                    param = param.replace('{0}', moviePath)
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
                QMessageBox.about(self.window,_("Error"),_("Unable to launch videoplayer"))

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
            downloadFullPath = QFileDialog.getSaveFileName(None, _("Save as..."), downloadFullPath, sub_extension).__str__()
            log.debug("Downloading to: %r"% downloadFullPath)
        elif optionWhereToDownload == QVariant("SAME_FOLDER"):
            folderPath = video.getFolderPath()
            dir = QDir(QString(folderPath))
            #downloadFullPath = dir.filePath(QString(subFileName)).__str__()
            downloadFullPath = os.path.join(folderPath, subFileName).decode('utf8')
            log.debug("Downloading to: %r"% downloadFullPath)
        elif optionWhereToDownload == QVariant("PREDEFINED_FOLDER"):
            folderPath = settings.value("options/whereToDownloadFolder", QVariant("")).toString()
            dir = QDir(QString(folderPath)) 
            downloadFullPath = dir.filePath(QString(subFileName)).__str__()
            log.debug("Downloading to: %r"% downloadFullPath)

        return downloadFullPath
    def onButtonDownload(self):
        #We download the subtitle in the same folder than the video
            subs = self.videoModel.getCheckedSubtitles()
            replace_all  = False
            if not subs:
                QMessageBox.about(self.window,_("Error"),_("No subtitles selected to be downloaded"))
                return
            total_subs = len(subs)
            percentage = 100/total_subs
            count = 0
            answer = None
            success_downloaded = 0
            
            self.status_progress = QProgressDialog(_("Downloading files..."), _("&Abort"), 0, 100, self.window)
            self.status_progress.setWindowTitle(_('Downloading files...'))
            self.status_progress.forceShow()
            for i, sub in enumerate(subs):
                if not self.progress():
                    break
                destinationPath = self.getDownloadPath(sub.getVideo(), sub)
                if not destinationPath:
                    break
                log.debug("Trying to download subtitle '%s'" % destinationPath)
                self.progress(count,_("Downloading subtitle %s (%d/%d)") % (QFileInfo(destinationPath).fileName(), i + 1, total_subs))
                
                #Check if we have write permissions, otherwise show warning window
                while True: 
                    #If the file and the folder don't have writte access.
                    if not QFileInfo(destinationPath).isWritable() and not QFileInfo(QFileInfo(destinationPath).absoluteDir().path()).isWritable() :
                        warningBox = QMessageBox(_("Error write permission"), 
                                                                    _("%s cannot be saved.\nCheck that the folder exists and you have write-access permissions.") %destinationPath , 
                                                                    QMessageBox.Warning, 
                                                                    QMessageBox.Retry | QMessageBox.Default ,
                                                                    QMessageBox.Discard | QMessageBox.Escape, 
                                                                    QMessageBox.NoButton, 
                                                                    self.window)

                        saveAsButton = warningBox.addButton(QString(_("Save as...")), QMessageBox.ActionRole)
                        answer = warningBox.exec_()
                        if answer == QMessageBox.Retry:
                            continue
                        elif answer == QMessageBox.Discard :
                            break #Let's get out from the While true
                        elif answer ==  QMessageBox.NoButton: #If we choose the SAVE AS
                            fileName = QFileDialog.getSaveFileName(None, _("Save subtitle as..."), destinationPath, 'All (*.*)')
                            if fileName:
                                destinationPath = fileName
                    else: #If we have write access we leave the while loop.
                        break 
                        
                #If we have chosen Discard subtitle button.
                if answer == QMessageBox.Discard:
                    count += percentage
                    continue #Continue the next subtitle
                    
                optionWhereToDownload =  QSettings().value("options/whereToDownload", QVariant("SAME_FOLDER"))
                #Check if doesn't exists already, otherwise show fileExistsBox dialog
                if QFileInfo(destinationPath).exists() and not replace_all and optionWhereToDownload != QVariant("ASK_FOLDER"):
                    # The "remote filename" below is actually not the real filename. Real name could be confusing
                    # since we always rename downloaded sub to match movie filename. 
                    fileExistsBox = QMessageBox(_("File already exists"),_("Local: %s\n\nRemote: %s\n\nHow would you like to proceed?") % (destinationPath, QFileInfo(destinationPath).fileName()), QMessageBox.Warning, QMessageBox.NoButton, QMessageBox.NoButton, QMessageBox.NoButton, self.window)
                    skipButton = fileExistsBox.addButton(QString(_("Skip")), QMessageBox.ActionRole)
                    replaceButton = fileExistsBox.addButton(QString(_("Replace")), QMessageBox.ActionRole)
                    replaceAllButton = fileExistsBox.addButton(QString(_("Replace all")), QMessageBox.ActionRole)
                    saveAsButton = fileExistsBox.addButton(QString(_("Save as...")), QMessageBox.ActionRole)
                    cancelButton = fileExistsBox.addButton(QString(_("Cancel")), QMessageBox.ActionRole)
                    fileExistsBox.exec_()
                    answer = fileExistsBox.clickedButton()
                    if answer == replaceAllButton:
                        replace_all = True # Don't ask us again (for this batch of files)
                    elif answer == saveAsButton:
                        # We will find a uniqiue filename and suggest this to user.
                        # add .<lang> to (inside) the filename. If that is not enough, start adding numbers.
                        # There should also be a preferences setting "Autorename files" or similar ( =never ask) FIXME
                        suggBaseName, suggFileExt = os.path.splitext(destinationPath)
                        fNameCtr = 0 # Counter used to generate a unique filename
                        suggestedFileName = suggBaseName + '.' + sub.getLanguageXXX() + suggFileExt
                        while (os.path.exists(suggestedFileName)):
                            fNameCtr += 1
                            suggestedFileName = suggBaseName + '.' + sub.getLanguageXXX() + '-' + str(fNameCtr) + suggFileExt
                        fileName = QFileDialog.getSaveFileName(None, _("Save subtitle as..."), suggestedFileName, 'All (*.*)')
                        if fileName: 
                            destinationPath = fileName
                        else:
                            count += percentage
                            continue # Skip this particular file if no filename chosen
                    elif answer == skipButton:
                        count += percentage
                        continue # Skip this particular file
                    elif answer == cancelButton:
                        break # Break out of DL loop - cancel was pushed
                QCoreApplication.processEvents()
                self.progress(count,_("Downloading subtitle %s (%d/%d)") % (QFileInfo(destinationPath).fileName(), i + 1, total_subs))
                try:
                   log.debug("Downloading subtitle '%s'" % destinationPath)
                   if self.OSDBServer.DownloadSubtitles({sub.getIdFileOnline():destinationPath}):
                       success_downloaded += 1
                   else:
                     QMessageBox.about(self.window,_("Error"),_("Unable to download subtitle %s") %sub.getFileName())
                except Exception, e: 
                    traceback.print_exc(e)
                    QMessageBox.about(self.window,_("Error"),_("Unable to download subtitle %s") % sub.getFileName())
                finally:
                    count += percentage
            self.status("%d from %d subtitles downloaded succesfully" % (success_downloaded, total_subs))
            self.progress(100)

    def showErrorConnection(self):
        warningBox = QMessageBox(_("Error write permission"), 
                                    _("%s cannot be saved.\nCheck that the folder exists and you have write-access permissions.") %destinationPath , 
                                    QMessageBox.Warning, 
                                    QMessageBox.Retry | QMessageBox.Default ,
                                    QMessageBox.Discard | QMessageBox.Escape, 
                                    QMessageBox.NoButton, 
                                    self.window)
        answer = warningBox.exec_()
        if answer == QMessageBox.Retry:
            pass #Try to create connection + login
        elif answer == QMessageBox.Discard :
            return
        
    """Control the STATUS BAR PROGRESS"""
    def progress(self, val = None,msg = None):
        
        #by calling progres(), it will return False if it has been canceled
        if (val == None and msg == None ):
            return not self.status_progress.wasCanceled() 
            
        if msg != None:
            self.status_progress.setLabelText(msg)
        if val < 0:
            self.status_progress.setMaximum(0)
        else: 
            self.status_progress.setValue(val)
        
        for i in range(1000):
            i = i * 5
            QCoreApplication.processEvents()
    
    def status(self, msg):
        self.status_progress.setMaximum(100)
        #self.status_progress.reset()
        #self.status_progress.setLabelText(msg)
        self.progress(100)
        QCoreApplication.processEvents()
        

    
    def establishServerConnection(self):
        self.status_progress = QProgressDialog(_("Connecting to server..."), _("&Cancel"), 0,0, self.window)
        self.status_progress.setWindowTitle(_('Connecting'))
        self.status_progress.setCancelButton(None)
        self.status_progress.show()
        self.progress(0)
                
        settings = QSettings()
        settingsProxyHost = settings.value("options/ProxyHost", QVariant()).toString()
        settingsProxyPort = settings.value("options/ProxyPort", QVariant("8080")).toInt()[0]
        if not self.options.proxy:  #If we are not defining the proxy from command line 
            if settingsProxyHost: #Let's see if we have defined a proxy in our Settings
                self.options.proxy = str(settingsProxyHost + ":" + str(settingsProxyPort))
                
        if self.options.proxy:
            self.progress(0,_("Connecting to server using proxy %s") % self.options.proxy) 
            
        try:
            self.OSDBServer = SDService('osdb',proxy = self.options.proxy) 
            self.SDDBServer = SDService('sddb', self.options.server, self.options.proxy)

            self.progress(100, _("Connected succesfully"))
            QCoreApplication.processEvents()
            self.status_progress.close()
            return True
        except TimeoutFunctionException:
            self.status_progress.close()
            self.showErrorConnection()
            
        except Exception, e: 
            traceback.print_exc(e)
            #self.progress(0, "Error contacting the server")
            self.status_progress.close()
            #replace by a dialog with button.
            QCoreApplication.processEvents()
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
        directory=QtGui.QFileDialog.getExistingDirectory(None,_("Select a directory"),path.toString())
        if directory:
            settings.setValue("mainwindow/workingDirectory", QVariant(directory))
            directory =  str(directory.toUtf8())
            videos_found,subs_found = FileScan.ScanFolder(directory,recursively = False,report_progress = None)
            log.info("Videos found: %i Subtitles found: %i"%(len(videos_found), len(subs_found)))
            self.uploadModel.emit(SIGNAL("layoutAboutToBeChanged()"))
            for row, video in enumerate(videos_found):
                self.uploadModel.addVideos(row, [ video])
                subtitle = Subtitle.AutoDetectSubtitle(video.getFilePath())
                if subtitle:
                    sub = SubtitleFile(False,subtitle) 
                    self.uploadModel.addSubs(row, [sub])
            if not len(videos_found):
                for row, sub in enumerate(subs_found):
                    self.uploadModel.addSubs(row, [sub])
            self.uploadView.resizeRowsToContents()
            self.uploadModel.emit(SIGNAL("layoutChanged()"))
            thread.start_new_thread(self.AutoDetectNFOfile, (directory, ))
            thread.start_new_thread(self.uploadModel.ObtainUploadInfo, ())
            

    def AutoDetectNFOfile(self, folder):
        imdb_id = FileScan.AutoDetectNFOfile(folder)
        if imdb_id:
            results = self.OSDBServer.GetIMDBMovieDetails(imdb_id)
            if results['title']:
                self.emit(SIGNAL('imdbDetected(QString,QString,QString)'), imdb_id,results['title'],  "nfo")

    def onUploadButton(self, clicked):
        ok, error = self.uploadModel.validate()
        if not ok:
            QMessageBox.about(self.window,_("Error"),error)
            return
        else:
            imdb_id = self.uploadIMDB.itemData(self.uploadIMDB.currentIndex())
            if imdb_id == QVariant(): #No IMDB
                QMessageBox.about(self.window,_("Error"),_("Please identify the movie."))
                return
            else:
                self.status_progress = QProgressDialog(_("Uploading subtitle"), _("&Abort"), 0, 0, self.window)
                self.status_progress.setWindowTitle(_("Uploading..."))
                self.window.setCursor(Qt.WaitCursor)
                self.status_progress.forceShow()
                self.progress(0)
                QCoreApplication.processEvents()
                
                log.debug("Compressing subtitle...")
                details = {}
                details['IDMovieImdb'] = str(imdb_id.toString().toUtf8())
                lang_xxx = self.uploadLanguages.itemData(self.uploadLanguages.currentIndex())
                details['sublanguageid'] = str(lang_xxx.toString().toUtf8()) 
                details['movieaka'] = ''
                details['moviereleasename'] = str(self.uploadReleaseText.text().toUtf8()) 
                comments = str(self.uploadComments.toPlainText().toUtf8()) 
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
                    self.status_progress.close()
                    if info['status'] == "200 OK":
                        successBox = QMessageBox(_("Successful Upload"), 
                                                                        _("Subtitles succesfully uploaded.\nMany Thanks!") , 
                                                                        QMessageBox.Information, 
                                                                        QMessageBox.Ok | QMessageBox.Default | QMessageBox.Escape,
                                                                        QMessageBox.NoButton,
                                                                        QMessageBox.NoButton, 
                                                                        self.window)

                        saveAsButton = successBox.addButton(QString(_("View Subtitle Info")), QMessageBox.ActionRole)
                        answer = successBox.exec_()
                        if answer ==  QMessageBox.NoButton:
                            webbrowser.open( info['data'], new=2, autoraise=1)
                        self.uploadCleanWindow()
                    else:
                        QMessageBox.about(self.window,_("Error"),_("Problem while uploading...\nError: %s") % info['status'])
                except:
                    self.status_progress.close()
                    QMessageBox.about(self.window,_("Error"),_("Error contacting the server. Please restart or try later"))
                self.window.setCursor(Qt.ArrowCursor)
    
    def uploadCleanWindow(self):
        self.uploadReleaseText.setText("")
        self.uploadComments.setText("")
        self.progress(0)
        self.upload_autodetected_lang = ""
        self.upload_autodetected_imdb = ""
        #Note: We don't reset the language
        self.uploadModel.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.uploadModel.removeAll()
        self.uploadModel.emit(SIGNAL("layoutChanged()"))
        self.label_autodetect_imdb.hide()
        self.label_autodetect_lang.hide()
        index = self.uploadIMDB.findData(QVariant())
        if index != -1 :
            self.uploadIMDB.setCurrentIndex (index)
            
    def onUploadIMDBNewSelection(self, id, title, origin = ""):
        id = str(id.toUtf8())
        log.debug("onUploadIMDBNewSelection, id: %s, title: %s, origin: %s" %(id, title, origin))
        if origin == "nfo" and not self.upload_autodetected_imdb or self.upload_autodetected_imdb == "nfo":
            self.label_autodetect_imdb.setText(_(u'↓ Movie autodetected from .nfo file'))
            self.label_autodetect_imdb.show()
        elif origin == "database" and not self.upload_autodetected_imdb:
            self.label_autodetect_imdb.setText(_(u'↓ Movie autodetected from database'))
            self.label_autodetect_imdb.show()
        else:
            self.label_autodetect_imdb.hide()
            
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
            
    def onUploadLanguageDetection(self, lang_xxx, origin = ""):
        settings = QSettings()
        origin = str(origin.toUtf8())
        optionUploadLanguage = settings.value("options/uploadLanguage", QVariant())
        if optionUploadLanguage != QVariant():
            self.label_autodetect_lang.hide()
        else: #if we have selected <Autodetect> in preferences
            if origin == "database" and self.upload_autodetected_lang != "filename" and self.upload_autodetected_lang != "selected":
                self.label_autodetect_lang.setText(_(u'↑ Language autodetected from database'))
                self.label_autodetect_lang.show()
                self.upload_autodetected_lang = origin
            elif origin == "filename" and self.upload_autodetected_lang != "selected":
                self.label_autodetect_lang.setText(_(u"↑ Language autodetected from subtitle's filename"))
                self.label_autodetect_lang.show()
                self.upload_autodetected_lang = origin
            elif origin == "content" and not self.upload_autodetected_lang or self.upload_autodetected_lang == "content":
                self.label_autodetect_lang.setText(_(u"↑ Language autodetected from subtitle's content"))
                self.label_autodetect_lang.show()
                self.upload_autodetected_lang = origin
            elif not origin:
                self.label_autodetect_lang.hide()
            #Let's select the item with that id. 
            index = self.uploadLanguages.findData(QVariant(lang_xxx))
            if index != -1:
                self.uploadLanguages.setCurrentIndex (index)
                return
            
    def updateButtonsUpload(self):
        self.uploadView.resizeRowsToContents()
        selected = self.uploadSelectionModel.selection()
        total_selected = selected.count()
        if  total_selected== 1:
            self.uploadModel.rowsSelected = [selected.last().bottomRight().row()]
            self.buttonUploadMinusRow.setEnabled(True)
            if self.uploadModel.rowsSelected[0] != self.uploadModel.getTotalRows() -1:
                self.buttonUploadDownRow.setEnabled(True)
            else:
                self.buttonUploadDownRow.setEnabled(False)
                
            if self.uploadModel.rowsSelected[0] != 0:
                self.buttonUploadUpRow.setEnabled(True)
            else:
                self.buttonUploadUpRow.setEnabled(False)
                
        elif total_selected > 1:
                self.buttonUploadDownRow.setEnabled(False)
                self.buttonUploadUpRow.setEnabled(False)
                self.buttonUploadMinusRow.setEnabled(True)
                self.uploadModel.rowsSelected = []
                for range in selected:
                    self.uploadModel.rowsSelected.append(range.bottomRight().row())
        else: #nothing selected 
                self.uploadModel.rowsSelected = None
                self.buttonUploadDownRow.setEnabled(False)
                self.buttonUploadUpRow.setEnabled(False)
                self.buttonUploadMinusRow.setEnabled(False)

    def onUploadChangeSelection(self, selected, unselected):
        self.updateButtonsUpload()
        
    def onUploadClickViewCell(self, index):
        row, col = index.row(), index.column()
        settings = QSettings()
        currentDir = settings.value("mainwindow/workingDirectory", QVariant())

        if col == UploadListView.COL_VIDEO:
            fileName = QFileDialog.getOpenFileName(None, _("Browse video..."), currentDir.toString(), videofile.SELECT_VIDEOS)
            if fileName:
                settings.setValue("mainwindow/workingDirectory", QVariant(QFileInfo(fileName).absolutePath()))
                video = VideoFile(str(fileName.toUtf8())) 
                self.uploadModel.emit(SIGNAL("layoutAboutToBeChanged()"))
                self.uploadModel.addVideos(row, [video])
                subtitle = Subtitle.AutoDetectSubtitle(video.getFilePath())
                if subtitle:
                    sub = SubtitleFile(False,subtitle) 
                    self.uploadModel.addSubs(row, [sub])
                    thread.start_new_thread(self.uploadModel.ObtainUploadInfo, ())
                self.uploadView.resizeRowsToContents()
                self.uploadModel.emit(SIGNAL("layoutChanged()"))
                fileName = str(fileName.toUtf8())
                thread.start_new_thread(self.AutoDetectNFOfile, (os.path.dirname(fileName), ))
                
        else:
            fileName = QFileDialog.getOpenFileName(None, _("Browse subtitle..."), currentDir.toString(), subtitlefile.SELECT_SUBTITLES)
            if fileName:
                settings.setValue("mainwindow/workingDirectory", QVariant(QFileInfo(fileName).absolutePath()))
                sub = SubtitleFile(False, str(fileName.toUtf8())) 
                self.uploadModel.emit(SIGNAL("layoutAboutToBeChanged()"))
                self.uploadModel.addSubs(row, [sub])
                self.uploadView.resizeRowsToContents()
                self.uploadModel.emit(SIGNAL("layoutChanged()"))
                thread.start_new_thread(self.uploadModel.ObtainUploadInfo, ())


    def OnChangeReleaseName(self, name):
        self.uploadReleaseText.setText(name)
        
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
                    log.debug("Video Player found at: %s" %  repr(path))
                    predefinedVideoPlayer = {'programPath': path,  'parameters': player['parameters']}
                    break
                except WindowsError:
                    log.debug("Cannot find registry for %s" % player['regRoot'])
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

    def onButtonSearchByTitle(self):
        self.status_progress = QProgressDialog(_("Searching..."), "&Abort", 0, 0, self.window)
        self.status_progress.setWindowTitle(_('Searching...'))
        self.status_progress.forceShow()
        self.window.setCursor(Qt.WaitCursor)
        self.progress(-1)
        self.moviesModel.clearTree()
        self.moviesView.expandAll() #This was a solution found to refresh the treeView
        QCoreApplication.processEvents()
        s = SearchByName()
        selectedLanguageXXX = str(self.filterLanguageForTitle.itemData(self.filterLanguageForTitle.currentIndex()).toString())
        search_text = str(self.movieNameText.text().toUtf8())
        # Fix for user entering "'" in search field. If we find more chars that breaks things we'll handle this in a better way,
        # like a string of forbidden chars (pr the other way around, string of good chars)
        search_text = re.sub('\'', '', search_text)
        self.progress(0)
        #This should be in a thread to be able to Cancel
        movies = s.search_movie(search_text,'all')
        self.moviesModel.setMovies(movies, selectedLanguageXXX)
        if len(movies) == 1:
            self.moviesView.expandAll() 
        else:
            self.moviesView.collapseAll() 
        QCoreApplication.processEvents()
        self.window.setCursor(Qt.ArrowCursor)
        self.status_progress.close()
    
    def onFilterLangChangedPermanent(self, languages):
        languages = str(languages.toUtf8())
        languages_array = languages.split(",")

        if len(languages_array) > 1:
            index = self.filterLanguageForTitle.findData(QVariant(languages))
            if index == -1 :
                    self.filterLanguageForVideo.addItem(languages, QVariant(languages))
                    self.filterLanguageForTitle.addItem(languages, QVariant(languages))
        index = self.filterLanguageForTitle.findData(QVariant(languages))
        if index != -1 :
            self.filterLanguageForTitle.setCurrentIndex (index)

        index = self.filterLanguageForVideo.findData(QVariant(languages))
        if index != -1 :
            self.filterLanguageForVideo.setCurrentIndex (index)

    def onFilterLanguageSearchName(self, index):
        selectedLanguageXXX = str(self.filterLanguageForTitle.itemData(index).toString())
        log.debug("Filtering subtitles by language : %s" % selectedLanguageXXX)
        self.moviesView.clearSelection()
        self.moviesModel.clearTree()
        self.moviesModel.setLanguageFilter(selectedLanguageXXX)

        self.moviesView.expandAll()
    
    def onUploadSelectLanguage(self, index):
        self.upload_autodetected_lang = "selected"
        self.label_autodetect_lang.hide()
        
    def onUploadSelectImdb(self, index):
        self.upload_autodetected_imdb = "selected"
        self.label_autodetect_imdb.hide()
    
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
                QMessageBox.about(self.window,_("Error"),_("No subtitles selected to be downloaded"))
                return
        percentage = 100/total_subs
        count = 0
        answer = None
        success_downloaded = 0

        settings = QSettings()
        path = settings.value("mainwindow/workingDirectory", QVariant())
        zipDestDir=QtGui.QFileDialog.getExistingDirectory(None,_("Select the directory where to save the subtitle(s)"),path.toString())
        if zipDestDir:
            settings.setValue("mainwindow/workingDirectory", QVariant(zipDestDir))

        self.status_progress = QProgressDialog(_("Downloading files..."), _("&Abort"), 0, 100, self.window)
        self.status_progress.setWindowTitle(_('Downloading'))
        self.status_progress.show()
        self.progress(0)

# Download and unzip files automatically. We might want to move this to an external module, perhaps?
        unzipedOK = 0
        dlOK = False
 
        for i, sub in enumerate(subs):
            if not self.status_progress.wasCanceled(): #Skip rest of loop if Abort was pushed in progress bar

                url = sub.getExtraInfo("downloadLink")
#                webbrowser.open( url, new=2, autoraise=1)
                zipFileID = re.search("(\/.*\/)(.*)\Z", url).group(2)
                zipFileName = "sub-" + zipFileID + ".zip"

                zipDestFile = os.path.join(str(zipDestDir), zipFileName)

                log.debug("About to download %s to %s" % (url, zipDestFile))
                count += percentage
                self.progress(count, _("Downloading %s to %s") % (url, zipDestFile))

                # Download the file from opensubtitles.org
                # Note that we take for granted it will be in .zip format! Might not be so for other sites
                # This should be tested for when more sites are added or find true filename like browser does FIXME
                try:
                    subSocket = urllib2.urlopen(url)
                    subDlStream = subSocket.read()
                    oFile = open(zipDestFile, 'wb')
                    oFile.write(subDlStream)
                    oFile.close()
                    subSocket.close()
                    dlOK = True
                except Exception, e:
                    dlkOK = False
                    log.debug(e)
                    QMessageBox.critical(self.window,_("Error"),_("An error occured downloading %s:\nError:%s") % (url, e), QMessageBox.Abort)
                QCoreApplication.processEvents()

                # Only try unziping if download was succesful
                if dlOK:
                    try:
                        zipf = zipfile.ZipFile(zipDestFile, "r")
                        for fname in zipf.namelist():
                            if (fname.endswith('/')) or (fname.endswith('\\')):
                                os.mkdir(os.path.join(str(zipDestDir), fname))
                            else: # Prefix file with <subID-> if it already exists for uniqeness
                                if not os.path.exists(os.path.join(str(zipDestDir), fname)):
                                    outfile = open(os.path.join(str(zipDestDir), fname), 'wb')
                                else:
                                    outfile = open(os.path.join(str(zipDestDir),  zipFileID + '-' + fname), 'wb')
                                outfile.write(zipf.read(fname))
                                outfile.close()
                        zipf.close()
                        os.unlink(zipDestFile) # Remove zipfile-for nice-ness. Could be an option perhaps?
                        unzipedOK += 1
                    except Exception, e:
                        log.debug(e)
                        QMessageBox.critical(self.window,_("Error"),_("An error occured unziping %s:\nError: %s") % (zipDestFile, e), QMessageBox.Abort)

        self.progress(100)
        self.status_progress.close()
        if (unzipedOK > 0):
            QMessageBox.about(self.window,_("%d subtitles downloaded successfully") % (unzipedOK), _("The downloaded subtitle(s) may not be in sync with your video file(s), please check this manually.\n\nIf there is no sync problem, please consider re-uploading using subdownloader. This will automate the search for other users!"))

    def onExpandMovie(self, index):
        movie = index.internalPointer().data
        if not movie.subtitles and movie.totalSubs:
            self.status_progress = QProgressDialog(_("Searching..."), _("&Abort"), 0, 0, self.window)
            self.status_progress.setWindowTitle(_('Search'))
            self.status_progress.forceShow()
            self.window.setCursor(Qt.WaitCursor)

            s = SearchByName()
            selectedLanguageXXX = str(self.filterLanguageForTitle.itemData(self.filterLanguageForTitle.currentIndex()).toString())
            self.progress(0) #To view/refresh the qprogressdialog
            temp_movie = s.search_movie(None,'all',MovieID_link= movie.MovieSiteLink)
            #The internal results are not filtered by language, so in case we change the filter, we don't need to request again.
            #print temp_movie
            try:
                movie.subtitles = temp_movie[0].subtitles 
            except AttributeError:
                # this means only one subtitle was returned
                movie.subtitles = [temp_movie[1]]
            self.moviesModel.updateMovie(index, selectedLanguageXXX) #The treeview is filtered by language
            self.moviesView.collapse(index)
            self.moviesView.expand(index)
            self.status_progress.close()
            QCoreApplication.processEvents()
            self.window.setCursor(Qt.ArrowCursor)

def onUpgradeDetected():
        QMessageBox.about(self.window,_("A new version of SubDownloader has been released."))
        
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
