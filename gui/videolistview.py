#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.Qt import QApplication, QString, QFont, QAbstractListModel, \
                     QVariant, QAbstractTableModel, QTableView, QListView, \
                     QLabel, QAbstractItemView, QPixmap, QIcon, QSize, \
                     QSpinBox, QPoint, QPainterPath, QItemDelegate, QPainter, \
                     QPen, QColor, QLinearGradient, QBrush, QStyle, \
                     QByteArray, QBuffer, QMimeData, \
                     QDrag, QRect      

import subdownloader.videofile as videofile
import pickle


class VideoListModel(QAbstractTableModel):
    
    TIME_READ_FMT = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self._data = None
        self._subs = []
        self._videos = []
        self._headers = ["VideoFile"]  
    
    def set_videos(self,videos_found):
        self._videos = videos_found

    def dropMimeData(self, data, action, row, column, parent):
        print row,column 
    
    def rowCount(self, parent): 
        return len(self._videos)
        
    def columnCount(self, parent): 
        return len(self._headers)
    
    
    def headerData(self, section, orientation, role): 
        if role != Qt.DisplayRole:
            return QVariant()
        text = ""
        if orientation == Qt.Horizontal:      
            text = self._headers[section]
            return QVariant(self.trUtf8(text))
        return QVariant()
    
    def id_from_index(self, index): return self._data[index.row()]["id"]
    def id_from_row(self, row): return self._videos[row].getFileName()

    def flags(self, index):
        flags = QAbstractTableModel.flags(self, index)   
        return flags
    
    def getSubsFromIndex(self,index):
        return self._videos[index].getSubtitles()
    def getVideoFromIndex(self,index):
        return self._videos[index]
        
    def data(self, index, role):
        row, col = index.row(), index.column()
        
        if role == Qt.DisplayRole:      
            text = None
            video = self._videos[row]
            text = video.getFileName()
                #Setting "MovieName aka MovieNameEng"
                #if not video.hasMovieName():
                    #text = video.getFileName()
                #else:
                    #text = video.getMovieName()
                    #if video.hasMovieNameEng():
                        #text += " aka "+video.getMovieNameEng()
                        
                #Setting the number of subtitles found.
            if video.hasSubtitles():
                text = " ("+str(video.getTotalSubtitles())+" subs) " + text
                
            if text == None: 
                text = "Unknown"
            return QVariant(text)
        
        #elif Qt.FontRole and index.isValid():
            #video = self._videos[row]
            #if video.hasOsdbInfo(): 
                #font = QFont()
                #font.setBold(True)
                ##font.setItalic(True)
                #return QVariant(font)
        #elif  Qt.TextColorRole and index.isValid():
            #video = self._videos[row]
            #if video.hasOsdbInfo(): 
                #return QVariant(QColor(Qt.red))
        
        elif role == Qt.ToolTipRole and index.isValid():
                if index.column() == 0:
                    edit = "<b>COMMENTS</b> here.<br>"
                return QVariant(edit)
            
        return QVariant()
    
class VideoListView(QTableView):
    def __init__(self, parent): 
        self._drag_start_position = QPoint()
        QTableView.__init__(self, parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        #self.setSortingEnabled(True)
        #self.setItemDelegate(LibraryDelegate(self, rating_column=4))
    
    #def dragEnterEvent(self, event):
        #print event.mimeData()
        
    def mouseMoveEvent(self, event):
        QTableView.mousePressEvent(self, event)
        if event.buttons() & Qt.LeftButton != Qt.LeftButton: 
            return
        if (event.pos() - self._drag_start_position).manhattanLength() < \
                                        QApplication.startDragDistance(): 
            return
        self.start_drag(self._drag_start_position)
    
    def start_drag(self, pos):    
        index = self.indexAt(pos)
        drag = QDrag(self)
        mime_data = QMimeData()
        drag.setMimeData(mime_data)
        if index.isValid():
            rows = frozenset([ index.row() for index in self.selectedIndexes()])
            subs = [ self.model()._videos[row] for row in rows ]
            drag.mimeData().setData("application/x-subdownloader-video-id", \
                    pickle.dumps(subs))
            #QByteArray("\n".join(ids))
            drag.start()

    
    def files_dropped(self, files, event):
        if not files: return
        index = self.indexAt(event.pos())    
        if index.isValid():
            self.model().add_formats(files, index)      
        else: self.emit(SIGNAL('books_dropped'), files)      
