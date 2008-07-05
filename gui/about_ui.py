# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created: Sat Jul  5 01:49:15 2008
#      by: PyQt4 UI code generator 4.4.3-snapshot-20080627
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.setWindowModality(QtCore.Qt.WindowModal)
        AboutDialog.resize(400, 400)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        AboutDialog.setMinimumSize(QtCore.QSize(400, 400))
        AboutDialog.setMaximumSize(QtCore.QSize(400, 600))
        AboutDialog.setAutoFillBackground(False)
        self.vboxlayout = QtGui.QVBoxLayout(AboutDialog)

        spacerItem = QtGui.QSpacerItem(20, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.vboxlayout.addItem(spacerItem)
