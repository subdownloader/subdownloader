# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging
from pathlib import Path
import webbrowser

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget

from subdownloader.movie import RemoteMovieNetwork
from subdownloader.subtitle2 import RemoteSubtitleFile

from subdownloader.client.gui.callback import ProgressCallbackWidget
from subdownloader.client.gui.generated.searchNameWidget_ui import Ui_SearchNameWidget
from subdownloader.client.gui.models.searchNameModel import VideoTreeModel
from subdownloader.client.gui.util import SubtitleDownloadProcess
from subdownloader.languages.language import Language
from subdownloader.provider.SDService import ProviderConnectionError  # FIXME: move to provider

log = logging.getLogger('subdownloader.client.gui.widgets.searchNameWidget')


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
        self._state.signals.interface_language_changed.connect(self.on_interface_language_changed)
        self._state.signals.login_status_changed.connect(self.on_login_state_changed)

        self._state.signals.interface_language_changed.connect(self.on_interface_language_changed)

        self.ui.searchProvidersCombo.set_state(self._state)

    def get_state(self):
        return self._state

    def setup_ui(self):
        self.ui.setupUi(self)

        self.ui.buttonSearchByName.clicked.connect(self.onButtonSearchByTitle)

        self.ui.movieNameText.returnPressed.connect(self.onButtonSearchByTitle)

        self.ui.buttonDownloadByTitle.clicked.connect(self.onButtonDownloadByTitle)
        self.ui.buttonDownloadByTitle.setEnabled(False)

        self.ui.buttonIMDBByTitle.clicked.connect(self.onViewOnlineInfo)
        self.ui.buttonIMDBByTitle.setEnabled(False)

        self.moviesModel = VideoTreeModel(self)
        self.ui.moviesView.setModel(self.moviesModel)
        self.ui.moviesView.view_imdb_online.connect(self.onViewImdbOnline)
        self.ui.moviesView.view_subtitle_online.connect(self.onViewSubtitleOnline)
        self.ui.moviesView.download_subtitle.connect(self.onDownloadSelectedSub)
        self.moviesModel.node_clicked.connect(self.on_item_clicked)
        self.moviesModel.checkStateChanged.connect(self.subtitlesMovieCheckedChanged)

        # Set unknown text here instead of `retranslate()` because widget translates itself
        self.ui.filterLanguage.set_unknown_text(_('All languages'))
        self.ui.filterLanguage.selected_language_changed.connect(self.on_language_combobox_filter_change)

        self.ui.searchProvidersCombo.set_general_visible(True)
        self.ui.searchProvidersCombo.selected_provider_state_changed.connect(self.moviesModel.on_selected_provider_state_changed)

        self.language_filter_change.connect(self.moviesModel.on_filter_languages_change)

        self.retranslate()

    def retranslate(self):
        self.ui.searchProvidersCombo.set_general_text(_('All providers'))

    @pyqtSlot(Language)
    def on_interface_language_changed(self, language):
        self.ui.retranslateUi(self)
        self.retranslate()

    @pyqtSlot()
    def on_login_state_changed(self):
        log.debug('on_login_state_changed()')
        nb_connected = self._state.providers.get_number_connected_providers()
        if nb_connected:
            self.ui.buttonSearchByName.setEnabled(True)
            # self.ui.buttonDownloadByTitle.setEnabled(True)
        else:
            self.ui.buttonSearchByName.setEnabled(False)
            # self.ui.buttonDownloadByTitle.setEnabled(False)

    @pyqtSlot(Language)
    def on_language_combobox_filter_change(self, language):
        if language.is_generic():
            self.language_filter_change.emit(self._state.get_download_languages())
        else:
            self.language_filter_change.emit([language])

    @pyqtSlot(list)
    def on_permanent_language_filter_change(self, languages):
        selected_language = self.ui.filterLanguage.get_selected_language()
        if selected_language.is_generic():
            self.language_filter_change.emit(languages)

    @pyqtSlot()
    def onButtonSearchByTitle(self):
        nb_connected = self._state.providers.get_number_connected_providers()
        if not nb_connected:
            return

        search_text = self.ui.movieNameText.text().strip()
        if not search_text:
            QMessageBox.about(self, _('Info'), _('You must enter at least one character'))
            return

        self.ui.buttonSearchByName.setEnabled(False)

        callback = ProgressCallbackWidget(self)

        callback.set_title_text(_('Search'))
        callback.set_label_text(_('Searching...'))
        callback.set_block(True)
        callback.show()
        callback.update(0)

        try:
            query = self._state.providers.query_text(search_text)
            query.search_more_movies()
        except ProviderConnectionError:
            QMessageBox.warning(self, _('Error occured'), _('A problem occured. Please try later.'))
            callback.finish()
            self.ui.buttonSearchByName.setEnabled(True)
            return
        callback.finish()

        self.moviesModel.set_query(query)

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

        if not subs:
            QMessageBox.about(
                self, _('Error'), _('No subtitles selected to be downloaded'))
            return

        path = self._state.get_video_path()
        zipDestDir = QFileDialog.getExistingDirectory(
            self, _('Select the directory where to save the subtitle(s)'), str(path))
        if not zipDestDir:
            return
        zipDestDir = Path(zipDestDir)
        self._state.set_default_download_path(zipDestDir)

        downloaded_subs = self.download_subtitles(subs)
        self.moviesModel.uncheck_subtitles(downloaded_subs)

    def download_subtitles(self, rsubs):
        sub_downloader = SubtitleDownloadProcess(parent=self.parent(), rsubtitles=rsubs, state=self._state, parent_add=False)
        sub_downloader.download_all()
        new_subs = sub_downloader.downloaded_subtitles()
        return new_subs

    @pyqtSlot(RemoteMovieNetwork)
    def onViewImdbOnline(self, movie):
        movie_identity = movie.get_identities()
        if movie_identity.imdb_identity:
            webbrowser.open(movie_identity.imdb_identity.get_imdb_url(), new=2, autoraise=1)
            return
        QMessageBox.information(self.parent(), _('IMDb unknown'), _('IMDb is unknown'))

    @pyqtSlot(RemoteSubtitleFile)
    def onViewSubtitleOnline(self, sub):
        webbrowser.open(sub.get_link(), new=2, autoraise=1)

    @pyqtSlot(RemoteSubtitleFile)
    def onDownloadSelectedSub(self, rsub):
        self.download_subtitles([rsub])

    @pyqtSlot()
    def onViewOnlineInfo(self):
        node = self.moviesModel.get_selected_node()
        data = node.get_data()
        if isinstance(data, RemoteMovieNetwork):
            movie_identity = data.get_identities()
            if movie_identity.imdb_identity:
                webbrowser.open(movie_identity.imdb_identity.get_imdb_url(), new=2, autoraise=1)
            else:
                QMessageBox.information(self.parent(), _('imdb unknown'), _('imdb is unknown'))
        elif isinstance(data, RemoteSubtitleFile):
            webbrowser.open(data.get_link(), new=2, autoraise=1)

    @pyqtSlot(object)
    def on_item_clicked(self, item):
        if isinstance(item, RemoteMovieNetwork):
            self.ui.buttonIMDBByTitle.setIcon(QIcon(':/images/info.png'))
            self.ui.buttonIMDBByTitle.setText(_('Movie Info'))
            movie_identity = item.get_identities()
            if movie_identity.imdb_identity:
                self.ui.buttonIMDBByTitle.setEnabled(True)
        elif isinstance(item, RemoteSubtitleFile):
            self.ui.buttonIMDBByTitle.setIcon(QIcon(item.get_provider().get_icon()))
            self.ui.buttonIMDBByTitle.setText(_('Sub Info'))
            self.ui.buttonIMDBByTitle.setEnabled(True)
        else:
            self.ui.buttonIMDBByTitle.setEnabled(False)
