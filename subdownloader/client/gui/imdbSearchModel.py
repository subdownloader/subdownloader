# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QAbstractTableModel
from PyQt5.QtWidgets import QHeaderView, QTableView


class ImdbSearchModel(QAbstractTableModel):
    NB_COLS = 2
    COL_IMDB_ID = 0
    COL_NAME = 1

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._item_identities = []
        self._headers = None

    def set_imdb_data(self, imdb_data):
        self.beginResetModel()
        self._item_identities = [data for data in imdb_data]
        self.endResetModel()

    def rowCount(self, parent=None):
        return len(self._item_identities)

    def columnCount(self, parent=None):
        return self.NB_COLS

    def data(self, index, role=None):
        row, col = index.row(), index.column()
        if role == Qt.DisplayRole:
            provider_identity = self._item_identities[row]
            if col == self.COL_IMDB_ID:
                imdb_identity = provider_identity.imdb_identity
                return imdb_identity.get_imdb_id()
            else:  # if col == self.COL_NAME:
                video_identity = provider_identity.video_identity
                return video_identity.get_name()

        return None

    def get_identity_at_row(self, row):
        return self._item_identities[row]

    def sort(self, column, order=Qt.AscendingOrder):
        reverse = order is Qt.DescendingOrder
        self.beginResetModel()
        if column == self.COL_IMDB_ID:
            def key(identity):
                return identity.get_imdb_identity().get_imdb_id()
        else:
            def key(identity):
                return identity.video_identity.get_name().lower()
        self._item_identities = sorted(self._item_identities, key=key,
                                       reverse=reverse)
        self.endResetModel()

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == self.COL_IMDB_ID:
                    return _('Id')
                else:
                    return _('Name')
            else:
                return None


class ImdbListView(QTableView):
    def __init__(self, parent=None):
        QTableView.__init__(self, parent)
        self._imdb_model = ImdbSearchModel()
        self.setup_ui()

    def setup_ui(self):
        self.setModel(self._imdb_model)

        self.setSelectionMode(QTableView.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setGridStyle(Qt.DotLine)

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        self.verticalHeader().hide()

        self.selectionModel().selectionChanged.connect(self.imdb_selection_changed)

        self.retranslate()

    def retranslate(self):
        self._imdb_model.headerDataChanged.emit(Qt.Horizontal, 0, ImdbSearchModel.NB_COLS - 1)

    def set_imdb_data(self, imdb_data):
        self._imdb_model.set_imdb_data(imdb_data)

    @pyqtSlot(int)
    def on_header_clicked(self, section):
        self._imdb_model.sort(section)

    imdb_selection_changed = pyqtSignal()

    def get_selected_identity(self):
        selection = self.selectionModel().selection()

        if not selection.count():
            return None

        selection_range = selection.first()
        return self._imdb_model.get_identity_at_row(selection_range.top())
