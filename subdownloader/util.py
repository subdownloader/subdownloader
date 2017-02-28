# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

def asciify(data):
    """
    Limit the byte data string to only ascii characters and convert it to a string.
    Non-representable characters are dropped.
    :param data: byte data string to convert to ascii
    :return: string
    """
    return str(filter(lambda x:ord(x)<128, data))
