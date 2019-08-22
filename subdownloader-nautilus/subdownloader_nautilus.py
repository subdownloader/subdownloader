# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import gettext
import subprocess

try:
    from shutil import which as find_executable
except ImportError:
    from distutils.spawn import find_executable

from gi.repository import Nautilus, GObject

SUBDOWNLOADER_PATH = find_executable('subdownloader')

if SUBDOWNLOADER_PATH:
    translator = gettext.translation(domain='SubDownloader', fallback=True)
    translator.install()

    class SubDownloaderMenu(GObject.GObject, Nautilus.MenuProvider):
        def __init__(self):
            pass

        def get_file_items(self, window, files):
            subdownloader_menu = Nautilus.MenuItem(
                name='SubDownloaderMenu::SubDownloader',
                label=_('Search SubDownloader...'),
                tip=_('Launch SubDownloader with these files.'),
            )
            subdownloader_menu.connect('activate', self.search_subdownloader, files)

            return [subdownloader_menu, ]

        def get_background_items(self, window, file):
            return []

        def start_subdownloader(self, paths):
            args = [
                SUBDOWNLOADER_PATH,
                '--gui',
                '--error',
                '-V',
            ]
            args.extend((str(p) for p in paths))
            return subprocess.Popen(args)

        def search_subdownloader(self, menu, files):
            paths = list(file.get_location().get_path() for file in files)
            self.start_subdownloader(paths)
