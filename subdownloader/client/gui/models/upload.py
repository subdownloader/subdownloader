# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QAbstractTableModel, QModelIndex

log = logging.getLogger('subdownloader.client.gui.models.upload')


class UploadDataItem(object):
    NB_COLS = 2
    COL_VIDEO = 0
    COL_SUB = 1

    def __init__(self):
        self._data = [None, None]

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value


class UploadDataCollection(object):
    def __init__(self):
        self._data = []

    def reset(self, nb=2):
        self._data = [UploadDataItem() for _ in range(nb)]

    def set_videos(self, videos):
        self._data = [UploadDataItem() for _ in videos]

    def iter_videos(self):
        return iter(v for v, s in self._data if v)

    def iter_subtitles(self):
        return iter(s for v, s in self._data if s)

    def sort(self, column, reverse=False):
        l = [(i, d) for (i, d) in enumerate(self._data) if d[column]]
        index_upl = sorted(l, key=lambda d: d[1][column].get_filename(), reverse=reverse)
        data = [d for i, d in index_upl]
        none_keys = set(range(len(self._data))) - set(i for i, d in index_upl)
        data += [self._data[i] for i in none_keys]
        self._data = data

    def insert_count(self, row, count):
        self._data = self._data[:row] + [UploadDataItem() for _ in range(count)] + self._data[row:]

    def remove_count(self, row, count):
        self._data = self._data[:row] + self._data[(row+count):]

    def remove_rows(self, rows):
        new_rows = set(range(len(self))) - set(rows)
        self._data = [self._data[row] for row in new_rows]

    def move_row(self, row_from, row_to):
        data = self._data[:row_from] + self._data[row_from+1:]
        self._data = data[:row_to] + [self._data[row_from]] + data[row_to:]

    def is_valid(self):
        if not len(self._data):
            return False
        for data in self._data:
            for col in range(UploadDataItem.NB_COLS):
                if data[col] is None:
                    return False
        return True

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)


class UploadModel(QAbstractTableModel):
    upload_data_changed = pyqtSignal(int, int)

    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self._data = UploadDataCollection()
        self.reset_data()

    def get_data_collection(self):
        return self._data

    @pyqtSlot()
    def reset_data(self):
        self.beginResetModel()
        self._data.reset()
        self.endResetModel()

    def set_videos(self, videos):
        self.beginResetModel()
        self._data.reset(len(videos))
        self.endResetModel()

        for video_i, video in enumerate(videos):
            vid_index = self.createIndex(video_i, UploadDataItem.COL_VIDEO)
            self.setData(vid_index, video, Qt.UserRole)

            sub_index = self.createIndex(video_i, UploadDataItem.COL_SUB)
            try:
                subtitle = next(video.get_subtitles().iter_local_subtitles())
                self.setData(sub_index, subtitle, Qt.UserRole)
            except StopIteration:
                pass

    def data(self, index, role=None):
        row, col = index.row(), index.column()

        if role == Qt.DisplayRole:
            data = self._data[row][col]

            if col == UploadDataItem.COL_VIDEO:
                if data is None:
                    return _("Double click here to select video...")
                else:
                    return data.get_filename()
            elif col == UploadDataItem.COL_SUB:
                if data is None:
                    return _("Double click here to select subtitle...")
                else:
                    return data.get_filename()

        return None

    def setData(self, index, value, role=None):
        row, col = index.row(), index.column()

        if role == Qt.UserRole:
            self._data[row][col] = value
            self.dataChanged.emit(index, index)
            self.upload_data_changed.emit(row, col)
            return True

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return UploadDataItem.NB_COLS

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == UploadDataItem.COL_VIDEO:
                    return _("Video File")
                else:
                    return  _("Subtitle File")
            elif orientation ==Qt.Vertical:
                return 'CD{i}'.format(i=1 + section)

    def sort(self, column, order=Qt.AscendingOrder):
        reverse = order is Qt.DescendingOrder
        self.beginResetModel()
        self._data.sort(column, reverse=reverse)
        self.endResetModel()

    @pyqtSlot()
    def insertRows(self, row, count, parent=None):
        if parent is None:
            parent = QModelIndex()
        self.beginInsertRows(parent, row, row + count - 1)
        self._data.insert_count(row, count)
        self.endInsertRows()

    @pyqtSlot()
    def removeRows(self, row, count, parent=None):
        self.beginRemoveRows(parent, row, row + count - 1)
        self._data.remove_count(row, count)
        self.endRemoveRows()

    def remove_multiple_rows(self, rows):
        self.beginResetModel()
        self._data.remove_rows(rows)
        self.endResetModel()

    def move_rows_up(self, rows):
        parent = QModelIndex()
        for row in sorted(rows):
            self.beginMoveRows(parent, row, row, parent, row - 1)
            self._data.move_row(row, row - 1)
            self.endMoveRows()

    def move_rows_down(self, rows):
        parent = QModelIndex()
        for row in sorted(rows, reverse=True):
            self.beginMoveRows(parent, row, row, parent, row + 2)
            self._data.move_row(row, row + 1)
            self.endMoveRows()
