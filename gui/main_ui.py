# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Sun Aug  5 15:07:19 2007
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,1003,654).size()).expandedTo(MainWindow.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(10,0,181,42))
        self.label_4.setObjectName("label_4")

        self.splitter_3 = QtGui.QSplitter(self.centralwidget)
        self.splitter_3.setGeometry(QtCore.QRect(200,10,101,21))
        self.splitter_3.setOrientation(QtCore.Qt.Vertical)
        self.splitter_3.setObjectName("splitter_3")

        self.label_2 = QtGui.QLabel(self.splitter_3)
        self.label_2.setObjectName("label_2")

        self.folderView = QtGui.QTreeView(self.centralwidget)
        self.folderView.setGeometry(QtCore.QRect(10,30,181,351))
        self.folderView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.folderView.setObjectName("folderView")

        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10,400,891,231))
        self.groupBox.setObjectName("groupBox")

        self.button_upload = QtGui.QPushButton(self.groupBox)
        self.button_upload.setGeometry(QtCore.QRect(790,190,91,27))
        self.button_upload.setIcon(QtGui.QIcon(":/images/upload.png"))
        self.button_upload.setObjectName("button_upload")

        self.pushButton = QtGui.QPushButton(self.groupBox)
        self.pushButton.setGeometry(QtCore.QRect(180,40,91,27))
        self.pushButton.setObjectName("pushButton")

        self.lineEdit = QtGui.QLineEdit(self.groupBox)
        self.lineEdit.setGeometry(QtCore.QRect(20,40,151,29))
        self.lineEdit.setObjectName("lineEdit")

        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(20,20,86,17))
        self.label.setObjectName("label")

        self.upload_view = UploadListView(self.groupBox)
        self.upload_view.setGeometry(QtCore.QRect(310,20,511,161))
        self.upload_view.setAcceptDrops(True)
        self.upload_view.setDragEnabled(True)
        self.upload_view.setDragDropMode(QtGui.QAbstractItemView.DropOnly)
        self.upload_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.upload_view.setObjectName("upload_view")

        self.button_chglng = QtGui.QPushButton(self.groupBox)
        self.button_chglng.setGeometry(QtCore.QRect(180,80,91,27))
        self.button_chglng.setObjectName("button_chglng")

        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(200,250,601,17))
        self.label_3.setObjectName("label_3")

        self.tree_subs = QtGui.QTreeWidget(self.centralwidget)
        self.tree_subs.setGeometry(QtCore.QRect(200,273,371,128))
        self.tree_subs.setDragEnabled(True)
        self.tree_subs.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.tree_subs.setObjectName("tree_subs")

        self.button_chgtitle = QtGui.QPushButton(self.centralwidget)
        self.button_chgtitle.setGeometry(QtCore.QRect(910,30,91,27))
        self.button_chgtitle.setObjectName("button_chgtitle")

        self.button_download = QtGui.QPushButton(self.centralwidget)
        self.button_download.setGeometry(QtCore.QRect(910,60,91,27))
        self.button_download.setIcon(QtGui.QIcon(":/images/download.png"))
        self.button_download.setObjectName("button_download")

        self.video_view = VideoListView(self.centralwidget)
        self.video_view.setGeometry(QtCore.QRect(200,30,371,211))
        self.video_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.video_view.setDragEnabled(True)
        self.video_view.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.video_view.setObjectName("video_view")

        self.subs_osdb_view = SubOsdbListView(self.centralwidget)
        self.subs_osdb_view.setGeometry(QtCore.QRect(600,120,301,281))
        self.subs_osdb_view.setObjectName("subs_osdb_view")
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,1003,25))
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
        self.label_4.setText(QtGui.QApplication.translate("MainWindow", "Select Folder:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Videos found:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Upload Subtitles", None, QtGui.QApplication.UnicodeUTF8))
        self.button_upload.setText(QtGui.QApplication.translate("MainWindow", "Upload", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Choose IMDB", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Select Movie: ", None, QtGui.QApplication.UnicodeUTF8))
        self.button_chglng.setText(QtGui.QApplication.translate("MainWindow", "Change Lng", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Subs found:", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_subs.headerItem().setText(0,QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.button_chgtitle.setText(QtGui.QApplication.translate("MainWindow", "Change Title", None, QtGui.QApplication.UnicodeUTF8))
        self.button_download.setText(QtGui.QApplication.translate("MainWindow", "Download", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDownload_Subtitle.setText(QtGui.QApplication.translate("MainWindow", "Download Subtitle", None, QtGui.QApplication.UnicodeUTF8))
        self.actionUpload_Subtitle.setText(QtGui.QApplication.translate("MainWindow", "Upload Subtitle", None, QtGui.QApplication.UnicodeUTF8))

from uploadlistview import UploadListView
from subosdblistview import SubOsdbListView
from videolistview import VideoListView
import images_rc
