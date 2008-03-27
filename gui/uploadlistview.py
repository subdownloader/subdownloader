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

import pickle
import subdownloader.languages.Languages as languages
            
class UploadListModel(QAbstractTableModel):
    
    TIME_READ_FMT = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self._data = None
        self._subs = []
        self._videos = []
        self._headers = ["VideoFile", "SubTitle"]  
    
    def dropMimeData(self, data, action, row, column, parent):
        print row,column
        
    def flags(self, index):
        flags = QAbstractTableModel.flags(self, index)
        if index.isValid():       
            if index.row() == 0:  
                flags |= Qt.ItemIsDropEnabled
        return flags
    
    def add_videos(self,index,videos):
        count = index
        for video in videos:            
            try:
                self._videos[count] = video
            except:
                self._videos.insert(count,video)
            count += 1
    
    def add_subs(self,index,subs):
        count = index
        for sub in subs:            
            try:
                self._subs[count] = sub
            except:
                self._subs.insert(count,sub)
            count += 1
        self.update_lang_upload()
    
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
            lang = sub.getLanguage()
            if lang == None:
                lang = languages.AutoDetectLang(sub.getFilePath())
                sub.setLanguage(lang)
            all_langs.append(lang)

        max = 0
        max_lang = ""
        for lang in all_langs:
            if all_langs.count(lang) > max:
                max = all_langs.count(lang)
                max_lang = lang
        print max_lang
        self.emit(SIGNAL('language_updated(QString)'),max_lang)
            
    def rowCount(self, parent): 
        return max(len(self._subs),len(self._videos)) + 1
        
    def columnCount(self, parent): 
        return len(self._headers)
        
    def headerData(self, section, orientation, role): 
        if role != Qt.DisplayRole:
            return QVariant()
        text = ""
        if orientation == Qt.Horizontal:      
            text = self._headers[section]
            return QVariant(self.trUtf8(text))
        else: return QVariant("CD"+str(1+section))
        
    def id_from_index(self, index): return self._data[index.row()]["id"]
    def id_from_row(self, row): return self._data[row]["id"]
    
    def data(self, index, role):
        COL_VIDEO = 0
        COL_SUB = 1
        extra_line = False
        total_cds = max(len(self._subs),len(self._videos))
        row, col = index.row(), index.column()
        if row >= total_cds:
               extra_line = True
                
        if role == Qt.DisplayRole:      
            text = None
            if   col == COL_VIDEO: 
                if row >= total_cds:
                    text = "Drag more videofiles here"
                else:
                    try:
                        text = self._videos[row].getFileName()
                    except:
                        text = "Drag videofile here"
            elif col == COL_SUB: 
                if row >= total_cds:
                    text = "Drag more subtitles here"
                else:
                    try:
                        text = self._subs[row].getFileName()
                    except:
                        text = "Drag subtitle here"
            if text == None: 
                text = "Unknown"
            return QVariant(text)
        elif role == Qt.ToolTipRole and index.isValid():
            if extra_line:
                if index.column() == COL_VIDEO:
                    edit = "<b>Drag and drop</b> the videos<br>\
                        from the <b>Videos found</b> list above."
                if index.column() == COL_SUB:
                    edit = "<b>Drag and drop</b> the subtitles<br>\
                        from the <b>Subs found</b> list above."
                return QVariant(edit)
        return QVariant()

class UploadListView(QTableView):
    def __init__(self, parent):    
        QTableView.__init__(self, parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
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
