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
#sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QVariant, QSize, QEventLoop, QString, \
                         QBuffer, QIODevice, QModelIndex,QDir
from PyQt4.QtGui import QPixmap, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical

from subdownloader.gui.SplashScreen import SplashScreen, NoneSplashScreen

from subdownloader import * 
from subdownloader.OSDBServer import OSDBServer
from subdownloader.gui import installErrorHandler, Error, _Warning, extension


from subdownloader.gui.uploadlistview import UploadListModel, UploadListView
from subdownloader.gui.videotreeview import VideoTreeModel

from subdownloader.gui.main_ui import Ui_MainWindow
from subdownloader.FileManagement import FileScan, Subtitle
from subdownloader.videofile import  *
from subdownloader.subtitlefile import *


import subdownloader.languages.Languages as languages

import logging
log = logging.getLogger("subdownloader.gui.main")

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
        settings.beginGroup("MainWindow")
        self.window.resize(settings.value("size", QVariant(QSize(1000, 700))).\
                            toSize())
        settings.endGroup()
        #self.database_path = settings.value("database path", QVariant(os.path\
         #                           .expanduser("~/library.db"))).toString()
    
    def write_settings(self):
        settings = QSettings()
        settings.beginGroup("MainWindow")
        settings.setValue("size", QVariant(self.window.size()))
        settings.endGroup()
    
    def close_event(self, e):
        self.write_settings()
        e.accept()
    
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
        self.read_settings()
        
        #self.treeView.reset()
        window.show()
        model = QDirModel(window)
        
        #SETTING UP FOLDERVIEW
        model.setFilter(QDir.AllDirs|QDir.NoDotAndDotDot)
        self.folderView.setModel(model)
        index = model.index(QDir.rootPath())
        self.folderView.setRootIndex(index)
        
        self.folderView.header().hide()
        self.folderView.hideColumn(3)
        self.folderView.hideColumn(2)
        self.folderView.hideColumn(1)

        QObject.connect(self.folderView, SIGNAL("activated(QModelIndex)"), \
                            self.folderView_clicked)
        QObject.connect(self.folderView, SIGNAL("clicked(QModelIndex)"), \
                            self.folderView_clicked)

        #SETTING UP SEARCH_VIDEO_VIEW
        self.videoModel = VideoTreeModel(window)
        self.videoView.setModel(self.videoModel)
        QObject.connect(self.videoView, SIGNAL("activated(QModelIndex)"), self.onClickVideoTreeView)
        QObject.connect(self.videoView, SIGNAL("clicked(QModelIndex)"), self.onClickVideoTreeView)
        QObject.connect(self.videoModel, SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.subtitlesCheckedChanged)
        
        QObject.connect(self.buttonDownload, SIGNAL("clicked(bool)"), self.onButtonDownload)
        QObject.connect(self.buttonIMDB, SIGNAL("clicked(bool)"), self.onButtonIMDB)
        
        #SETTING UP UPLOAD_VIEW
        self.uploadModel = UploadListModel(window)
        self.uploadView.setModel(self.uploadModel)

        #Resizing the headers to take all the space(50/50) in the TableView
        header = self.uploadView.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.Stretch)
        
        QObject.connect(self.buttonUploadBrowseFolder, SIGNAL("clicked(bool)"), self.onUploadBrowseFolder)
        QObject.connect(self.uploadView, SIGNAL("activated(QModelIndex)"), self.onClickUploadViewCell)
        QObject.connect(self.uploadView, SIGNAL("clicked(QModelIndex)"), self.onClickUploadViewCell)
        

        self.folderView.show()
        
        #Fill Out the Filters Language SelectBoxes
        self.InitializeFilterLanguages()
        
        self.status_progress = QtGui.QProgressBar(self.statusbar)
        self.status_progress.setProperty("value",QVariant(0))
        
        self.status_progress.setOrientation(QtCore.Qt.Horizontal)
        self.status_label = QtGui.QLabel("v"+ APP_VERSION,self.statusbar)
        
        self.statusbar.insertWidget(0,self.status_label)
        self.statusbar.addPermanentWidget(self.status_progress,2)
        if not options.test:
            self.establish_connection()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        
        #FOR TESTING
        if options.test:
            #self.SearchVideos('/media/xp/pelis/')
            pass
    
    def InitializeFilterLanguages(self):
        self.filterLanguageForVideo.addItem(QtGui.QApplication.translate("MainWindow", "All", None, QtGui.QApplication.UnicodeUTF8))
        self.filterLanguageForTitle.addItem(QtGui.QApplication.translate("MainWindow", "All", None, QtGui.QApplication.UnicodeUTF8))
        for lang in languages.LANGUAGES:
            self.filterLanguageForVideo.addItem(QtGui.QApplication.translate("MainWindow", lang["LanguageName"], None, QtGui.QApplication.UnicodeUTF8))
            self.filterLanguageForTitle.addItem(QtGui.QApplication.translate("MainWindow", lang["LanguageName"], None, QtGui.QApplication.UnicodeUTF8))
            
        self.filterLanguageForVideo.adjustSize()
        self.filterLanguageForTitle.adjustSize()

        QObject.connect(self.filterLanguageForVideo, SIGNAL("currentIndexChanged(int)"), self.onFilterLanguageVideo)
    
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
            #This effect causes the progress bar turn all sides
            #FIXME: We need to send a refresh signal.
            self.status_progress.setMinimum(0)
            self.status_progress.setMaximum(0)
            
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
            self.status_progress.setFormat("No videos founded")
    
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
    def folderView_clicked(self, index):
        if index.isValid():
            data = self.folderView.model().filePath(index)
        
        folder_path = unicode(data, 'utf-8')
        self.SearchVideos(folder_path)

    def onButtonIMDB(self, checked):
        video = self.videoModel.getSelectedItem().data
        movie_info = video.getMovieInfo()
        if movie_info:
            QMessageBox.about(self.window,"WWW","Open website: http://www.imdb.com/title/tt%s" % movie_info["IDMovieImdb"])
            
    def onButtonDownload(self, checked):
        #We download the subtitle in the same folder than the video
            subs = self.videoModel.getCheckedSubtitles()
            percentage = 100/len(subs)
            count = 0
            self.status("Connecting to download...")
            for sub in subs:
                self.progress(count,"Downloading subtitle... "+sub.getIdOnline())
                count += percentage
                destinationPath = os.path.join(sub.getVideo().getFolderPath(),sub.getFileName())
                log.debug("Downloading subtitle '%s'" % destinationPath)
                try:
                    videos_result = self.OSDBServer.DownloadSubtitles({sub.getIdOnline():destinationPath})
                except Exception, e: 
                    QMessageBox.about(self.window,"Error","Unable to download subtitle "+sub.getIdOnline())
                    traceback.print_exc(e)

            self.status("Subtitles downloaded succesfully.")
            self.progress(100)

    def videos_leftclicked(self, index):
        if index.isValid():
            subs = self.video_model.getSubsFromIndex(index.row())
        #print len(subs)
        self.subs_osdb_model.setSubs(subs)
        self.subs_osdb_view.setModel(self.subs_osdb_model)
        self.subs_osdb_view.resizeColumnsToContents()
        
    def videos_rightclicked(self, point):
        menu = QtGui.QMenu(self.video_view)
        menu.addAction(self.actionUpload_Subtitle)
        menu.exec_(self.video_view.mapToGlobal(point))
        #if index.isValid():
            #print "hello"
        
    def subs_odbc_rightclicked(self, point):
        menu = QtGui.QMenu(self.subs_osdb_view)
        menu.addAction(self.actionDownload_Subtitle)
        menu.exec_(self.subs_osdb_view.mapToGlobal(point))
        #if index.isValid():
            #print "hello"

    def subs_rightclicked(self, point):
        menu = QtGui.QMenu(self.sub_view)
        menu.addAction(self.actionUpload_Subtitle)
        menu.exec_(self.sub_view.mapToGlobal(point))
        #if index.isValid():
            #print "hello"

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
        self.window.setCursor(Qt.WaitCursor)

        self.status("Connecting to server")        
        try:
            self.OSDBServer = OSDBServer(self.options)
        except Exception, e: 
            traceback.print_exc(e)
            qFatal("Unable to connect to server. Please try later")
        self.progress(100)
        self.status_progress.setFormat("Connected")
    
        self.window.setCursor(Qt.ArrowCursor)
        
    #UPLOAD METHODS
    def onUploadBrowseFolder(self):
        directory=QtGui.QFileDialog.getExistingDirectory(None,"Select a directory","Select a directory")
        if directory:
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
            self.uploadModel.emit(SIGNAL("layoutChanged()"))

    def onClickUploadViewCell(self, index):
        COL_VIDEO = 0 #FIXME: Use global variables
        COL_SUB = 1
        row, col = index.row(), index.column()
        if col == COL_VIDEO:
            fileName = QFileDialog.getOpenFileName(None, "Select Video", "", videofile.SELECT_VIDEOS)
            if fileName:
                video = VideoFile(str(fileName.toUtf8())) 
                self.uploadModel.emit(SIGNAL("layoutAboutToBeChanged()"))
                self.uploadModel.addVideos(row, [video])
                self.uploadView.resizeRowsToContents()
                self.uploadModel.emit(SIGNAL("layoutChanged()"))
        else:
            fileName = QFileDialog.getOpenFileName(None, "Select Subtitle", "", subtitlefile.SELECT_SUBTITLES)
            if fileName:
                sub = SubtitleFile(False, str(fileName.toUtf8())) 
                self.uploadModel.emit(SIGNAL("layoutAboutToBeChanged()"))
                self.uploadModel.addSubs(row, [sub])
                self.uploadView.resizeRowsToContents()
                self.uploadModel.emit(SIGNAL("layoutChanged()"))
                self.uploadModel.update_lang_upload()
                


def main(options):
    
    from PyQt4.Qt import QApplication, QMainWindow
    
    log.debug("Building main dialog")
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.showMessage(QApplication.translate("subdownloader", "Building main dialog..."))
    window = QMainWindow()
    window.setWindowTitle(APP_TITLE)
    window.setWindowIcon(QIcon(":/icon"))
    installErrorHandler(QErrorMessage(window))
    QCoreApplication.setOrganizationName("IvanGarcia")
    QCoreApplication.setApplicationName(APP_TITLE)
    
    log.debug("Showing main dialog")
    Main(window,"", options)    
    
    return app.exec_()

#if __name__ == "__main__": 
#    sys.exit(main())
