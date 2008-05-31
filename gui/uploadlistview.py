#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, SIGNAL,  QCoreApplication, QEventLoop
from PyQt4.Qt import QApplication, QString, QFont, QAbstractListModel, \
                     QVariant, QAbstractTableModel, QTableView, QListView, \
                     QLabel, QAbstractItemView, QPixmap, QIcon, QSize, \
                     QSpinBox, QPoint, QPainterPath, QItemDelegate, QPainter, \
                     QPen, QColor, QLinearGradient, QBrush, QStyle, \
                     QByteArray, QBuffer, QMimeData, \
                     QDrag, QRect
                     
from PyQt4.QtGui import QItemSelection

import subdownloader.languages.Languages as languages
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
                
    def verify(self):
        if not self.getTotalRows() or self.getTotalRows() == 1 and not self._subs[0] and not self._videos[0]:
            return {'ok': False ,  'error_msg':'The list of video/subtitle is empty'}

        for i in range(self.getTotalRows()):
            if not self._subs[i] and not self._videos[i] :
               if i != self.getTotalRows()-1:
                    return {'ok': False ,  'error_msg':'Some of the upload rows are empty'}
               else:
                   return {'ok': True}
                
            if not self._subs[i] or not self._videos[i]  and i != self.getTotalRows()-1:
                return {'ok': False ,  'error_msg':'Some of the video/subtitles are empty'}
                
        return {'ok': True}
        
    def update_lang_upload(self):
        ##Trying to autodetect the language

        #if detected_lang != None:
            #lang_xx = languages.name2xx(detected_lang)
            #image_file = lang_xx + '.gif'
            #icon = QtGui.QIcon(":/images/flags/" + image_file)
            #item = self.subhashes_treeitems[sub.getHash()]
            #item.setIcon(0,icon)
            #item.setText(0,detected_lang)
            #count += percentage
            #self.progress(count,"Autodetecting Language: " + os.path.basename(sub.getFilePath()))

        all_langs = []
        for sub in self._subs:
            if sub:
                lang = sub.getLanguage()
                if lang == None:
                    lang = languages.AutoDetectLang(sub.getFilePath())
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
        self._main.uploadLanguages.emit(SIGNAL('language_updated(QString)'),xxx_lang)
  
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
            previousRowSelection = QItemSelection(self.createIndex(self.rowSelected -1, UploadListView.COL_VIDEO),self.createIndex(self.rowSelected-1, UploadListView.COL_SUB))
            self._main.uploadSelectionModel.select(previousRowSelection, self._main.uploadSelectionModel.ClearAndSelect)
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

class UploadListView(QTableView):
    COL_VIDEO = 0
    COL_SUB = 1
    def __init__(self, parent):    
        QTableView.__init__(self, parent)
        self.setAcceptDrops(1)
             
#    def dragMoveEvent(self, event):
#        md = event.mimeData()
#        if md.hasFormat('application/x-subdownloader-video-id'):
#            event.acceptProposedAction()
#        elif md.hasFormat('application/x-subdownloader-subtitle-id'):
#            event.acceptProposedAction()
#    
#    def dropEvent(self, event):
#        md = event.mimeData()
#        if md.hasFormat('application/x-subdownloader-video-id'):
#            index = self.indexAt(event.pos())
#            if index.isValid():
#                a = md.data('application/x-subdownloader-video-id')
#                videos = pickle.loads(a)
#                self.model().add_videos(index.row(),videos)
#                print index.row(), index.column()
#                self.setModel(self.model())
#                self.resizeColumnsToContents()
#        elif md.hasFormat('application/x-subdownloader-subtitle-id'):
#            index = self.indexAt(event.pos())
#            if index.isValid():
#                a = md.data('application/x-subdownloader-subtitle-id')
#                subs = pickle.loads(a)
#                self.model().add_subs(index.row(),subs)
#                print index.row(), index.column()
#                self.setModel(self.model())
#                self.resizeColumnsToContents()
#
#    
#    def dragEnterEvent(self, event):
#        #event.setDropAction(Qt.IgnoreAction)
#        md = event.mimeData()
#        index = self.indexAt(event.pos())
#        print index.column()
#        if md.hasFormat('application/x-subdownloader-video-id') and index.column() == 0:
#            event.accept()
#        elif md.hasFormat('application/x-subdownloader-subtitle-id') and index.column() == 1:
#            event.accept()
#        
