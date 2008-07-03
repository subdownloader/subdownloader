#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Copyright (C) 2007 Ivan Garcia <contact@ivangarcia.org>
##    This program is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License along
##    with this program; if not, write to the Free Software Foundation, Inc.,
##    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
Module implementing a splashscreen
"""

import os.path

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QPixmap, QSplashScreen, QColor

class SplashScreen(QSplashScreen):
    """
    Class implementing a splashscreen for subdownloader.
    """
    def __init__(self):
        """
        Constructor
        """
        img_path = os.path.join(os.getcwd(), 'gui', 'images', 'splash.png')
        pixmap = QPixmap(img_path)
        self.labelAlignment = Qt.Alignment(Qt.AlignBottom | Qt.AlignRight | Qt.AlignAbsolute)
        QSplashScreen.__init__(self, pixmap)
        self.show()
        QApplication.flush()
        
    def showMessage(self, msg):
        """
        Public method to show a message in the bottom part of the splashscreen.
        
        @param msg message to be shown (string or QString)
        """
        QSplashScreen.showMessage(self, msg, self.labelAlignment, QColor(Qt.white))
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
