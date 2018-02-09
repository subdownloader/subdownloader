# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging
import webbrowser

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QDialog, QMessageBox

from subdownloader.client.gui.generated.imdbSearch_ui import Ui_IMDBSearchDialog
from subdownloader.identification import Identities

log = logging.getLogger('subdownloader.client.gui.imdbSearch')


class ImdbSearchDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.ui = Ui_IMDBSearchDialog()

        self.setup_ui()

    def setup_ui(self):
        self.ui.setupUi(self)

        self.ui.searchMovieButton.clicked.connect(self.on_search)
        self.ui.movieInfoButton.clicked.connect(self.on_button_movie_info)

        self.ui.okButton.setEnabled(False)
        self.ui.okButton.clicked.connect(self.on_button_ok)

        self.ui.cancelButton.clicked.connect(self.on_button_cancel)

        self.ui.searchResultsView.imdb_selection_changed.connect(self.on_imdb_selection_change)

        self.retranslate()

    def retranslate(self):
        pass

    @pyqtSlot()
    def on_search(self):
        query = self.ui.movieSearch.text().strip()
        if not query:
            QMessageBox.about(
                self, _('Error'), _('Please fill out the search title'))
        else:
            self.setCursor(Qt.WaitCursor)

            imdb_data = self.parent().get_state().get_OSDBServer().imdb_query(query=query)
            if imdb_data is None:
                log.exception('Error contacting OSDBServer.SearchMoviesOnIMDB')
                QMessageBox.about(
                    self, _("Error"), _('Error contacting the server. Please try again later'))
            else:
                self.ui.searchResultsView.set_imdb_data(imdb_data)

            self.setCursor(Qt.ArrowCursor)

    def update_buttons(self):
        identity = self.ui.searchResultsView.get_selected_identity()
        if identity is None:
            self.ui.movieInfoButton.setEnabled(False)
            self.ui.okButton.setEnabled(False)
        else:
            self.ui.movieInfoButton.setEnabled(True)
            self.ui.okButton.setEnabled(True)

    @pyqtSlot()
    def on_imdb_selection_change(self):
        self.update_buttons()

    @pyqtSlot()
    def on_button_movie_info(self):
        identity = self.ui.searchResultsView.get_selected_identity()
        if identity is None:
            QMessageBox.about(
                self, _('Error'), _('Please search and select a movie from the list'))
        else:
            imdb_identity = identity.imdb_identity
            webbrowser.open(imdb_identity.get_imdb_url(), new=2, autoraise=1)

    identity_selected = pyqtSignal(Identities)

    @pyqtSlot()
    def on_button_ok(self):
        identity = self.ui.searchResultsView.get_selected_identity()
        if identity is None:
            QMessageBox.about(
                self, _('Error'), _('Please search and select a movie from the list'))
        else:
            self.identity_selected.emit(identity)
            self.accept()

    @pyqtSlot()
    def on_button_cancel(self):
        self.reject()
