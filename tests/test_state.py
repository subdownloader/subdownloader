# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import unittest

from subdownloader.client.arguments import get_argument_options
from subdownloader.client.state import BaseState
from subdownloader.client.configuration import Settings

from tests.util import create_temporary_directory


class TestBaseState(unittest.TestCase):
    def setUp(self):
        self.tempdir = create_temporary_directory()
        self.settings_path = self.tempdir.path / 'SubDownloader.conf'
        self.state = BaseState()
        self.settings = Settings(self.settings_path)

    def tearDown(self):
        del self.tempdir
        del self.settings_path
        del self.state
        del self.settings

    def test_paths(self):
        BaseState.get_default_settings_folder()

    def test_default_video_paths(self):
        self.assertListEqual([], self.state.get_video_paths())

    def test_save_load(self):
        self.assertListEqual([], list(self.tempdir.path.iterdir()))
        self.state.save_settings(self.settings)
        self.assertListEqual([self.settings_path], list(self.tempdir.path.iterdir()))

        copyState = BaseState()
        copyState.load_settings(self.settings)
