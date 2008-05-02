# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Fri May  2 23:41:17 2008
#      by: PyQt4 UI code generator 4.3.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,776,653).size()).expandedTo(MainWindow.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.vboxlayout = QtGui.QVBoxLayout(self.centralwidget)


        self.tabs = QtGui.QTabWidget(self.centralwidget)
        self.tabs.setObjectName("tabs")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.tab)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.hboxlayout = QtGui.QHBoxLayout()


        self.buttonPlay = QtGui.QPushButton(self.tab)
        self.buttonPlay.setEnabled(False)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonPlay.sizePolicy().hasHeightForWidth())
        self.buttonPlay.setSizePolicy(sizePolicy)
        self.buttonPlay.setObjectName("buttonPlay")
        self.hboxlayout.addWidget(self.buttonPlay)

        self.buttonDownload = QtGui.QPushButton(self.tab)
        self.buttonDownload.setEnabled(False)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonDownload.sizePolicy().hasHeightForWidth())
        self.buttonDownload.setSizePolicy(sizePolicy)

        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.buttonDownload.setFont(font)
        self.buttonDownload.setObjectName("buttonDownload")
        self.hboxlayout.addWidget(self.buttonDownload)

        self.buttonIMDB = QtGui.QPushButton(self.tab)
        self.buttonIMDB.setEnabled(False)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonIMDB.sizePolicy().hasHeightForWidth())
        self.buttonIMDB.setSizePolicy(sizePolicy)
        self.buttonIMDB.setIcon(QtGui.QIcon(":/images/info.png"))
        self.buttonIMDB.setIconSize(QtCore.QSize(32,16))
        self.buttonIMDB.setObjectName("buttonIMDB")
        self.hboxlayout.addWidget(self.buttonIMDB)

        spacerItem = QtGui.QSpacerItem(231,27,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.label_9 = QtGui.QLabel(self.tab)
        self.label_9.setObjectName("label_9")
        self.hboxlayout.addWidget(self.label_9)

        self.filterLanguageForVideo = QtGui.QComboBox(self.tab)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filterLanguageForVideo.sizePolicy().hasHeightForWidth())
        self.filterLanguageForVideo.setSizePolicy(sizePolicy)
        self.filterLanguageForVideo.setMinimumSize(QtCore.QSize(100,0))
        self.filterLanguageForVideo.setObjectName("filterLanguageForVideo")
        self.hboxlayout.addWidget(self.filterLanguageForVideo)
        self.vboxlayout1.addLayout(self.hboxlayout)

        self.splitter = QtGui.QSplitter(self.tab)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.groupBox_5 = QtGui.QGroupBox(self.splitter)
        self.groupBox_5.setObjectName("groupBox_5")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.groupBox_5)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.folderView = QtGui.QTreeView(self.groupBox_5)
        self.folderView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.folderView.setObjectName("folderView")
        self.vboxlayout2.addWidget(self.folderView)

        self.groupBox_videosFound = QtGui.QGroupBox(self.splitter)
        self.groupBox_videosFound.setObjectName("groupBox_videosFound")

        self.hboxlayout1 = QtGui.QHBoxLayout(self.groupBox_videosFound)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.videoView = QtGui.QTreeView(self.groupBox_videosFound)
        self.videoView.setObjectName("videoView")
        self.hboxlayout1.addWidget(self.videoView)
        self.vboxlayout1.addWidget(self.splitter)
        self.tabs.addTab(self.tab,"")

        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")

        self.vboxlayout3 = QtGui.QVBoxLayout(self.tab_3)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.lineEdit_2 = QtGui.QLineEdit(self.tab_3)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.hboxlayout2.addWidget(self.lineEdit_2)

        self.pushButton_2 = QtGui.QPushButton(self.tab_3)
        self.pushButton_2.setObjectName("pushButton_2")
        self.hboxlayout2.addWidget(self.pushButton_2)

        spacerItem1 = QtGui.QSpacerItem(29,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem1)

        self.label_3 = QtGui.QLabel(self.tab_3)
        self.label_3.setObjectName("label_3")
        self.hboxlayout2.addWidget(self.label_3)

        self.comboBox = QtGui.QComboBox(self.tab_3)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setObjectName("comboBox")
        self.hboxlayout2.addWidget(self.comboBox)
        self.vboxlayout3.addLayout(self.hboxlayout2)

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setObjectName("hboxlayout3")

        spacerItem2 = QtGui.QSpacerItem(581,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem2)

        self.label_10 = QtGui.QLabel(self.tab_3)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setObjectName("label_10")
        self.hboxlayout3.addWidget(self.label_10)

        self.filterLanguageForTitle = QtGui.QComboBox(self.tab_3)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filterLanguageForTitle.sizePolicy().hasHeightForWidth())
        self.filterLanguageForTitle.setSizePolicy(sizePolicy)
        self.filterLanguageForTitle.setMinimumSize(QtCore.QSize(100,0))
        self.filterLanguageForTitle.setObjectName("filterLanguageForTitle")
        self.hboxlayout3.addWidget(self.filterLanguageForTitle)
        self.vboxlayout3.addLayout(self.hboxlayout3)

        self.vboxlayout4 = QtGui.QVBoxLayout()
        self.vboxlayout4.setObjectName("vboxlayout4")

        self.groupBox_4 = QtGui.QGroupBox(self.tab_3)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.groupBox_4.setObjectName("groupBox_4")

        self.hboxlayout4 = QtGui.QHBoxLayout(self.groupBox_4)
        self.hboxlayout4.setObjectName("hboxlayout4")

        self.sub_view = SubListView(self.groupBox_4)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sub_view.sizePolicy().hasHeightForWidth())
        self.sub_view.setSizePolicy(sizePolicy)
        self.sub_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sub_view.setDragEnabled(True)
        self.sub_view.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.sub_view.setObjectName("sub_view")
        self.hboxlayout4.addWidget(self.sub_view)
        self.vboxlayout4.addWidget(self.groupBox_4)
        self.vboxlayout3.addLayout(self.vboxlayout4)
        self.tabs.addTab(self.tab_3,"")

        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName("tab_4")

        self.vboxlayout5 = QtGui.QVBoxLayout(self.tab_4)
        self.vboxlayout5.setObjectName("vboxlayout5")

        self.vboxlayout6 = QtGui.QVBoxLayout()
        self.vboxlayout6.setObjectName("vboxlayout6")

        self.groupBox_2 = QtGui.QGroupBox(self.tab_4)
        self.groupBox_2.setObjectName("groupBox_2")

        self.vboxlayout7 = QtGui.QVBoxLayout(self.groupBox_2)
        self.vboxlayout7.setObjectName("vboxlayout7")

        self.vboxlayout8 = QtGui.QVBoxLayout()
        self.vboxlayout8.setObjectName("vboxlayout8")

        self.hboxlayout5 = QtGui.QHBoxLayout()
        self.hboxlayout5.setObjectName("hboxlayout5")

        self.buttonUploadBrowseFolder = QtGui.QToolButton(self.groupBox_2)
        self.buttonUploadBrowseFolder.setIcon(QtGui.QIcon(":/images/openfolder.png"))
        self.buttonUploadBrowseFolder.setIconSize(QtCore.QSize(24,24))
        self.buttonUploadBrowseFolder.setObjectName("buttonUploadBrowseFolder")
        self.hboxlayout5.addWidget(self.buttonUploadBrowseFolder)

        self.line_3 = QtGui.QFrame(self.groupBox_2)
        self.line_3.setFrameShape(QtGui.QFrame.VLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.hboxlayout5.addWidget(self.line_3)

        self.buttonUploadPlusRow = QtGui.QToolButton(self.groupBox_2)
        self.buttonUploadPlusRow.setEnabled(True)
        self.buttonUploadPlusRow.setIcon(QtGui.QIcon(":/images/plus.png"))
        self.buttonUploadPlusRow.setIconSize(QtCore.QSize(24,24))
        self.buttonUploadPlusRow.setObjectName("buttonUploadPlusRow")
        self.hboxlayout5.addWidget(self.buttonUploadPlusRow)

        self.buttonUploadMinusRow = QtGui.QToolButton(self.groupBox_2)
        self.buttonUploadMinusRow.setEnabled(False)
        self.buttonUploadMinusRow.setIcon(QtGui.QIcon(":/images/minus.png"))
        self.buttonUploadMinusRow.setIconSize(QtCore.QSize(24,24))
        self.buttonUploadMinusRow.setObjectName("buttonUploadMinusRow")
        self.hboxlayout5.addWidget(self.buttonUploadMinusRow)

        self.line_2 = QtGui.QFrame(self.groupBox_2)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.hboxlayout5.addWidget(self.line_2)

        self.buttonUploadUpRow = QtGui.QToolButton(self.groupBox_2)
        self.buttonUploadUpRow.setEnabled(False)
        self.buttonUploadUpRow.setIcon(QtGui.QIcon(":/images/up.png"))
        self.buttonUploadUpRow.setIconSize(QtCore.QSize(24,24))
        self.buttonUploadUpRow.setObjectName("buttonUploadUpRow")
        self.hboxlayout5.addWidget(self.buttonUploadUpRow)

        self.buttonUploadDownRow = QtGui.QToolButton(self.groupBox_2)
        self.buttonUploadDownRow.setEnabled(False)
        self.buttonUploadDownRow.setIcon(QtGui.QIcon(":/images/down.png"))
        self.buttonUploadDownRow.setIconSize(QtCore.QSize(24,24))
        self.buttonUploadDownRow.setObjectName("buttonUploadDownRow")
        self.hboxlayout5.addWidget(self.buttonUploadDownRow)

        spacerItem3 = QtGui.QSpacerItem(401,33,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout5.addItem(spacerItem3)

        self.buttonUpload = QtGui.QPushButton(self.groupBox_2)
        self.buttonUpload.setEnabled(False)

        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.buttonUpload.setFont(font)
        self.buttonUpload.setObjectName("buttonUpload")
        self.hboxlayout5.addWidget(self.buttonUpload)
        self.vboxlayout8.addLayout(self.hboxlayout5)

        self.uploadView = UploadListView(self.groupBox_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uploadView.sizePolicy().hasHeightForWidth())
        self.uploadView.setSizePolicy(sizePolicy)
        self.uploadView.setAcceptDrops(True)
        self.uploadView.setDragEnabled(True)
        self.uploadView.setDragDropMode(QtGui.QAbstractItemView.DropOnly)
        self.uploadView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.uploadView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.uploadView.setGridStyle(QtCore.Qt.DotLine)
        self.uploadView.setObjectName("uploadView")
        self.vboxlayout8.addWidget(self.uploadView)
        self.vboxlayout7.addLayout(self.vboxlayout8)

        self.line = QtGui.QFrame(self.groupBox_2)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.vboxlayout7.addWidget(self.line)
        self.vboxlayout6.addWidget(self.groupBox_2)

        self.groupBox = QtGui.QGroupBox(self.tab_4)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(300,0))
        self.groupBox.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.groupBox.setObjectName("groupBox")

        self.gridlayout = QtGui.QGridLayout(self.groupBox)
        self.gridlayout.setObjectName("gridlayout")

        self.label_4 = QtGui.QLabel(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMaximumSize(QtCore.QSize(10,16777215))
        self.label_4.setObjectName("label_4")
        self.gridlayout.addWidget(self.label_4,0,0,1,1)

        self.label = QtGui.QLabel(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,1,1,1)

        self.comboBox_3 = QtGui.QComboBox(self.groupBox)
        self.comboBox_3.setObjectName("comboBox_3")
        self.gridlayout.addWidget(self.comboBox_3,0,2,1,1)

        self.buttonUploadFindIMDB = QtGui.QPushButton(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonUploadFindIMDB.sizePolicy().hasHeightForWidth())
        self.buttonUploadFindIMDB.setSizePolicy(sizePolicy)
        self.buttonUploadFindIMDB.setMinimumSize(QtCore.QSize(0,0))
        self.buttonUploadFindIMDB.setMaximumSize(QtCore.QSize(50,16777215))
        self.buttonUploadFindIMDB.setObjectName("buttonUploadFindIMDB")
        self.gridlayout.addWidget(self.buttonUploadFindIMDB,0,3,1,1)

        self.label_8 = QtGui.QLabel(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setMaximumSize(QtCore.QSize(10,16777215))
        self.label_8.setObjectName("label_8")
        self.gridlayout.addWidget(self.label_8,1,0,1,1)

        self.label_5 = QtGui.QLabel(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setObjectName("label_5")
        self.gridlayout.addWidget(self.label_5,1,1,1,1)

        self.comboBox_2 = QtGui.QComboBox(self.groupBox)
        self.comboBox_2.setObjectName("comboBox_2")
        self.gridlayout.addWidget(self.comboBox_2,1,2,1,1)

        self.label_6 = QtGui.QLabel(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setObjectName("label_6")
        self.gridlayout.addWidget(self.label_6,2,1,1,1)

        self.lineEdit = QtGui.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.gridlayout.addWidget(self.lineEdit,2,2,1,1)

        self.label_7 = QtGui.QLabel(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setObjectName("label_7")
        self.gridlayout.addWidget(self.label_7,3,1,1,1)

        self.textEdit = QtGui.QTextEdit(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setMaximumSize(QtCore.QSize(16777215,100))
        self.textEdit.setObjectName("textEdit")
        self.gridlayout.addWidget(self.textEdit,3,2,1,1)
        self.vboxlayout6.addWidget(self.groupBox)
        self.vboxlayout5.addLayout(self.vboxlayout6)
        self.tabs.addTab(self.tab_4,"")

        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.tabs.addTab(self.tab_5,"")

        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabs.addTab(self.tab_2,"")
        self.vboxlayout.addWidget(self.tabs)
        MainWindow.setCentralWidget(self.centralwidget)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "SubDownloader", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonPlay.setText(QtGui.QApplication.translate("MainWindow", "Play", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonDownload.setText(QtGui.QApplication.translate("MainWindow", "Download", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonIMDB.setText(QtGui.QApplication.translate("MainWindow", "Show Movie Info", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("MainWindow", "Show :", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_5.setTitle(QtGui.QApplication.translate("MainWindow", "Select Folder:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_videosFound.setTitle(QtGui.QApplication.translate("MainWindow", "Videos found:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab), QtGui.QApplication.translate("MainWindow", "Search from Video file(s)", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("MainWindow", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Search in: ", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.addItem(QtGui.QApplication.translate("MainWindow", "OpenSubtitles.org", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.addItem(QtGui.QApplication.translate("MainWindow", "subtitles.images.o2.cz", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.addItem(QtGui.QApplication.translate("MainWindow", "mysubtitles.com", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.addItem(QtGui.QApplication.translate("MainWindow", "subtitlesbox.com", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.addItem(QtGui.QApplication.translate("MainWindow", "divxsubtitles.net", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("MainWindow", "Show :", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("MainWindow", "Subtitles found:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_3), QtGui.QApplication.translate("MainWindow", "Search by Movie Name", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("MainWindow", "Select Folder with Videos / Subtitles: ", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonUploadBrowseFolder.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonUploadPlusRow.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonUploadMinusRow.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonUploadUpRow.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonUploadDownRow.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonUpload.setText(QtGui.QApplication.translate("MainWindow", "Upload", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Details", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("MainWindow", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; color:#ff0000;\">*</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "IMDB: ", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonUploadFindIMDB.setText(QtGui.QApplication.translate("MainWindow", "Find", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("MainWindow", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; color:#ff0000;\">*</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("MainWindow", "Language:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("MainWindow", "Release:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("MainWindow", "Comments:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_4), QtGui.QApplication.translate("MainWindow", "Upload subtitles", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_5), QtGui.QApplication.translate("MainWindow", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_2), QtGui.QApplication.translate("MainWindow", "Contact us / Tip us :-)", None, QtGui.QApplication.UnicodeUTF8))

from sublistview import SubListView
from uploadlistview import UploadListView
import images_rc
