#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) 2007-2009 Ivan Garcia capiscuas@gmail.com
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    see <http://www.gnu.org/licenses/>.

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QVariant, QSize, QEventLoop, QString, \
                         QBuffer, QIODevice, QModelIndex,QDir
from PyQt4.QtGui import QPixmap, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel, QItemSelectionModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical

from gui.login_ui import Ui_LoginDialog
import webbrowser
import time, thread
import logging
log = logging.getLogger("subdownloader.gui.login")

class loginDialog(QtGui.QDialog): 
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)
        self._main  = parent
        settings = QSettings()

        QObject.connect(self.ui.loginConnectButton, SIGNAL("clicked(bool)"), self.onButtonConnect)
        QObject.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.onButtonAccept)
        QObject.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.onButtonClose)
        username = settings.value("options/LoginUsername", QVariant()).toString()
        password = settings.value("options/LoginPassword", QVariant()).toString()
        self.ui.optionLoginUsername.setText(username)
        self.ui.optionLoginPassword.setText(password)
        
        if not username: 
            username = _('Anonymous')
            
        if hasattr(self._main, 'OSDBServer') and self._main.OSDBServer.is_connected():
            self.ui.loginLabelStatus.setText(_("Succesfully logged as: %s") % username)
        else:
            self.ui.loginLabelStatus.setText(_("Not Connected"))

    def onButtonClose(self):
        self.reject()
        
    def onButtonAccept(self):
        settings = QSettings()
        newUsername =  self.ui.optionLoginUsername.text()
        newPassword = self.ui.optionLoginPassword.text()
        oldUsername = settings.value("options/LoginUsername", QVariant())
        oldPassword = settings.value("options/LoginPassword", QVariant())
        if newUsername != oldUsername.toString() or newPassword != oldPassword.toString():
            settings.setValue("options/LoginUsername",QVariant(newUsername))
            settings.setValue("options/LoginPassword", QVariant(newPassword))
            log.debug('Login credentials has changed. Trying to login.')
            self.connect()
        self.accept() #We close the window
        
    def onButtonConnect(self):
        self.connect()
        
    def connect(self):
        username =  self.ui.optionLoginUsername.text()
        password = self.ui.optionLoginPassword.text()
        
        self._main.window.setCursor(Qt.WaitCursor)
        if not hasattr(self, 'OSDBServer'):
            if not self._main.establishServerConnection():# and self.OSDBServer.is_connected():
                self._main.window.setCursor(Qt.ArrowCursor)
                QMessageBox.about(self._main.window,_("Error"),_("Error contacting the server. Please try again later"))
                return
        
        if not username: 
            displayUsername = _('Anonymous')
        else:
            displayUsername = username
                
        if self._main.login_user(str(username.toUtf8()),str(password.toUtf8()),self._main.window):
            self.ui.loginLabelStatus.setText(_("Successfully logged as: %s") % displayUsername)
        else:
            self.ui.loginLabelStatus.setText(_("Cannot loggin as: %s") % displayUsername)
        self._main.window.setCursor(Qt.ArrowCursor)
        QCoreApplication.processEvents()

