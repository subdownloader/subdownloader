#!/usr/bin/env python
# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
    QSettings, QSize, QEventLoop, \
    QBuffer, QIODevice, QModelIndex, QDir
from PyQt4.QtGui import QPixmap, QErrorMessage, QLineEdit, \
    QMessageBox, QFileDialog, QIcon, QDialog, \
    QInputDialog, QDirModel, QItemSelectionModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical

from .main import toString

from gui.login_ui import Ui_LoginDialog
import logging
log = logging.getLogger("subdownloader.gui.login")


class loginDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)
        self._main = parent
        settings = QSettings()

        QObject.connect(
            self.ui.buttonBox, SIGNAL("accepted()"), self.onButtonAccept)
        QObject.connect(
            self.ui.buttonBox, SIGNAL("rejected()"), self.onButtonClose)
        username = toString(settings.value("options/LoginUsername", ""))
        password = toString(settings.value("options/LoginPassword", ""))
        self.ui.optionLoginUsername.setText(username)
        self.ui.optionLoginPassword.setText(password)

    def onButtonClose(self):
        self.reject()

    def onButtonAccept(self):
        settings = QSettings()
        newUsername = self.ui.optionLoginUsername.text()
        newPassword = self.ui.optionLoginPassword.text()
        oldUsername = toString(settings.value("options/LoginUsername", ""))
        oldPassword = toString(settings.value("options/LoginPassword", ""))

        if newUsername != oldUsername or newPassword != oldPassword:
            settings.setValue("options/LoginUsername", newUsername)
            settings.setValue("options/LoginPassword", newPassword)

        self.connect()
        self.accept()  # We close the window

    def connect(self):
        username = self.ui.optionLoginUsername.text()
        password = self.ui.optionLoginPassword.text()

        self._main.window.setCursor(Qt.WaitCursor)
        if not hasattr(self, 'OSDBServer'):
            # and self.OSDBServer.is_connected():
            if not self._main.establishServerConnection():
                self._main.window.setCursor(Qt.ArrowCursor)
                QMessageBox.about(self._main.window, _("Error"), _(
                    "Error contacting the server. Please try again later"))
                return

        self._main.login_user(
            str(username.toUtf8()), str(password.toUtf8()), self._main.window)
        self._main.window.setCursor(Qt.ArrowCursor)
        QCoreApplication.processEvents()
