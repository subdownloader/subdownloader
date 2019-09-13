# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from PyQt5.QtCore import Qt, QAbstractTableModel


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
