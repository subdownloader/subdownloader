# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtWidgets import QDialog

from subdownloader import APP_VERSION
from subdownloader.client.gui.about_ui import Ui_AboutDialog

log = logging.getLogger("subdownloader.client.gui.about")


class AboutDialog(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self.ui.label_version.setText(APP_VERSION)
        self.ui.buttonClose.clicked.connect(self.onButtonClose)

    def onButtonClose(self):
        self.reject()
