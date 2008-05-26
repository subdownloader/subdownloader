# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Tue May 27 01:06:18 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,780,593).size()).expandedTo(MainWindow.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setGeometry(QtCore.QRect(0,0,780,569))
        self.centralwidget.setObjectName("centralwidget")

        self.vboxlayout = QtGui.QVBoxLayout(self.centralwidget)


        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.tabs = QtGui.QTabWidget(self.centralwidget)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabs.sizePolicy().hasHeightForWidth())
        self.tabs.setSizePolicy(sizePolicy)
        self.tabs.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabs.setObjectName("tabs")

        self.tab = QtGui.QWidget()
        self.tab.setGeometry(QtCore.QRect(0,0,756,520))
        self.tab.setObjectName("tab")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.tab)
        self.vboxlayout2.setObjectName("vboxlayout2")

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
        self.vboxlayout2.addLayout(self.hboxlayout)

        self.splitter = QtGui.QSplitter(self.tab)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.groupBox_folderselect = QtGui.QGroupBox(self.splitter)
        self.groupBox_folderselect.setObjectName("groupBox_folderselect")

        self.vboxlayout3 = QtGui.QVBoxLayout(self.groupBox_folderselect)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.folderView = QtGui.QTreeView(self.groupBox_folderselect)
        self.folderView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.folderView.setObjectName("folderView")
        self.vboxlayout3.addWidget(self.folderView)

        self.groupBox_videosFound = QtGui.QGroupBox(self.splitter)
        self.groupBox_videosFound.setObjectName("groupBox_videosFound")

        self.hboxlayout1 = QtGui.QHBoxLayout(self.groupBox_videosFound)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.videoView = QtGui.QTreeView(self.groupBox_videosFound)
        self.videoView.setObjectName("videoView")
        self.hboxlayout1.addWidget(self.videoView)
        self.vboxlayout2.addWidget(self.splitter)
        self.tabs.addTab(self.tab,"")

        self.tab_3 = QtGui.QWidget()
        self.tab_3.setGeometry(QtCore.QRect(0,0,756,520))
        self.tab_3.setObjectName("tab_3")

        self.vboxlayout4 = QtGui.QVBoxLayout(self.tab_3)
        self.vboxlayout4.setObjectName("vboxlayout4")

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
        self.vboxlayout4.addLayout(self.hboxlayout2)

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
        self.vboxlayout4.addLayout(self.hboxlayout3)

        self.vboxlayout5 = QtGui.QVBoxLayout()
        self.vboxlayout5.setObjectName("vboxlayout5")

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
        self.vboxlayout5.addWidget(self.groupBox_4)
        self.vboxlayout4.addLayout(self.vboxlayout5)
        self.tabs.addTab(self.tab_3,"")

        self.tab_4 = QtGui.QWidget()
        self.tab_4.setGeometry(QtCore.QRect(0,0,756,520))
        self.tab_4.setObjectName("tab_4")

        self.vboxlayout6 = QtGui.QVBoxLayout(self.tab_4)
        self.vboxlayout6.setObjectName("vboxlayout6")

        self.vboxlayout7 = QtGui.QVBoxLayout()
        self.vboxlayout7.setObjectName("vboxlayout7")

        self.groupBox_2 = QtGui.QGroupBox(self.tab_4)
        self.groupBox_2.setObjectName("groupBox_2")

        self.vboxlayout8 = QtGui.QVBoxLayout(self.groupBox_2)
        self.vboxlayout8.setObjectName("vboxlayout8")

        self.vboxlayout9 = QtGui.QVBoxLayout()
        self.vboxlayout9.setObjectName("vboxlayout9")

        self.hboxlayout5 = QtGui.QHBoxLayout()
        self.hboxlayout5.setObjectName("hboxlayout5")

        self.buttonUploadBrowseFolder = QtGui.QToolButton(self.groupBox_2)
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
        self.buttonUploadPlusRow.setIconSize(QtCore.QSize(24,24))
        self.buttonUploadPlusRow.setObjectName("buttonUploadPlusRow")
        self.hboxlayout5.addWidget(self.buttonUploadPlusRow)

        self.buttonUploadMinusRow = QtGui.QToolButton(self.groupBox_2)
        self.buttonUploadMinusRow.setEnabled(False)
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
        self.buttonUploadUpRow.setIconSize(QtCore.QSize(24,24))
        self.buttonUploadUpRow.setObjectName("buttonUploadUpRow")
        self.hboxlayout5.addWidget(self.buttonUploadUpRow)

        self.buttonUploadDownRow = QtGui.QToolButton(self.groupBox_2)
        self.buttonUploadDownRow.setEnabled(False)
        self.buttonUploadDownRow.setIconSize(QtCore.QSize(24,24))
        self.buttonUploadDownRow.setObjectName("buttonUploadDownRow")
        self.hboxlayout5.addWidget(self.buttonUploadDownRow)

        spacerItem3 = QtGui.QSpacerItem(401,33,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout5.addItem(spacerItem3)

        self.buttonUpload = QtGui.QPushButton(self.groupBox_2)
        self.buttonUpload.setEnabled(True)

        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.buttonUpload.setFont(font)
        self.buttonUpload.setObjectName("buttonUpload")
        self.hboxlayout5.addWidget(self.buttonUpload)
        self.vboxlayout9.addLayout(self.hboxlayout5)

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
        self.vboxlayout9.addWidget(self.uploadView)
        self.vboxlayout8.addLayout(self.vboxlayout9)

        self.line = QtGui.QFrame(self.groupBox_2)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.vboxlayout8.addWidget(self.line)
        self.vboxlayout7.addWidget(self.groupBox_2)

        self.groupBox = QtGui.QGroupBox(self.tab_4)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Preferred)
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

        self.uploadIMDB = QtGui.QComboBox(self.groupBox)
        self.uploadIMDB.setObjectName("uploadIMDB")
        self.gridlayout.addWidget(self.uploadIMDB,0,2,1,1)

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

        self.uploadLanguages = QtGui.QComboBox(self.groupBox)
        self.uploadLanguages.setObjectName("uploadLanguages")
        self.gridlayout.addWidget(self.uploadLanguages,1,2,1,1)

        self.label_6 = QtGui.QLabel(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setObjectName("label_6")
        self.gridlayout.addWidget(self.label_6,2,1,1,1)

        self.uploadReleaseText = QtGui.QLineEdit(self.groupBox)
        self.uploadReleaseText.setObjectName("uploadReleaseText")
        self.gridlayout.addWidget(self.uploadReleaseText,2,2,1,1)

        self.label_7 = QtGui.QLabel(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setObjectName("label_7")
        self.gridlayout.addWidget(self.label_7,3,1,1,1)

        self.uploadComments = QtGui.QTextEdit(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uploadComments.sizePolicy().hasHeightForWidth())
        self.uploadComments.setSizePolicy(sizePolicy)
        self.uploadComments.setMaximumSize(QtCore.QSize(16777215,100))
        self.uploadComments.setObjectName("uploadComments")
        self.gridlayout.addWidget(self.uploadComments,3,2,1,1)
        self.vboxlayout7.addWidget(self.groupBox)
        self.vboxlayout6.addLayout(self.vboxlayout7)
        self.tabs.addTab(self.tab_4,"")

        self.tab_5 = QtGui.QWidget()
        self.tab_5.setGeometry(QtCore.QRect(0,0,756,520))
        self.tab_5.setObjectName("tab_5")

        self.frame_6 = QtGui.QFrame(self.tab_5)
        self.frame_6.setGeometry(QtCore.QRect(9,9,681,451))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy)
        self.frame_6.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_6.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")

        self.frame_4 = QtGui.QFrame(self.frame_6)
        self.frame_4.setGeometry(QtCore.QRect(430,190,241,121))
        self.frame_4.setFrameShape(QtGui.QFrame.Box)
        self.frame_4.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")

        self.label_22 = QtGui.QLabel(self.frame_4)
        self.label_22.setGeometry(QtCore.QRect(10,10,111,18))

        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_22.setFont(font)
        self.label_22.setObjectName("label_22")

        self.optionProxyHost = QtGui.QLineEdit(self.frame_4)
        self.optionProxyHost.setGeometry(QtCore.QRect(80,30,151,23))
        self.optionProxyHost.setObjectName("optionProxyHost")

        self.label_14 = QtGui.QLabel(self.frame_4)
        self.label_14.setGeometry(QtCore.QRect(21,58,44,22))
        self.label_14.setObjectName("label_14")

        self.label_13 = QtGui.QLabel(self.frame_4)
        self.label_13.setGeometry(QtCore.QRect(21,31,44,22))
        self.label_13.setObjectName("label_13")

        self.optionProxyPort = QtGui.QSpinBox(self.frame_4)
        self.optionProxyPort.setGeometry(QtCore.QRect(80,60,71,25))
        self.optionProxyPort.setMaximum(99999)
        self.optionProxyPort.setProperty("value",QtCore.QVariant(8080))
        self.optionProxyPort.setObjectName("optionProxyPort")

        self.frame_3 = QtGui.QFrame(self.frame_6)
        self.frame_3.setGeometry(QtCore.QRect(0,320,671,121))
        self.frame_3.setFrameShape(QtGui.QFrame.Box)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")

        self.label_15 = QtGui.QLabel(self.frame_3)
        self.label_15.setGeometry(QtCore.QRect(21,21,122,29))
        self.label_15.setObjectName("label_15")

        self.optionVideoAppCombo = QtGui.QComboBox(self.frame_3)
        self.optionVideoAppCombo.setGeometry(QtCore.QRect(148,24,122,22))
        self.optionVideoAppCombo.setObjectName("optionVideoAppCombo")

        self.label_18 = QtGui.QLabel(self.frame_3)
        self.label_18.setGeometry(QtCore.QRect(390,80,260,18))
        self.label_18.setObjectName("label_18")

        self.optionVideoAppChooseLocation = QtGui.QPushButton(self.frame_3)
        self.optionVideoAppChooseLocation.setGeometry(QtCore.QRect(390,50,83,27))
        self.optionVideoAppChooseLocation.setObjectName("optionVideoAppChooseLocation")

        self.label_21 = QtGui.QLabel(self.frame_3)
        self.label_21.setGeometry(QtCore.QRect(10,0,301,18))

        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_21.setFont(font)
        self.label_21.setObjectName("label_21")

        self.label_17 = QtGui.QLabel(self.frame_3)
        self.label_17.setGeometry(QtCore.QRect(21,81,76,23))
        self.label_17.setObjectName("label_17")

        self.label_16 = QtGui.QLabel(self.frame_3)
        self.label_16.setGeometry(QtCore.QRect(21,51,76,23))
        self.label_16.setObjectName("label_16")

        self.optionVideoAppLocation = QtGui.QLineEdit(self.frame_3)
        self.optionVideoAppLocation.setGeometry(QtCore.QRect(102,51,278,23))
        self.optionVideoAppLocation.setObjectName("optionVideoAppLocation")

        self.optionVideoAppParams = QtGui.QLineEdit(self.frame_3)
        self.optionVideoAppParams.setGeometry(QtCore.QRect(102,81,278,23))
        self.optionVideoAppParams.setObjectName("optionVideoAppParams")

        self.frame_2 = QtGui.QFrame(self.frame_6)
        self.frame_2.setGeometry(QtCore.QRect(0,0,411,221))
        self.frame_2.setFrameShape(QtGui.QFrame.Box)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")

        self.label_20 = QtGui.QLabel(self.frame_2)
        self.label_20.setGeometry(QtCore.QRect(10,0,142,18))

        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_20.setFont(font)
        self.label_20.setObjectName("label_20")

        self.optionPredefinedFolderText = QtGui.QLineEdit(self.frame_2)
        self.optionPredefinedFolderText.setGeometry(QtCore.QRect(160,90,161,23))
        self.optionPredefinedFolderText.setReadOnly(True)
        self.optionPredefinedFolderText.setObjectName("optionPredefinedFolderText")

        self.label_25 = QtGui.QLabel(self.frame_2)
        self.label_25.setGeometry(QtCore.QRect(10,140,161,27))
        self.label_25.setObjectName("label_25")

        self.layoutWidget = QtGui.QWidget(self.frame_2)
        self.layoutWidget.setGeometry(QtCore.QRect(10,158,291,61))
        self.layoutWidget.setObjectName("layoutWidget")

        self.vboxlayout10 = QtGui.QVBoxLayout(self.layoutWidget)
        self.vboxlayout10.setObjectName("vboxlayout10")

        self.optionDownloadSameFilename = QtGui.QRadioButton(self.layoutWidget)
        self.optionDownloadSameFilename.setChecked(True)
        self.optionDownloadSameFilename.setObjectName("optionDownloadSameFilename")
        self.vboxlayout10.addWidget(self.optionDownloadSameFilename)

        self.optionDownloadOnlineSubName = QtGui.QRadioButton(self.layoutWidget)
        self.optionDownloadOnlineSubName.setObjectName("optionDownloadOnlineSubName")
        self.vboxlayout10.addWidget(self.optionDownloadOnlineSubName)

        self.optionButtonChooseFolder = QtGui.QPushButton(self.frame_2)
        self.optionButtonChooseFolder.setGeometry(QtCore.QRect(330,90,75,27))
        self.optionButtonChooseFolder.setObjectName("optionButtonChooseFolder")

        self.line_5 = QtGui.QFrame(self.frame_2)
        self.line_5.setGeometry(QtCore.QRect(10,130,391,16))
        self.line_5.setFrameShape(QtGui.QFrame.HLine)
        self.line_5.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_5.setObjectName("line_5")

        self.label_26 = QtGui.QLabel(self.frame_2)
        self.label_26.setGeometry(QtCore.QRect(10,20,161,27))
        self.label_26.setObjectName("label_26")

        self.layoutWidget1 = QtGui.QWidget(self.frame_2)
        self.layoutWidget1.setGeometry(QtCore.QRect(11,35,211,86))
        self.layoutWidget1.setObjectName("layoutWidget1")

        self.vboxlayout11 = QtGui.QVBoxLayout(self.layoutWidget1)
        self.vboxlayout11.setObjectName("vboxlayout11")

        self.optionDownloadFolderAsk = QtGui.QRadioButton(self.layoutWidget1)
        self.optionDownloadFolderAsk.setObjectName("optionDownloadFolderAsk")
        self.vboxlayout11.addWidget(self.optionDownloadFolderAsk)

        self.optionDownloadFolderSame = QtGui.QRadioButton(self.layoutWidget1)
        self.optionDownloadFolderSame.setChecked(True)
        self.optionDownloadFolderSame.setObjectName("optionDownloadFolderSame")
        self.vboxlayout11.addWidget(self.optionDownloadFolderSame)

        self.optionDownloadFolderPredefined = QtGui.QRadioButton(self.layoutWidget1)
        self.optionDownloadFolderPredefined.setObjectName("optionDownloadFolderPredefined")
        self.vboxlayout11.addWidget(self.optionDownloadFolderPredefined)

        self.frame = QtGui.QFrame(self.frame_6)
        self.frame.setGeometry(QtCore.QRect(0,230,411,81))
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setLineWidth(1)
        self.frame.setObjectName("frame")

        self.label_19 = QtGui.QLabel(self.frame)
        self.label_19.setGeometry(QtCore.QRect(10,0,142,18))

        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_19.setFont(font)
        self.label_19.setObjectName("label_19")

        self.optionIntegrationExplorer = QtGui.QCheckBox(self.frame)
        self.optionIntegrationExplorer.setGeometry(QtCore.QRect(10,50,311,22))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.optionIntegrationExplorer.sizePolicy().hasHeightForWidth())
        self.optionIntegrationExplorer.setSizePolicy(sizePolicy)
        self.optionIntegrationExplorer.setMinimumSize(QtCore.QSize(0,22))
        self.optionIntegrationExplorer.setObjectName("optionIntegrationExplorer")

        self.optionInterfaceLanguage = QtGui.QComboBox(self.frame)
        self.optionInterfaceLanguage.setGeometry(QtCore.QRect(193,24,177,22))
        self.optionInterfaceLanguage.setObjectName("optionInterfaceLanguage")

        self.label_24 = QtGui.QLabel(self.frame)
        self.label_24.setGeometry(QtCore.QRect(11,21,177,29))

        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.label_24.setFont(font)
        self.label_24.setObjectName("label_24")

        self.frame_7 = QtGui.QFrame(self.frame_6)
        self.frame_7.setGeometry(QtCore.QRect(430,0,241,181))
        self.frame_7.setFrameShape(QtGui.QFrame.Box)
        self.frame_7.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")

        self.label_27 = QtGui.QLabel(self.frame_7)
        self.label_27.setGeometry(QtCore.QRect(10,0,142,18))

        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_27.setFont(font)
        self.label_27.setObjectName("label_27")

        self.label_28 = QtGui.QLabel(self.frame_7)
        self.label_28.setGeometry(QtCore.QRect(10,20,191,27))
        self.label_28.setObjectName("label_28")

        self.optionDefaultUploadLanguage = QtGui.QComboBox(self.frame_7)
        self.optionDefaultUploadLanguage.setGeometry(QtCore.QRect(50,50,177,22))
        self.optionDefaultUploadLanguage.setObjectName("optionDefaultUploadLanguage")

        self.frame_5 = QtGui.QFrame(self.frame_7)
        self.frame_5.setGeometry(QtCore.QRect(0,80,241,91))
        self.frame_5.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_5.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")

        self.label_38 = QtGui.QLabel(self.frame_5)
        self.label_38.setGeometry(QtCore.QRect(10,10,231,18))

        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.label_38.setFont(font)
        self.label_38.setObjectName("label_38")

        self.optionLoginUsername = QtGui.QLineEdit(self.frame_5)
        self.optionLoginUsername.setGeometry(QtCore.QRect(104,31,110,23))
        self.optionLoginUsername.setObjectName("optionLoginUsername")

        self.optionLoginPassword = QtGui.QLineEdit(self.frame_5)
        self.optionLoginPassword.setGeometry(QtCore.QRect(104,61,110,23))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.optionLoginPassword.sizePolicy().hasHeightForWidth())
        self.optionLoginPassword.setSizePolicy(sizePolicy)
        self.optionLoginPassword.setObjectName("optionLoginPassword")

        self.label_39 = QtGui.QLabel(self.frame_5)
        self.label_39.setGeometry(QtCore.QRect(31,31,68,23))
        self.label_39.setObjectName("label_39")

        self.label_40 = QtGui.QLabel(self.frame_5)
        self.label_40.setGeometry(QtCore.QRect(31,61,68,23))
        self.label_40.setObjectName("label_40")

        self.layoutWidget2 = QtGui.QWidget(self.tab_5)
        self.layoutWidget2.setGeometry(QtCore.QRect(10,470,735,41))
        self.layoutWidget2.setObjectName("layoutWidget2")

        self.hboxlayout6 = QtGui.QHBoxLayout(self.layoutWidget2)
        self.hboxlayout6.setObjectName("hboxlayout6")

        spacerItem4 = QtGui.QSpacerItem(620,28,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout6.addItem(spacerItem4)

        self.optionsButtonApplyChanges = QtGui.QPushButton(self.layoutWidget2)
        self.optionsButtonApplyChanges.setObjectName("optionsButtonApplyChanges")
        self.hboxlayout6.addWidget(self.optionsButtonApplyChanges)
        self.tabs.addTab(self.tab_5,"")

        self.tab_2 = QtGui.QWidget()
        self.tab_2.setGeometry(QtCore.QRect(0,0,756,520))
        self.tab_2.setObjectName("tab_2")

        self.layoutWidget3 = QtGui.QWidget(self.tab_2)
        self.layoutWidget3.setGeometry(QtCore.QRect(40,130,643,73))
        self.layoutWidget3.setObjectName("layoutWidget3")

        self.vboxlayout12 = QtGui.QVBoxLayout(self.layoutWidget3)
        self.vboxlayout12.setObjectName("vboxlayout12")

        self.label_2 = QtGui.QLabel(self.layoutWidget3)

        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setWordWrap(True)
        self.label_2.setIndent(1)
        self.label_2.setObjectName("label_2")
        self.vboxlayout12.addWidget(self.label_2)

        self.line_4 = QtGui.QFrame(self.layoutWidget3)
        self.line_4.setFrameShape(QtGui.QFrame.HLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.vboxlayout12.addWidget(self.line_4)

        self.hboxlayout7 = QtGui.QHBoxLayout()
        self.hboxlayout7.setObjectName("hboxlayout7")

        self.label_11 = QtGui.QLabel(self.layoutWidget3)
        self.label_11.setObjectName("label_11")
        self.hboxlayout7.addWidget(self.label_11)

        self.label_12 = QtGui.QLabel(self.layoutWidget3)

        font = QtGui.QFont()
        font.setWeight(75)
        font.setUnderline(True)
        font.setStrikeOut(False)
        font.setBold(True)
        self.label_12.setFont(font)
        self.label_12.setCursor(QtCore.Qt.PointingHandCursor)
        self.label_12.setAutoFillBackground(False)
        self.label_12.setTextFormat(QtCore.Qt.PlainText)
        self.label_12.setScaledContents(False)
        self.label_12.setOpenExternalLinks(True)
        self.label_12.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.label_12.setObjectName("label_12")
        self.hboxlayout7.addWidget(self.label_12)
        self.vboxlayout12.addLayout(self.hboxlayout7)
        self.tabs.addTab(self.tab_2,"")
        self.vboxlayout1.addWidget(self.tabs)
        self.vboxlayout.addLayout(self.vboxlayout1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setGeometry(QtCore.QRect(0,569,780,24))
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "SubDownloader", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonPlay.setText(QtGui.QApplication.translate("MainWindow", "Play", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonDownload.setText(QtGui.QApplication.translate("MainWindow", "Download", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonIMDB.setText(QtGui.QApplication.translate("MainWindow", "Movie Info", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("MainWindow", "Show :", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_folderselect.setTitle(QtGui.QApplication.translate("MainWindow", "Select Folder:", None, QtGui.QApplication.UnicodeUTF8))
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
        self.uploadIMDB.addItem(QtGui.QApplication.translate("MainWindow", "Click on FIND button to choose the IMDB link", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonUploadFindIMDB.setText(QtGui.QApplication.translate("MainWindow", "Find", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("MainWindow", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; color:#ff0000;\">*</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("MainWindow", "Language:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("MainWindow", "Release:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("MainWindow", "Comments:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_4), QtGui.QApplication.translate("MainWindow", "Upload subtitles", None, QtGui.QApplication.UnicodeUTF8))
        self.label_22.setText(QtGui.QApplication.translate("MainWindow", "Network Proxy", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setText(QtGui.QApplication.translate("MainWindow", "Port:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setText(QtGui.QApplication.translate("MainWindow", "Host:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setText(QtGui.QApplication.translate("MainWindow", "Video application:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_18.setText(QtGui.QApplication.translate("MainWindow", "{0} = video file path; {1} = subtitle path", None, QtGui.QApplication.UnicodeUTF8))
        self.optionVideoAppChooseLocation.setText(QtGui.QApplication.translate("MainWindow", "Choose...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_21.setText(QtGui.QApplication.translate("MainWindow", "External application for video playback", None, QtGui.QApplication.UnicodeUTF8))
        self.label_17.setText(QtGui.QApplication.translate("MainWindow", "Parameters:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_16.setText(QtGui.QApplication.translate("MainWindow", "Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_20.setText(QtGui.QApplication.translate("MainWindow", "Downloads", None, QtGui.QApplication.UnicodeUTF8))
        self.label_25.setText(QtGui.QApplication.translate("MainWindow", "Filename of the Subtitle:", None, QtGui.QApplication.UnicodeUTF8))
        self.optionDownloadSameFilename.setText(QtGui.QApplication.translate("MainWindow", "Same name as video file", None, QtGui.QApplication.UnicodeUTF8))
        self.optionDownloadOnlineSubName.setText(QtGui.QApplication.translate("MainWindow", "Same name as the online subtitle", None, QtGui.QApplication.UnicodeUTF8))
        self.optionButtonChooseFolder.setText(QtGui.QApplication.translate("MainWindow", "Choose...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_26.setText(QtGui.QApplication.translate("MainWindow", "Destination folder:", None, QtGui.QApplication.UnicodeUTF8))
        self.optionDownloadFolderAsk.setText(QtGui.QApplication.translate("MainWindow", "Always ask user", None, QtGui.QApplication.UnicodeUTF8))
        self.optionDownloadFolderSame.setText(QtGui.QApplication.translate("MainWindow", "Same folder as video file", None, QtGui.QApplication.UnicodeUTF8))
        self.optionDownloadFolderPredefined.setText(QtGui.QApplication.translate("MainWindow", "Predefined folder:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_19.setText(QtGui.QApplication.translate("MainWindow", "Others", None, QtGui.QApplication.UnicodeUTF8))
        self.optionIntegrationExplorer.setText(QtGui.QApplication.translate("MainWindow", "Enable Context Menu in Windows Explorer", None, QtGui.QApplication.UnicodeUTF8))
        self.label_24.setText(QtGui.QApplication.translate("MainWindow", "Interface Language:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_27.setText(QtGui.QApplication.translate("MainWindow", "Uploads", None, QtGui.QApplication.UnicodeUTF8))
        self.label_28.setText(QtGui.QApplication.translate("MainWindow", "Default language of subtitles", None, QtGui.QApplication.UnicodeUTF8))
        self.label_38.setText(QtGui.QApplication.translate("MainWindow", "Upload files as OpenSubtitles user:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_39.setText(QtGui.QApplication.translate("MainWindow", "Username:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_40.setText(QtGui.QApplication.translate("MainWindow", "Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.optionsButtonApplyChanges.setText(QtGui.QApplication.translate("MainWindow", "Apply Changes", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_5), QtGui.QApplication.translate("MainWindow", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "If you would have contact us about bugs or just want to tip us on how to improve our work, choose how to do so.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("MainWindow", "Bugs, issues and suggestions:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("MainWindow", "http://code.google.com/p/subdownloader/issues/list", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_2), QtGui.QApplication.translate("MainWindow", "Contacts", None, QtGui.QApplication.UnicodeUTF8))

from sublistview import SubListView
from uploadlistview import UploadListView
import images_rc
