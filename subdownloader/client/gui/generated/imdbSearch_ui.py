# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/maarten/programming/subdownloader_old/scripts/gui/ui/imdbSearch.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_IMDBSearchDialog(object):
    def setupUi(self, IMDBSearchDialog):
        IMDBSearchDialog.setObjectName("IMDBSearchDialog")
        IMDBSearchDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        IMDBSearchDialog.setModal(True)
        self._2 = QtWidgets.QVBoxLayout(IMDBSearchDialog)
        self._2.setObjectName("_2")
        self.label = QtWidgets.QLabel(IMDBSearchDialog)
        self.label.setObjectName("label")
        self._2.addWidget(self.label)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.movieSearch = QtWidgets.QLineEdit(IMDBSearchDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.movieSearch.sizePolicy().hasHeightForWidth())
        self.movieSearch.setSizePolicy(sizePolicy)
        self.movieSearch.setText("")
        self.movieSearch.setObjectName("movieSearch")
        self.horizontalLayout_2.addWidget(self.movieSearch)
        self.providerSearch = ProviderComboBox(IMDBSearchDialog)
        self.providerSearch.setObjectName("providerSearch")
        self.horizontalLayout_2.addWidget(self.providerSearch)
        self.searchMovieButton = QtWidgets.QPushButton(IMDBSearchDialog)
        self.searchMovieButton.setObjectName("searchMovieButton")
        self.horizontalLayout_2.addWidget(self.searchMovieButton)
        self._2.addLayout(self.horizontalLayout_2)
        self.searchResultsView = ImdbListView(IMDBSearchDialog)
        self.searchResultsView.setObjectName("searchResultsView")
        self._2.addWidget(self.searchResultsView)
        self.hboxlayout = QtWidgets.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")
        self.movieInfoButton = QtWidgets.QPushButton(IMDBSearchDialog)
        self.movieInfoButton.setEnabled(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/info.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.movieInfoButton.setIcon(icon)
        self.movieInfoButton.setObjectName("movieInfoButton")
        self.hboxlayout.addWidget(self.movieInfoButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.okButton = QtWidgets.QPushButton(IMDBSearchDialog)
        self.okButton.setObjectName("okButton")
        self.hboxlayout.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(IMDBSearchDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.hboxlayout.addWidget(self.cancelButton)
        self._2.addLayout(self.hboxlayout)

        self.retranslateUi(IMDBSearchDialog)
        QtCore.QMetaObject.connectSlotsByName(IMDBSearchDialog)

    def retranslateUi(self, IMDBSearchDialog):
        _translate = QtCore.QCoreApplication.translate
        IMDBSearchDialog.setWindowTitle(_("IMDb search"))
        self.label.setText(_("Enter the Movie Title or IMDb id:"))
        self.searchMovieButton.setText(_("Search"))
        self.movieInfoButton.setText(_("Movie Info"))
        self.okButton.setText(_("OK"))
        self.cancelButton.setText(_("Cancel"))
from subdownloader.client.gui.views.imdb import ImdbListView
from subdownloader.client.gui.views.provider import ProviderComboBox
