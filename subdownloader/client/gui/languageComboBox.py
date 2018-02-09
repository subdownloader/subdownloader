# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from abc import abstractmethod
import logging

from subdownloader.languages.language import Language, legal_languages, UnknownLanguage
from subdownloader.client.internationalization import i18n_get_supported_locales

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QAbstractListModel, QModelIndex, QSize, Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QComboBox

log = logging.getLogger('subdownloader.client.gui.languageComboBox')


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


class AbstractLanguageComboBox(QComboBox):

    selected_language_changed = pyqtSignal(Language)

    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self._model = LanguageModel(unknown_text=UnknownLanguage.create_generic().name(),
                                    unknown_visible=True,
                                    languages=self.legal_languages())
        self._current_language = None

        self.setup_ui()

    @abstractmethod
    def legal_languages(self):
        pass

    def set_unknown_text(self, unknown_text):
        self._model.set_unknown_text(unknown_text)

    def set_unknown_visible(self, unknown_visible):
        self._model.set_unknown_visible(unknown_visible)

    def get_selected_language(self):
        return self._current_language

    def set_selected_language(self, lang):
        index = self._model.language_to_index(lang)
        if index is None:
            log.warning('Cannot set language to "{lang}". Language unknown.'.format(lang=lang))
        else:
            self.setCurrentIndex(index)

    def setup_ui(self):
        self.setModel(self._model)

        self.currentIndexChanged.connect(self.onCurrentIndexChanged)

        self.setCurrentIndex(0)
        self._current_language = self._model.language_at_index(self.currentIndex())

    @pyqtSlot(int)
    def onCurrentIndexChanged(self, index):
        self._current_language = self._model.language_at_index(index)
        self.selected_language_changed.emit(self._current_language)


class LanguageComboBox(AbstractLanguageComboBox):
    def legal_languages(self):
        return [l for l in legal_languages()]


class InterfaceLanguageComboBox(AbstractLanguageComboBox):
    def legal_languages(self):
        return [Language.from_locale(locale) for locale in i18n_get_supported_locales()]
