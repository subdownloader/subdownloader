#!/usr/bin/env python
# Copyright (c) 2010 SubDownloader Developers - See COPYING - GPLv3

'''
FileManagement package
'''
import re, string

def get_extension(path):
    if re.search("\.\w+$", path):
        return re.search("\w+$", path).group(0)
    return ""

def clear_string(strng):
    return re.sub('[^a-zA-Z0-9]', '', strng)

def without_extension(filename):
    ext = get_extension(filename)
    return filename.replace("."+ext, "")
