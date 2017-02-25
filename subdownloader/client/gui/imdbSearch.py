# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

import logging
import webbrowser

from PyQt5.QtCore import Qt, pyqtSlot, QCoreApplication, \
    QEventLoop, QItemSelection, QItemSelectionModel
from PyQt5.QtWidgets import QDialog, QHeaderView, QMessageBox
from subdownloader.client.gui.imdb_ui import Ui_IMDBSearchDialog

from subdownloader.client.gui.imdblistview import ImdbListModel


class imdbSearchDialog(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.log = logging.getLogger("subdownloader.gui.imdbSearch")
        self.ui = Ui_IMDBSearchDialog()
        self.ui.setupUi(self)

        self.ui.searchMovieButton.clicked.connect(self.onSearchMovieButton)
        self.ui.movieInfoButton.clicked.connect(self.onMovieInfoButton)
        self.ui.okButton.clicked.connect(self.onOkButton)
        self.ui.cancelButton.clicked.connect(self.onCancelButton)

        header = self.ui.searchResultsView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.hide()
        self.ui.searchResultsView.verticalHeader().hide()

        self.imdbModel = ImdbListModel(self)
        self.ui.searchResultsView.setModel(self.imdbModel)
        # FIXME: This connection should be cleaner.
        self.imdbSelectionModel = QItemSelectionModel(self.imdbModel)
        self.ui.searchResultsView.setSelectionModel(self.imdbSelectionModel)
        self.imdbSelectionModel.selectionChanged.connect(
            self.onIMDBChangeSelection)
        self.ui.searchResultsView.activated.connect(self.onOkButton)

    @pyqtSlot()
    def onSearchMovieButton(self):
        if not self.ui.movieSearch.text():
            QMessageBox.about(
                self, _("Error"), _("Please fill out the search title"))
        else:
            self.setCursor(Qt.WaitCursor)
            try:
                results = self.parent().get_state().get_OSDBServer().SearchMoviesOnIMDB(
                    self.ui.movieSearch.text())
                # In case of empty results
                if not results or not len(results) or "id" not in results[0]:
                    results = []
            except Exception as e:
                self.log.exception('Error contacting OSDBServer.SearchMoviesOnIMDB')
                QMessageBox.about(
                    self, _("Error"), _("Error contacting the server. Please try again later"))
                results = []

            self.imdbModel.layoutAboutToBeChanged.emit()
            self.imdbModel.setImdbResults(results)
            QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
            self.imdbModel.layoutChanged.emit()
            self.ui.searchResultsView.resizeRowsToContents()
            self.setCursor(Qt.ArrowCursor)

    def updateButtonsIMDB(self):
        self.ui.searchResultsView.resizeRowsToContents()
        selected = self.imdbSelectionModel.selection()
        if selected.count():
            self.imdbModel.rowSelected = selected.last().bottomRight().row()
            self.ui.movieInfoButton.setEnabled(True)
            self.ui.okButton.setEnabled(True)
        else:
            self.imdbModel.rowSelected = None
            self.ui.movieInfoButton.setEnabled(False)
            self.ui.okButton.setEnabled(False)

    @pyqtSlot(QItemSelection, QItemSelection)
    def onIMDBChangeSelection(self, selected, unselected):
        self.updateButtonsIMDB()

    @pyqtSlot()
    def onMovieInfoButton(self):
        if self.imdbModel.rowSelected == None:
            QMessageBox.about(
                self, _("Error"), _("Please search and select a movie from the list"))
        else:
            imdbID = self.imdbModel.getSelectedImdb()["id"]
            webbrowser.open("http://www.imdb.com/title/tt%s" %
                            imdbID, new=2, autoraise=1)

    @pyqtSlot()
    def onOkButton(self):
        if self.imdbModel.rowSelected == None:
            QMessageBox.about(
                self, _("Error"), _("Please search and select a movie from the list"))
        else:
            selection = self.imdbModel.getSelectedImdb()
            self.parent().imdbDetected.emit(
                selection["id"], selection["title"], "search")
            self.accept()

    @pyqtSlot()
    def onCancelButton(self):
        self.reject()
