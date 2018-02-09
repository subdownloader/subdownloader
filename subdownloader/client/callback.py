# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging

from subdownloader.callback import ProgressCallback

log = logging.getLogger('subdownloader.client.callback')


class ClientCallback(ProgressCallback):
    def __init__(self, minimum=None, maximum=None):
        ProgressCallback.__init__(self, minimum=minimum, maximum=maximum)

        self._block = False

        self._label_text = ''
        self._title_text = ''
        self._updated_text = ''
        self._finished_text = ''
        self._cancellable = True

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
        self._cancellable = cancellable

    def show(self):
        log.debug('show()')
        self.on_show()

    def on_show(self):
        pass
