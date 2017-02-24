# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

from PyQt5.QtCore import Qt, pyqtSignal, QAbstractTableModel
from PyQt5.QtWidgets import QTableView


class ImdbListView(QTableView):

    def __init__(self, parent):
        QTableView.__init__(self, parent)


class ImdbListModel(QAbstractTableModel):

    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self._imdb = []
        self._headers = ["Id"]
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
            return None
        text = ""
        if orientation == Qt.Horizontal:
            text = self._headers[section]
            return self.trUtf8(text)
        else:
            return None

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == Qt.DisplayRole:
            if self._imdb[row] != None:
                text = self._imdb[row]["id"] + " : " + self._imdb[row]["title"]
            else:
                text = "Unknown"
            return text

        return None
