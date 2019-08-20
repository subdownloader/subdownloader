# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from pathlib import Path
import unittest

from tests.resources import resources_init, RESOURCE_AVI, RESOURCE_PATH
from tests.util import ChangeDirectoryScope

from subdownloader.callback import ProgressCallback
from subdownloader.filescan import scan_videopath


class TestFileScan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        resources_init()

    def test_scan_videopath_no_vid(self):
        videos, subtitles = scan_videopath(Path(__file__).resolve().parent, ProgressCallback(), recursive=False)
        self.assertTrue(len(videos) == 0)

    def test_scan_videopath(self):
        videos, subtitles = scan_videopath(RESOURCE_PATH, ProgressCallback(), recursive=False)
        video = next(video for video in videos if video.get_filepath().resolve() == RESOURCE_AVI)

    def test_scan_videopath_recursive(self):
        videos, subtitles = scan_videopath(Path(__file__).resolve().parent, ProgressCallback(), recursive=True)
        video = next(video for video in videos if video.get_filepath().resolve() == RESOURCE_AVI)

    def test_scan_videopath_recursive_relative_current(self):
        with ChangeDirectoryScope(Path(__file__).resolve().parent):
            videos, subtitles = scan_videopath(Path('.'), ProgressCallback(), recursive=True)
            self.assertTrue(len(videos) > 0)
            video = next(video for video in videos if video.get_filepath().resolve() == RESOURCE_AVI)

    def test_scan_videopath_recursive_relative_parent(self):
        with ChangeDirectoryScope((RESOURCE_PATH / 'child')):
            videos, subtitles = scan_videopath(Path('..'), ProgressCallback(), recursive=True)
            self.assertTrue(len(videos) > 0)
            video = next(video for video in videos if video.get_filepath().resolve() == RESOURCE_AVI)
