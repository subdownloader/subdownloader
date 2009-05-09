#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) 2007-2009 Ivan Garcia capiscuas@gmail.com
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
#    see <http://www.gnu.org/licenses/>.

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
        self._imdb = []
        self._headers = ["Id"]
        self._main = None
        self.rowSelected = None

    def setImdbResults(self, results):
        self._imdb = results
    
    def getSelectedImdb(self):
        if self.rowSelected != None:
            return self._imdb[self.rowSelected]
        else:
            return None
        
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
