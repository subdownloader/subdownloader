# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QSettings
from PyQt5.QtWidgets import QDialog, QMessageBox

from subdownloader.client.gui.callback import ProgressCallbackWidget
from subdownloader.client.gui.login_ui import Ui_LoginDialog

log = logging.getLogger('subdownloader.client.gui.login')


class LoginDialog(QDialog):

    login_password_changed = pyqtSignal(str, str)

    DEFAULT_USERNAME = ''
    DEFAULT_PASSWORD = ''

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)

        self._username = self.DEFAULT_USERNAME
        self._password = self.DEFAULT_PASSWORD

        self.settings = QSettings()

        self.ui.buttonBox.accepted.connect(self.onButtonAccept)
        self.ui.buttonBox.rejected.connect(self.onButtonClose)

    def readSettings(self):
        self._username = self.settings.value('options/LoginUsername', self.DEFAULT_USERNAME)
        self.ui.optionLoginUsername.setText(self._username)

        self._password = self.settings.value('options/LoginPassword', self.DEFAULT_PASSWORD)
        self.ui.optionLoginPassword.setText(self._password)


    @pyqtSlot()
    def onButtonClose(self):
        self.reject()

    @pyqtSlot()
    def onButtonAccept(self):
        self._username= self.ui.optionLoginUsername.text()
        self._password = self.ui.optionLoginPassword.text()
        oldUsername = self.settings.value('options/LoginUsername', self.DEFAULT_USERNAME)
        oldPassword = self.settings.value('options/LoginPassword', self.DEFAULT_PASSWORD)

        if self._username != oldUsername or self._password != oldPassword:
            self.settings.setValue('options/LoginUsername', self._username)
            self.settings.setValue('options/LoginPassword', self._password)
            self.login_password_changed.emit(self._username, self._password)

        self.connect()
        self.accept()  # We close the window

    def connect(self):
        if not self.parent().get_state().connected():
            callback = ProgressCallbackWidget(self)
            callback.set_block(True)

            connected = self.parent().get_state().connect(callback)

            if not connected:
                QMessageBox.about(self, _('Error'), _(
                    'Error contacting the server. Please try again later'))
                return

        callback = ProgressCallbackWidget(self)
        callback.set_block(True)
        self.parent().get_state().login_user(self._username, self._password, callback)
        QCoreApplication.processEvents()
