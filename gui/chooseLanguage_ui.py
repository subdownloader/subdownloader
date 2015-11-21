# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chooseLanguage.ui'
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

class Ui_ChooseLanguageDialog(object):
    def setupUi(self, ChooseLanguageDialog):
        ChooseLanguageDialog.setObjectName(_fromUtf8("ChooseLanguageDialog"))
        ChooseLanguageDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ChooseLanguageDialog.resize(282, 337)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ChooseLanguageDialog.sizePolicy().hasHeightForWidth())
        ChooseLanguageDialog.setSizePolicy(sizePolicy)
        ChooseLanguageDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(ChooseLanguageDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(ChooseLanguageDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.languagesList = QtGui.QListWidget(ChooseLanguageDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.languagesList.sizePolicy().hasHeightForWidth())
        self.languagesList.setSizePolicy(sizePolicy)
        self.languagesList.setObjectName(_fromUtf8("languagesList"))
        self.verticalLayout.addWidget(self.languagesList)
        self.line = QtGui.QFrame(ChooseLanguageDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.label_2 = QtGui.QLabel(ChooseLanguageDialog)
        self.label_2.setTextFormat(QtCore.Qt.RichText)
        self.label_2.setOpenExternalLinks(True)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.line_2 = QtGui.QFrame(ChooseLanguageDialog)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.verticalLayout.addWidget(self.line_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(158, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.OKButton = QtGui.QPushButton(ChooseLanguageDialog)
        self.OKButton.setObjectName(_fromUtf8("OKButton"))
        self.horizontalLayout.addWidget(self.OKButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ChooseLanguageDialog)
        QtCore.QMetaObject.connectSlotsByName(ChooseLanguageDialog)

    def retranslateUi(self, ChooseLanguageDialog):
        ChooseLanguageDialog.setWindowTitle(_translate("ChooseLanguageDialog", "Choose language:", None))
        self.label.setText(_translate("ChooseLanguageDialog", "Available languages:", None))
        self.label_2.setText(_translate("ChooseLanguageDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Click <a href=\"http://www.subdownloader.net/translate.html\"><span style=\" text-decoration: underline; color:#0057ae;\">here</span></a> to help us to translate </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">SubDownloader into  your language.</p></body></html>", None))
        self.OKButton.setText(_translate("ChooseLanguageDialog", "OK", None))


class ChooseLanguageDialog(QtGui.QDialog, Ui_ChooseLanguageDialog):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QDialog.__init__(self, parent, f)

        self.setupUi(self)

