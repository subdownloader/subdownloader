# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from typing import Optional, Sequence

from subdownloader.client.gui.models.imdbSearchModel import ImdbSearchModel
from subdownloader.provider.imdb import ImdbMovieMatch

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QHeaderView, QTableView


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

    def set_imdb_data(self, imdb_data: Sequence[ImdbMovieMatch]):
        self._imdb_model.set_imdb_data(imdb_data)

    @pyqtSlot(int)
    def on_header_clicked(self, section: int) -> None:
        self._imdb_model.sort(section)

    imdb_selection_changed = pyqtSignal()

    def get_selected_imdb(self) -> Optional[ImdbMovieMatch]:
        selection = self.selectionModel().selection()

        if not selection.count():
            return None

        selection_range = selection.first()
        return self._imdb_model.get_imdb_at_row(selection_range.top())
