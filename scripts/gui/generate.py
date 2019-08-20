#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import sys

if sys.version_info < (3, 4):
    print('This generator only supports Python 3.4+')
    sys.exit(1)

import logging
from pathlib import Path

from handler_ui import UiFile
from handler_qrc import QrcFile

logging.root.setLevel(logging.NOTSET)
logging.root.addHandler(logging.StreamHandler())
log = logging.getLogger('generate')
log.setLevel(logging.INFO)

qrc_files = [
    'images.qrc',
]

ui_files = [
    'about.ui',
    'imdbSearch.ui',
    'login.ui',
    'main.ui',
    'preferences.ui',
    'searchFileWidget.ui',
    'searchNameWidget.ui',
    'uploadWidget.ui',
]

default_import_from = 'subdownloader.client.gui'


def generate(command='run', import_from=default_import_from, dry=False, targets=list(), force=False):
    source_dir = Path(__file__).absolute().parent
    ui_source_dir = source_dir / 'ui'
    rc_source_dir = source_dir / 'rc'

    target_dir = Path(__file__).absolute().parents[2] / 'subdownloader' / 'client' / 'gui' / 'generated'

    actions = set()
    if not targets:
        actions.update(QrcFile(source=rc_source_dir / qrc, target=target_dir / QrcFile.generate_target(qrc)) for qrc in qrc_files)
        actions.update(UiFile(source=ui_source_dir / ui, target=target_dir / UiFile.generate_target(ui), import_from=import_from) for ui in ui_files)
    else:
        for target in targets:
            target = Path(target)
            if target.suffix != '.py':
                log.error('Fatal error: target "{}" must be a python file.'.format(target))
                sys.exit(1)
            if target.stem.endswith('_rc'):
                source = source_dir / 'rc' / Path(target.stem[:-3]).with_suffix('.qrc')
                actions.add(QrcFile(source=source, target=target))
            elif target.stem.endswith('_ui'):
                source = source_dir / 'ui' / Path(target.stem[:-3]).with_suffix('.ui')
                actions.add(UiFile(source=source, target=target, import_from=import_from))
            else:
                log.error('Unknown target type: "{}"'.format(target))
                sys.exit(1)

    errors = set()
    outdated = set()

    self_mtime = Path(__file__).lstat().st_mtime

    for action in actions:
        try:
            if force:
                outdated.add(action)
            if action.target.exists() and self_mtime > action.target.lstat().st_mtime:
                outdated.add(action)
            if action.target_outdated():
                outdated.add(action)
                log.debug('"{}" is outdated.'.format(action.target))
        except ValueError:
            errors.add(action)

    if errors:
        log.error('Fatal error: {}'.format(' '.join('"{}"'.format(e.source) for e in errors)))
        sys.exit(1)

    if command is 'run':
        for to_run in outdated:
            to_run.run(dry)
    elif command is 'clean':
        for action in actions:
            action.clean(dry)
    else:
        log.error('Unknown command "{}"'.format(command))
        sys.exit(1)

    log.info('Finished')


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Generate')

    parser.add_argument('-d', '--dry-run', dest='dry', action='store_true', help='Determine dependencies. Do not generate targets.')
    parser.add_argument('--import-from', metavar='MODULE', default=default_import_from, help='Module of the gui files. (default="{}")'.format(default_import_from))
    parser.add_argument('-F', '--force', dest='force', action='store_true', help='Force generation of targets.')

    action = parser.add_mutually_exclusive_group()
    action.add_argument('-R', '--run', dest='command', action='store_const', const='run', default='run', help='Run default target. (default)')
    action.add_argument('-C', '--clean', dest='command', action='store_const', const='clean', help='Clean all targets.')

    parser.add_argument('targets', metavar='TARGET', nargs='*', help='File to generate.')

    args = parser.parse_args()
    generate(command=args.command, import_from=args.import_from, dry=args.dry, targets=args.targets, force=args.force)


if __name__ == '__main__':
    main()
