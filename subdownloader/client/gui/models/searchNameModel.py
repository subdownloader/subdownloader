# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QAbstractItemModel, QModelIndex, QSize
from PyQt5.QtGui import QColor, QFont, QIcon

from subdownloader.client.gui.models.searchFileModel import Node

# FIXME: get rid of these imports (dependency on qtwidgets and provider)
from PyQt5.QtWidgets import QMessageBox
from subdownloader.client.gui.callback import ProgressCallbackWidget
from subdownloader.client.gui.views.provider import _Optional
from subdownloader.movie import RemoteMovieNetwork
from subdownloader.provider.provider import ProviderConnectionError
from subdownloader.subtitle2 import RemoteSubtitleFile, SubtitleFileNetwork

log = logging.getLogger('subdownloader.client.gui.videotreeview')


class SearchMore:
    def __init__(self, text):
        self._text = text

    @property
    def text(self):
        return self._text


class SearchMoreMovies(SearchMore):
    def __init__(self, text):
        SearchMore.__init__(self, text)


class SearchMoreSubtitles(SearchMore):
    def __init__(self, text, movie):
        SearchMore.__init__(self, text)
        self._movie = movie

    @property
    def movie(self):
        return self._movie


# FIXME: use canFetchMore/fetchMore
# FIXME: split model and view
class VideoTreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self._all_root = Node(data=None, parent=None)
        self._root = self._all_root.clone()
        self._selected_node = None
        self._language_filter = []
        self._provider_filter = None
        self._treeview = None

    def set_treeview(self, treeview):
        self._treeview = treeview

    checkStateChanged = pyqtSignal()

    @pyqtSlot(QModelIndex)
    def on_node_expanded(self, index):
        node = index.internalPointer()
        node.set_expanded(True)

        data = node.get_data()
        if isinstance(data, RemoteMovieNetwork):
            remote_movie_network = data
            if not remote_movie_network.get_nb_subs_available() and remote_movie_network.get_nb_subs_total():
                callback = ProgressCallbackWidget(self._treeview)
                callback.set_title_text(_('Search'))
                callback.set_label_text(_('Searching...'))
                callback.set_cancellable(False)
                callback.set_block(True)

                callback.show()

                success = False
                try:
                    # FIXME: use callback
                    success = remote_movie_network.search_more_subtitles()
                except ProviderConnectionError:
                    pass

                if not success:
                    QMessageBox.about(self._treeview, _('Info'),
                                      _('An unknown problem occurred or this type of movie cannot be handled.'))
                    self._treeview.collapse(index)
                    node.set_expanded(False)
                    callback.finish()
                    return

                # FIXME: do not use Node objects but add metadata to objects
                self.underlying_data_changed()

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

        # FIXME: add callback to search_more_movies and search_more_subtitles
        if isinstance(data, SearchMoreMovies):
            self._query.search_more_movies()
            self.underlying_data_changed()
        elif isinstance(data, SearchMoreSubtitles):
            data.movie.search_more_subtitles()
            self.underlying_data_changed()
        else:
            self.node_clicked.emit(data)

    @pyqtSlot(list)
    def on_filter_languages_change(self, languages):
        self._language_filter = list(languages)
        self._apply_filters()

    @pyqtSlot(_Optional)
    def on_selected_provider_state_changed(self, opt):
        self._provider_filter = opt.value
        self._apply_filters()

    def _apply_filters(self):
        self.beginResetModel()
        self._root = self._all_root.clone()
        for node_movie_network in self._root.get_children():
            movie_network = node_movie_network.get_data()
            if not isinstance(movie_network, RemoteMovieNetwork):
                continue
            for node_subtitle_network in list(node_movie_network.get_children()):
                subtitle_network = node_subtitle_network.get_data()
                if not isinstance(subtitle_network, SubtitleFileNetwork):
                    continue
                if self._language_filter and subtitle_network.get_language() not in self._language_filter:
                    node_movie_network.remove_child(node_subtitle_network)
                else:
                    if self._provider_filter:
                        for node_remote_subtitle in list(node_subtitle_network.get_children()):
                            remote_subtitle = node_remote_subtitle.get_data()
                            if not isinstance(remote_subtitle, RemoteSubtitleFile):
                                continue
                            if remote_subtitle.get_provider() != type(self._provider_filter):
                                node_subtitle_network.remove_child(node_remote_subtitle)

        self.endResetModel()

        for node_movie_network_i, node_movie_network in enumerate(self._root.get_children()):
            movie_network_index = self.createIndex(node_movie_network_i, 0, node_movie_network)
            self._treeview.setExpanded(movie_network_index, node_movie_network.is_expanded())
            for node_subtitle_network_i, node_subtitle_network in enumerate(node_movie_network.get_children()):
                subtitle_network_index = self.createIndex(node_subtitle_network_i, 0, node_subtitle_network)
                self._treeview.setExpanded(subtitle_network_index, node_subtitle_network.is_expanded())

    @pyqtSlot()
    def underlying_data_changed(self):
        # Remove unknown movie networks and add new movie networks as Node
        new_movie_networks = list(self._query.movies)

        if self._all_root.get_children() and isinstance(self._all_root.get_children()[-1].get_data(), SearchMore):
            self._all_root.remove_child(self._all_root.get_children()[-1])

        for node_movie_network in list(self._all_root.get_children()):
            movie_network = node_movie_network.get_data()
            if movie_network not in self._query.movies:
                self._all_root.remove_child(node_movie_network)
            else:
                new_movie_networks.remove(movie_network)

        for new_movie_network in new_movie_networks:
            self._all_root.add_child(new_movie_network)

        for node_movie_network in self._all_root.get_children():
            movie_network = node_movie_network.get_data()

            if node_movie_network.get_children() and isinstance(node_movie_network.get_children()[-1].get_data(), SearchMore):
                node_movie_network.remove_child(node_movie_network.get_children()[-1])

            new_subtitle_networks = list(movie_network.get_subtitles())
            for node_subtitle_network in list(node_movie_network.get_children()):
                subtitle_network = node_subtitle_network.get_data()
                if not isinstance(subtitle_network, SubtitleFileNetwork):
                    continue

                if subtitle_network not in new_subtitle_networks:
                    node_movie_network.remove_child(node_subtitle_network)
                else:
                    new_subtitle_networks.remove(subtitle_network)

            for new_subtitle_network in new_subtitle_networks:
                node_movie_network.add_child(new_subtitle_network)

            for node_subtitle_network in list(node_movie_network.get_children()):
                subtitle_network = node_subtitle_network.get_data()
                if not isinstance(subtitle_network, SubtitleFileNetwork):
                    continue

                new_subtitles = list(subtitle_network.get_subtitles())
                for subtitle_node in list(node_subtitle_network.get_children()):
                    subtitle = subtitle_node.get_data()
                    if subtitle not in new_subtitles:
                        node_subtitle_network.remove_child(subtitle_node)
                    else:
                        new_subtitles.remove(subtitle)

                for new_subtitle in new_subtitles:
                    node_subtitle_network.add_child(new_subtitle)

            if movie_network.more_subtitles_available():
                node_movie_network.add_child(SearchMoreSubtitles(text=_('More subtitles ...'), movie=movie_network))

        if self._query.more_movies_available():
            self._all_root.add_child(SearchMoreMovies(text=_('More movies ...')))

        self._apply_filters()

    def set_query(self, query):
        self._query = query
        self._all_root = Node(data=None, parent=None)

        self.underlying_data_changed()

    def setData(self, index, value, role=None):
        if not index.isValid():
            return False
        node = index.internalPointer()
        data = node.get_data()

        if isinstance(data, RemoteSubtitleFile):
            if role == Qt.CheckStateRole:
                node.set_checked(value)
                node_network = node.get_parent()
                parent_index = self.createIndex(node_network.parent_index(), 0, node_network)
                self.dataChanged.emit(parent_index, parent_index, [Qt.CheckStateRole])
                self.checkStateChanged.emit()
                return True
        elif isinstance(data, SubtitleFileNetwork):
            if role == Qt.CheckStateRole:
                node_remote_subtitles = node.get_children()
                current_checked = self.data(index, role)
                checked = any == Qt.Checked
                if current_checked == Qt.Unchecked:
                    # Check only one remote subtitle
                    for node_rsubtitle in node_remote_subtitles:
                        if isinstance(node_rsubtitle.get_data(), RemoteSubtitleFile):
                            node_rsubtitle.set_checked(True)
                            break
                else:
                    # If currently checked, uncheck all. If partially checked, check all.
                    for node_rsubtitle in node_remote_subtitles:
                        if isinstance(node_rsubtitle.get_data(), RemoteSubtitleFile):
                            node_rsubtitle.set_checked(checked)

                next_index = self.createIndex(index.row() + 1, index.column(), index.internalPointer())
                self.dataChanged.emit(index, next_index, [Qt.CheckStateRole])
                self.checkStateChanged.emit()

                return True
        return False

    def data(self, index, role=None):
        if not index.isValid():
            return None
        node = index.internalPointer()
        data = node.get_data()

        if isinstance(data, RemoteMovieNetwork):
            movie_network = data

            if role == Qt.ForegroundRole:
                return QColor(Qt.blue)

            if role == Qt.DecorationRole:
                return QIcon(':/images/info.png').pixmap(QSize(24, 24), QIcon.Normal)

            if role == Qt.FontRole:
                return QFont('Arial', 9, QFont.Bold)

            if role == Qt.DisplayRole:
                imdb_identity = movie_network.get_identities().imdb_identity
                video_identity = movie_network.get_identities().video_identity
                text = '{movie_name} [{movie_year}] [{imdb_string}: ' \
                       '{imdb_rating}] ({nb_local}/{nb_server} subtitles)'.format(
                            movie_name=video_identity.get_name(),
                            movie_year=video_identity.get_year(),
                            imdb_string=_('IMDb rating'),
                            imdb_rating=imdb_identity.get_imdb_rating() if imdb_identity.get_imdb_rating() else '/',
                            nb_local=movie_network.get_nb_subs_available(),
                            nb_server=movie_network.get_nb_subs_total(),
                        )
                return text
            return None
        elif isinstance(data, SubtitleFileNetwork):
            sub = data

            if role == Qt.DecorationRole:
                language = data.get_language()
                icon_mode = QIcon.Normal
                return QIcon(':/images/flags/{xx}.png'.format(xx=language.xx())).pixmap(QSize(24, 24), icon_mode)

            if role == Qt.FontRole:
                return QFont('Arial', 9, QFont.Bold)

            if role == Qt.CheckStateRole:
                nodes_rsubtitle = list(filter(lambda n : isinstance(n.get_data(), RemoteSubtitleFile), node.get_children()))
                nb_subtitles = len(nodes_rsubtitle)
                nb_selected = sum([1 if node_rsub.is_checked() else 0 for node_rsub in nodes_rsubtitle])
                if nb_selected == 0:
                    return Qt.Unchecked
                elif nb_selected < nb_subtitles:
                    return Qt.PartiallyChecked
                else:
                    return Qt.Checked

            if role == Qt.DisplayRole:
                line = '[{language}] {providers_str} | {size_str}'.format(
                    language=sub.get_language().name(),
                    providers_str=_('{nb_providers} provider(s)').format(
                        nb_providers=sub.nb_providers()),
                    size_str='{kibibytes:.2f} kiB'.format(kibibytes=sub.get_file_size()/1024),
                )
                return line
            return None

        elif isinstance(data, RemoteSubtitleFile):
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
                detail_str = '{rating_str} | {uploader_str}'.format(
                    rating_str=_('Rating: {rating}').format(rating=sub.get_rating()),
                    uploader_str=_('Uploader: {uploader}').format(uploader=uploader),
                )

                line = '[{provider}] {filename} | {detail}'.format(
                    provider=sub.get_provider().get_name(),
                    filename=sub.get_filename(),
                    detail=detail_str,
                )
                return line
            return None
        elif isinstance(data, SearchMore):
            if role == Qt.DisplayRole:
                return data.text
        else:
            log.warning('VideoTreeModel.get_data(): unknown data type')
            return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        data = index.internalPointer().get_data()
        if isinstance(data, RemoteMovieNetwork):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        elif isinstance(data, SubtitleFileNetwork):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsAutoTristate | Qt.ItemIsUserCheckable
        elif isinstance(data, RemoteSubtitleFile):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren | Qt.ItemIsUserCheckable
        elif isinstance(data, SearchMore):
            return Qt.ItemIsEnabled
        else:
            return Qt.NoItemFlags

    def get_selected_node(self):
        return self._selected_node

    def get_checked_subtitles(self):
        checked_subtitles = []
        for node_movie in self._root.get_children():
            for node_subtitle_network in node_movie.get_children():
                for node_rsubtitle in node_subtitle_network.get_children():
                    if node_rsubtitle.is_checked():
                        checked_subtitles.append(node_rsubtitle.get_data())
        return checked_subtitles

    def uncheck_subtitles(self, subs):
        for node_movie in self._root.get_children():
            for node_subtitle_network in node_movie.get_children():
                for node_rsubtitle in node_subtitle_network.get_children():
                    if isinstance(node_rsubtitle.get_data(), RemoteSubtitleFile) and node_rsubtitle.get_data() in subs:
                        node_rsubtitle.set_checked(False)
        self.underlying_data_changed()
        self.checkStateChanged.emit()

    def getSelectedItem(self, index):
        # FIXME: give better name!
        # We want to know the current Selected Item
        if index is None:
            index = QModelIndex()

        if not index.isValid():
            return None

        selected_node = index.internalPointer()
        return selected_node.get_data()

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
        if isinstance(data, RemoteMovieNetwork):
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
