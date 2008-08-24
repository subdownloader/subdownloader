#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, SIGNAL,  QCoreApplication, QEventLoop, QSettings
from PyQt4.Qt import QApplication, QString, QFont, QAbstractListModel, \
                     QVariant, QAbstractTableModel, QTableView, QListView, \
                     QLabel, QAbstractItemView, QPixmap, QIcon, QSize, \
                     QSpinBox, QPoint, QPainterPath, QItemDelegate, QPainter, \
                     QPen, QColor, QLinearGradient, QBrush, QStyle, \
                     QByteArray, QBuffer, QMimeData, \
                     QDrag, QRect
                     
from PyQt4.QtGui import QItemSelection

from FileManagement import get_extension, clear_string, without_extension
import FileManagement.VideoTools as VideoTools
import FileManagement.Subtitle as Subtitle
import languages.Languages as languages

from modules.videofile import  *
from modules.subtitlefile import *

import logging
log = logging.getLogger("subdownloader.gui.uploadlistview")

class UploadListModel(QAbstractTableModel):
    
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self._data = None
        self._subs = [None, None]
        self._videos = [None, None]
        self._headers = ["VideoFile", "SubTitle"]
        self._main = None
        self.rowSelected = None
    
    def dropMimeData(self, data, action, row, column, parent):
        print row,column
        
    def flags(self, index):
        flags = QAbstractTableModel.flags(self, index)
        if index.isValid():       
            if index.row() == 0:  
                flags |= Qt.ItemIsDropEnabled
        return flags
    
    def addVideos(self,index,videos):
        for video in videos:    
                if len(self._videos) <= index:
                        self._videos.insert(index,video)
                        self._subs.insert(index, None)
                else:
                        self._videos[index] = video
                index += 1

    def addSubs(self,index,subs ):
        for sub in subs:
                if len(self._subs) <= index:
                    self._subs.insert(index,sub)
                    self._videos.insert(index, None)
                else:
                    self._subs[index] = sub
                index += 1
                
    def validate(self):
        if not self.getTotalRows() or self.getTotalRows() == 1 and not self._subs[0] and not self._videos[0]:
            return False ,'The list of video/subtitle is empty'
            
        valid_subs = []
        valid_videos = []
        for i in range(self.getTotalRows()):
            if self._subs[i]: 
                if valid_subs.count(self._subs[i].getFilePath()) > 0:
                    return False ,'Subtitle %s is repeated' % str(i +1)
                else:
                    valid_subs.append(self._subs[i].getFilePath())
            if self._videos[i]: 
                if valid_videos.count(self._videos[i].getFilePath()) > 0:
                    return False ,'Videofie %s is repeated' % str(i +1)
                else:
                    valid_videos.append(self._videos[i].getFilePath())
                
            if not self._subs[i] and not self._videos[i] :
               if i != self.getTotalRows()-1:
                    return False ,'Some of the upload rows are empty'
               else:
                   return True, ""
                
            if not self._subs[i] or not self._videos[i]  and i != self.getTotalRows()-1:
                return False ,'Some of the video/subtitles are empty'
                
        return True, ""
    
    def update_imdb_upload(self):
        #Trying to autodetect the imdb from the server
        all_langs = []
        videos = []
        for i, video in enumerate(self._videos):
            if self._videos[i] != None and self._subs[i] != None:
                tmp_video = VideoFile(video.getFilePath())
                tmp_video.setSubtitles([self._subs[i]])
                videos.append(tmp_video)
        if videos:
            results = self._main.OSDBServer.TryUploadSubtitles(videos, no_update = True)
            if results['alreadyindb'] == 0 and results['data']:
                video_imdb =  self._main.OSDBServer.getBestImdbInfo(results['data'])
            elif results['alreadyindb'] == 1:
                video_imdb = {"IDMovieImdb": results['data']["IDMovieImdb"], "MovieName": results['data']["MovieName"]}
            if video_imdb:
                     self._main.emit(SIGNAL('imdbDetected(QString,QString,QString)'),video_imdb["IDMovieImdb"], video_imdb["MovieName"], "database")
                     
    def update_lang_upload(self):
        #Trying to autodetect the language

        all_langs = []
        for sub in self._subs:
            if sub:
                lang = sub.getLanguage()
                if lang == None:
                    lang = Subtitle.AutoDetectLang(sub.getFilePath())
                    sub.setLanguage(lang)
                all_langs.append(lang)
