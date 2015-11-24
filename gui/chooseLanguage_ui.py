# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chooseLanguage.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ChooseLanguageDialog(object):
    def setupUi(self, ChooseLanguageDialog):
        ChooseLanguageDialog.setObjectName("ChooseLanguageDialog")
        ChooseLanguageDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ChooseLanguageDialog.resize(282, 337)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ChooseLanguageDialog.sizePolicy().hasHeightForWidth())
        ChooseLanguageDialog.setSizePolicy(sizePolicy)
        ChooseLanguageDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(ChooseLanguageDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(ChooseLanguageDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.languagesList = QtWidgets.QListWidget(ChooseLanguageDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.languagesList.sizePolicy().hasHeightForWidth())
        self.languagesList.setSizePolicy(sizePolicy)
        self.languagesList.setObjectName("languagesList")
        self.verticalLayout.addWidget(self.languagesList)
        self.line = QtWidgets.QFrame(ChooseLanguageDialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.label_2 = QtWidgets.QLabel(ChooseLanguageDialog)
        self.label_2.setTextFormat(QtCore.Qt.RichText)
        self.label_2.setOpenExternalLinks(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.line_2 = QtWidgets.QFrame(ChooseLanguageDialog)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(158, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.OKButton = QtWidgets.QPushButton(ChooseLanguageDialog)
        self.OKButton.setObjectName("OKButton")
        self.horizontalLayout.addWidget(self.OKButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ChooseLanguageDialog)
        QtCore.QMetaObject.connectSlotsByName(ChooseLanguageDialog)

    def retranslateUi(self, ChooseLanguageDialog):
        _translate = QtCore.QCoreApplication.translate
        ChooseLanguageDialog.setWindowTitle(_translate("ChooseLanguageDialog", "Choose language:"))
        self.label.setText(_translate("ChooseLanguageDialog", "Available languages:"))
        self.label_2.setText(_translate("ChooseLanguageDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Click <a href=\"http://www.subdownloader.net/translate.html\"><span style=\" text-decoration: underline; color:#0057ae;\">here</span></a> to help us to translate </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">SubDownloader into  your language.</p></body></html>"))
        self.OKButton.setText(_translate("ChooseLanguageDialog", "OK"))

