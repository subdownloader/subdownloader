#!/bin/env python
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import sys
import re


def fix_translation():
    regex = re.compile('_translate\(".*?",\s(".*?")\s*?\)')
    replace_with = r'_(\1)'

    def fix(line):
        return regex.sub(replace_with, line)
    return fix

fixes = [
    fix_translation(),
]


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Parse Qt5 generated _ui.py files.'
    )
    parser.add_argument('-i', dest='input', default=None, metavar='FILE', help='Input file')
    parser.add_argument('-o', dest='output', default=None, metavar='FILE', help='Output file')

    args = parser.parse_args()

    if args.input:
        file_in = open(args.input)
    else:
        file_in = sys.stdin

    if args.output:
        file_out = open(args.output)
    else:
        file_out = sys.stdout

    for line in file_in.readlines():
        for fix in fixes:
            line = fix(line)
            file_out.write(line)

if __name__ == '__main__':
    main()
