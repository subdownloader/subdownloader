# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging

from subdownloader.languages.language import UnknownLanguage

from PyQt5.QtCore import QAbstractListModel, QModelIndex, QSize, Qt
from PyQt5.QtGui import QFont, QIcon

log = logging.getLogger('subdownloader.client.gui.models.language')


class LanguageModel(QAbstractListModel):
    def __init__(self, unknown_text, unknown_visible, languages, parent=None):
        QAbstractListModel.__init__(self, parent)
        self._unknown_visible = unknown_visible
        self._unknown_text = unknown_text

        self._languages = languages

    def set_unknown_visible(self, unknown_visible):
        if self._unknown_visible == unknown_visible:
            return

        if unknown_visible:
            self.beginInsertRows(QModelIndex(), 0, 0)
            self._unknown_visible = unknown_visible
            self.endInsertRows()
        else:
            self.beginRemoveRows(QModelIndex(), 0, 0)
            self._unknown_visible = unknown_visible
            self.endRemoveRows()

    def set_unknown_text(self, unknown_text):
        self._unknown_text = unknown_text
        if self._unknown_visible:
            index = self.index(0)
            self.dataChanged.emit(index, index)

    def language_at_index(self, index):
        if self._unknown_visible:
            if index == 0:
                return UnknownLanguage.create_generic()
            index -= 1
        return self._languages[index]

    def data(self, index, role=None):
        if not index.isValid():
            return None
        language = self.language_at_index(index.row())

        if role == Qt.UserRole:
            return language

        if role == Qt.FontRole:
            if language.is_generic():
                font = QFont()
                font.setItalic(True)
                return font

        if role == Qt.DecorationRole:
            xx = language.xx()
            return QIcon(':/images/flags/{xx}.png'.format(xx=xx)).pixmap(QSize(24, 24), QIcon.Normal)

        if role == Qt.DisplayRole:
            if language.is_generic():
                return _(self._unknown_text)
            else:
                return language.name()
        return None

    def index(self, row, column=0, parent=QModelIndex()):
        if row < 0 or column < 0:
            return QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, column, None)

        return QModelIndex()

    def headerData(self, *args, **kwargs):
        return None

    def rowCount(self, parent=None, *args, **kwargs):
        if not parent.isValid():
            return len(self._languages) + (1 if self._unknown_visible else 0)
        return 0

    def language_to_index(self, language):
        if self._unknown_visible:
            if language.is_generic():
                return 0
        try:
            index = next(index for index, lang in enumerate(self._languages) if language == lang)
            return index + (1 if self._unknown_visible else 0)
        except StopIteration:
            return None
