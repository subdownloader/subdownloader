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
                 onUpdateCb=None, onFinishCb=None, onRangeChangeCb=None, onCancelCb=None):
        """
        Create a a new ProgressCallback object.
        :param minimum: minimum value of the range (None if no percentage is required)
        :param maximum: maximum value of the range (None if no percentage is required)
        :param onUpdateCb: callback when an update is available (no ratelimit). See on_update for prototype.
        :param onFinishCb: callback when the action has finished (no ratelimit). See on_finish for prototype.
        :param onRangeChangeCb: callback when the range has changed (no ratelimit). See on_rangeChange for prototype.
        """
        self.log = logging.getLogger('subdownloader.callback.ProgressCallback')
        self.log.debug('init: min={}, max={}'.format(minimum, maximum))
        self._min = minimum
        self._max = maximum
        self._onUpdateCb = onUpdateCb
        self._onFinishCb = onFinishCb
        self._onRangeChangeCb = onRangeChangeCb
        self._onCancelCb = onCancelCb

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
        self.on_rangeChange(minimum, maximum)

    def get_range(self):
        """
        Returns the minimum and maximum
        :return: A tuple with the minimum and maximum
        """
        return self._min, self._max

    def to_percentage(self, value):
        """
        Convert value to percentage. Pass through value if the range is invalid.
        :param value: value to convert to a percentage
        """
        if self.range_initialized() or (self._min != self._max):
            return 100 * float(value - self._min) / (self._max - self._min)
        else:
            return value

    def update(self, value, *args, **kwargs):
        """
        Call this function to inform that an update is available.
        This function does NOT call finish when value == maximum.
        :param value: The current index/position of the action. (Should be, but must not be, in the range [min, max])
        :param args: extra positional arguments to pass on
        :param kwargs: extra keyword arguments to pass on
        """
        self.log.debug('update({})'.format(value))
        self.on_update(value, *args, **kwargs)

    def finish(self, value, *args, **kwargs):
        """
        Call this function to inform that the operation is finished.
        :param value: any data
        :param args: extra positional arguments to pass on
        :param kwargs: extra keyword arguments to pass on
        """
        self.log.debug('finish({}) called'.format(value))
        self.on_finish(value, *args, **kwargs)

    def cancel(self):
        """
        Call this function to inform that the operation has been cancelled.
        """
        self.log.debug('cancel() called')
        self.on_cancel()

    def on_rangeChange(self, minimum, maximum):
        """
        Override this function if a custom action is required upon range change.
        :param minimum: New minimum value
        :param maximum: New maximum value
        """
        if self._onRangeChangeCb:
            self._onRangeChangeCb(minimum, maximum)

    def on_update(self, value, *args, **kwargs):
        """
        Override this function if a custom update action is required.
        :param value: The current index/position of the action. (Should be, but must not be, in the range [min, max])
        :param args: extra positional arguments to pass on
        :param kwargs: extra keyword arguments to pass on
        """
        if self._onUpdateCb:
            self._onUpdateCb(value, *args, **kwargs)

    def on_finish(self, value, *args, **kwargs):
        """
        Override this function if a custom finish action is required.
        :param value: The parameter of finish is passed unchanged
        :param args: extra positional arguments to pass on
        :param kwargs: extra keyword arguments to pass on
        """
        if self._onFinishCb:
            self._onFinishCb(value)

    def on_cancel(self):
        """
        Override this function if a custom cancel action is required
        """
        if self._onCancelCb:
            self._onCancelCb()
