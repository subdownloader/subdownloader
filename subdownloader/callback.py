# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging


class ProgressCallback(object):
    """
    This class allows calling function to be informed of eventual progress.
    Subclasses should only override the 'updated' and 'finished' members functions.
    Or you can simply pass a updated and finished callback.
    """
    def __init__(self, minimum=None, maximum=None,
                 updatedCb=None, finishedCb=None, rangeChangedCb=None):
        """
        Create a a new ProgressCallback object.
        :param minimum: minimum value of the range (None if no percentage is required)
        :param maximum: maximum value of the range (None if no percentage is required)
        :param updatedCb: callback when an update is available (no ratelimit). See updated for prototype.
        :param finishedCb: callback when the action has finished (no ratelimit). See finished for prototype.
        :param rangeChangedCb: callback when the range has changed (no ratelimit). See rangeChanged for prototype.
        """
        self.log = logging.getLogger('subdownloader.callback.ProgressCallback')
        self.log.debug('init: min={}, max={}'.format(minimum, maximum))
        self._min = minimum
        self._max = maximum
        self._updatedCb = updatedCb
        self._finishedCb = finishedCb
        self._rangeChangedCb = rangeChangedCb

    def range_initialized(self):
        """
        Check whether a range is set.
        """
        return None not in self.get_range()

    def set_range(self, minimum=None, maximum=None):
        """
        Set a range.
        The range is passed unchanged to the rangeChanged member function.
        :param minimum: minimum value of the range (None if no percentage is required)
        :param maximum: maximum value of the range (None if no percentage is required)
        """
        self._min = minimum
        self._max = maximum
        self.rangeChanged(minimum, maximum)

    def get_range(self):
        """
        Returns the minimum and maximum
        :return: A tuple with the minimum and maximum
        """
        return self._min, self._max

    def update(self, value):
        """
        Call this function to inform that an update is available.
        This function does NOT call finish when value == maximum.
        :param value: The current index/position of the action. (Should be, but must not be, in the range [max, min]
        """
        self.log.debug('update({}) called'.format(value))
        if self.range_initialized() or (self._min == self._max):
            percentage = 100 * float(value - self._min) / (self._max - self._min)
            self.log.debug('percentage = {:.2f}% range=({},{})'.format(
                percentage, self._min, self._max))
            self.updated(value, percentage)
        else:
            self.log.debug('calling updated with range uninitialized')
            self.updated(value, value)

    def finish(self, value):
        """
        Call this function to inform that the operation is finished.
        :param value: any data
        """
        self.log.debug('finish({}) called'.format(value))
        self.finished(value)

    def set_updated_cb(self, cb):
        """
        Set the function that should be called upon an update.
        :param cb: a function (see updated for prototype)
        """
        self._updatedCb = cb

    def set_finished_cb(self, cb):
        """
        Set the function that should be called upon finish.
        :param cb: a function (see finished for prototype)
        """
        self._finishedCb = cb

    def set_rangeChanged_cb(self, cb):
        """
        Set the function that should be called upon change of range.
        :param cb: a function (see rangeChanged for prototype)
        """
        self._rangeChangedCb = cb

    def rangeChanged(self, minimum, maximum):
        """
        Override this function if a custom action is required upon range change.
        :param minimum: New minimum value
        :param maximum: New maximum value
        """
        if self._rangeChangedCb:
            self._rangeChangedCb(minimum, maximum)

    def updated(self, value, percentage):
        """
        Override this function if a custom updated action is required.
        :param value: The value that has been passed to update
        :param percentage: A percentage. If the range is invalid, same as value.
        """
        if self._updatedCb:
            self._updatedCb(value, percentage)

    def finished(self, value):
        """
        Override this function if a custom finished action is required.
        :param value: The parameter of finish is passed unchanged
        """
        if self._finishedCb:
            self._finishedCb(value)