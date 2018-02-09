# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QSplashScreen


class SplashScreen(QSplashScreen):

    """
    Class implementing a splashscreen for subdownloader.
    """

    def __init__(self):
        """
        Constructor
        """
        QSplashScreen.__init__(self, QPixmap(':/images/splash.png'), Qt.WindowStaysOnTopHint)
        QApplication.flush()

    def showMessage(self, message, *args):
        """
        Public method to show a message in the bottom part of the splashscreen.

        @param message message to be shown (string or QString)
        """
        QSplashScreen.showMessage(
            self, message, Qt.AlignBottom | Qt.AlignRight | Qt.AlignAbsolute, QColor(Qt.white))

    def clearMessage(self):
        """
        Public method to clear the message shown.
        """
        QSplashScreen.clearMessage(self)


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
