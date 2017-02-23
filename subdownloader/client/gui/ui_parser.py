#!/bin/env python
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import sys
import re

def fixTranslation():
    regex = re.compile('_translate\(".*?",\s(".*?")\s*?\)')
    repl = r'_(\1)'

    def fix(line):
        return regex.sub(repl, line)
    return fix

fixes = [
    fixTranslation(),
]

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Parse Qt5 generated _ui.py files.')

    args = parser.parse_args()

    for line in sys.stdin.readlines():
        for fix in fixes:
            line = fix(line)
        sys.stdout.write(line)
