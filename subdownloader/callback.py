# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging

log = logging.getLogger('subdownloader.callback.ProgressCallback')


class ProgressCallback(object):
    """
    This class allows calling function to be informed of eventual progress.
    Subclasses should only override the on_*** function members.
    """
    def __init__(self, minimum=None, maximum=None):
        """
        Create a a new ProgressCallback object.
        :param minimum: minimum value of the range (None if no percentage is required)
        :param maximum: maximum value of the range (None if no percentage is required)
        """
        log.debug('init: min={min}, max={max}'.format(min=minimum, max=maximum))
        self._min = minimum
        self._max = maximum

        self._canceled = False

    def range_initialized(self):
        """
        Check whether a range is set.
        """
        return None not in self.get_range()

    def set_range(self, minimum, maximum):
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

    def get_child_progress(self, parent_min, parent_max):
        """
        Create a new child ProgressCallback.
        Minimum and maximum values of the child are mapped to parent_min and parent_max of this parent ProgressCallback.
        :param parent_min: minimum value of the child is mapped to parent_min of this parent ProgressCallback
        :param parent_max: maximum value of the child is mapped to parent_max of this parent ProgressCallback
        :return: instance of SubProgressCallback
        """
        return SubProgressCallback(parent=self, parent_min=parent_min, parent_max=parent_max)

    def update(self, value, *args, **kwargs):
        """
        Call this function to inform that an update is available.
        This function does NOT call finish when value == maximum.
        :param value: The current index/position of the action. (Should be, but must not be, in the range [min, max])
        :param args: extra positional arguments to pass on
        :param kwargs: extra keyword arguments to pass on
        """
        log.debug('update(value={value}, args={args}, kwargs={kwargs})'.format(value=value, args=args, kwargs=kwargs))
        self.on_update(value, *args, **kwargs)

    def finish(self, *args, **kwargs):
        """
        Call this function to inform that the operation is finished.
        :param args: extra positional arguments to pass on
        :param kwargs: extra keyword arguments to pass on
        """
        log.debug('finish(args={args}, kwargs={kwargs})'.format(args=args, kwargs=kwargs))
        self.on_finish(*args, **kwargs)

    def cancel(self):
        """
        Call this function to inform that the operation has been cancelled.
        """
        log.debug('cancel()')
        self._canceled = True
        self.on_cancel()

    def on_rangeChange(self, minimum, maximum):
        """
        Override this function if a custom action is required upon range change.
        :param minimum: New minimum value
        :param maximum: New maximum value
        """
        pass

    def on_update(self, value, *args, **kwargs):
        """
        Override this function if a custom update action is required.
        :param value: The current index/position of the action. (Should be, but must not be, in the range [min, max])
        :param args: extra positional arguments to pass on
        :param kwargs: extra keyword arguments to pass on
        """
        pass

    def on_finish(self, *args, **kwargs):
        """
        Override this function if a custom finish action is required.
        :param args: extra positional arguments to pass on
        :param kwargs: extra keyword arguments to pass on
        """
        pass

    def on_cancel(self):
        """
        Override this function if a custom cancel action is required
        """
        pass


    def canceled(self):
        """
        Return true when the progress has been canceled.
        :return: Boolean value
        """
        return self._canceled


class SubProgressCallback(ProgressCallback):
    """
    A SubProgressCallback is a ProgressCallback that will map updates to the parent updates.
    """
    def __init__(self, parent, parent_min, parent_max):
        """
        Initialize a new SubProgresCallback.
        The range [min, max) of this SubProgressCallback are mapped to [parent_min, parent_max) of the parent callback.
        :param parent: The parent ProgressCallback
        :param parent_min: The minimum value of the parent
        :param parent_max: The maximum value of the parent
        """
        ProgressCallback.__init__(self)
        self._parent = parent
        self._parent_min = parent_min
        self._parent_max = parent_max

    def on_update(self, value, *args, **kwargs):
        """
        Inform the parent of progress.
        :param value: The value of this subprogresscallback
        :param args: Extra positional arguments
        :param kwargs: Extra keyword arguments
        """
        parent_value = self._parent_min
        if self._max != self._min:
            sub_progress = (value - self._min) / (self._max - self._min)
            parent_value = self._parent_min + sub_progress * (self._parent_max - self._parent_min)
        self._parent.update(parent_value, *args, **kwargs)

    def on_cancel(self):
        """
        If a SubProgressCallback is canceled, cancel the parent ProgressCallback.
        :return:
        """
        self._parent.cancel()
