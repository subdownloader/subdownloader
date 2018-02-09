# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
import webbrowser

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QPoint, QSettings, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog, QMenu, QMessageBox, QWidget

from subdownloader.languages.language import UnknownLanguage
from subdownloader.provider.SDService import OpenSubtitles_SubtitleFile
from subdownloader.movie import RemoteMovie

from subdownloader.client.gui.callback import ProgressCallbackWidget
from subdownloader.client.gui.generated.searchNameWidget_ui import Ui_SearchNameWidget
from subdownloader.client.gui.state import State
from subdownloader.client.gui.searchNameModel import VideoTreeModel
from subdownloader.languages.language import Language
from subdownloader.util import write_stream

log = logging.getLogger('subdownloader.client.gui.searchNameWidget')


class SearchNameWidget(QWidget):

    language_filter_change = pyqtSignal(list)

    def __init__(self):
        QWidget.__init__(self)

        self._state = None
        self.moviesModel = None

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

        self.ui.buttonSearchByName.clicked.connect(self.onButtonSearchByTitle)
        self.ui.movieNameText.returnPressed.connect(self.onButtonSearchByTitle)
        self.ui.buttonDownloadByTitle.clicked.connect(self.onButtonDownloadByTitle)

        self.ui.buttonIMDBByTitle.clicked.connect(self.onViewOnlineInfo)
        self.ui.buttonIMDBByTitle.setEnabled(False)

        self.moviesModel = VideoTreeModel(self)
        self.moviesModel.connect_treeview(self.ui.moviesView)
        self.moviesModel.node_clicked.connect(self.on_item_clicked)
        self.moviesModel.dataChanged.connect(self.subtitlesMovieCheckedChanged)

        # FIXME: load settings from general place
        upload_language = Language.from_xxx(
            QSettings().value('options/uploadLanguage', UnknownLanguage.create_generic()))
        self.ui.filterLanguage.selected_language_changed.connect(self.on_language_combobox_filter_change)

        self.language_filter_change.connect(self.moviesModel.on_filter_languages_change)

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
        elif state == State.LOGIN_STATUS_LOGGED_IN:
            self.ui.buttonDownloadByTitle.setEnabled(True)
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

    @pyqtSlot()
    def onButtonSearchByTitle(self):
        search_text = self.ui.movieNameText.text().strip()
        if not search_text:
            QMessageBox.about(self, _("Info"), _("You must enter at least one character in movie name"))
            return

        self.ui.buttonSearchByName.setEnabled(False)

        callback = ProgressCallbackWidget(self)

        callback.set_title_text(_('Search'))
        callback.set_label_text(_("Searching..."))
        callback.set_block(True)

        callback.show()
        callback.update(0)

        result = self.moviesModel.search_movies(query=search_text)

        if not result:
            QMessageBox.about(self, _("Info"), _("The server is momentarily unavailable. Please try later."))

        callback.finish()
        self.ui.buttonSearchByName.setEnabled(True)

    @pyqtSlot()
    def subtitlesMovieCheckedChanged(self):
        subs = self.moviesModel.get_checked_subtitles()
        if subs:
            self.ui.buttonDownloadByTitle.setEnabled(True)
        else:
            self.ui.buttonDownloadByTitle.setEnabled(False)

    @pyqtSlot()
    def onButtonDownloadByTitle(self):
        subs = self.moviesModel.get_checked_subtitles()
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

        dlOK = 0
        writtenOK = 0

        for i, sub in enumerate(subs):
            # Skip rest of loop if Abort was pushed in progress bar
            if callback.canceled():
                break

            srt_filename = "sub-" + sub.get_id_online() + ".srt"
            srt_path = os.path.join(zipDestDir, srt_filename)

            log.debug("About to download %s %s to %s" % (i, sub.__repr__, srt_path))
            log.debug("IdFileOnline: %s" % (sub.get_id_online()))
            callback.update(i, sub.get_id_online(), zipDestDir)

            try:
                data_stream = sub.download(provider_instance=self.get_state().get_OSDBServer(), callback=callback)
                dlOK += 1
            except Exception:
                log.warning('Unable to download subtitle with id={subtitle_id}'.format(subtitle_id=sub.get_id_online()),
                          exc_info=True)
                QMessageBox.about(self, _('Error'), _('Unable to download subtitle with id={subtitle_id}').format(
                    subtitle_id=sub.get_id_online()))
                continue
            try:
                write_stream(data_stream, srt_path)
                writtenOK += 1
            except Exception:
                log.warning('Unable to write subtitle to disk. path={path}'.format(path=zipDestFile), exc_info=True)
            QCoreApplication.processEvents()
        callback.finish()
        if dlOK:
            QMessageBox.about(
                self,
                _("{} subtitles downloaded successfully").format(writtenOK),
                _("{} subtitles downloaded successfully").format(writtenOK))

    @pyqtSlot(QPoint)
    def onContext(self, point):  # Create a menu
        # FIXME: code duplication with Main.onContext and/or SearchNameWidget and/or SearchFileWidget
        node = self.moviesModel.get_selected_node()
        if node is None:
            return

        menu = QMenu("Menu", self)
        data = node.get_data()
        if isinstance(data, RemoteMovie):
            online_action = QAction(QIcon(":/images/info.png"), _("View IMDb info"), self)
            online_action.triggered.connect(self.onViewOnlineInfo)
            menu.addAction(online_action)
        elif isinstance(data, OpenSubtitles_SubtitleFile):
            download_action = QAction(QIcon(":/images/download.png"), _("Download"), self)
            download_action.triggered.connect(self.onButtonDownloadByTitle)
            menu.addAction(download_action)

            online_action = QAction(QIcon(":/images/sites/opensubtitles.png"), _("View online info"), self)
            online_action.triggered.connect(self.onViewOnlineInfo)
            menu.addAction(online_action)

        menu.exec_(self.ui.moviesView.mapToGlobal(point))

    @pyqtSlot()
    def onViewOnlineInfo(self):
        node = self.moviesModel.get_selected_node()
        data = node.get_data()
        if isinstance(data, RemoteMovie):
            movie_identity = data.get_identities()
            if movie_identity.imdb_identity:
                webbrowser.open(movie_identity.imdb_identity.get_imdb_url(), new=2, autoraise=1)
        elif isinstance(data, OpenSubtitles_SubtitleFile):
            sub = data
            webbrowser.open(
                'http://www.opensubtitles.org/en/subtitles/{id_online}'.format(id_online=sub.get_id_online()),
                new=2, autoraise=1)

    @pyqtSlot(object)
    def on_item_clicked(self, item):
        if isinstance(item, RemoteMovie):
            self.ui.buttonIMDBByTitle.setEnabled(True)
            movie_identity = item.get_identities()
            if movie_identity.imdb_identity:
                self.ui.buttonIMDBByTitle.setEnabled(True)
                self.ui.buttonIMDBByTitle.setIcon(QIcon(":/images/info.png"))
                self.ui.buttonIMDBByTitle.setText(_("Movie Info"))
        elif isinstance(item, OpenSubtitles_SubtitleFile):
            self.ui.buttonIMDBByTitle.setEnabled(True)
            self.ui.buttonIMDBByTitle.setEnabled(True)
            self.ui.buttonIMDBByTitle.setIcon(
                QIcon(":/images/sites/opensubtitles.png"))
            self.ui.buttonIMDBByTitle.setText(_("Sub Info"))
        else:
            self.ui.buttonIMDBByTitle.setEnabled(False)
