
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject
from PyQt4.QtGui import QPixmap, QErrorMessage, QLineEdit,  QMessageBox
from subdownloader.gui.imdb_ui import Ui_IMDBSearchDialog
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
        
    def onSearchMovieButton(self):
        if not self.ui.movieSearch.text():
            QMessageBox.about(self,"Error","Please fill out the search title")
        else:
            webbrowser.open( "http://www.imdb.com/title/tt%s"% "000000", new=2, autoraise=1)
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
