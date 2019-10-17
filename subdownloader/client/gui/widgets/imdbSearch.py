# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging
import webbrowser

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QDialog, QMessageBox

from subdownloader.client.gui.generated.imdbSearch_ui import Ui_IMDBSearchDialog
from subdownloader.provider.imdb import ImdbMovieMatch
from subdownloader.provider.provider import ProviderConnectionError

log = logging.getLogger('subdownloader.client.gui.imdbSearch')


class ImdbSearchDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.ui = Ui_IMDBSearchDialog()
        self.setup_ui()

        self._state = None

    def setup_ui(self) -> None:
        self.ui.setupUi(self)

        self.ui.searchMovieButton.clicked.connect(self.on_search)
        self.ui.movieInfoButton.clicked.connect(self.on_button_movie_info)

        self.ui.okButton.setEnabled(False)
        self.ui.okButton.clicked.connect(self.on_button_ok)

        self.ui.cancelButton.clicked.connect(self.on_button_cancel)

        self.ui.searchResultsView.imdb_selection_changed.connect(self.on_imdb_selection_change)
        self.ui.providerSearch.set_general_visible(False)

        self.retranslate()

    def retranslate(self) -> None:
        pass

    def set_state(self, state) -> None:
        self._state = state

        self.ui.providerSearch.set_state(self._state)
        self.ui.providerSearch.setCurrentIndex(0)

    @pyqtSlot()
    def on_search(self) -> None:
        query = self.ui.movieSearch.text().strip()
        if not query:
            QMessageBox.about(self, _('Error'), _('Please fill out the search title'))
            return

        self.setCursor(Qt.WaitCursor)
        providerState = self.ui.providerSearch.get_selected_provider_state()
        provider = providerState.provider
        try:
            imdb_data = provider.imdb_search_title(title=query)
            if imdb_data is None:
                log.error('Error contacting OSDBServer.SearchMoviesOnIMDB')
            else:
                self.ui.searchResultsView.set_imdb_data(imdb_data)
        except ProviderConnectionError:
            QMessageBox.about(
                self, _("Error"), _('Error contacting the server. Please try again later'))
        self.setCursor(Qt.ArrowCursor)

    def update_buttons(self) -> None:
        identity = self.ui.searchResultsView.get_selected_imdb()
        if identity is None:
            self.ui.movieInfoButton.setEnabled(False)
            self.ui.okButton.setEnabled(False)
        else:
            self.ui.movieInfoButton.setEnabled(True)
            self.ui.okButton.setEnabled(True)

    @pyqtSlot()
    def on_imdb_selection_change(self) -> None:
        self.update_buttons()

    @pyqtSlot()
    def on_button_movie_info(self) -> None:
        imdb = self.ui.searchResultsView.get_selected_imdb()
        if imdb is None:
            QMessageBox.about(
                self, _('Error'), _('Please search and select a movie from the list'))
        else:
            webbrowser.open(imdb.url, new=2, autoraise=1)

    identity_selected = pyqtSignal(ImdbMovieMatch)

    @pyqtSlot()
    def on_button_ok(self) -> None:
        imdb = self.ui.searchResultsView.get_selected_imdb()
        if imdb is None:
            QMessageBox.about(
                self, _('Error'), _('Please search and select a movie from the list'))
        else:
            self.identity_selected.emit(imdb)
            self.accept()

    @pyqtSlot()
    def on_button_cancel(self) -> None:
        self.reject()
