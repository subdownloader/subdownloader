# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging
from subdownloader.client.callback import ClientCallback
import progressbar


"""
Default widgets to use with the progressbar library.
"""
DEFAULT_WIDGETS = [
        progressbar.Bar(marker='>', left='[', right=']'),
        progressbar.Percentage(), ' ', progressbar.ETA()
    ]


class ProgressBarCallback(ClientCallback):
    """
    This callback will use the progressbar library to show the progress of some action.
    """
    def __init__(self, minimum=None, maximum=None, widgets=DEFAULT_WIDGETS):
        """
        Initialize a new ProgressBarCallback (and thus show a progressbar).
        :param minimum: minimum value as integer
        :param maximum: maximum value as integer
        :param widgets: widgets to show as list of progressbar.Widget
        """
        ClientCallback.__init__(self, minimum=minimum, maximum=maximum)
        self._bar = progressbar.ProgressBar(widgets=widgets)

    def on_show(self):
        self._bar.start()

    def on_update(self, value, *args, **kwargs):
        """
        Update the progressbar with the new value and percentage
        :param value: value as integer
        :param args: extra positional arguments to pass on
        :param kwargs: extra keyword arguments to pass on
        """
        self._bar.update(value)

    def on_finish(self, *args, **kwargs):
        """
        Inform this ProgressBarCallback that the action is finished
        """
        self._bar.finish()

    def on_rangeChange(self, minimum, maximum):
        self._bar.maxval = maximum
