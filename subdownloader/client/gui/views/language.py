# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from abc import abstractmethod
import logging

from subdownloader.languages.language import Language, legal_languages, UnknownLanguage
from subdownloader.client.internationalization import i18n_get_supported_locales
from subdownloader.client.gui.models.language import LanguageModel


from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QComboBox

log = logging.getLogger('subdownloader.client.gui.views.language')


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
