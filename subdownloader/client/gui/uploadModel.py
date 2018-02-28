# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging
from pathlib import Path

from subdownloader.filescan import scan_videopath
from subdownloader.subtitle2 import LocalSubtitleFile

from subdownloader.client.gui import get_select_subtitles, get_select_videos
from subdownloader.client.gui.callback import ProgressCallbackWidget

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QAbstractTableModel, QFileInfo, QItemSelectionModel, \
    QModelIndex, QSettings
from PyQt5.QtWidgets import QFileDialog, QTableView

log = logging.getLogger('subdownloader.client.gui.uploadModel')


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


class UploadListView(QTableView):

    upload_data_changed = pyqtSignal()

    def __init__(self, parent):
        QTableView.__init__(self, parent)
        self._uploadModel = UploadModel(self)
        self.setup_ui()

    def get_data_collection(self):
        return self._uploadModel.get_data_collection()

    def selected_rows(self):
        return [r.row() for r in self.selectionModel().selectedRows()]

    def setup_ui(self):
        self.setModel(self._uploadModel)

        # FIXME: restore drag & drop functionality
        # self.ui.uploadView.setDragEnabled(True)
        # self.ui.uploadView.setDragDropMode(QAbstractItemView.DropOnly)

        self.doubleClicked.connect(self.on_edit_item)
        self.horizontalHeader().sectionClicked.connect(self.on_header_click)
        self.retranslate()

    def retranslate(self):
        self._uploadModel.headerDataChanged.emit(Qt.Horizontal, 0, UploadDataItem.NB_COLS - 1)

    @pyqtSlot()
    def on_browse_folder(self):
        # FIXME: refactor/generalize calls to mainwindow/workingDirectory
        settings = QSettings()
        path = settings.value('mainwindow/workingDirectory', '')
        directory = QFileDialog.getExistingDirectory(self, _('Select a directory'), path)
        if not directory:
            return
        settings.setValue('mainwindow/workingDirectory', directory)

        callback = ProgressCallbackWidget(self)
        callback.show()

        log.debug('on_browse_folder({folder})'.format(folder=directory))
        videos, subs = scan_videopath(Path(directory), callback=callback, recursive=False)
        log.debug('#videos: {nb_vids}, #subtitles: {nb_subs}'.format(
            nb_vids=len(videos), nb_subs=len(subs)))

        self._uploadModel.set_videos(videos)
        self.upload_data_changed.emit()

    @pyqtSlot()
    def on_add_row(self):
        try:
            last = self.selected_rows()[-1]
        except IndexError:
            last = self._uploadModel.rowCount()
        self._uploadModel.insertRows(last, 1)
        index_new_row = self._uploadModel.createIndex(last, 0)
        self.selectionModel().select(index_new_row, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        self.upload_data_changed.emit()

    @pyqtSlot()
    def on_remove_selection(self):
        self._uploadModel.remove_multiple_rows(self.selected_rows())
        self.selectionModel().clearSelection()
        self.upload_data_changed.emit()

    @pyqtSlot()
    def on_reset(self):
        self._uploadModel.reset_data()
        self.upload_data_changed.emit()

    @pyqtSlot()
    def on_move_selection_down(self):
        rows = self.selected_rows()
        self._uploadModel.move_rows_down(rows)
        self.upload_data_changed.emit()

    @pyqtSlot()
    def on_move_selection_up(self):
        rows = self.selected_rows()
        self._uploadModel.move_rows_up(rows)
        self.upload_data_changed.emit()

    @pyqtSlot(QModelIndex)
    def on_edit_item(self, index):
        row, col = index.row(), index.column()
        settings = QSettings()
        working_directory = settings.value('mainwindow/workingDirectory', '')

        if col == UploadDataItem.COL_VIDEO:
            dialog_title = _("Browse video...")
            extensions = get_select_videos()
        else: # if col == UploadDataItem.COL_SUB:
            dialog_title = _("Browse subtitle...")
            extensions = get_select_subtitles()

        file_path, t = QFileDialog.getOpenFileName(self, dialog_title, working_directory, extensions)
        if not file_path:
            return
        file_path = Path(file_path)
        settings.setValue('mainwindow/workingDirectory', str(file_path.parent))

        model = self._uploadModel

        if col == UploadDataItem.COL_VIDEO:
            callback = ProgressCallbackWidget(self)
            callback.show()
            videos, subs = scan_videopath(file_path, callback=callback, recursive=False)
            video = videos[0]
            index = model.createIndex(row, UploadDataItem.COL_VIDEO)
            model.setData(index, video, Qt.UserRole)

        elif col == UploadDataItem.COL_SUB:
            subtitle = LocalSubtitleFile(file_path)
            index = model.createIndex(row, UploadDataItem.COL_SUB)
            model.setData(index, subtitle, Qt.UserRole)
        else:
            log.warning('on_edit_item: nknown column: {column}'.format(column=col))

        self.upload_data_changed.emit()

    @pyqtSlot(int)
    def on_header_click(self, section):
        self._uploadModel.sort(section)
        self.upload_data_changed.emit()
