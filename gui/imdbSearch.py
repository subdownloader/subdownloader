
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QVariant, QSize, QEventLoop, QString, \
                         QBuffer, QIODevice, QModelIndex,QDir
from PyQt4.QtGui import QPixmap, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel, QItemSelectionModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical

from subdownloader.gui.imdb_ui import Ui_IMDBSearchDialog
from subdownloader.gui.imdblistview import ImdbListModel, ImdbListView
import webbrowser

class imdbSearchDialog(QtGui.QDialog): 
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_IMDBSearchDialog()
        self.ui.setupUi(self)
        self.movieSelected = None
        
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
        
    def onSearchMovieButton(self):
        if not self.ui.movieSearch.text():
            QMessageBox.about(self,"Error","Please fill out the search title")
        else:
            self.imdbModel.emit(SIGNAL("layoutAboutToBeChanged()"))
            self.imdbModel.setImdbResults([{"id":"339999", "title":"dsdada"}, {"id":"999999", "title":"dsadasdas"}])
            QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
            self.imdbModel.emit(SIGNAL("layoutChanged()"))
            self.ui.searchResultsView.resizeRowsToContents()
            
    def updateButtonsIMDB(self):
        self.uploadView.resizeRowsToContents()
        selected = self.uploadSelectionModel.selection()
        if selected.count():
            self.uploadModel.rowSelected = selected.last().bottomRight().row()
            self.buttonUploadMinusRow.setEnabled(True)
            if self.uploadModel.rowSelected != self.uploadModel.getTotalRows() -1:
                self.buttonUploadDownRow.setEnabled(True)
            else:
                self.buttonUploadDownRow.setEnabled(False)
                
            if self.uploadModel.rowSelected != 0:
                self.buttonUploadUpRow.setEnabled(True)
            else:
                self.buttonUploadUpRow.setEnabled(False)
        else:
            self.uploadModel.rowSelected = None
            self.buttonUploadDownRow.setEnabled(False)
            self.buttonUploadUpRow.setEnabled(False)
            self.buttonUploadMinusRow.setEnabled(False)
            
    def onIMDBChangeSelection(self, selected, unselected):
        self.updateButtonsIMDB()
        
    def onMovieInfoButton(self):
        if not self.movieSelected:
            QMessageBox.about(self,"Error","Please search and select a movie from the list")
        else:
            webbrowser.open( "http://www.imdb.com/title/tt%s"% "000000", new=2, autoraise=1)
    def onOkButton(self):
        if not self.movieSelected:
            QMessageBox.about(self,"Error","Please search and select a movie from the list")
        else:
            self.close()
    def onCancelButton(self):
        self.close()

