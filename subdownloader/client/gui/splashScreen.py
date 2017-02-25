#!/usr/bin/env python
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QSplashScreen
from subdownloader.client.gui import images_rc

class SplashScreen(QSplashScreen):

    """
    Class implementing a splashscreen for subdownloader.
    """

    def __init__(self):
        """
        Constructor
        """
        pixmap = QPixmap(':/images/splash.png')
        self.labelAlignment = Qt.Alignment(
            Qt.AlignBottom | Qt.AlignRight | Qt.AlignAbsolute)
        QSplashScreen.__init__(self, pixmap, Qt.WindowStaysOnTopHint)
        QApplication.flush()

    def showMessage(self, msg):
        """
        Public method to show a message in the bottom part of the splashscreen.

        @param msg message to be shown (string or QString)
        """
        QSplashScreen.showMessage(
            self, msg, self.labelAlignment, QColor(Qt.white))
        QApplication.processEvents()

    def clearMessage(self):
        """
        Public method to clear the message shown.
        """
        QSplashScreen.clearMessage(self)
        QApplication.processEvents()


class NoneSplashScreen(object):

    """
    Class implementing a "None" splashscreen for subdownloader.

    This class implements the same interface as the real splashscreen,
    but simply does nothing.
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def showMessage(self, msg):
        """
        Public method to show a message in the bottom part of the splashscreen.

        @param msg message to be shown (string or QString)
        """
        pass

    def clearMessage(self):
        """
        Public method to clear the message shown.
        """
        pass

    def finish(self, widget):
        """
        Public method to finish the splash screen.

        @param widget widget to wait for (QWidget)
        """
        pass
