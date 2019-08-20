# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import io
from pathlib import Path
import unittest

from subdownloader.client.cli import get_default_options
from subdownloader.client.cli.cli import CliCmd
from subdownloader.client.cli.state import CliState
from subdownloader.client.configuration import Settings

from tests.util import create_temporary_file
from tests.resources import RESOURCE_PATH, RESOURCE_AVI


class TestCli(unittest.TestCase):
    def setUp(self):
        self.state = CliState()
        self.temp_file = create_temporary_file()
        self.settings = Settings(self.temp_file.file)
        self.stdin = io.StringIO()
        self.stdout = io.StringIO()
        self.options = get_default_options()
        self.cli = CliCmd(self.state, self.options)
        self.cli.stdin = self.stdin
        self.cli.stdout = self.stdout

    def assertValidHelp(self, stream):
        txt = stream.getvalue()
        self.assertFalse(self.cli.nohelp in txt)
        self.assertGreater(len(txt), 0)

    def assertValidSyntax(self, stream):
        txt = stream.getvalue()
        self.assertFalse('Unknown syntax' in txt)

    def clearStream(self, stream):
        stream.seek(0)
        stream.truncate()

    @unittest.skip  # FIXME: re-enable test!
    def test_help(self):
        self.cli.onecmd('help')
        txt = self.stdout.getvalue()
        self.assertGreater(len(txt), 0)
        self.assertFalse(self.cli.undoc_header in txt, 'Undocumented items exist')
        self.assertValidSyntax(self.stdout)
        self.clearStream(self.stdout)

    def test_quit(self):
        self.cli.onecmd('help quit')
        self.assertValidHelp(self.stdout)
        self.assertValidSyntax(self.stdout)
        self.clearStream(self.stdout)

        self.assertNotEqual(0, self.cli.return_code)
        self.cli.onecmd('quit')
        self.assertValidSyntax(self.stdout)
        self.assertEqual(0, self.cli.return_code)
        self.clearStream(self.stdout)

    def test_loop(self):
        self.cli.cmdqueue += ['quit', ]
        self.cli.cmdloop()
        self.assertValidSyntax(self.stdout)
        self.assertEqual(0, self.cli.return_code)

    def test_filescan_dir(self):
        self.filescan_tester((RESOURCE_PATH, ))

    def test_filescan_file(self):
        self.filescan_tester((RESOURCE_AVI, ))

    def filescan_tester(self, paths):
        self.cli.onecmd('help filescan')
        self.assertValidHelp(self.stdout)
        self.assertValidSyntax(self.stdout)
        self.clearStream(self.stdout)

        str_paths = ' '.join('"{}"'.format(path) for path in paths)
        for cmd in ('filepath {}'.format(str_paths), 'filescan', ):
            self.cli.onecmd(cmd)
        self.assertValidSyntax(self.stdout)

        self.clearStream(self.stdout)
        self.cli.onecmd('videos')
        self.assertValidSyntax(self.stdout)
        self.stdout.seek(0)
        lines = self.stdout.readlines()
        self.assertGreater(len(lines), 1)
