#!/usr/bin/env python
# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog

from gui.about_ui import Ui_AboutDialog
import logging
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
