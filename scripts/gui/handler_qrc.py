# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
from pathlib import Path
from subprocess import check_output
from xml.etree.ElementTree import parse as parse_xml


log = logging.getLogger('generate.qrc')

PYRCC = 'pyrcc5'

self_mtime = Path(__file__).lstat().st_mtime


class QrcFile(object):
    FUNCTION_NAME = 'register_resources'

    def __init__(self, source, target):
        self.source = source
        self.target = target

    @staticmethod
    def generate_target(source):
        src = Path(source)
        return src.parent / (src.stem + '_rc.py')

    def target_outdated(self):
        outdated = False
        error = False

        if not self.source.exists():
            log.error('File {} does not exist.'.format(self.source))
            raise ValueError('Fatal error.')

        if self.target.exists():
            if self_mtime > self.target.lstat().st_mtime:
                outdated = True

            target_mtime = self.target.lstat().st_mtime
            if self.source.lstat().st_mtime > target_mtime:
                outdated = True
        else:
            target_mtime = -1
            outdated = True

        files = [Path(file.text) for file in parse_xml(self.source).findall('./qresource/file')]
        for file in files:
            real_file = self.source.parent / file
            if not real_file.exists():
                log.error('File {} does not exist. (defined in {})'.format(file, self.source))
                error = True
            if real_file.lstat().st_mtime > target_mtime:
                outdated = True

        if error:
            raise ValueError('Fatal error.')

        return outdated

    def run(self, dry):
        args = [PYRCC, str(self.source), '-o', str(self.target), '-name', self.FUNCTION_NAME]
        log.info('Running {}'.format(args))
        if not dry:
            check_output(args)

    def clean(self, dry):
        log.info('Removing {}'.format(self.target))
        if not dry:
            self.target.unlink()