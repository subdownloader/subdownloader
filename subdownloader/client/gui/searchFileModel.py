# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtCore import pyqtSlot, Qt, QAbstractItemModel, QModelIndex, QSize
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette

from subdownloader.subtitle2 import LocalSubtitleFile, RemoteSubtitleFile, SubtitleFileNetwork, SubtitleFileStorage
from subdownloader.video2 import VideoFile

log = logging.getLogger('subdownloader.client.gui.videomodel2')


class Node:
    def __init__(self, data, parent, clone_original=None):
        self._data = data
        self._checked = False
        self._parent = parent
        self._children = []
        self._expanded = False
        self._clone_original = clone_original

    def get_data(self):
        return self._data

    def set_checked(self, checked):
        if self._clone_original:
            self._clone_original.set_checked(checked)
        else:
            self._checked = checked

    def is_checked(self):
        if self._clone_original:
            return self._clone_original.is_checked()
        else:
            return self._checked

    def set_expanded(self, expanded):
        if self._clone_original:
            self._clone_original.set_expanded(expanded)
        else:
            self._expanded = expanded

    def is_expanded(self):
        if self._clone_original:
            return self._clone_original.is_expanded()
        else:
            return self._expanded

    def get_parent(self):
        return self._parent

    def get_children(self):
        return self._children

    def add_child(self, data):
        node = Node(data, self)
        self._children.append(node)
        return node

    def remove_child(self, node):
        self._children.remove(node)

    def index(self, child):
        return self._children.index(child)

    def parent_index(self):
        if self._parent:
            try:
                return self._parent.index(self)
            except ValueError:
                return 0
        else:
            return 0

    def get_clone_origin(self):
        if self._clone_original is None:
            return self
        else:
            return self._clone_original.get_clone_origin()

    def clone(self, parent=None):
        node = Node(data=self._data, parent=parent, clone_original=self)
        node._checked = self._checked
        for child in self.get_children():
            node._children.append(child.clone(parent=node))
        return node


