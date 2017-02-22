# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

from PyQt5.QtWidgets import QComboBox


class LanguageComboBox(QComboBox):
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
