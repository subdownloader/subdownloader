# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/maarten/programming/subdownloader_old/scripts/gui/ui/about.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.setWindowModality(QtCore.Qt.WindowModal)
        AboutDialog.resize(450, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        AboutDialog.setMinimumSize(QtCore.QSize(450, 600))
        AboutDialog.setMaximumSize(QtCore.QSize(450, 600))
        AboutDialog.setAutoFillBackground(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 16, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_project = QtWidgets.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(24)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_project.setFont(font)
        self.label_project.setObjectName("label_project")
        self.horizontalLayout.addWidget(self.label_project)
        self.label_version = QtWidgets.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_version.setFont(font)
        self.label_version.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_version.setObjectName("label_version")
        self.horizontalLayout.addWidget(self.label_version)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.lblIcon = QtWidgets.QLabel(AboutDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblIcon.sizePolicy().hasHeightForWidth())
        self.lblIcon.setSizePolicy(sizePolicy)
        self.lblIcon.setText("")
        self.lblIcon.setObjectName("lblIcon")
        self.verticalLayout.addWidget(self.lblIcon)
        self.tabs = QtWidgets.QTabWidget(AboutDialog)
        self.tabs.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabs.sizePolicy().hasHeightForWidth())
        self.tabs.setSizePolicy(sizePolicy)
        self.tabs.setSizeIncrement(QtCore.QSize(5, 5))
        self.tabs.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.tabs.setObjectName("tabs")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridlayout = QtWidgets.QGridLayout(self.tab)
        self.gridlayout.setContentsMargins(0, 0, 0, 0)
        self.gridlayout.setObjectName("gridlayout")
        self.txtAbout = QtWidgets.QTextBrowser(self.tab)
        self.txtAbout.setAcceptDrops(False)
        self.txtAbout.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.txtAbout.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Cantarell\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'DejaVu Sans\'; font-size:10pt;\">Homepage:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"url\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">url</span></a></p></body></html>")
        self.txtAbout.setOpenExternalLinks(True)
        self.txtAbout.setObjectName("txtAbout")
        self.gridlayout.addWidget(self.txtAbout, 0, 0, 1, 1)
        self.tabs.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridlayout1 = QtWidgets.QGridLayout(self.tab_2)
        self.gridlayout1.setContentsMargins(0, 0, 0, 0)
        self.gridlayout1.setObjectName("gridlayout1")
        self.txtAuthors = QtWidgets.QTextBrowser(self.tab_2)
        self.txtAuthors.setAcceptDrops(False)
        self.txtAuthors.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.txtAuthors.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Cantarell\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">name &lt;</span><a href=\"mailto:mail\"><span style=\" text-decoration: underline; color:#2a76c6;\">mail</span></a><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">&gt;</span></p></body></html>")
        self.txtAuthors.setOpenExternalLinks(True)
        self.txtAuthors.setObjectName("txtAuthors")
        self.gridlayout1.addWidget(self.txtAuthors, 0, 0, 1, 1)
        self.tabs.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.gridlayout2 = QtWidgets.QGridLayout(self.tab_3)
        self.gridlayout2.setContentsMargins(0, 0, 0, 0)
        self.gridlayout2.setObjectName("gridlayout2")
        self.txtLicense = QtWidgets.QTextBrowser(self.tab_3)
        self.txtLicense.setAcceptDrops(False)
        self.txtLicense.setFrameShape(QtWidgets.QFrame.VLine)
        self.txtLicense.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtLicense.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.txtLicense.setOpenExternalLinks(True)
        self.txtLicense.setObjectName("txtLicense")
        self.gridlayout2.addWidget(self.txtLicense, 0, 0, 1, 1)
        self.tabs.addTab(self.tab_3, "")
        self.verticalLayout.addWidget(self.tabs)
        self.hboxlayout = QtWidgets.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.buttonClose = QtWidgets.QPushButton(AboutDialog)
        self.buttonClose.setStyleSheet("")
        self.buttonClose.setObjectName("buttonClose")
        self.hboxlayout.addWidget(self.buttonClose)
        self.verticalLayout.addLayout(self.hboxlayout)

        self.retranslateUi(AboutDialog)
        self.tabs.setCurrentIndex(0)
        self.buttonClose.clicked.connect(AboutDialog.close)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_("About Subdownloader"))
        self.label_project.setText(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Tahoma\'; font-size:10pt; font-weight:600; font-style:italic;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\"><span style=\" font-size:24pt; font-weight:600;\">Subdownloader</span></p></body></html>"))
        self.label_version.setText(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Tahoma\'; font-size:10pt; font-weight:600; font-style:italic;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'serif\'; font-size:14pt; font-style:normal;\">X.Y.Z</span></p></body></html>"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab), _("About"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_2), _("Authors"))
        self.txtLicense.setHtml(_translate("AboutDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Cantarell\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">license</span></p></body></html>"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_3), _("License Agreement"))
        self.buttonClose.setText(_("Close"))

