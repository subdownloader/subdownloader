# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from subdownloader.provider.imdb import ImdbMovieMatch
from typing import Optional, Sequence
from PyQt5.QtCore import QModelIndex, QObject, Qt, QAbstractTableModel


class ImdbSearchModel(QAbstractTableModel):
    NB_COLS = 2
    COL_IMDB_ID = 0
    COL_NAME = 1

    def __init__(self, parent: QObject=None):
        QAbstractTableModel.__init__(self, parent)
        self._imdb_data = []
        self._headers = None

    def set_imdb_data(self, imdb_data: Sequence[ImdbMovieMatch]) -> None:
        self.beginResetModel()
        self._imdb_data = list(imdb_data)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex=None) -> int:
        return len(self._imdb_data)

    def columnCount(self, parent: QModelIndex=None) -> int:
        return self.NB_COLS

    def data(self, index: QModelIndex, role=None) -> Optional[str]:
        row, col = index.row(), index.column()
        if role == Qt.DisplayRole:
            imdb = self._imdb_data[row]
            if col == self.COL_IMDB_ID:
                return imdb.imdb_id
            else:  # if col == self.COL_NAME:
                return imdb.title_year

        return None

    def get_imdb_at_row(self, row: int) -> ImdbMovieMatch:
        return self._imdb_data[row]

    def sort(self, column: int, order=Qt.AscendingOrder) -> None:
        reverse = order is Qt.DescendingOrder
        self.beginResetModel()
        if column == self.COL_IMDB_ID:
            def key(identity):
                return identity.get_imdb_identity().get_imdb_id()
        else:
            def key(identity):
                return identity.video_identity.get_name().lower()
        self._imdb_data = sorted(self._imdb_data, key=key,
                                 reverse=reverse)
        self.endResetModel()

    def headerData(self, section: int, orientation: int, role=None) -> Optional[str]:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == self.COL_IMDB_ID:
                    return _('Id')
                else:
                    return _('Name')
            else:
                return None
