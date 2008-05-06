from subdownloader.gui.imdb_ui import Ui_IMDBSearchDialog
from PyQt4 import QtCore, QtGui

class imdbSearchDialog(QtGui.QDialog): 
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_IMDBSearchDialog()
        self.ui.setupUi(self)
    def something_else(self):
        pass
