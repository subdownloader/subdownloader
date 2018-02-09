# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QSettings
from PyQt5.QtWidgets import QDialog, QMessageBox

from subdownloader.client.gui.callback import ProgressCallbackWidget
from subdownloader.client.gui.generated.login_ui import Ui_LoginDialog

log = logging.getLogger('subdownloader.client.gui.login')


class LoginDialog(QDialog):

    login_password_changed = pyqtSignal(str, str)

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)

        # FIXME: no parent.get_state()
        self._username = parent.get_state().DEFAULT_USERNAME
        self._password = parent.get_state().DEFAULT_USERNAME

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
        pass

    @pyqtSlot()
    def onButtonAccept(self):
        self._username = self.ui.optionLoginUsername.text()
        self._password = self.ui.optionLoginPassword.text()
        oldUsername = self.settings.value('options/LoginUsername', self.parent().get_state().DEFAULT_USERNAME)
        oldPassword = self.settings.value('options/LoginPassword', self.parent().get_state().DEFAULT_PASSWORD)

        if self._username != oldUsername or self._password != oldPassword:
            self.settings.setValue('options/LoginUsername', self._username)
            self.settings.setValue('options/LoginPassword', self._password)
            self.login_password_changed.emit(self._username, self._password)

        login_parent_state(self.parent(), self.parent().get_state())


def login_parent_state(parent, state):
    if not state.connected():
        callback = ProgressCallbackWidget(parent)
        callback.set_block(True)

        connected = state.connect_server(callback=callback)

        if not connected:
            QMessageBox.about(parent, _('Error'), _(
                'Error contacting the server. Please try again later.'))
            callback.cancel()
            return False
        callback.finish()

    callback = ProgressCallbackWidget(parent)
    callback.set_block(True)

    logged_in = state.login_user(callback=callback)
    if not logged_in:
        QMessageBox.about(parent, _('Error'), _(
            'Error logging in into the server. Please try again later.'))
        callback.cancel()
        return False
    callback.finish()

    QCoreApplication.processEvents()
    return True
