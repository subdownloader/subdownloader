# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging
from subdownloader.movie import LocalMovie, VideoSubtitle

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QAbstractTableModel, QModelIndex

log = logging.getLogger('subdownloader.client.gui.models.upload')


class UploadDataCollection(object):
    NB_COLS = 2
    COL_VIDEO = 0
    COL_SUB = 1

    def __init__(self):
        self._local_movie = LocalMovie()

    def set_local_movie(self, local_movie):
        self._local_movie = local_movie

    def reset_size(self, nb=2):
        self._local_movie.set_data([VideoSubtitle() for _ in range(nb)])

    def iter_videos(self):
        return iter(vs.video for vs in self._local_movie.get_data() if vs.video)

    def iter_subtitles(self):
        return iter(vs.subtitle for vs in self._local_movie.get_data() if vs.subtitle)

    def sort(self, column, reverse=False):
        def vs_getitem(vs, column):
            if column == UploadDataCollection.COL_VIDEO:
                return vs.video
            else:  # column == UploadDataCollection.COL_SUBTITLE:
                return vs.subtitle

        data = self._local_movie.get_data()

        l = [(i, vs) for (i, vs) in enumerate(data) if vs_getitem(vs, column)]
        index_upl = sorted(l, key=lambda d: vs_getitem(d[1], column).get_filename(), reverse=reverse)
        data = [d for i, d in index_upl]
        none_keys = set(range(len(data))) - set(i for i, d in index_upl)
        data += [data[i] for i in none_keys]
        self._local_movie.set_data(data)

    def insert_count(self, row, count):
        data = self._local_movie.get_data()
        data = data[:row] + [VideoSubtitle() for _ in range(count)] + data[row:]
        self._local_movie.set_data(data)

    def remove_count(self, row, count):
        data = self._local_movie.get_data()
        data = data[:row] + data[(row + count):]
        self._local_movie.set_data(data)

    def remove_rows(self, rows):
        data = self._local_movie.get_data()
        new_rows = set(range(len(self))) - set(rows)
        data = [data[row] for row in new_rows]
        self._local_movie.set_data(data)

    def move_row(self, row_from, row_to):
        data = self._local_movie.get_data()
        data_row = [data[row_from]]
        data = data[:row_from] + data[row_from+1:]
        data = data[:row_to] + data_row + data[row_to:]
        self._local_movie.set_data(data)

    def is_valid(self):
        data = self._local_movie.get_data()
        if not len(data):
            return False
        return all(sv.check() for sv in data)

    def __getitem__(self, key):
        return self._local_movie.get_data()[key]

    def __len__(self):
        return len(self._local_movie.get_data())


class UploadModel(QAbstractTableModel):
    upload_data_changed = pyqtSignal(int, int)

    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self._data = UploadDataCollection()

    def get_data_collection(self):
        return self._data

    def set_local_movie(self, local_movie):
        self.beginResetModel()
        self._data.set_local_movie(local_movie)
        self.endResetModel()

    def set_videos(self, videos):
        self.beginResetModel()
        self._data.reset_size(len(videos))
        self.endResetModel()

        for video_i, video in enumerate(videos):
            vid_index = self.createIndex(video_i, UploadDataCollection.COL_VIDEO)
            self.setData(vid_index, video, Qt.UserRole)

            sub_index = self.createIndex(video_i, UploadDataCollection.COL_SUB)
            try:
                subtitle = next(video.get_subtitles().iter_local_subtitles())
                self.setData(sub_index, subtitle, Qt.UserRole)
            except StopIteration:
                pass

    def data(self, index, role=None):
        row, col = index.row(), index.column()

        if role == Qt.DisplayRole:
            vs = self._data[row]

            if col == UploadDataCollection.COL_VIDEO:
                if vs.video is None:
                    return _('Double click here to select video...')
                else:
                    return vs.video.get_filename()
            elif col == UploadDataCollection.COL_SUB:
                if vs.subtitle is None:
                    return _('Double click here to select subtitle...')
                else:
                    return vs.subtitle.get_filename()

        return None

    def setData(self, index, value, role=None):
        row, col = index.row(), index.column()

        if role == Qt.UserRole:
            vs = self._data[row]
            if col == UploadDataCollection.COL_VIDEO:
                vs.video = value
            else:  # col == UploadDataCollection.COL_SUB:
                vs.subtitle = value
            self.dataChanged.emit(index, index)
            self.upload_data_changed.emit(row, col)
            return True

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return UploadDataCollection.NB_COLS

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == UploadDataCollection.COL_VIDEO:
                    return _('Video File')
                else:
                    return _('Subtitle File')
            elif orientation ==Qt.Vertical:
                return _('CD {}').format(1 + section)

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

    def on_reset(self):
        self.beginResetModel()
        self.endResetModel()
