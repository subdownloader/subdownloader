#!/usr/bin/env python
# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

import os
import sys
import re


def fixTranslation():
    regex = re.compile(
        'QtGui\.QApplication\.translate\(context,\s(text),\sdisambig.*?\)')
    repl = r'_(\1)'

    def fix(line):
        return regex.sub(repl, line)
    return fix

existingFiles = []


def fixImports():
    regex = re.compile('(?:from ([a-zA-Z0-9_\-]*) )?import ([a-zA-Z0-9_\-]*)')

    def replFunc(matchObj):
        module = matchObj.group(1) if matchObj.group(1) else matchObj.group(2)
        fileName = module + '.py'
        member = matchObj.group(2) if matchObj.group(1) else None
        fileExists = os.path.exists(fileName) or fileName in existingFiles
        if fileExists:
            if member:
                return 'from .{} import {}'.format(module, member)
            else:
                return 'from . import {}'.format(module)
        else:
            if member:
                return 'from {} import {}'.format(module, member)
            else:
                return 'import {}'.format(module)

    def fix(line):
        return regex.sub(replFunc, line)
    return fix


def removeLine(what):
    def remove(line):
        if what in line:
            return ''
        else:
            return line
    return remove

fixes = [
    fixTranslation(),
    fixImports(),
    removeLine('Margin'),
    removeLine('boxlayout.setObjectName'),
]

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Parse Qt4 generated _ui.py files.')
    parser.add_argument('files', metavar='FILE', type=str, nargs='*',
                        help='Assume files to exist.')

    args = parser.parse_args()
    existingFiles = args.files

    for line in sys.stdin.readlines():
        for fix in fixes:
            line = fix(line)
        sys.stdout.write(line)
