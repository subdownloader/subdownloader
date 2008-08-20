
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QVariant, QSize, QEventLoop, QString, \
                         QBuffer, QIODevice, QModelIndex,QDir
from PyQt4.QtGui import QPixmap, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel, QItemSelectionModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical

from gui.imdb_ui import Ui_IMDBSearchDialog
from gui.imdblistview import ImdbListModel, ImdbListView
import webbrowser

class imdbSearchDialog(QtGui.QDialog): 
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_IMDBSearchDialog()
        self.ui.setupUi(self)
        self._main  = parent
        
        QObject.connect(self.ui.searchMovieButton, SIGNAL("clicked(bool)"), self.onSearchMovieButton)
        QObject.connect(self.ui.movieInfoButton, SIGNAL("clicked(bool)"), self.onMovieInfoButton)
        QObject.connect(self.ui.okButton, SIGNAL("clicked(bool)"), self.onOkButton)
        QObject.connect(self.ui.cancelButton, SIGNAL("clicked(bool)"), self.onCancelButton)
        
        header = self.ui.searchResultsView.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.Stretch)
        header.hide()
        self.ui.searchResultsView.verticalHeader().hide()
        
        self.imdbModel = ImdbListModel(self)
        self.ui.searchResultsView.setModel(self.imdbModel)
        self.imdbModel._main = self #FIXME: This connection should be cleaner.
        self.imdbSelectionModel = QItemSelectionModel(self.imdbModel)
        self.ui.searchResultsView.setSelectionModel(self.imdbSelectionModel)
        QObject.connect(self.imdbSelectionModel, SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self.onIMDBChangeSelection)
        QObject.connect(self.ui.searchResultsView, SIGNAL("activated(QModelIndex)"), self.onOkButton)

    def onSearchMovieButton(self):
        if not self.ui.movieSearch.text():
            QMessageBox.about(self,"Error","Please fill out the search title")
        else:
            self.setCursor(Qt.WaitCursor)
            text = self.ui.movieSearch.text()
            try:
                results = self._main.OSDBServer.SearchMoviesOnIMDB(str(text.toUtf8()))
                if not results or not len(results) or not results[0].has_key("id"): #In case of empty results 
                    results = []
            except:
                QMessageBox.about(self,"Error","Error contacting the server.\nPlease restart or try later.")
                results = []
            
            self.imdbModel.emit(SIGNAL("layoutAboutToBeChanged()"))
            self.imdbModel.setImdbResults(results)
            QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
            self.imdbModel.emit(SIGNAL("layoutChanged()"))
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
            
    def onIMDBChangeSelection(self, selected, unselected):
        self.updateButtonsIMDB()
        
    def onMovieInfoButton(self):
        if self.imdbModel.rowSelected == None:
            QMessageBox.about(self,"Error","Please search and select a movie from the list")
        else: 
            imdbID = self.imdbModel.getSelectedImdb()["id"]
            webbrowser.open( "http://www.imdb.com/title/tt%s"% imdbID, new=2, autoraise=1)
    def onOkButton(self):
        if self.imdbModel.rowSelected == None:
            QMessageBox.about(self,"Error","Please search and select a movie from the list")
        else:
            selection = self.imdbModel.getSelectedImdb()
            self._main.emit(SIGNAL('imdbDetected(QString,QString,QString)'),selection["id"], selection["title"], "search")
            self.accept()
    def onCancelButton(self):
        self.reject()

