# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'imdb.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_IMDBSearchDialog(object):
    def setupUi(self, IMDBSearchDialog):
        IMDBSearchDialog.setObjectName(_fromUtf8("IMDBSearchDialog"))
        IMDBSearchDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        IMDBSearchDialog.resize(522, 406)
        IMDBSearchDialog.setModal(True)
        self.vboxlayout = QtGui.QVBoxLayout(IMDBSearchDialog)
        self.label = QtGui.QLabel(IMDBSearchDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.vboxlayout.addWidget(self.label)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.movieSearch = QtGui.QLineEdit(IMDBSearchDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.movieSearch.sizePolicy().hasHeightForWidth())
        self.movieSearch.setSizePolicy(sizePolicy)
        self.movieSearch.setText(_fromUtf8(""))
        self.movieSearch.setObjectName(_fromUtf8("movieSearch"))
        self.hboxlayout.addWidget(self.movieSearch)
        self.searchMovieButton = QtGui.QPushButton(IMDBSearchDialog)
        self.searchMovieButton.setObjectName(_fromUtf8("searchMovieButton"))
        self.hboxlayout.addWidget(self.searchMovieButton)
        self.vboxlayout.addLayout(self.hboxlayout)
        self.searchResultsView = ImdbListView(IMDBSearchDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchResultsView.sizePolicy().hasHeightForWidth())
        self.searchResultsView.setSizePolicy(sizePolicy)
        self.searchResultsView.setAcceptDrops(True)
        self.searchResultsView.setDragEnabled(True)
        self.searchResultsView.setDragDropMode(QtGui.QAbstractItemView.DropOnly)
        self.searchResultsView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.searchResultsView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.searchResultsView.setGridStyle(QtCore.Qt.DotLine)
        self.searchResultsView.setObjectName(_fromUtf8("searchResultsView"))
        self.vboxlayout.addWidget(self.searchResultsView)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.movieInfoButton = QtGui.QPushButton(IMDBSearchDialog)
        self.movieInfoButton.setEnabled(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/info.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.movieInfoButton.setIcon(icon)
        self.movieInfoButton.setIconSize(QtCore.QSize(32, 16))
        self.movieInfoButton.setObjectName(_fromUtf8("movieInfoButton"))
        self.hboxlayout1.addWidget(self.movieInfoButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        self.okButton = QtGui.QPushButton(IMDBSearchDialog)
        self.okButton.setEnabled(False)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.hboxlayout1.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton(IMDBSearchDialog)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.hboxlayout1.addWidget(self.cancelButton)
        self.vboxlayout.addLayout(self.hboxlayout1)

        self.retranslateUi(IMDBSearchDialog)
        QtCore.QMetaObject.connectSlotsByName(IMDBSearchDialog)

    def retranslateUi(self, IMDBSearchDialog):
        IMDBSearchDialog.setWindowTitle(_translate("IMDBSearchDialog", "IMDB search dialog:", None))
        self.label.setText(_translate("IMDBSearchDialog", "Enter the Movie Title or IMDB id:", None))
        self.searchMovieButton.setText(_translate("IMDBSearchDialog", "Search Movie", None))
        self.movieInfoButton.setText(_translate("IMDBSearchDialog", "Movie Info", None))
        self.okButton.setText(_translate("IMDBSearchDialog", "OK", None))
        self.cancelButton.setText(_translate("IMDBSearchDialog", "Cancel", None))

from .imdblistview import ImdbListView
from . import images_rc

class IMDBSearchDialog(QtGui.QDialog, Ui_IMDBSearchDialog):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QDialog.__init__(self, parent, f)

        self.setupUi(self)

