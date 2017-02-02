# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QCoreApplication, QSettings
from PyQt5.QtWidgets import QDialog, QMessageBox

from gui.login_ui import Ui_LoginDialog
import logging
log = logging.getLogger("subdownloader.gui.login")


class loginDialog(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)
        self._main = parent
        settings = QSettings()

        self.ui.buttonBox.accepted.connect(self.onButtonAccept)
        self.ui.buttonBox.rejected.connect(self.onButtonClose)
        username = settings.value("options/LoginUsername", "")
        password = settings.value("options/LoginPassword", "")
        self.ui.optionLoginUsername.setText(username)
        self.ui.optionLoginPassword.setText(password)

    @pyqtSlot()
    def onButtonClose(self):
        self.reject()

    @pyqtSlot()
    def onButtonAccept(self):
        settings = QSettings()
        newUsername = self.ui.optionLoginUsername.text()
        newPassword = self.ui.optionLoginPassword.text()
        oldUsername = settings.value("options/LoginUsername", "")
        oldPassword = settings.value("options/LoginPassword", "")

        if newUsername != oldUsername or newPassword != oldPassword:
            settings.setValue("options/LoginUsername", newUsername)
            settings.setValue("options/LoginPassword", newPassword)

        self.connect()
        self.accept()  # We close the window

    def connect(self):
        username = self.ui.optionLoginUsername.text()
        password = self.ui.optionLoginPassword.text()

        self.setCursor(Qt.WaitCursor)
        if not hasattr(self, 'OSDBServer'):
            # and self.OSDBServer.is_connected():
            if not self._main.establishServerConnection():
                self.setCursor(Qt.ArrowCursor)
                QMessageBox.about(self, _("Error"), _(
                    "Error contacting the server. Please try again later"))
                return

        self._main.login_user(username, password)
        self.setCursor(Qt.ArrowCursor)
        QCoreApplication.processEvents()
