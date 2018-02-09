# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QAbstractItemModel, QModelIndex, QSize
from PyQt5.QtGui import QColor, QFont, QIcon

from subdownloader.client.gui.searchFileModel import Node

# FIXME: get rid of these imports (dependency on qtwidgets and provider)
from PyQt5.QtWidgets import QMessageBox
from subdownloader.client.gui.callback import ProgressCallbackWidget
from subdownloader.movie import RemoteMovie
from subdownloader.provider.SDService import OpenSubtitles_SubtitleFile, SearchByName
from subdownloader.subtitle2 import RemoteSubtitleFile

log = logging.getLogger('subdownloader.client.gui.videotreeview')


class SearchMore:
    def __init__(self, what, text):
        self._what = what
        self._text = text

    def what(self):
        return self._what

    def text(self):
        return self._text


# FIXME: use canFetchMore/fetchMore
# FIXME: split model and view
class VideoTreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self._all_root = Node(data=None, parent=None)
        self._root = self._all_root.clone()
        self._selected_node = None
        self._language_filter = []
        self._treeview = None

    def connect_treeview(self, treeview):
        self._treeview = treeview
        self._treeview.setModel(self)
        self._treeview.expanded.connect(self.on_node_expanded)
        self._treeview.collapsed.connect(self.on_node_collapsed)
        self._treeview.clicked.connect(self.on_node_clicked)

    @pyqtSlot(QModelIndex)
    def on_node_expanded(self, index):
        node = index.internalPointer()
        node.set_expanded(True)

        data = node.get_data()
        if isinstance(data, RemoteMovie):
            movie = data
            if not movie.get_nb_subs_available() and movie.get_nb_subs_total():
                callback = ProgressCallbackWidget(self._treeview)
                callback.set_title_text(_('Search'))
                callback.set_label_text(_("Searching..."))
                callback.set_cancellable(False)
                callback.set_block(True)

                callback.show()

                # FIXME: don't create SearchByName object here
                s = SearchByName('')
                callback.update(0)
                added_subtitles = s.search_more_subtitles(movie=movie)
                if added_subtitles is None:
                    QMessageBox.about(self._treeview, _("Info"),
                                      _("An unknown problem occurred or this type of movie cannot be handled."))
                    self._treeview.collapse(index)
                else:
                    node_origin = node.get_clone_origin()
                    for subtitle in added_subtitles:
                        node_origin.add_child(subtitle)
                    if movie.get_nb_subs_available() < movie.get_nb_subs_total():
                        node_origin.add_child(SearchMore(what=movie, text=_('More subtitles ...')))
                    self._apply_filters()
                callback.finish()

    @pyqtSlot(QModelIndex)
    def on_node_collapsed(self, index):
        node = index.internalPointer()
        node.set_expanded(False)

    node_clicked = pyqtSignal(object)

    @pyqtSlot(QModelIndex)
    def on_node_clicked(self, index):
        node = index.internalPointer()
        self._selected_node = node

        data = node.get_data()

        if isinstance(data, SearchMore):
            search_what = data.what()
            if isinstance(search_what, SearchByName):
                print('FIXME: SEARCH MORE MOVIES...')
            elif isinstance(search_what, RemoteMovie):
                print('FIXME: SEARCH MORE SUBTITLES...')
        else:
            self.node_clicked.emit(data)

    @pyqtSlot(list)
    def on_filter_languages_change(self, languages):
        self._language_filter = list(languages)
        self._apply_filters()

    def _apply_filters(self):
        self.beginResetModel()
        self._root = self._all_root.clone()
        # FIXME: apply filters...
        self.endResetModel()

        self.beginResetModel()
        self._root = self._all_root.clone()
        nodes_movie = list(self._root.get_children())
        for node_movie in nodes_movie:
            nodes_subtitle = list(node_movie.get_children())
            for node_subtitle in nodes_subtitle:
                data = node_subtitle.get_data()
                if isinstance(data, RemoteSubtitleFile):
                    subtitle = data
                    if self._language_filter and subtitle.get_language() not in self._language_filter:
                        node_movie.remove_child(node_subtitle)
        self.endResetModel()

        for node_movie_i, node_movie in enumerate(self._root.get_children()):
            movie_index = self.createIndex(node_movie_i, 0, node_movie)
            self._treeview.setExpanded(movie_index, node_movie.is_expanded())

    def search_movies(self, query):
        s = SearchByName(query=query)
        result = s.search_movies()
        if not result:
            return False

        movies = s.get_movies()

        self._all_root = Node(data=None, parent=None)
        for movie in movies:
            movie_node = self._all_root.add_child(movie)
            for subtitle in movie.get_subtitles():
                movie_node.add_child(subtitle)

        if len(s.get_movies()) < s.get_nb_movies_online():
            self._all_root.add_child(SearchMore(what=s, text=_("More movies ...")))

        self._apply_filters()
        return True

    def setData(self, index, value, role=None):
        if not index.isValid():
            return False
        node = index.internalPointer()
        data = node.get_data()

        if isinstance(data, OpenSubtitles_SubtitleFile):
            if role == Qt.CheckStateRole:
                node.set_checked(value)
                return True
        return False

    def data(self, index, role=None):
        if not index.isValid():
            return None
        node = index.internalPointer()
        data = node.get_data()

        if isinstance(data, RemoteMovie):
            movie = data

            if role == Qt.ForegroundRole:
                return QColor(Qt.blue)

            if role == Qt.DecorationRole:
                return QIcon(':/images/info.png').pixmap(QSize(24, 24), QIcon.Normal)

            if role == Qt.FontRole:
                return QFont('Arial', 9, QFont.Bold)

            if role == Qt.DisplayRole:
                imdb_identity = movie.get_identities().imdb_identity
                video_identity = movie.get_identities().video_identity
                text = '{movie_name} [{movie_year}] [{imdb_string}: ' \
                       '{imdb_rating}] ({nb_local}/{nb_server} subtitles)'.format(
                            movie_name=video_identity.get_name(),
                            movie_year=video_identity.get_year(),
                            imdb_string=_('IMDb rating'),
                            imdb_rating=imdb_identity.get_imdb_rating() if imdb_identity.get_imdb_rating() else '/',
                            nb_local=movie.get_nb_subs_available(),
                            nb_server=movie.get_nb_subs_total(),
                        )
                return text
            return None
        elif isinstance(data, OpenSubtitles_SubtitleFile):
            sub = data
            if role == Qt.DecorationRole:
                language = data.get_language()
                icon_mode = QIcon.Normal
                return QIcon(':/images/flags/{xx}.png'.format(xx=language.xx())).pixmap(QSize(24, 24), icon_mode)

            if role == Qt.FontRole:
                return QFont('Arial', 9, QFont.Bold)

            if role == Qt.CheckStateRole:
                if node.is_checked():
                    return Qt.Checked
                else:
                    return Qt.Unchecked

            if role == Qt.DisplayRole:
                uploader = sub.get_uploader()
                if not uploader:
                    uploader = _('Anonymous')

                line = '[{}]    '.format(sub.get_language().name())
                if sub.get_rating() != '0.0':  # if the rate is not 0
                    line += _('Rating: {}').format(sub.get_rating())
                # line += "  " + \
                #     _("Format: %s") % sub.getExtraInfo('format').upper()
                # line += "  " + \
                #     _("Downloads: %d") % int(
                #         sub.getExtraInfo('totalDownloads'))
                # line += "  " + \
                #     _("CDs: %d") % int(sub.getExtraInfo('totalCDs'))
                line += ' ' + _('Uploader: {}').format(uploader)
                return line
            return None
        elif isinstance(data, SearchMore):
            if role == Qt.DisplayRole:
                return data.text()
        else:
            log.warning('VideoTreeModel.get_data(): unknown data type')
            return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        data = index.internalPointer().get_data()
        if isinstance(data, RemoteMovie):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        elif isinstance(data, OpenSubtitles_SubtitleFile):
            return Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        elif isinstance(data, SearchMore):
            return Qt.ItemIsEnabled

    def get_selected_node(self):
        return self._selected_node

    def get_checked_subtitles(self):
        checked_subtitles = []
        for node_movie in self._root.get_children():
            for node_subtitle in node_movie.get_children():
                if node_subtitle.is_checked():
                    checked_subtitles.append(node_subtitle.get_data())
        return checked_subtitles

    def headerData(self, section, orientation, role=None):
        return None

    def index(self, row, column, parent=None, *args, **kwargs):
        if row < 0 or column < 0 or row >= self.rowCount(parent) or column >= self.columnCount(parent):
            return QModelIndex()

        if parent.isValid():
            parent_item = parent.internalPointer()
        else:
            parent_item = self._root

        if row >= len(parent_item.get_children()):
            return QModelIndex()

        child_item = parent_item.get_children()[row]
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        node = index.internalPointer()
        node_parent = node.get_parent()

        if node_parent == self._root:
            return QModelIndex()

        return self.createIndex(node_parent.parent_index(), 0, node_parent)

    def rowCount(self, parent=None, *args, **kwargs):
        if not parent or not parent.isValid():
            parent_node = self._root
        else:
            parent_node = parent.internalPointer()

        data = parent_node.get_data()
        if isinstance(data, RemoteMovie):
            movie = data
            if movie.get_nb_subs_available():
                return len(parent_node.get_children())
            else:
                if movie.get_nb_subs_total():
                    return 1
                else:
                    return 0
        else:
            return len(parent_node.get_children())

    def columnCount(self, parent=None, *args, **kwargs):
        if not parent or not parent.isValid():
            return 1
        else:
            return 1