# FIXME: split model and view
class VideoModel(QAbstractItemModel):
    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self._all_root = Node(data=None, parent=None)
        self._root = self._all_root.clone()
        self._language_filter = []
        self._treeview = None

    def connect_treeview(self, treeview):
        self._treeview = treeview
        self._treeview.setModel(self)
        self._treeview.expanded.connect(self.on_node_expanded)
        self._treeview.collapsed.connect(self.on_node_collapsed)

    @pyqtSlot(QModelIndex)
    def on_node_expanded(self, index):
        node = index.internalPointer()
        node.set_expanded(True)

    @pyqtSlot(QModelIndex)
    def on_node_collapsed(self, index):
        node = index.internalPointer()
        node.set_expanded(False)

    @pyqtSlot(list)
    def on_filter_languages_change(self, languages):
        self._language_filter = list(languages)
        self._apply_filters()

    def set_videos(self, videos):
        log.debug('set_videos(#videos={nbVideos})'.format(nbVideos=len(videos)))

        self._all_root = Node(data=None, parent=None)
        for video in videos:
            video_node = self._all_root.add_child(video)
            for subtitle_network in video.get_subtitles().get_subtitle_networks():
                subtitle_network_node = video_node.add_child(subtitle_network)
                for subtitle in subtitle_network.get_subtitles():
                    subtitle_node = subtitle_network_node.add_child(subtitle)
                    if isinstance(subtitle, LocalSubtitleFile):
                        subtitle_node.set_checked(True)

        self._apply_filters()

    def clear(self):
        log.debug("Clearing VideoTree")

        self._all_root = Node(data=None, parent=None)
        self._apply_filters()

    def _apply_filters(self):
        self.beginResetModel()
        self._root = self._all_root.clone()
        nodes_video = list(self._root.get_children())
        for node_video in nodes_video:
            nodes_subtitle_network = list(node_video.get_children())
            for node_subtitle_network in nodes_subtitle_network:
                subtitle_network = node_subtitle_network.get_data()
                if self._language_filter and subtitle_network.get_language() not in self._language_filter:
                    node_video.remove_child(node_subtitle_network)
        self.endResetModel()

        for node_video_i, node_video in enumerate(self._root.get_children()):
            video_index = self.createIndex(node_video_i, 0, node_video)
            self._treeview.setExpanded(video_index, node_video.is_expanded())
            for node_subtitle_i, node_subtitle in enumerate(node_video.get_children()):
                subtitle_index = self.createIndex(node_subtitle_i, 0, node_subtitle)
                self._treeview.setExpanded(subtitle_index, node_subtitle.is_expanded())

    def setData(self, index, any, role=None):
        if not index.isValid():
            return False
        node = index.internalPointer()
        data = node.get_data()

        if isinstance(data, RemoteSubtitleFile):
            if role == Qt.CheckStateRole:
                node.set_checked(any)
                node_parent = node.get_parent()
                parent_index = self.createIndex(node_parent.parent_index(), 0, node_parent)
                self.dataChanged.emit(parent_index, parent_index, [Qt.CheckStateRole])
                return True
        elif isinstance(data, SubtitleFileNetwork):
            if role == Qt.CheckStateRole:
                node_network_subtitles = node.get_children()
                current_checked = self.data(index, role)
                checked = any == Qt.Checked
                if current_checked == Qt.Unchecked:
                    # Check only one remote subtitle
                    for node_subtitle in node_network_subtitles:
                        if isinstance(node_subtitle.get_data(), RemoteSubtitleFile):
                            node_subtitle.set_checked(True)
                            break
                else:
                    # If currently checked, uncheck all. If partially checked, check all.
                    for node_subtitle in node_network_subtitles:
                        if isinstance(node_subtitle.get_data(), RemoteSubtitleFile):
                            node_subtitle.set_checked(checked)

                next_index = self.createIndex(index.row() + 1, index.column(), index.internalPointer())
                self.dataChanged.emit(index, next_index, [Qt.CheckStateRole])
                return True
        return False

    def data(self, index, role=None):
        if not index.isValid():
            return None
        node_data = index.internalPointer()
        data = node_data.get_data()

        if isinstance(data, VideoFile):
            if role == Qt.ForegroundRole:
                return QColor(Qt.blue)

            if role == Qt.BackgroundRole:
                return QPalette().brush(QPalette.Normal, QPalette.Base)

            #FIXME: get movie info
            movie_info = None #data.getMovieInfo()
            if role == Qt.DecorationRole:
                if movie_info:
                    return QIcon(':/images/info.png').pixmap(QSize(24, 24), QIcon.Normal)
                else:
                    return None

            if role == Qt.FontRole:
                return QFont('Arial', 9, QFont.Bold)

            if role == Qt.DisplayRole:
                if movie_info:
                    # The ENGLISH Movie Name is priority, if not shown, then we
                    # show the original name.
                    if movie_info["MovieNameEng"]:
                        movieName = movie_info["MovieNameEng"]
                    else:
                        movieName = movie_info["MovieName"]

                    info = "%s [%s]" % (movieName,  movie_info["MovieYear"])
                    if movie_info["MovieImdbRating"]:
                        info += " " + \
                            _("[IMDB Rate: %s]") % movie_info[
                                "MovieImdbRating"]
                    info += " <%s>" % data.get_filepath()
                    return info
                else:
                    return str(data.get_filepath())

            return None

        elif isinstance(data, SubtitleFileNetwork):
            node_network = node_data
            node_network_subtitles = node_network.get_children()
            sub = data

            if role == Qt.BackgroundRole:
                return QPalette().brush(QPalette.Normal, QPalette.AlternateBase)

            if role == Qt.DecorationRole:
                xx = data.get_language().xx()
                iconMode = QIcon.Disabled if isinstance(sub, LocalSubtitleFile) else QIcon.Normal
                return QIcon(':/images/flags/{xx}.png'.format(xx=xx)).pixmap(QSize(24, 24), iconMode)

            if role == Qt.FontRole:
                return QFont('Arial', 9, QFont.Bold)

            if role == Qt.CheckStateRole:
                nb_subtitles = len(node_network_subtitles)
                nb_selected = sum([1 if node_sub.is_checked() else 0 for node_sub in node_network_subtitles])
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

        elif isinstance(data, SubtitleFileStorage):
            sub = data

            if role == Qt.BackgroundRole:
                return QPalette().brush(QPalette.Normal, QPalette.Base)

            if role == Qt.DecorationRole:
                xx = data.get_language().xx()
                iconMode = QIcon.Disabled if isinstance(sub, LocalSubtitleFile) else QIcon.Normal
                return QIcon(':/images/flags/{xx}.png'.format(xx=xx)).pixmap(QSize(24, 24), iconMode)

            if role == Qt.ForegroundRole:
                if isinstance(sub, LocalSubtitleFile):
                    return QColor(Qt.red)

            if role == Qt.FontRole:
                return QFont('Arial', 9, QFont.Bold)

            if role == Qt.CheckStateRole:
                if isinstance(sub, LocalSubtitleFile):
                    return Qt.Checked
                if index.internalPointer().is_checked():
                    return Qt.Checked
                else:
                    return Qt.Unchecked

            if role == Qt.DisplayRole:
                if isinstance(sub, LocalSubtitleFile):
                    detail_str = '{already_str}'.format(
                        already_str=_('Already downloaded'),
                    )
                elif isinstance(sub, RemoteSubtitleFile):
                    uploader = sub.get_uploader()
                    if not uploader:
                        uploader = _('Anonymous')
                    detail_str = '{rating_str} | {uploader_str}'.format(
                        rating_str=_('Rating: {rating}').format(rating=sub.get_rating()),
                        uploader_str=_('Uploader: {uploader}').format(uploader=uploader),
                    )
                else:
                    log.error('Unknown subtitle type: {type_str}'.format(type_str=type(sub)))
                    detail_str = 'XXX'

                line = '[{language_name}] {filename} | {detail}'.format(
                    language_name=sub.get_language().name(),
                    filename=sub.get_filename(),
                    detail=detail_str,
                )
                return line
            return None

        else:
            log.error('VideoTreeModel.data(): illegal data type')
            return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        item = index.internalPointer().get_data()
        if isinstance(item, RemoteSubtitleFile):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren | Qt.ItemIsUserCheckable
        elif isinstance(item, LocalSubtitleFile):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren
        elif isinstance(item, VideoFile):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        elif isinstance(item, SubtitleFileNetwork):
            return Qt.ItemIsEnabled | Qt.ItemIsAutoTristate | Qt.ItemIsUserCheckable
        else:
            log.error('VideoTreeModel.flags(): illegal data type: {item_type}'.format(item_type=type(item)))
            return Qt.NoItemFlags

    def getSelectedItem(self, index):
        # FIXME: give better name!
        # We want to know the current Selected Item
        if index is None:
            index = QModelIndex()

        if not index.isValid():
            return None

        selected_node = index.internalPointer()
        return selected_node.get_data()

    def get_checked_subtitles(self):
        checked_subtitles = []
        for video_node in self._root.get_children():
            for network_node in video_node.get_children():
                for subtitle_node in network_node.get_children():
                    if isinstance(subtitle_node.get_data(), RemoteSubtitleFile) and subtitle_node.is_checked():
                        checked_subtitles.append(subtitle_node.get_data())
        return checked_subtitles

    def headerData(self, section, orientation, role=None):
        """
        Return header for row and column
        :param section: row or column number
        :param orientation: Qt.Horizontal or Qt.Vertical
        :param role: Qt.DiaplayRole
        :return: requested header data = None (no header)
        """
        return None

    def index(self, row, column, parent=None, *args, **kwargs):
        if row < 0 or column < 0: # or row >= self.rowCount(parent) or column >= self.columnCount(parent):
            return QModelIndex()

        if not parent or not parent.isValid():
            parent_item = self._root
        else:
            parent_item = parent.internalPointer()

        if row > len(parent_item.get_children()):
            return QModelIndex()

        child_item = parent_item.get_children()[row]
        return self.createIndex(row, column, child_item)

    def parent(self, index=None):
        if not index or not index.isValid():
            return QModelIndex()

        node = index.internalPointer()
        node_parent = node.get_parent()

        if not node_parent or node_parent == self._root:
            return QModelIndex()

        return self.createIndex(node_parent.parent_index(), 0, node_parent)

    def rowCount(self, parent=None, *args, **kwargs):
        if parent is None:
            parent = QModelIndex()

        if not parent.isValid():
            return len(self._root.get_children())

        parent_item = parent.internalPointer()
        return len(parent_item.get_children())

    def columnCount(self, parent=None, *args, **kwargs):
        if not parent or not parent.isValid():
            return 1
        else:
            return 1
