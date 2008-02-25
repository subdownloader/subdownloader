# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Tue Sep 25 22:00:53 2007
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

from sublistview import SubListView
from subosdblistview import SubOsdbListView
from uploadlistview import UploadListView
from videolistview import VideoListView
import images_rc


class Ui_MainWindow(object):
    
    def __init__(self):
        pass
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,914,589).size()).expandedTo(MainWindow.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.splitter_3 = QtGui.QSplitter(self.centralwidget)
        self.splitter_3.setGeometry(QtCore.QRect(200,10,101,21))
        self.splitter_3.setOrientation(QtCore.Qt.Vertical)
        self.splitter_3.setObjectName("splitter_3")

        self.groupBox_4 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(640,10,271,251))
        self.groupBox_4.setObjectName("groupBox_4")

        self.sub_view = SubListView(self.groupBox_4)
        self.sub_view.setGeometry(QtCore.QRect(10,20,241,221))
        self.sub_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sub_view.setDragEnabled(True)
        self.sub_view.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.sub_view.setObjectName("sub_view")

        self.groupBox_2 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10,280,261,261))
        self.groupBox_2.setObjectName("groupBox_2")

        self.button_download = QtGui.QPushButton(self.groupBox_2)
        self.button_download.setGeometry(QtCore.QRect(10,220,91,27))
        self.button_download.setIcon(QtGui.QIcon(":/images/download.png"))
        self.button_download.setObjectName("button_download")

        self.subs_osdb_view = SubOsdbListView(self.groupBox_2)
        self.subs_osdb_view.setGeometry(QtCore.QRect(10,20,241,191))
        self.subs_osdb_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.subs_osdb_view.setObjectName("subs_osdb_view")

        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(280,280,621,261))
        self.groupBox.setObjectName("groupBox")

        self.button_upload = QtGui.QPushButton(self.groupBox)
        self.button_upload.setGeometry(QtCore.QRect(790,20,91,27))
        self.button_upload.setIcon(QtGui.QIcon(":/images/upload.png"))
        self.button_upload.setObjectName("button_upload")

        self.pushButton = QtGui.QPushButton(self.groupBox)
        self.pushButton.setGeometry(QtCore.QRect(270,20,91,27))
        self.pushButton.setObjectName("pushButton")

        self.lineEdit = QtGui.QLineEdit(self.groupBox)
        self.lineEdit.setGeometry(QtCore.QRect(110,20,151,29))
        self.lineEdit.setObjectName("lineEdit")

        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10,20,86,17))
        self.label.setObjectName("label")

        self.label_language = QtGui.QLabel(self.groupBox)
        self.label_language.setGeometry(QtCore.QRect(110,50,81,17))

        font = QtGui.QFont(self.label_language.font())
        font.setWeight(75)
        font.setBold(True)
        self.label_language.setFont(font)
        self.label_language.setTextFormat(QtCore.Qt.PlainText)
        self.label_language.setObjectName("label_language")

        self.button_chglng = QtGui.QPushButton(self.groupBox)
        self.button_chglng.setGeometry(QtCore.QRect(190,50,20,20))
        self.button_chglng.setObjectName("button_chglng")

        self.upload_view = UploadListView(self.groupBox)
        self.upload_view.setGeometry(QtCore.QRect(20,70,511,161))
        self.upload_view.setAcceptDrops(True)
        self.upload_view.setDragEnabled(True)
        self.upload_view.setDragDropMode(QtGui.QAbstractItemView.DropOnly)
        self.upload_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.upload_view.setObjectName("upload_view")

        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(10,50,66,17))
        self.label_5.setObjectName("label_5")

        self.groupBox_3 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(320,10,311,251))
        self.groupBox_3.setObjectName("groupBox_3")

        self.video_view = VideoListView(self.groupBox_3)
        self.video_view.setGeometry(QtCore.QRect(10,20,411,221))
        self.video_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.video_view.setDragEnabled(True)
        self.video_view.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.video_view.setObjectName("video_view")

        self.groupBox_5 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_5.setGeometry(QtCore.QRect(10,10,291,251))
        self.groupBox_5.setObjectName("groupBox_5")

        self.folderView = QtGui.QTreeView(self.groupBox_5)
        self.folderView.setGeometry(QtCore.QRect(10,20,271,221))
        self.folderView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.folderView.setObjectName("folderView")
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,914,25))
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
        self.groupBox_4.setTitle(QtGui.QApplication.translate("MainWindow", "Subtitles found:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("MainWindow", "Subtitles Online:", None, QtGui.QApplication.UnicodeUTF8))
        self.button_download.setText(QtGui.QApplication.translate("MainWindow", "Download", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Upload Subtitles", None, QtGui.QApplication.UnicodeUTF8))
        self.button_upload.setText(QtGui.QApplication.translate("MainWindow", "Upload", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Choose IMDB", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Select Movie: ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_language.setText(QtGui.QApplication.translate("MainWindow", "Undefined", None, QtGui.QApplication.UnicodeUTF8))
        self.button_chglng.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("MainWindow", "Language:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("MainWindow", "Videos found:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_5.setTitle(QtGui.QApplication.translate("MainWindow", "Select Folder:", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDownload_Subtitle.setText(QtGui.QApplication.translate("MainWindow", "Download Subtitle", None, QtGui.QApplication.UnicodeUTF8))
        self.actionUpload_Subtitle.setText(QtGui.QApplication.translate("MainWindow", "Upload Subtitle", None, QtGui.QApplication.UnicodeUTF8))
