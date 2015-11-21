# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
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

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName(_fromUtf8("AboutDialog"))
        AboutDialog.setWindowModality(QtCore.Qt.WindowModal)
        AboutDialog.resize(400, 416)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        AboutDialog.setMinimumSize(QtCore.QSize(400, 400))
        AboutDialog.setMaximumSize(QtCore.QSize(400, 600))
        AboutDialog.setAutoFillBackground(False)
        self.verticalLayout = QtGui.QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(20, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_sd = QtGui.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Tahoma"))
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_sd.setFont(font)
        self.label_sd.setObjectName(_fromUtf8("label_sd"))
        self.horizontalLayout.addWidget(self.label_sd)
        self.label_version = QtGui.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Tahoma"))
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_version.setFont(font)
        self.label_version.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_version.setObjectName(_fromUtf8("label_version"))
        self.horizontalLayout.addWidget(self.label_version)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.lblIcon = QtGui.QLabel(AboutDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblIcon.sizePolicy().hasHeightForWidth())
        self.lblIcon.setSizePolicy(sizePolicy)
        self.lblIcon.setText(_fromUtf8(""))
        self.lblIcon.setObjectName(_fromUtf8("lblIcon"))
        self.verticalLayout.addWidget(self.lblIcon)
        self.tabs = QtGui.QTabWidget(AboutDialog)
        self.tabs.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabs.sizePolicy().hasHeightForWidth())
        self.tabs.setSizePolicy(sizePolicy)
        self.tabs.setSizeIncrement(QtCore.QSize(5, 5))
        self.tabs.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.tabs.setObjectName(_fromUtf8("tabs"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridlayout = QtGui.QGridLayout(self.tab)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.txtAbout = QtGui.QTextBrowser(self.tab)
        self.txtAbout.setAcceptDrops(False)
        self.txtAbout.setFrameShape(QtGui.QFrame.NoFrame)
        self.txtAbout.setOpenExternalLinks(True)
        self.txtAbout.setObjectName(_fromUtf8("txtAbout"))
        self.gridlayout.addWidget(self.txtAbout, 0, 0, 1, 1)
        self.tabs.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.gridlayout1 = QtGui.QGridLayout(self.tab_2)
        self.gridlayout1.setObjectName(_fromUtf8("gridlayout1"))
        self.txtAuthors = QtGui.QTextBrowser(self.tab_2)
        self.txtAuthors.setAcceptDrops(False)
        self.txtAuthors.setFrameShape(QtGui.QFrame.NoFrame)
        self.txtAuthors.setObjectName(_fromUtf8("txtAuthors"))
        self.gridlayout1.addWidget(self.txtAuthors, 0, 0, 1, 1)
        self.tabs.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.gridlayout2 = QtGui.QGridLayout(self.tab_3)
        self.gridlayout2.setObjectName(_fromUtf8("gridlayout2"))
        self.txtLicense = QtGui.QTextBrowser(self.tab_3)
        self.txtLicense.setAcceptDrops(False)
        self.txtLicense.setFrameShape(QtGui.QFrame.VLine)
        self.txtLicense.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtLicense.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
        self.txtLicense.setObjectName(_fromUtf8("txtLicense"))
        self.gridlayout2.addWidget(self.txtLicense, 0, 0, 1, 1)
        self.tabs.addTab(self.tab_3, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabs)
        self.hboxlayout = QtGui.QHBoxLayout()
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.buttonClose = QtGui.QPushButton(AboutDialog)
        self.buttonClose.setStyleSheet(_fromUtf8(""))
        self.buttonClose.setObjectName(_fromUtf8("buttonClose"))
        self.hboxlayout.addWidget(self.buttonClose)
        self.verticalLayout.addLayout(self.hboxlayout)

        self.retranslateUi(AboutDialog)
        self.tabs.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonClose, QtCore.SIGNAL(_fromUtf8("clicked()")), AboutDialog.close)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About Subdownloader", None))
        self.label_sd.setText(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Tahoma\'; font-size:10pt; font-weight:600; font-style:italic;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\"><span style=\" font-size:24pt; font-weight:600;\">Subdownloader</span></p></body></html>", None))
        self.label_version.setText(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Tahoma\'; font-size:10pt; font-weight:600; font-style:italic;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\"><span style=\" font-family:\'serif\'; font-size:14pt; font-weight:600;\">2.0.5</span></p></body></html>", None))
        self.txtAbout.setHtml(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'DejaVu Sans\'; font-size:10pt;\">Homepage:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.subdownloader.net/\"><span style=\" font-family:\'DejaVu Sans\'; font-size:10pt; text-decoration: underline; color:#0057ae;\">http://www.subdownloader.net/</span></a></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'DejaVu Sans\'; font-size:10pt; text-decoration: underline; color:#0057ae;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'DejaVu Sans\'; font-size:10pt;\">Bugs and new requests:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://bugs.launchpad.net/subdownloader\"><span style=\" font-family:\'DejaVu Sans\'; font-size:10pt; text-decoration: underline; color:#0057ae;\">https://bugs.launchpad.net/subdownloader</span></a></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'DejaVu Sans\'; font-size:10pt;\">IRC: </span><span style=\" font-family:\'DejaVu Sans\'; font-size:10pt; font-weight:600;\">irc.freenode.net</span><span style=\" font-family:\'DejaVu Sans\'; font-size:10pt;\"> - </span><span style=\" font-family:\'DejaVu Sans\'; font-size:10pt; font-weight:600;\">#subdownloader</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'DejaVu Sans\'; font-size:10pt; font-weight:600;\">Donations</span><span style=\" font-family:\'DejaVu Sans\'; font-size:10pt;\">:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.subdownloader.net/donations.html\"><span style=\" font-family:\'DejaVu Sans\'; font-size:10pt; text-decoration: underline; color:#0057ae;\">Our paypal account</span></a></p></body></html>", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab), _translate("AboutDialog", "About", None))
        self.txtAuthors.setHtml(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">Ivan Garcia &lt;</span><a href=\"mailto:ivangarcia@subdownloader.net\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">ivangarcia@subdownloader.net</span></a><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">&gt;</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">Marco Ferreira &lt;</span><a href=\"mailto:mferreira@subdownloader.net\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">mferreira@subdownloader.net</span></a><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">&gt;</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">Marco Rodrigues &lt;</span><a href=\"mailto:mferreira@subdownloader.net\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">gothicx@gmail.com</span></a><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">&gt;</span></p></body></html>", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_2), _translate("AboutDialog", "Authors", None))
        self.txtLicense.setHtml(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">Copyright (c) 2007-2010, Subdownloader Developers</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or(at your option) any later version.                   </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">This program is distributed in the hope that it will</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.                         </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc.,</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.  </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\"><br /></p></body></html>", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_3), _translate("AboutDialog", "License Agreement", None))
        self.buttonClose.setText(_translate("AboutDialog", "Close", None))


class AboutDialog(QtGui.QDialog, Ui_AboutDialog):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QDialog.__init__(self, parent, f)

        self.setupUi(self)

