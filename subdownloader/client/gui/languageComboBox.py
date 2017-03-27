# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

from subdownloader.languages.language import Language, legal_languages, UnknownLanguage
from subdownloader.client.internationalization import i18n_get_supported_locales

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QComboBox


class AbstractLanguageComboBox(QComboBox):

    selected_language_changed = pyqtSignal(Language)

    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self._unknown_text = UnknownLanguage.create_generic().name()
        self._unknown_visible = True
        self._current_language = None

        self.setupUi()

    def set_unknown_text(self, unknown_text):
        self._unknown_text = unknown_text
        if self._unknown_visible:
            self.setItemText(0, unknown_text)

    def get_selected_language(self):
        return self._current_language

    def set_selected_language(self, lang):
        index = self.findData(lang.raw_data())
        self.setCurrentIndex(index)

    def setupUi(self):
        if self._unknown_visible:
            self.addItem(self._unknown_text, UnknownLanguage.create_generic().raw_data())

        languages = sorted(self.legal_languages(), key=lambda x:x.name())

        for lang in languages:
            self.addItem(_(lang.name()), lang.raw_data())

        if self._unknown_visible:
            italic_font = self.font()
            italic_font.setItalic(True)
            self.setItemData(0, italic_font, Qt.FontRole)

        self.adjustSize()

        self.currentIndexChanged.connect(self.onCurrentIndexChanged)

        self.setCurrentIndex(0)
        self._current_language = Language.from_raw_data(self.itemData(0, Qt.UserRole))

    @pyqtSlot(int)
    def onCurrentIndexChanged(self, index):
        raw_data = self.itemData(index, Qt.UserRole)
        self._current_language = Language.from_raw_data(raw_data)
        self.selected_language_changed.emit(self._current_language)


class LanguageComboBox(AbstractLanguageComboBox):
    def legal_languages(self):
        return legal_languages()


class InterfaceLanguageComboBox(AbstractLanguageComboBox):
    def legal_languages(self):
        return [Language.from_locale(locale) for locale in i18n_get_supported_locales()]
