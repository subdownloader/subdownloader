# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Thu Jul 12 16:11:26 2007
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,903,638).size()).expandedTo(MainWindow.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(200,322,601,221))
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")

        self.label_3 = QtGui.QLabel(self.splitter)
        self.label_3.setObjectName("label_3")

        self.tree_subs = QtGui.QTreeWidget(self.splitter)
        self.tree_subs.setObjectName("tree_subs")

        self.splitter_3 = QtGui.QSplitter(self.centralwidget)
        self.splitter_3.setGeometry(QtCore.QRect(200,0,601,311))
        self.splitter_3.setOrientation(QtCore.Qt.Vertical)
        self.splitter_3.setObjectName("splitter_3")

        self.label_2 = QtGui.QLabel(self.splitter_3)
        self.label_2.setObjectName("label_2")

        self.tree_videos = QtGui.QTreeWidget(self.splitter_3)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tree_videos.sizePolicy().hasHeightForWidth())
        self.tree_videos.setSizePolicy(sizePolicy)
        self.tree_videos.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_videos.setObjectName("tree_videos")

        self.button_download = QtGui.QPushButton(self.centralwidget)
        self.button_download.setGeometry(QtCore.QRect(810,80,91,27))
        self.button_download.setIcon(QtGui.QIcon(":/images/download.png"))
        self.button_download.setObjectName("button_download")

        self.button_chgtitle = QtGui.QPushButton(self.centralwidget)
        self.button_chgtitle.setGeometry(QtCore.QRect(810,40,91,27))
        self.button_chgtitle.setObjectName("button_chgtitle")

        self.button_chglng = QtGui.QPushButton(self.centralwidget)
        self.button_chglng.setGeometry(QtCore.QRect(810,350,91,27))
        self.button_chglng.setObjectName("button_chglng")

        self.button_upload = QtGui.QPushButton(self.centralwidget)
        self.button_upload.setGeometry(QtCore.QRect(810,390,91,27))
        self.button_upload.setIcon(QtGui.QIcon(":/images/upload.png"))
        self.button_upload.setObjectName("button_upload")

        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(10,0,181,42))
        self.label_4.setObjectName("label_4")

        self.folderView = QtGui.QTreeView(self.centralwidget)
        self.folderView.setGeometry(QtCore.QRect(10,48,181,491))
        self.folderView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.folderView.setObjectName("folderView")
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,903,25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.actionDownload_Subtitle = QtGui.QAction(MainWindow)
        self.actionDownload_Subtitle.setIcon(QtGui.QIcon(":/images/download.png"))
        self.actionDownload_Subtitle.setObjectName("actionDownload_Subtitle")

        self.actionUpload_Subtitle = QtGui.QAction(MainWindow)
        self.actionUpload_Subtitle.setIcon(QtGui.QIcon(":/images/upload.png"))
        self.actionUpload_Subtitle.setObjectName("actionUpload_Subtitle")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Subs to Upload:", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_subs.headerItem().setText(0,QtGui.QApplication.translate("MainWindow", "Language?", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_subs.headerItem().setText(1,QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Search Results:", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_videos.headerItem().setText(0,QtGui.QApplication.translate("MainWindow", "Language", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_videos.headerItem().setText(1,QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.button_download.setText(QtGui.QApplication.translate("MainWindow", "Download", None, QtGui.QApplication.UnicodeUTF8))
        self.button_chgtitle.setText(QtGui.QApplication.translate("MainWindow", "Change Title", None, QtGui.QApplication.UnicodeUTF8))
        self.button_chglng.setText(QtGui.QApplication.translate("MainWindow", "Change Lng", None, QtGui.QApplication.UnicodeUTF8))
        self.button_upload.setText(QtGui.QApplication.translate("MainWindow", "Upload", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("MainWindow", "Select Folder:", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDownload_Subtitle.setText(QtGui.QApplication.translate("MainWindow", "Download Subtitle", None, QtGui.QApplication.UnicodeUTF8))
        self.actionUpload_Subtitle.setText(QtGui.QApplication.translate("MainWindow", "Upload Subtitle", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
