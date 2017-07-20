# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/maarten/programming/subdownloader_old/scripts/gui/ui/login.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
        LoginDialog.setWindowModality(QtCore.Qt.WindowModal)
        LoginDialog.resize(290, 182)
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
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.textUsername = QtWidgets.QLabel(self.groupBox)
        self.textUsername.setObjectName("textUsername")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.textUsername)
        self.optionLoginUsername = QtWidgets.QLineEdit(self.groupBox)
        self.optionLoginUsername.setObjectName("optionLoginUsername")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.optionLoginUsername)
        self.textPassword = QtWidgets.QLabel(self.groupBox)
        self.textPassword.setObjectName("textPassword")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.textPassword)
        self.optionLoginPassword = QtWidgets.QLineEdit(self.groupBox)
        self.optionLoginPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.optionLoginPassword.setObjectName("optionLoginPassword")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.optionLoginPassword)
        self.verticalLayout_2.addLayout(self.formLayout_2)
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
        LoginDialog.setWindowTitle(_("Authentication"))
        self.groupBox.setTitle(_("Login into OpenSubtitles.org"))
        self.textUsername.setText(_("Username:"))
        self.textPassword.setText(_("Password:"))

