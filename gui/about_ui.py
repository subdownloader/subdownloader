# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created: Mon Aug  4 19:07:49 2008
#      by: PyQt4 UI code generator 4.4.3-snapshot-20080731
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
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
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtGui.QSpacerItem(20, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_sd = QtGui.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(10)
        font.setWeight(75)
        font.setItalic(True)
        font.setBold(True)
        self.label_sd.setFont(font)
        self.label_sd.setObjectName("label_sd")
        self.horizontalLayout.addWidget(self.label_sd)
        self.label_version = QtGui.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(10)
        font.setWeight(75)
        font.setItalic(True)
        font.setBold(True)
        self.label_version.setFont(font)
        self.label_version.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_version.setObjectName("label_version")
        self.horizontalLayout.addWidget(self.label_version)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.lblIcon = QtGui.QLabel(AboutDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblIcon.sizePolicy().hasHeightForWidth())
        self.lblIcon.setSizePolicy(sizePolicy)
        self.lblIcon.setObjectName("lblIcon")
        self.verticalLayout.addWidget(self.lblIcon)
        self.tabs = QtGui.QTabWidget(AboutDialog)
        self.tabs.setWindowModality(QtCore.Qt.NonModal)
        self.tabs.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabs.sizePolicy().hasHeightForWidth())
        self.tabs.setSizePolicy(sizePolicy)
        self.tabs.setSizeIncrement(QtCore.QSize(5, 5))
        self.tabs.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.tabs.setObjectName("tabs")
        self.tab = QtGui.QWidget()
        self.tab.setGeometry(QtCore.QRect(0, 0, 378, 241))
        self.tab.setObjectName("tab")
        self.gridlayout = QtGui.QGridLayout(self.tab)
        self.gridlayout.setObjectName("gridlayout")
        self.txtAbout = QtGui.QTextBrowser(self.tab)
        self.txtAbout.setAcceptDrops(False)
        self.txtAbout.setFrameShape(QtGui.QFrame.NoFrame)
        self.txtAbout.setOpenExternalLinks(True)
        self.txtAbout.setObjectName("txtAbout")
        self.gridlayout.addWidget(self.txtAbout, 0, 0, 1, 1)
        self.tabs.addTab(self.tab, "")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setGeometry(QtCore.QRect(0, 0, 378, 241))
        self.tab_2.setObjectName("tab_2")
        self.gridlayout1 = QtGui.QGridLayout(self.tab_2)
        self.gridlayout1.setObjectName("gridlayout1")
        self.txtAuthors = QtGui.QTextBrowser(self.tab_2)
        self.txtAuthors.setAcceptDrops(False)
        self.txtAuthors.setFrameShape(QtGui.QFrame.NoFrame)
        self.txtAuthors.setObjectName("txtAuthors")
        self.gridlayout1.addWidget(self.txtAuthors, 0, 0, 1, 1)
        self.tabs.addTab(self.tab_2, "")
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setGeometry(QtCore.QRect(0, 0, 378, 241))
        self.tab_3.setObjectName("tab_3")
        self.gridlayout2 = QtGui.QGridLayout(self.tab_3)
        self.gridlayout2.setObjectName("gridlayout2")
        self.txtLicense = QtGui.QTextBrowser(self.tab_3)
        self.txtLicense.setAcceptDrops(False)
        self.txtLicense.setFrameShape(QtGui.QFrame.VLine)
        self.txtLicense.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtLicense.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
        self.txtLicense.setObjectName("txtLicense")
        self.gridlayout2.addWidget(self.txtLicense, 0, 0, 1, 1)
        self.tabs.addTab(self.tab_3, "")
        self.verticalLayout.addWidget(self.tabs)
        self.hboxlayout = QtGui.QHBoxLayout()

        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.buttonClose = QtGui.QPushButton(AboutDialog)
        self.buttonClose.setObjectName("buttonClose")
        self.hboxlayout.addWidget(self.buttonClose)
        self.verticalLayout.addLayout(self.hboxlayout)

        self.retranslateUi(AboutDialog)
        self.tabs.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonClose, QtCore.SIGNAL("clicked()"), AboutDialog.close)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QtGui.QApplication.translate("AboutDialog", "About Subdownloader", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sd.setText(QtGui.QApplication.translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Tahoma\'; font-size:10pt; font-weight:600; font-style:italic;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\"><span style=\" font-size:29pt; font-weight:600;\">Subdownloader</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_version.setText(QtGui.QApplication.translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Tahoma\'; font-size:10pt; font-weight:600; font-style:italic;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\"><span style=\" font-family:\'serif\'; font-size:14pt; font-weight:600;\">2.0.5</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.txtAbout.setHtml(QtGui.QApplication.translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Homepage:</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.subdownloader.net/\"><span style=\" text-decoration: underline; color:#0057ae;\">http://www.subdownloader.net/</span></a></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; text-decoration: underline; color:#0057ae;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; text-decoration: underline;\"><span style=\" text-decoration:none;\">Bugs and new requests:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://bugs.launchpad.net/subdownloader\"><span style=\" text-decoration: underline; color:#0057ae;\">https://bugs.launchpad.net/subdownloader</span></a></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">IRC: <span style=\" font-weight:600;\">FREENODE</span> server , <span style=\" font-weight:600;\">#subdownloader</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; text-decoration: underline;\"><span style=\" font-weight:600; text-decoration:none;\">Donate us</span><span style=\" text-decoration:none;\">:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=donations%40subdownloader%2enet&no_shipping=0&no_note=1&tax=0&currency_code=EUR&lc=PT&bn=PP%2dDonationsBF&charset=UTF%2d8\"><span style=\" text-decoration: underline; color:#0057ae;\">Our paypal account</span></a></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab), QtGui.QApplication.translate("AboutDialog", "&About", None, QtGui.QApplication.UnicodeUTF8))
        self.txtAuthors.setHtml(QtGui.QApplication.translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\">Ivan Garcia &lt;<a href=\"mailto:ivangarcia@subdownloader.net\"><span style=\" text-decoration: underline; color:#0057ae;\">ivangarcia@subdownloader.net</span></a>&gt;</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\">Marco Ferreira &lt;<a href=\"mailto:mferreira@subdownloader.net\"><span style=\" text-decoration: underline; color:#0057ae;\">mferreira@subdownloader.net</span></a>&gt;</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_2), QtGui.QApplication.translate("AboutDialog", "A&uthors", None, QtGui.QApplication.UnicodeUTF8))
        self.txtLicense.setHtml(QtGui.QApplication.translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\">Copyright (c) 2007-2008, Subdownloader Developers</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\">This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or(at your option) any later version.                   </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\"></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\">This program is distributed in the hope that it will</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\">be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.                         </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\">You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc.,</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\">59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.  </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_3), QtGui.QApplication.translate("AboutDialog", "&License Agreement", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonClose.setText(QtGui.QApplication.translate("AboutDialog", "&Close", None, QtGui.QApplication.UnicodeUTF8))

