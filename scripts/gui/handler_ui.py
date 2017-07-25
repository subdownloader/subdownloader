# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
from pathlib import Path
import re
from subprocess import check_output


log = logging.getLogger('generate.ui')

PYUIC = 'pyuic5'

self_mtime = Path(__file__).lstat().st_mtime


class UiFile(object):
    def __init__(self, source, target, import_from):
        self.source = source
        self.target = target
        self.import_from = import_from

    @staticmethod
    def generate_target(source):
        src = Path(source)
        return src.parent / (src.stem + '_ui.py')

    def target_outdated(self):
        outdated = False
        error = False

        if not self.source.exists():
            error = True
            log.error('File {} does not exist.'.format(self.source))

        if error:
            raise ValueError('Fatal error.')

        if self.target.exists():
            if self_mtime > self.target.lstat().st_mtime:
                outdated = True

            if self.source.lstat().st_mtime > self.target.lstat().st_mtime:
                outdated = True
        else:
            outdated = True

        return outdated

    def run(self, dry):
        args = [PYUIC, str(self.source), '--import-from', self.import_from]
        log.info('Running {}'.format(args))
        if not dry:
            output = check_output(args)
            fixed = self.fix_translations(output)
            with open(self.target, 'wb') as f:
                f.write(fixed)

    def clean(self, dry):
        log.info('Removing {}'.format(self.target))
        if not dry:
            self.target.unlink()

    @classmethod
    def fix_translations(cls, text):
        new_string, _ = re.subn(b'_translate\(".*?",\s(".*?")\s*?\)', b'_(\g<1>)', text)
        return new_string
