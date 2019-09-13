# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging
from pathlib import Path

from subdownloader.filescan import scan_videopath
from subdownloader.subtitle2 import LocalSubtitleFile

from subdownloader.client.gui import get_select_subtitles, get_select_videos
from subdownloader.client.gui.callback import ProgressCallbackWidget

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QItemSelectionModel, \
    QModelIndex, QSettings
from PyQt5.QtWidgets import QFileDialog, QTableView

from subdownloader.client.gui.models.upload import UploadModel, UploadDataItem

log = logging.getLogger('subdownloader.client.gui.views.upload')


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
