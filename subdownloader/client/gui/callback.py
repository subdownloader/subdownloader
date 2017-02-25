# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging

from subdownloader.callback import ProgressCallback

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QProgressDialog

log = logging.getLogger('subdownloader.client.gui.callback')


class ProgressCallbackWidget(ProgressCallback):
    def __init__(self, parent):
        ProgressCallback.__init__(self)
        self._canceled = False

        self.status_progress = None
        self._parent = parent
        self._block = False
        self._label_text = ''
        self._title_text = ''
        self._updated_text = ''
        self._finished_text = ''
        self._cancellable = True

        self.reinit()

        self.set_range(0, 1)

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

    def reinit(self):
        self.set_title_text(self._title_text)
        self.set_label_text(self._label_text)
        self.set_updated_text(self._updated_text)
        self.set_finished_text(self._finished_text)

        self.set_block(self._block)
        self.set_cancellable(self._cancellable)

    def set_cancellable(self, cancellable):
        if not self._cancellable and cancellable:
            log.warning('ProgressCallbackWidget.set_cancellable({cancellable}): invalid operation',format(
                cancellable=cancellable))
        self._cancellable = cancellable
        if self.status_progress:
            if not cancellable:
                self.status_progress.setCancelButton(None)

    def show(self):
        self.status_progress = QProgressDialog(self._parent, Qt.Window)
        self.status_progress.canceled.connect(self.on_cancel)

        self.status_progress.setWindowTitle(self._title_text)
        self.status_progress.setLabelText(self._label_text)

        self.set_cancellable(self._cancellable)

        if self.range_initialized():
            minimum, maximum = self.get_range()
            self.status_progress.setMinimum(minimum)
            self.status_progress.setMaximum(maximum)

        self.status_progress.show()
        if self._block:
            self.status_progress.setCursor(Qt.WaitCursor)

    def on_update(self, value, *args, **kwargs):
        self.status_progress.setValue(value)
        if self._updated_text:
            # FIXME: let the caller format the strings
            updatedMsg = self._updated_text.__mod__(args)
            self.status_progress.setLabelText(updatedMsg)
        QCoreApplication.processEvents()

    def on_finish(self, *args, **kwargs):
        # FIXME: let the caller format the strings
        finishedMsg = self._finished_text.__mod__(args)
        self.status_progress.setLabelText(finishedMsg)
        if self._block:
            self.status_progress.setCursor(Qt.ArrowCursor) # FIXME: restoreCursor? setCursor only in this class!!
        self.status_progress.close()
        self.status_progress = None
        QCoreApplication.processEvents()

    def on_rangeChange(self, minimum, maximum):
        if self.status_progress:
            self.status_progress.setMinimum(minimum)
            self.status_progress.setMaximum(maximum)
        QCoreApplication.processEvents()

    def on_cancel(self):
        self._canceled = True
        if self._block:
            self.status_progress.setCursor(Qt.ArrowCursor)

    def canceled(self):
        return self._canceled