#FIXME: Clean this code here and put it in a shared script for also CLI to use
        max = 0
        max_lang = ""
        for lang in all_langs:
            if all_langs.count(lang) > max:
                max = all_langs.count(lang)
                max_lang = lang
        
        xxx_lang = languages.name2xxx(max_lang)
        log.debug("Majoritary Language Autodetected for Upload subtitles = " + str(xxx_lang))
        if xxx_lang:
            self._main.uploadLanguages.emit(SIGNAL('language_updated(QString,QString)'),xxx_lang, "content")
  
    def getTotalRows(self):
        return self.rowCount(None)
    def rowCount(self, index):
           return max(len(self._subs),len(self._videos))

    def columnCount(self, parent): 
        return len(self._headers)
    
    def headerData(self, section, orientation, role): 
        if role != Qt.DisplayRole:
            return QVariant()
        text = ""
        if orientation == Qt.Horizontal:      
            text = self._headers[section]
            return QVariant(self.trUtf8(text))
        else: 
            return QVariant("CD"+str(1+section))
        
    def data(self, index, role):
        row, col = index.row(), index.column()

        if role == Qt.DisplayRole:      
            text = None
            if   col == UploadListView.COL_VIDEO: 
                if self._videos[row] == None:
                    text = "Click here to select video..."
                else:
                        text = self._videos[row].getFileName()
            elif col == UploadListView.COL_SUB: 
                if self._subs[row] == None:
                    text = "Click here to select subtitle..."
                else:
                        text = self._subs[row].getFileName()
            if text == None: 
                text = "Unknown"
            return QVariant(text)

        return QVariant()
    
    def onUploadButtonPlusRow(self, clicked):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        if(self.rowSelected != None):
             self._videos.insert(self.rowSelected +1, None)
             self._subs.insert(self.rowSelected +1, None)
        else:
            self._videos.append(None)
            self._subs.append(None)
        self.emit(SIGNAL("layoutChanged()"))
        self._main.updateButtonsUpload() 
        
    def onUploadButtonMinusRow(self, clicked):
         if self.rowSelected != None:
            self.emit(SIGNAL("layoutAboutToBeChanged()"))
            try:
                del self._videos[self.rowSelected]
                del self._subs[self.rowSelected]
            except:
                pass
            self.emit(SIGNAL("layoutChanged()"))
            if self.rowSelected > 0: 
                previousRowSelection = QItemSelection(self.createIndex(self.rowSelected -1, UploadListView.COL_VIDEO),self.createIndex(self.rowSelected-1, UploadListView.COL_SUB))
                self._main.uploadSelectionModel.select(previousRowSelection, self._main.uploadSelectionModel.ClearAndSelect)
            #elif not len(self._videos):
                #print "last row"
            
            self._main.updateButtonsUpload() 
        
    def onUploadButtonUpRow(self, clicked):
        if self.rowSelected != None:
            self.emit(SIGNAL("layoutAboutToBeChanged()"))
            if self.rowSelected != 0:
                temp = self._videos[self.rowSelected]
                self._videos[self.rowSelected] = self._videos[self.rowSelected -1]
                self._videos[self.rowSelected - 1] = temp
                
                temp = self._subs[self.rowSelected]
                self._subs[self.rowSelected] = self._subs[self.rowSelected -1]
                self._subs[self.rowSelected - 1] = temp
            self.emit(SIGNAL("layoutChanged()"))
            previousRowSelection = QItemSelection(self.createIndex(self.rowSelected -1, UploadListView.COL_VIDEO),self.createIndex(self.rowSelected-1, UploadListView.COL_SUB))
            self._main.uploadSelectionModel.select(previousRowSelection, self._main.uploadSelectionModel.ClearAndSelect)
            
        self._main.updateButtonsUpload() 

    def onUploadButtonDeleteAllRow(self):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.removeAll()
        self.emit(SIGNAL("layoutChanged()"))
    def onUploadButtonDownRow(self, clicked):
        if self.rowSelected != None:
            self.emit(SIGNAL("layoutAboutToBeChanged()"))
            if self.rowSelected != self.getTotalRows() -1:
                temp = self._videos[self.rowSelected]
                self._videos[self.rowSelected] = self._videos[self.rowSelected +1]
                self._videos[self.rowSelected + 1] = temp
                
                temp = self._subs[self.rowSelected]
                self._subs[self.rowSelected] = self._subs[self.rowSelected +1]
                self._subs[self.rowSelected + 1] = temp

            self.emit(SIGNAL("layoutChanged()"))
            nextRowSelection = QItemSelection(self.index(self.rowSelected +1 , UploadListView.COL_VIDEO),self.index(self.rowSelected +1, UploadListView.COL_SUB))
            self._main.uploadSelectionModel.select(nextRowSelection, self._main.uploadSelectionModel.ClearAndSelect)
        self._main.updateButtonsUpload() 
        
    def removeAll(self):
         self._videos = [None, None]
         self._subs = [None, None]

class UploadListView(QTableView):
    COL_VIDEO = 0
    COL_SUB = 1
    def __init__(self, parent):    
        QTableView.__init__(self, parent)
        self.setAcceptDrops(True)
        
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("text/plain")  or event.mimeData().hasFormat("text/uri-list"):
                event.accept()
        else:
                event.ignore()
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/plain")  or event.mimeData().hasFormat("text/uri-list"):
                event.accept()
        else:
                event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            paths = [str(u.toLocalFile().toUtf8()) for u in event.mimeData().urls()]
            fileName = paths[0] #If we drop many files, only the first one will be take into acount
            index = self.indexAt(event.pos())
            row, col = index.row(), index.column()
            settings = QSettings()
            if col == UploadListView.COL_VIDEO:
                if(VideoTools.isVideofile(fileName)): 
                    settings.setValue("mainwindow/workingDirectory", QVariant(fileName))
                    video = VideoFile(fileName) 
                    self.model().emit(SIGNAL("layoutAboutToBeChanged()"))
                    self.model().addVideos(row, [video])
                    subtitle = Subtitle.AutoDetectSubtitle(video.getFilePath())
                    if subtitle:
                        sub = SubtitleFile(False,subtitle) 
                        self.model().addSubs(row, [sub])
                        self.model().update_lang_upload()
                    self.resizeRowsToContents()
                    self.model().emit(SIGNAL("layoutChanged()"))
            else: #if it's the column in SUBTITLES
                print fileName
                if(Subtitle.isSubtitle(fileName)): 
                    settings.setValue("mainwindow/workingDirectory", QVariant(fileName))
                    sub = SubtitleFile(False, fileName) 
                    self.model().emit(SIGNAL("layoutAboutToBeChanged()"))
                    self.model().addSubs(row, [sub])
                    self.resizeRowsToContents()
                    self.model().emit(SIGNAL("layoutChanged()"))
                    self.model().update_lang_upload()
