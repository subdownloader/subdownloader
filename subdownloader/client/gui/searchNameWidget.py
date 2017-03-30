# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
import re
import sys
import webbrowser

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QModelIndex, QPoint, QSettings, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog, QMenu, QMessageBox, QWidget
from subdownloader.FileManagement.search import Link, Movie, SearchByName
from subdownloader.FileManagement.subtitlefile import SubtitleFile

from subdownloader.FileManagement.videofile import VideoFile
from subdownloader.client.gui.callback import ProgressCallbackWidget
from subdownloader.client.gui.searchNameWidget_ui import Ui_SearchNameWidget
from subdownloader.client.gui.state import State
from subdownloader.client.gui.videotreeview import VideoTreeModel
from subdownloader.languages.language import Language, UnknownLanguage

log = logging.getLogger('subdownloader.client.gui.searchNameWidget')


class SearchNameWidget(QWidget):

    language_filter_change = pyqtSignal(list)

    def __init__(self):
        QWidget.__init__(self)

        self._state = None

        self.ui = Ui_SearchNameWidget()
        self.setup_ui()

    def set_state(self, state):
        self._state = state
        self._state.login_status_changed.connect(self.on_login_state_changed)
        self._state.interface_language_changed.connect(self.on_interface_language_changed)

    def get_state(self):
        return self._state

    def setup_ui(self):
        self.ui.setupUi(self)

        self.ui.filterLanguage.selected_language_changed.connect(self.on_language_combobox_filter_change)

        self.language_filter_change.connect(self.on_language_filter_change)

        self.ui.buttonSearchByName.clicked.connect(self.onButtonSearchByTitle)
        self.ui.movieNameText.returnPressed.connect(self.onButtonSearchByTitle)
        self.ui.buttonDownloadByTitle.clicked.connect(self.onButtonDownloadByTitle)

        self.ui.buttonIMDBByTitle.clicked.connect(self.onViewOnlineInfo)
        self.moviesModel = VideoTreeModel(self)
        self.ui.moviesView.setModel(self.moviesModel)

        self.ui.moviesView.clicked.connect(self.onClickMovieTreeView)
        self.moviesModel.dataChanged.connect(self.subtitlesMovieCheckedChanged)

        self.ui.moviesView.expanded.connect(self.onExpandMovie)
        self.ui.moviesView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.moviesView.customContextMenuRequested.connect(self.onContext)

        self.retranslate()

    def retranslate(self):
        self.ui.filterLanguage.set_unknown_text(_("All languages"))

    @pyqtSlot(Language)
    def on_interface_language_changed(self, language):
        self.ui.retranslateUi(self)
        self.retranslate()

    @pyqtSlot(int, str)
    def on_login_state_changed(self, state, message):
        log.debug('on_login_state_changed(state={state}, message={message}'.format(state=state, message=message))
        if state in (State.LOGIN_STATUS_LOGGED_OUT, State.LOGIN_STATUS_BUSY):
            self.ui.buttonDownloadByTitle.setEnabled(False)
            self.ui.buttonIMDBByTitle.setEnabled(False)
        elif state == State.LOGIN_STATUS_LOGGED_IN:
            self.ui.buttonDownloadByTitle.setEnabled(True)
            self.ui.buttonIMDBByTitle.setEnabled(True)
        else:
            log.warning('unknown state')

    @pyqtSlot(Language)
    def on_language_combobox_filter_change(self, language):
        if language.is_generic():
            self.language_filter_change.emit(self.get_state().get_permanent_language_filter())
        else:
            self.language_filter_change.emit([language])

    @pyqtSlot(list)
    def on_permanent_language_filter_change(self, languages):
        selected_language = self.ui.filterLanguage.get_selected_language()
        if selected_language.is_generic():
            self.language_filter_change.emit(languages)

    @pyqtSlot(list)
    def on_language_filter_change(self, languages):
        log.debug("Filtering subtitles by language: {languages}".format(languages=languages))
        self.ui.moviesView.clearSelection()
        self.moviesModel.clearTree()
        self.moviesModel.setLanguageFilter(languages=languages)
        self.ui.moviesView.expandAll()

    @pyqtSlot()
    def onButtonSearchByTitle(self):
        if not self.ui.movieNameText.text().strip():
            QMessageBox.about(self, _("Info"), _("You must enter at least one character in movie name"))
        else:
            self.ui.buttonSearchByName.setEnabled(False)

            callback = ProgressCallbackWidget(self)

            callback.set_title_text(_('Search'))
            callback.set_label_text(_("Searching..."))
            callback.set_block(True)

            callback.show()
            callback.update(0)

            self.moviesModel.clearTree()
            # This was a solution found to refresh the treeView
            self.ui.moviesView.expandAll()
            s = SearchByName()
            selected_language = self.ui.filterLanguage.get_selected_language()
            selected_language_xxx = None if selected_language.is_generic() else selected_language.xxx()
            search_text = self.ui.movieNameText.text()
            # This should be in a thread to be able to Cancel
            movies = s.search_movie(languages=[UnknownLanguage.create_generic()], moviename=search_text)
            if movies is None:
                QMessageBox.about(self, _("Info"), _(
                    "The server is momentarily unavailable. Please try later."))
                callback.finish()
                self.ui.buttonSearchByName.setEnabled(True)
                return
            self.moviesModel.setMovies(movies, selected_language_xxx)
            if len(movies) == 1:
                self.ui.moviesView.expandAll()
            else:
                self.ui.moviesView.collapseAll()
            callback.finish()
            self.ui.buttonSearchByName.setEnabled(True)

    @pyqtSlot()
    def subtitlesMovieCheckedChanged(self):
        subs = self.moviesModel.getCheckedSubtitles()
        if subs:
            self.ui.buttonDownloadByTitle.setEnabled(True)
        else:
            self.ui.buttonDownloadByTitle.setEnabled(False)

    @pyqtSlot()
    def onButtonDownloadByTitle(self):
        subs = self.moviesModel.getCheckedSubtitles()
        total_subs = len(subs)
        if not subs:
            QMessageBox.about(
                self, _("Error"), _("No subtitles selected to be downloaded"))
            return

        settings = QSettings()
        path = settings.value("mainwindow/workingDirectory", "")
        zipDestDir = QFileDialog.getExistingDirectory(
            self, _("Select the directory where to save the subtitle(s)"), path)
        if not zipDestDir:
            return
        if zipDestDir:
            settings.setValue("mainwindow/workingDirectory", zipDestDir)

        callback = ProgressCallbackWidget(self)

        callback.set_title_text(_('Downloading'))
        callback.set_label_text(_("Downloading files..."))
        callback.set_updated_text(_("Downloading {0} to {1}"))
        callback.set_block(True)

        callback.set_range(0, len(subs))

        callback.show()

        # Download and unzip files automatically. We might want to move this to an
        # external module, perhaps?
        unzippedOK = 0
        dlOK = 0

        for i, sub in enumerate(subs):
            # Skip rest of loop if Abort was pushed in progress bar
            if callback.canceled():
                break

            try:
                url = sub.getExtraInfo("downloadLink")
                log.debug("sub.getExtraInfo downloadLink  %s " % (url))
            except KeyError:
                url = Link().OneLink(0)
                log.debug("Link().OneLink downloadLink  %s " % (url))
                #                webbrowser.open( url, new=2, autoraise=1)
            zipFileID = re.search("(\/.*\/)(.*)\Z", url).group(2)
            zipFileName = "sub-" + zipFileID + ".srt"

            try:
                zipDestFile = os.path.join(zipDestDir, zipFileName).decode(
                    sys.getfilesystemencoding())
            except AttributeError:
                zipDestFile = (zipDestDir + '/' + zipFileName)
            log.debug("About to download %s %s to %s" % (i, sub.__repr__, zipDestFile))
            log.debug("IdFileOnline: %s" % (sub.getIdFileOnline()))
            callback.update(i, sub.getIdFileOnline(), zipDestDir)

            # Download the file from opensubtitles.org
            # Note that we take for granted it will be in .zip format! Might not be so for other sites
            # This should be tested for when more sites are added or find
            # true filename like browser does FIXME
            try:
                if self.get_state().download_subtitles({sub.getIdFileOnline(): zipDestFile}):
                    dlOK += 1
                    unzippedOK += 1
                else:
                    QMessageBox.about(self, _("Error"), _(
                        "Unable to download subtitle %s") % sub.get_filepath())
            except Exception as e:
                log.debug(e)
                QMessageBox.about(self, _("Error"),
                    _("Unable to download subtitle %s") % sub.get_filepath())
                QMessageBox.critical(self, _("Error"),
                    _("An error occurred downloading \"{url}\":\nError:{error_str}").format(url=url, error_str=e),
                    QMessageBox.Abort)
            QCoreApplication.processEvents()
        callback.finish()
        if dlOK:
            QMessageBox.about(
                self,
                _("{} subtitles downloaded successfully").format(unzippedOK),
                _("The downloaded subtitle(s) may not be in sync with your video file(s), please check this manually.\n"
                  "\nIf there is no sync problem, please consider re-uploading using subdownloader. "
                  "This will automate the search for other users!"))

    @pyqtSlot(QModelIndex)
    def onExpandMovie(self, index):
        if index.internalPointer() is None:
            return
        movie = index.internalPointer().data
        if type(movie) == Movie and not movie.subtitles and movie.totalSubs:

            callback = ProgressCallbackWidget(self)
            callback.set_title_text(_('Search'))
            callback.set_label_text(_("Searching..."))
            callback.set_cancellable(False)
            callback.set_block(True)

            callback.show()

            s = SearchByName()
            selected_language = self.ui.filterLanguage.get_selected_language()
            selected_language_xxx = None if selected_language.is_generic() else selected_language.xxx()
            callback.update(0)
            temp_movie = s.search_movie(languages=[UnknownLanguage.create_generic()], MovieID_link=movie.MovieSiteLink)
            # The internal results are not filtered by language, so in case we change the filter, we don't need to request again.
            # print temp_movie
            try:
                movie.subtitles = temp_movie[0].subtitles
            except IndexError:
                QMessageBox.about(
                    self, _("Info"), _("This is a TV series and it cannot be handled."))
                callback.finish()
                return
            except AttributeError:
                # this means only one subtitle was returned
                movie.subtitles = [temp_movie[1]]
            # The treeview is filtered by language
            self.moviesModel.updateMovie(index, selected_language_xxx)
            self.ui.moviesView.collapse(index)
            self.ui.moviesView.expand(index)
            callback.finish()

    @pyqtSlot(QPoint)
    def onContext(self, point):  # Create a menu
        # FIXME: code duplication with Main.onContext and/or SearchNameWidget and/or SearchFileWidget
        menu = QMenu("Menu", self)
        listview = self.ui.moviesView
        index = listview.currentIndex()
        treeItem = listview.model().getSelectedItem(index)
        if treeItem != None:
            if type(treeItem.data) == VideoFile:
                video = treeItem.data
                movie_info = video.getMovieInfo()
                if movie_info:
                    subWebsiteAction = QAction(
                        QIcon(":/images/info.png"), _("View IMDB info"), self)
                    subWebsiteAction.triggered.connect(self.onViewOnlineInfo)
                else:
                    subWebsiteAction = QAction(
                        QIcon(":/images/info.png"), _("Set IMDB info..."), self)
                    subWebsiteAction.triggered.connect(self.onSetIMDBInfo)
                menu.addAction(subWebsiteAction)
            elif type(treeItem.data) == SubtitleFile:  # Subtitle
                treeItem.checked = True
                self.moviesModel.dataChanged.emit(index, index)
                downloadAction = QAction(
                    QIcon(":/images/download.png"), _("Download"), self)
                # Video tab, TODO:Replace me with a enum
                downloadAction.triggered.connect(self.onButtonDownloadByTitle)
                subWebsiteAction = QAction(
                    QIcon(":/images/sites/opensubtitles.png"), _("View online info"), self)

                menu.addAction(downloadAction)
                subWebsiteAction.triggered.connect(self.onViewOnlineInfo)
                menu.addAction(subWebsiteAction)
            elif type(treeItem.data) == Movie:
                movie = treeItem.data
                subWebsiteAction = QAction(
                    QIcon(":/images/info.png"), _("View IMDB info"), self)
                subWebsiteAction.triggered.connect(self.onViewOnlineInfo)
                menu.addAction(subWebsiteAction)

        # Show the context menu.
        menu.exec_(listview.mapToGlobal(point))

    @pyqtSlot()
    def onViewOnlineInfo(self):
        # FIXME: code duplication with Main.onContext and/or SearchNameWidget and/or SearchFileWidget
        # Tab for SearchByHash TODO:replace this 0 by an ENUM value
        listview = self.ui.moviesView
        index = listview.currentIndex()
        treeItem = listview.model().getSelectedItem(index)

        if type(treeItem.data) == VideoFile:
            video = self.videoModel.getSelectedItem().data
            movie_info = video.getMovieInfo()
            if movie_info:
                imdb = movie_info["IDMovieImdb"]
                if imdb:
                    webbrowser.open(
                        "http://www.imdb.com/title/tt%s" % imdb, new=2, autoraise=1)
        elif type(treeItem.data) == SubtitleFile:  # Subtitle
            sub = treeItem.data
            if sub.isOnline():
                webbrowser.open(
                    "http://www.opensubtitles.org/en/subtitles/%s/" % sub.getIdOnline(), new=2, autoraise=1)

        elif type(treeItem.data) == Movie:
            movie = self.moviesModel.getSelectedItem().data
            imdb = movie.IMDBId
            if imdb:
                webbrowser.open(
                    "http://www.imdb.com/title/tt%s" % imdb, new=2, autoraise=1)

    @pyqtSlot()
    def onSetIMDBInfo(self):
        #FIXME: DUPLICATED WITH SEARCHFILEWIDGET
        QMessageBox.about(
            self, _("Info"), "Not implemented yet. Sorry...")

    @pyqtSlot(QModelIndex)
    def onClickMovieTreeView(self, index):
        treeItem = self.moviesModel.getSelectedItem(index)
        if type(treeItem.data) == Movie:
            movie = treeItem.data
            if movie.IMDBId:
                self.ui.buttonIMDBByTitle.setEnabled(True)
                self.ui.buttonIMDBByTitle.setIcon(QIcon(":/images/info.png"))
                self.ui.buttonIMDBByTitle.setText(_("Movie Info"))
        else:
            treeItem.checked = not (treeItem.checked)
            self.moviesModel.dataChanged.emit(
                index, index)
            self.ui.buttonIMDBByTitle.setEnabled(True)
            self.ui.buttonIMDBByTitle.setIcon(
                QIcon(":/images/sites/opensubtitles.png"))
            self.ui.buttonIMDBByTitle.setText(_("Sub Info"))
