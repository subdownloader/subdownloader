# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'expiration.ui'
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

class Ui_ExpirationDialog(object):
    def setupUi(self, ExpirationDialog):
        ExpirationDialog.setObjectName(_fromUtf8("ExpirationDialog"))
        ExpirationDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ExpirationDialog.resize(483, 295)
        ExpirationDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(ExpirationDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_expiration = QtGui.QLabel(ExpirationDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_expiration.setFont(font)
        self.label_expiration.setObjectName(_fromUtf8("label_expiration"))
        self.verticalLayout.addWidget(self.label_expiration)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.buttonRegister = QtGui.QPushButton(ExpirationDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.buttonRegister.setFont(font)
        self.buttonRegister.setObjectName(_fromUtf8("buttonRegister"))
        self.horizontalLayout_2.addWidget(self.buttonRegister)
        spacerItem = QtGui.QSpacerItem(188, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.label_5 = QtGui.QLabel(ExpirationDialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout.addWidget(self.label_5)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ExpirationDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.activation_email = QtGui.QLineEdit(ExpirationDialog)
        self.activation_email.setObjectName(_fromUtf8("activation_email"))
        self.gridLayout.addWidget(self.activation_email, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(ExpirationDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.activation_fullname = QtGui.QLineEdit(ExpirationDialog)
        self.activation_fullname.setObjectName(_fromUtf8("activation_fullname"))
        self.gridLayout.addWidget(self.activation_fullname, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(ExpirationDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.activation_licensekey = QtGui.QLineEdit(ExpirationDialog)
        self.activation_licensekey.setObjectName(_fromUtf8("activation_licensekey"))
        self.gridLayout.addWidget(self.activation_licensekey, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(238, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonCancel = QtGui.QPushButton(ExpirationDialog)
        self.buttonCancel.setObjectName(_fromUtf8("buttonCancel"))
        self.horizontalLayout.addWidget(self.buttonCancel)
        self.buttonActivate = QtGui.QPushButton(ExpirationDialog)
        self.buttonActivate.setObjectName(_fromUtf8("buttonActivate"))
        self.horizontalLayout.addWidget(self.buttonActivate)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ExpirationDialog)
        QtCore.QMetaObject.connectSlotsByName(ExpirationDialog)

    def retranslateUi(self, ExpirationDialog):
        ExpirationDialog.setWindowTitle(_translate("ExpirationDialog", "Program has expired", None))
        self.label_expiration.setText(_translate("ExpirationDialog", "The program has expired after %d days of usage.", None))
        self.buttonRegister.setText(_translate("ExpirationDialog", "Register Online...", None))
        self.label_5.setText(_translate("ExpirationDialog", "After registering, you will receive a license key via email.", None))
        self.label.setText(_translate("ExpirationDialog", "Email:", None))
        self.label_2.setText(_translate("ExpirationDialog", "Full Name:", None))
        self.label_3.setText(_translate("ExpirationDialog", "License key:", None))
        self.buttonCancel.setText(_translate("ExpirationDialog", "Cancel", None))
        self.buttonActivate.setText(_translate("ExpirationDialog", "Activate", None))


class ExpirationDialog(QtGui.QDialog, Ui_ExpirationDialog):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QDialog.__init__(self, parent, f)

        self.setupUi(self)

