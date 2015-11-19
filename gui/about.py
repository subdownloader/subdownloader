#!/usr/bin/env python
# Copyright (c) 2010 SubDownloader Developers - See COPYING - GPLv3

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QVariant, QSize, QEventLoop, QString, \
                         QBuffer, QIODevice, QModelIndex,QDir
from PyQt4.QtGui import QPixmap, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel, QItemSelectionModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical

from gui.about_ui import Ui_AboutDialog
import logging
log = logging.getLogger("subdownloader.gui.about")

class aboutDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self._main  = parent
        settings = QSettings()
        QObject.connect(self.ui.buttonClose, SIGNAL("clicked(bool)"), self.onButtonClose)

    def onButtonClose(self):
        self.reject()

