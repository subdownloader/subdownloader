# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging

from subdownloader.client.state import ProviderStateCallback

from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt
from PyQt5.QtGui import QColor, QFont, QIcon

log = logging.getLogger('subdownloader.client.gui.models.provider')


class ProviderStateModelCallback(ProviderStateCallback):
    def __init__(self, provider_model):
        ProviderStateCallback.__init__(self)
        self._provider_model = provider_model

    def __getattribute__(self, item):
        if item.startswith('on_'):
            item = '_func'
        return object.__getattribute__(self, item)

    def _func(self, *args, **kwargs):
        self._provider_model.underlying_data_changed()


class ProviderModel(QAbstractListModel):
    def __init__(self, general_text_visible=True, general_text=None):
        QAbstractListModel.__init__(self)
        self._state = None
        self._filter_enable = True
        self._general_visible = general_text_visible
        self._callback = ProviderStateModelCallback(self)
        if general_text is None:
            general_text = 'GENERAL_TEXT'
        self._general_text = general_text

    def underlying_data_changed(self):
        self.dataChanged.emit(self.index(0), self.index(self.rowCount(QModelIndex())))

    def set_general_visible(self, general_visible):
        if self._general_visible == general_visible:
            return

        if general_visible:
            self.beginInsertRows(QModelIndex(), 0, 0)
            self._general_visible = general_visible
            self.endInsertRows()
        else:
            self.beginRemoveRows(QModelIndex(), 0, 0)
            self._general_visible = general_visible
            self.endRemoveRows()

    def set_filter_enable(self, filter_enable):
        if self._filter_enable != filter_enable:
            self.beginResetModel()
            self._filter_enable = filter_enable
            self.endResetModel()

    def set_general_text(self, general_text):
        self._general_text = general_text
        if self._general_visible:
            index = self.index(0)
            self.dataChanged.emit(index, index)

    def set_state(self, state):
        dx = 1 if self._general_visible else 0
        if self._state:
            self._state.remove_callback(self._callback)
            self.beginRemoveRows(QModelIndex(), dx, dx + self.rowCount(QModelIndex()))
            self._state = None
            self.endRemoveRows()

        if state is None:
            return

        self._state = state
        self._state.providers.add_callback(self._callback)
        self.beginInsertRows(QModelIndex(), dx, dx + self.rowCount(QModelIndex()))
        self.endInsertRows()

    def provider_state_at_index(self, index):
        if self._general_visible:
            if index == 0:
                return None
            index -= 1

        if self._state is None:
            return None
        if self._filter_enable:
            return self._state.providers.get(index)
        else:
            return self._state.providers.all_states[index]

    def data(self, index, role=None):
        if not index.isValid():
            return None
        provider_state = self.provider_state_at_index(index.row())

        if provider_state is None:
            if role == Qt.FontRole:
                font = QFont()
                font.setItalic(True)
                return font
            elif role == Qt.DisplayRole:
                return self._general_text
        else:
            if role == Qt.UserRole:
                return provider_state
            elif role == Qt.DecorationRole:
                path = provider_state.provider.get_icon()
                if path:
                    return QIcon(path)
                else:
                    return None
            elif role == Qt.TextColorRole:
                if not provider_state.getEnabled():
                    color = QColor(Qt.lightGray)
                    return color
            elif role == Qt.DisplayRole:
                return provider_state.provider.get_name()

        return None

    def index(self, row, column=0, parent=QModelIndex()):
        if row < 0 or column < 0:
            return QModelIndex()

        if row == 0:
            return self.createIndex(row, column, None)

        if self._state is None:
            return QModelIndex()

        if row > self._state.providers.get_number_providers():
            return QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, column, None)

        return QModelIndex()

    def index_of_provider(self, provider):
        if self._state is None:
            return None
        if self._filter_enable:
            providers = list(ps.provider for ps in self._state.providers.get_providers())
        else:
            providers = list(ps.provider for ps in self._state.providers.all_states)
        if self._general_visible:
            providers.insert(0, None)
        try:
            return providers.index(provider)
        except ValueError:
            return None

    def headerData(self, *args, **kwargs):
        return None

    def rowCount(self, parent=None, *args, **kwargs):
        if self._state is None:
            return 1 if self._general_visible else 0

        if parent is None or not parent.isValid():
            if self._filter_enable:
                nb = self._state.providers.get_number_providers()
            else:
                nb = len(self._state.providers.all_states)
            if self._general_visible:
                nb += 1
            return nb
        return 0
