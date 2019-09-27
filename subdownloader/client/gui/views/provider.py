# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging

from subdownloader.client.gui.models.provider import ProviderModel

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QComboBox

log = logging.getLogger('subdownloader.client.gui.views.provider')


class _Optional:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<_Optional:{}>'.format(self.value)


class ProviderComboBox(QComboBox):
    selected_provider_state_changed = pyqtSignal(_Optional)

    def __init__(self, parent):
        QComboBox.__init__(self, parent)
        self._model = ProviderModel()
        self._current_provider_state = None

        self.setup_ui()

    def set_general_text(self, general_text):
        self._model.set_general_text(general_text)

    def set_general_visible(self, general_visible):
        self._model.set_general_visible(general_visible)

    def set_filter_enable(self, filter_enable):
        self._model.set_filter_enable(filter_enable)

    def set_state(self, state):
        current_index = self.currentIndex()
        self._model.set_state(state)
        if current_index >= self._model.rowCount():
            current_index = self._model.rowCount() - 1
        self.setCurrentIndex(current_index)

    def get_selected_provider_state(self):
        return self._current_provider_state

    def setup_ui(self):
        self.setModel(self._model)

        self.setIconSize(QSize(16, 16))

        self.setCurrentIndex(0)
        self._current_provider_state = self._model.provider_state_at_index(self.currentIndex())

        self.currentIndexChanged.connect(self.onCurrentIndexChanged)

    @pyqtSlot(int)
    def onCurrentIndexChanged(self, index):
        self._current_provider_state = self._model.provider_state_at_index(index)
        self.selected_provider_state_changed.emit(_Optional(self._current_provider_state))
