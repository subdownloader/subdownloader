# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import unittest

from tests.resources import resources_init, RESOURCE_AVI, RESOURCE_PATH

from subdownloader.video2 import VideoFile, NotAVideoException
from subdownloader.metadata import available as metadata_available


class TestVideofile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        resources_init()
        cls.RESOURCE_NE = RESOURCE_PATH / 'NON_EXISTING_MOVIE.mp4'

    def setUp(self):
        self.v = VideoFile(RESOURCE_AVI)

    def test_filepath(self):
        self.assertEqual(self.v.get_filepath(), RESOURCE_AVI)

    def test_folderpath(self):
        self.assertEqual(self.v.get_folderpath(), RESOURCE_AVI.parent)

    def test_nonexisting(self):
        with self.assertRaises(NotAVideoException):
            VideoFile(self.RESOURCE_NE)

    def test_size(self):
        self.assertEqual(self.v.get_size(), 12909756)

    def test_osdb_hash(self):
        self.assertEqual(self.v.get_osdb_hash(), '8e245d9679d31e12')

    @unittest.skipIf(not metadata_available(), 'Metadata not available')
    def test_metadata(self):
        self.assertAlmostEqual(self.v.get_fps(), 23.97, places=1)

    def test_subtitles_initial(self):
        self.assertListEqual(self.v.get_subtitles().get_subtitle_networks(), [])
