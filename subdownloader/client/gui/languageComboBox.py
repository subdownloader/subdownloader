# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

from abc import abstractmethod

from subdownloader.languages.language import Language, legal_languages, UnknownLanguage
from subdownloader.client.internationalization import i18n_get_supported_locales

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QAbstractItemModel, QModelIndex, QSize, Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QComboBox


class LanguageModel(QAbstractItemModel):
    def __init__(self, unknown_text, unknown_visible, legal_languages, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self._unknown_text = unknown_text
        self._unknown_visible = unknown_visible
        self._languages = [UnknownLanguage.create_generic()] if unknown_visible else []
        self._languages += sorted(legal_languages, key=lambda x : x.name())

    def set_unknown_text(self, unknown_text):
        self._unknown_text = unknown_text

    def data(self, index, role=None):
        if not index or not index.isValid():
            return False
        languages = index.internalPointer()
        language = languages[index.row()]

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

    def parent(self, index):
        return QModelIndex()

    def index(self, row, column, parent=None, *args, **kwargs):
        if row < 0 or column < 0:
            return QModelIndex()

        if not parent or not parent.isValid():
            return self.createIndex(row, 0, self._languages)

        return QModelIndex()

    def headerData(self, *args, **kwargs):
        return None

    def rowCount(self, parent=None, *args, **kwargs):
        if not parent or not parent.isValid():
            return len(self._languages)
        return 0

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def language_at_index(self, index):
        return self._languages[index]

    def language_to_index(self, language):
        index = next(index for index, lang in enumerate(self._languages) if language.raw_data() == lang.raw_data())
        return index

class AbstractLanguageComboBox(QComboBox):

    selected_language_changed = pyqtSignal(Language)

    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self._model = LanguageModel(unknown_text=UnknownLanguage.create_generic().name(),
                                    unknown_visible=True,
                                    legal_languages=self.legal_languages())
        self._current_language = None

        self.setup_ui()

    @abstractmethod
    def legal_languages(self):
        pass

    def set_unknown_text(self, unknown_text):
        self._model.set_unknown_text(unknown_text)

    def get_selected_language(self):
        return self._current_language

    def set_selected_language(self, lang):
        index = self._model.language_to_index(lang)
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
        return legal_languages()


class InterfaceLanguageComboBox(AbstractLanguageComboBox):
    def legal_languages(self):
        return [Language.from_locale(locale) for locale in i18n_get_supported_locales()]
