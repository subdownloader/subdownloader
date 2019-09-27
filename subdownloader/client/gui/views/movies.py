# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu, QTreeView

from subdownloader.movie import RemoteMovieNetwork
from subdownloader.subtitle2 import RemoteSubtitleFile, SubtitleFileNetwork
from subdownloader.client.gui.models.searchNameModel import VideoTreeModel

log = logging.getLogger('subdownloader.client.gui.views.movies')


class MoviesTreeView(QTreeView):
    def __init__(self, parent):
        QTreeView.__init__(self, parent)
        self._moviesModel = VideoTreeModel()
        # FIXME: Use QAbstractProxyModel to filter

        self.setup_ui()
        self._moviesModel = None

    def setModel(self, model):
        QTreeView.setModel(self, model)
        self._moviesModel = model
        self._moviesModel.set_treeview(self)
        self.expanded.connect(self._moviesModel.on_node_expanded)
        self.collapsed.connect(self._moviesModel.on_node_collapsed)
        self.clicked.connect(self._moviesModel.on_node_clicked)

    def setup_ui(self):
        self.setHeaderHidden(True)
        self.setUniformRowHeights(True)

    def reset(self):
        QTreeView.reset(self)

    view_imdb_online = pyqtSignal(RemoteMovieNetwork)
    view_subtitle_online = pyqtSignal(RemoteSubtitleFile)
    download_subtitle = pyqtSignal(RemoteSubtitleFile)

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return
        self._moviesModel.on_node_clicked(index)

        node = self._moviesModel.get_selected_node()
        if node is None:
            return

        menu = QMenu('Menu', self)
        data = node.get_data()
        if isinstance(data, RemoteMovieNetwork):
            online_action = QAction(QIcon(':/images/info.png'), _('View IMDb info'), self)
            online_action.triggered.connect(self._onContextMenuImdb)
            menu.addAction(online_action)
        if isinstance(data, (SubtitleFileNetwork, RemoteSubtitleFile)):
            download_action = QAction(QIcon(':/images/download.png'), _('Download'), self)
            download_action.triggered.connect(self._onContextMenuDownload)
            menu.addAction(download_action)
        if isinstance(data, RemoteSubtitleFile):
            online_action = QAction(QIcon(data.get_provider().get_icon()), _('View online info'), self)
            online_action.triggered.connect(self._onContextMenuSubtitleDetails)
            menu.addAction(online_action)
        menu.exec_(self.mapToGlobal(event.pos()))

    def _onContextMenuImdb(self):
        node = self._moviesModel.get_selected_node()
        data = node.get_data()
        assert isinstance(data, RemoteMovieNetwork)
        self.view_imdb_online.emit(data)

    def _onContextMenuDownload(self):
        node = self._moviesModel.get_selected_node()
        data = node.get_data()
        assert isinstance(data, (SubtitleFileNetwork, RemoteSubtitleFile))
        if isinstance(data, SubtitleFileNetwork):
            data = data[0]
        assert isinstance(data, RemoteSubtitleFile)
        self.download_subtitle.emit(data)

    def _onContextMenuSubtitleDetails(self):
        node = self._moviesModel.get_selected_node()
        data = node.get_data()
        assert isinstance(data, RemoteSubtitleFile)
        self.view_subtitle_online.emit(data)
