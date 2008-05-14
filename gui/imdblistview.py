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

class ImdbListView(QTableView):
    def __init__(self, parent):    
        QTableView.__init__(self, parent)

class ImdbListModel(QAbstractTableModel):
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self._data = None
        self._imdb = []
        self._headers = ["Id"]
        self._main = None
        self.rowSelected = None

    def setImdbResults(self, results):
        self._imdb = results
        
    def flags(self, index):
        flags = QAbstractTableModel.flags(self, index)
        if index.isValid():       
            if index.row() == 0:  
                flags |= Qt.ItemIsDropEnabled
        return flags
      
    def getTotalRows(self):
        return len(self._imdb)
        
    def rowCount(self, index):
           return len(self._imdb)

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
            return QVariant()
        
    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == Qt.DisplayRole:      
            if self._imdb[row] != None:
                text = self._imdb[row]["id"] +" : " + self._imdb[row]["title"]
            else:
                text = "Unknown"
            return QVariant(text)

        return QVariant()
