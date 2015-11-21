# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName(_fromUtf8("LoginDialog"))
        LoginDialog.setWindowModality(QtCore.Qt.WindowModal)
        LoginDialog.resize(290, 154)
        self.verticalLayout = QtGui.QVBoxLayout(LoginDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(LoginDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_57 = QtGui.QLabel(self.groupBox)
        self.label_57.setObjectName(_fromUtf8("label_57"))
        self.gridLayout.addWidget(self.label_57, 0, 0, 1, 1)
        self.optionLoginUsername = QtGui.QLineEdit(self.groupBox)
        self.optionLoginUsername.setObjectName(_fromUtf8("optionLoginUsername"))
        self.gridLayout.addWidget(self.optionLoginUsername, 0, 1, 1, 1)
        self.label_58 = QtGui.QLabel(self.groupBox)
        self.label_58.setObjectName(_fromUtf8("label_58"))
        self.gridLayout.addWidget(self.label_58, 1, 0, 1, 1)
        self.optionLoginPassword = QtGui.QLineEdit(self.groupBox)
        self.optionLoginPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.optionLoginPassword.setObjectName(_fromUtf8("optionLoginPassword"))
        self.gridLayout.addWidget(self.optionLoginPassword, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(LoginDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LoginDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LoginDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LoginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        LoginDialog.setWindowTitle(_translate("LoginDialog", "Authentication", None))
        self.groupBox.setTitle(_translate("LoginDialog", "Login into OpenSubtitles.org", None))
        self.label_57.setText(_translate("LoginDialog", "Username:", None))
        self.label_58.setText(_translate("LoginDialog", "Password:", None))


class LoginDialog(QtGui.QDialog, Ui_LoginDialog):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QDialog.__init__(self, parent, f)

        self.setupUi(self)

