#!/usr/bin/env python3

from subdownloader.compat import PY2

if PY2:
    read_input = raw_input
else:
    read_input = input
