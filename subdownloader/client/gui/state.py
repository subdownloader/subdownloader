# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from enum import Enum
import logging

from subdownloader.client.state import BaseState, ProviderStateCallback
from subdownloader.languages.language import Language

from PyQt5.QtCore import pyqtSignal, QObject, QPoint, QSize

log = logging.getLogger('subdownloader.client.gui.state')


class GuiProviderStateCallbacks(ProviderStateCallback):
    def __init__(self, state):
        ProviderStateCallback.__init__(self)
        self._state = state

    def on_login(self, stage):
        if stage == ProviderStateCallback.Stage.Finished:
            self._state.signals.login_status_changed.emit()

    def on_disconnect(self, stage):
        if stage == ProviderStateCallback.Stage.Finished:
            self._state.signals.login_status_changed.emit()


class GuiStateSignals(QObject):
    interface_language_changed = pyqtSignal(Language)
    permanent_language_filter_changed = pyqtSignal(list)
    login_status_changed = pyqtSignal()


class GuiStateConfigKey(Enum):
    WINDOW_POSITION = ('mainwindow', 'pos2', )
    WINDOW_SIZE = ('mainwindow', 'size2', )


class GuiState(BaseState):
    def __init__(self):
        self._signals = GuiStateSignals()
        callback = GuiProviderStateCallbacks(self)
        BaseState.__init__(self, callback)

        self._window_position = None
        self._window_size = None

    @property
    def signals(self):
        return self._signals

    def load_settings(self, settings):
        BaseState.load_settings(self, settings)

        try:
            tup_pos = settings.get_ints(GuiStateConfigKey.WINDOW_POSITION.value, default=None)
            if tup_pos is not None:
                self._window_position = tuple(tup_pos)
        except ValueError:
            pass

        try:
            tup_size= settings.get_ints(GuiStateConfigKey.WINDOW_SIZE.value, default=None)
            if tup_size is not None:
                self._window_size = tuple(tup_size)
        except ValueError:
            pass

    def save_settings(self, settings):
        if self._window_position:
            settings.set_ints(GuiStateConfigKey.WINDOW_POSITION.value, self._window_position)

        if self._window_size:
            settings.set_ints(GuiStateConfigKey.WINDOW_SIZE.value, self._window_size)
        BaseState.save_settings(self, settings)

    def get_window_size(self):
        return self._window_size

    def set_window_size(self, size):
        self._window_size = self._assert_tup2(size)

    def get_window_position(self):
        return self._window_position

    def set_window_position(self, size):
        self._window_position = self._assert_tup2(size)

    @staticmethod
    def _assert_tup2(val2):
        if isinstance(val2, QPoint):
            val2 = (val2.x(), val2.y(), )
        if isinstance(val2, QSize):
            val2 = (val2.width(), val2.height(), )
        if val2:
            if len(val2) != 2:
                # FIXME: log
                val2 = None
            else:
                val2 = tuple(val2)
        else:
            val2 = None
        return val2
