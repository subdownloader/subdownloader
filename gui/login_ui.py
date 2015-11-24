# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
        LoginDialog.setWindowModality(QtCore.Qt.WindowModal)
        LoginDialog.resize(290, 154)
        self.verticalLayout = QtWidgets.QVBoxLayout(LoginDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(LoginDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_57 = QtWidgets.QLabel(self.groupBox)
        self.label_57.setObjectName("label_57")
        self.gridLayout.addWidget(self.label_57, 0, 0, 1, 1)
        self.optionLoginUsername = QtWidgets.QLineEdit(self.groupBox)
        self.optionLoginUsername.setObjectName("optionLoginUsername")
        self.gridLayout.addWidget(self.optionLoginUsername, 0, 1, 1, 1)
        self.label_58 = QtWidgets.QLabel(self.groupBox)
        self.label_58.setObjectName("label_58")
        self.gridLayout.addWidget(self.label_58, 1, 0, 1, 1)
        self.optionLoginPassword = QtWidgets.QLineEdit(self.groupBox)
        self.optionLoginPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.optionLoginPassword.setObjectName("optionLoginPassword")
        self.gridLayout.addWidget(self.optionLoginPassword, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(LoginDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LoginDialog)
        self.buttonBox.accepted.connect(LoginDialog.accept)
        self.buttonBox.rejected.connect(LoginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        _translate = QtCore.QCoreApplication.translate
        LoginDialog.setWindowTitle(_translate("LoginDialog", "Authentication"))
        self.groupBox.setTitle(_translate("LoginDialog", "Login into OpenSubtitles.org"))
        self.label_57.setText(_translate("LoginDialog", "Username:"))
        self.label_58.setText(_translate("LoginDialog", "Password:"))

