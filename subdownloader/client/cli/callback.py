# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
from subdownloader.callback import ProgressCallback
import progressbar


"""
Default widgets to use with the progressbar library.
"""
DEFAULT_WIDGETS = [
        progressbar.Bar(marker='>', left='[', right=']'),
        progressbar.Percentage(), ' ', progressbar.ETA()
    ]


class ProgressBarCallback(ProgressCallback):
    """
    This callback will use the progressbar library to show the progress of some action.
    """
    def __init__(self, widgets, minimum=None, maximum=None):
        """
        Initialize a new ProgressBarCallback (and thus show a progressbar).
        :param widgets: widgets to show as list of progressbar.Widget
        :param minimum: mimimum value as integer
        :param maximum: maximum value as integer
        """
        ProgressCallback.__init__(self, minimum=minimum, maximum=maximum)
        self._bar = progressbar.ProgressBar(widgets=widgets)
        self._bar.start()

    def set_range(self, minimum=None, maximum=None):
        """
        Set the range of this ProgressBarCallback
        :param minimum: minimum as integer
        :param maximum: maximum as integer
        """
        ProgressCallback.set_range(self, minimum, maximum)
        self._bar.maxval = maximum

    def on_update(self, value, percentage):
        """
        Update the progressbar with the new value and percentage
        :param value: value as integer
        :param percentage: percentage as float in range [0, 100]. Can be equal to value if no range is set.
        """
        self._bar.update(value)

    def finished(self, ok):
        """
        Inform this ProgressBarCallback that the action is finished
        :param ok: True if action was successful
        """
        self._bar.finish()
