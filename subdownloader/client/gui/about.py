# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog

from subdownloader.client.gui.about_ui import Ui_AboutDialog

log = logging.getLogger("subdownloader.gui.about")


class aboutDialog(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self._main = parent
        settings = QSettings()
        self.ui.buttonClose.clicked.connect(self.onButtonClose)

    def onButtonClose(self):
        self.reject()
