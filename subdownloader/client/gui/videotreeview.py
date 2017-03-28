# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QSize
from PyQt5.QtGui import QColor, QFont, QIcon

from subdownloader.FileManagement.search import Movie
from subdownloader.FileManagement.subtitlefile import SubtitleFile
from subdownloader.FileManagement.videofile import VideoFile

log = logging.getLogger('subdownloader.client.gui.videotreeview')


class Node:
    def __init__(self, data, parent=None):
        self.data = data
        self.checked = False
        self.parent = parent
        self.children = []

    def add_child(self, data):
        node = Node(data, self)
        self.children.append(node)
        return node

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        else:
            return 0


class VideoTreeModel(QAbstractItemModel):

    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self.root = Node('')
        self.selectedNode = None
        self.languageFilter = None
        self.videoResultsBackup = []
        self.moviesResultsBackup = None

    def setVideos(self, videoResults, filter=None, append=False):
        log.debug('VideoTreeModel.setVideos(#videoResults={nbVideoResults})'.format(nbVideoResults=len(videoResults)))
        if append:
            self.videoResultsBackup += videoResults
        else:
            self.videoResultsBackup = videoResults

        if videoResults:
            for video in videoResults:
                videoNode = self.root.add_child(video)
                for sub in video._subs:
                    sub_lang_xxx = sub.getLanguage().xxx()
                    # Filter subtitles by Language
                    if (not filter) or (sub_lang_xxx in filter):
                        videoNode.add_child(sub)

    def setMovies(self, moviesResults, filter=None):
        self.moviesResultsBackup = moviesResults

        if moviesResults:
            for movie in moviesResults:
                movieNode = self.root.add_child(movie)
                if len(movie.subtitles):
                    # We'll recount the number of subtitles after filtering
                    movieNode.data.totalSubs = 0
                for sub in movie.subtitles:
                    sub_lang_xxx = sub.getLanguage().xxx()
                    # Filter subtitles by Language
                    if (not filter) or (sub_lang_xxx in filter):
                        movieNode.add_child(sub)
                        movieNode.data.totalSubs += 1

    def clearTree(self):
        log.debug("Clearing VideoTree")
        self.modelAboutToBeReset.emit()
        self.selectedNode = None
        self.languageFilter = None
        del self.root
        self.root = Node("")
        self.modelReset.emit()  # Better than emit the dataChanged signal

    def selectMostRatedSubtitles(self):
        for video in self.root.children:
            if len(video.children):
                # We suppossed that the first subtitle is the most rated one
                subtitle = video.children[0]
                if not (subtitle.data).isLocal():
                    subtitle.checked = True

    def unselectSubtitles(self):
        for video in self.root.children:
            for subtitle in video.children:
                subtitle.checked = False

    def setLanguageFilter(self, languages):
        # self.clearTree()
        self.languageFilter = languages
        languages_str = [language.xxx() for language in languages]
        if self.videoResultsBackup:
            self.setVideos(self.videoResultsBackup, languages_str)
        elif self.moviesResultsBackup:
            self.setMovies(self.moviesResultsBackup, languages_str)

    def data(self, index, role):
        if not index.isValid():
            return None
        data = index.internalPointer().data

        if type(data) == SubtitleFile:
            sub = data
            if role == Qt.DecorationRole:
                xx = data.getLanguage().xx()
                iconMode = QIcon.Disabled if sub.isLocal() else QIcon.Normal
                return QIcon(':/images/flags/{xx}.png'.format(xx=xx)).pixmap(QSize(24, 24), iconMode)

            if role == Qt.ForegroundRole:
                if sub.isLocal():
                    return QColor(Qt.red)

            if role == Qt.FontRole:
                return QFont('Arial', 9, QFont.Bold)

            if role == Qt.CheckStateRole:
                if index.internalPointer().checked:
                    return Qt.Checked
                else:
                    return Qt.Unchecked

            if role == Qt.DisplayRole:
                uploader = sub.getUploader()
                if not uploader:
                    uploader = _('Anonymous')

                # Constructing the row text to show in the TreeView
                line = "[%s]" % _(sub.getLanguage().name())

                if hasattr(sub, "_filename"):  # if hash searching
                    line += "    %s  " % sub.get_filepath()
                    if sub.getRating() != '0.0':  # if the rate is not 0
                        line += _("[Rate: %s]") % str(sub.getRating())

                if sub.isLocal():
                    line += "  " + _("(Already downloaded)")
                    return line
                elif hasattr(sub, "_filename"):  # Subtitle found from hash
                    line += "  " + _("Uploader: %s") % uploader
                    return line
                else:  # Subtitle found from movie name
                    line = "[%s]    " % _(sub.getLanguage().name())
                    if sub.getRating() != '0.0':  # if the rate is not 0
                        line += _("Rate: %s") % str(sub.getRating())
                    line += "  " + \
                        _("Format: %s") % sub.getExtraInfo('format').upper()
                    line += "  " + \
                        _("Downloads: %d") % int(
                            sub.getExtraInfo('totalDownloads'))
                    line += "  " + \
                        _("CDs: %d") % int(sub.getExtraInfo('totalCDs'))
                    line += "  " + _("Uploader: %s") % uploader
                    return line
            return None
        elif type(data) == VideoFile:
            if role == Qt.ForegroundRole:
                return QColor(Qt.blue)

            movie_info = data.getMovieInfo()
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
                    return data.get_filepath()

            return None
        elif type(data) == Movie:
            if role == Qt.ForegroundRole:
                return QColor(Qt.blue)

            movie = data
            if role == Qt.DecorationRole:
                return QIcon(':/images/info.png').pixmap(QSize(24, 24), QIcon.Normal)

            if role == Qt.FontRole:
                return QFont('Arial', 9, QFont.Bold)

            if role == Qt.DisplayRole:
                info = "%s [%s]" % (movie.MovieName,  movie.MovieYear)
                if movie.IMDBRating:
                    info += "  " + _("[IMDB Rate: %s]") % movie.IMDBRating
                info += "  " + _("(%d subtitles)") % int(movie.totalSubs)

                if not len(movie.subtitles):
                    # TODO: Clicking to expand (+) no subtitles are displayed
                    # (LP: #312689)
                    pass
                    #info += " (Double Click here)"

                return info

            return None
        else:
            log.error('VideoTreeModel.data(): illegal data type')
            return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        data = index.internalPointer().data
        if type(data) == SubtitleFile:  # It's a SUBTITLE treeitem.
            return Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        elif type(data) == VideoFile:  # It's a VIDEO treeitem.
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        elif type(data) == Movie:  # It's a Movie  treeitem.
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def updateMovie(self, index, filter=None):
        movie = index.internalPointer().data
        movieNode = index.internalPointer()
        movieNode.children = []
        for sub in movie.subtitles:
            sub_lang_xxx = sub.getLanguage().xxx()
            # Filter subtitles by Language
            if (not filter) or (filter == sub_lang_xxx):
                movieNode.add_child(sub)

    def getSelectedItem(self, index=None):
        if index == None:  # We want to know the current Selected Item
            return self.selectedNode

        if not index.isValid():
            return None
        else:
            self.selectedNode = index.internalPointer()
            return index.internalPointer()

    def getCheckedSubtitles(self):
        checkedSubs = []
        for video in self.root.children:
            for subtitle in video.children:
                if subtitle.checked:
                    checkedSubs.append(subtitle.data)
        return checkedSubs

    def headerData(self, section, orientation, role):
        """
        Return header for row and column
        :param section: row or column number
        :param orientation: Qt.Horizontal or Qt.Vertical
        :param role: Qt.DiaplayRole
        :return: requested header data = None (no header)
        """
        return None

    def index(self, row, column, parent):
        if row < 0 or column < 0 or row >= self.rowCount(parent) or column >= self.columnCount(parent):
            return QModelIndex()

        if parent.isValid():
            parentItem = parent.internalPointer()
        else:
            parentItem = self.root

        if row >= len(parentItem.children):
            return QModelIndex()

        childItem = parentItem.children[row]
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent

        if parentItem == self.root:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.isValid():
            parentItem = parent.internalPointer()
        else:
            parentItem = self.root

        if type(parentItem.data) == Movie:
            # FIXME: len(movie.subtitles) == #subtitles fetched, movie.totalSubs == #subtitles on server
            # ==> be able to fetch more subtitles until len(movie.subtitles) == movie.totalsubtitles
            movie = parentItem.data
            if movie.subtitles:
                # We have local subtitles for this move
                return len(movie.subtitles)
            else:
                # Mo local subtitles for this movie ==> available on server?
                if movie.totalSubs > 0:
                    # if the server has some, fake one child (1 row)
                    return 1
                else:
                    # the server has none, so no child (0 rows)
                    return 0
        else:
            return len(parentItem.children)

    def columnCount(self, parent):
        if parent.isValid():
            return 1
        else:
            # header
            return 1
