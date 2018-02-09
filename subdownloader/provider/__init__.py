# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3


def window_iterator(data, width):
    """
    Instead of iterating element by element, get a number of elements at each iteration step.
    :param data: data to iterate on
    :param width: maximum number of elements to get in each iteration step
    :return:
    """
    start = 0
    while start < len(data):
        yield data[start:start+width]
        start += width
