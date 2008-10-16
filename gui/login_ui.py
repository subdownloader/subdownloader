# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created: Thu Oct 16 17:25:32 2008
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
        LoginDialog.setWindowModality(QtCore.Qt.WindowModal)
        LoginDialog.resize(290, 193)
        self.verticalLayout = QtGui.QVBoxLayout(LoginDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtGui.QGroupBox(LoginDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_57 = QtGui.QLabel(self.groupBox)
        self.label_57.setObjectName("label_57")
        self.gridLayout.addWidget(self.label_57, 0, 0, 1, 1)
        self.optionLoginUsername = QtGui.QLineEdit(self.groupBox)
        self.optionLoginUsername.setObjectName("optionLoginUsername")
        self.gridLayout.addWidget(self.optionLoginUsername, 0, 1, 1, 1)
        self.label_58 = QtGui.QLabel(self.groupBox)
        self.label_58.setObjectName("label_58")
        self.gridLayout.addWidget(self.label_58, 1, 0, 1, 1)
        self.optionLoginPassword = QtGui.QLineEdit(self.groupBox)
        self.optionLoginPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.optionLoginPassword.setObjectName("optionLoginPassword")
        self.gridLayout.addWidget(self.optionLoginPassword, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.loginLabelStatus = QtGui.QLabel(LoginDialog)
        self.loginLabelStatus.setObjectName("loginLabelStatus")
        self.horizontalLayout.addWidget(self.loginLabelStatus)
        self.loginConnectButton = QtGui.QPushButton(LoginDialog)
        self.loginConnectButton.setMaximumSize(QtCore.QSize(70, 16777215))
        self.loginConnectButton.setObjectName("loginConnectButton")
        self.horizontalLayout.addWidget(self.loginConnectButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(LoginDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LoginDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), LoginDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), LoginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        LoginDialog.setWindowTitle(_("Login:"))
        self.groupBox.setTitle(_("Login into OpenSubtitles.org"))
        self.label_57.setText(_("Username:"))
        self.label_58.setText(_("Password:"))
        self.loginLabelStatus.setText(_("Currently logged as :"))
        self.loginConnectButton.setText(_("Connect"))


