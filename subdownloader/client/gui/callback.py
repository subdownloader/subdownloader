# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging

from subdownloader.client.callback import ClientCallback

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QPushButton, QProgressDialog

log = logging.getLogger('subdownloader.client.gui.callback')


class ProgressCallbackWidget(ClientCallback):
    def __init__(self, parent):
        ClientCallback.__init__(self)

        self.status_progress = None
        self._parent = parent
        self._block = False

        self._label_text = ''
        self._title_text = ''
        self._updated_text = ''
        self._finished_text = ''
        self._cancellable = True

        self.status_progress = QProgressDialog(self._parent, Qt.Dialog)

        self.status_progress.setWindowModality(Qt.WindowModal)

        self.set_range(0, 1)

    def __del__(self):
        self.status_progress.close()
        del self.status_progress

    def set_block(self, block):
        self._block = block

    def set_title_text(self, title_text):
        self._title_text = title_text

    def set_label_text(self, label_text):
        self._label_text = label_text

    def set_updated_text(self, updated_text):
        self._updated_text = updated_text

    def set_finished_text(self, finished_label):
        self._finished_text = finished_label

    def set_cancellable(self, cancellable):
        if not self._cancellable and cancellable:
            log.warning('ProgressCallbackWidget.set_cancellable({cancellable}): invalid operation'.format(
                cancellable=cancellable))
        if cancellable:
            if not self._cancellable:
                self.status_progress.setCancelButton(QPushButton(_('Cancel')))
        else:
            self.status_progress.setCancelButton(None)
        self._cancellable = cancellable

    def on_show(self):
        # FIXME: status_progress may be None if on_update is called BEFORE show..
        # FIXME: rename to start..
        self.status_progress.reset()

        self.set_block(self._block)
        self.set_cancellable(self._cancellable)

        self.status_progress.setWindowTitle(self._title_text)
        self.status_progress.setLabelText(self._label_text)

        minimum, maximum = self.get_range()

        self.status_progress.setMinimum(minimum)
        self.status_progress.setMaximum(maximum)

        self.status_progress.show()
        if self._block:
            self._parent.setCursor(Qt.WaitCursor)

    def on_update(self, value, *args, **kwargs):
        self.status_progress.setValue(value)
        if self._updated_text:
            # FIXME: let the caller format the strings
            updatedMsg = self._updated_text.format(*args)
            self.status_progress.setLabelText(updatedMsg)
        QCoreApplication.processEvents()

    def on_finish(self, *args, **kwargs):
        # FIXME: let the caller format the strings
        finishedMsg = self._finished_text.format(*args)
        # self.status_progress.setLabelText(finishedMsg)
        self.status_progress.hide()
        if self._block:
            self._parent.setCursor(Qt.ArrowCursor) # FIXME: restoreCursor? setCursor only in this class!!
        QCoreApplication.processEvents()

    def on_rangeChange(self, minimum, maximum):
        self.status_progress.setMinimum(minimum)
        self.status_progress.setMaximum(maximum)
        QCoreApplication.processEvents()

    def on_cancel(self):
        self.status_progress.cancel()
        if self._block:
            self._parent.setCursor(Qt.ArrowCursor)
        QCoreApplication.processEvents()

    def canceled(self):
        return self.status_progress.wasCanceled()
