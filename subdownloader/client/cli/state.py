# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from pathlib import Path

from subdownloader.client.state import BaseState, SubtitlePathStrategy


class CliState(BaseState):
    def __init__(self):
        BaseState.__init__(self)

        self._interactive = False
        self._console = False
        self._recursive = False

        self.set_subtitle_download_path_strategy(SubtitlePathStrategy.SAME)

        # FIXME: log state

    def load_settings(self, settings):
        # BaseState.load_settings(settings)
        # Do not load settings from file in cli
        pass

    def load_options(self, options):
        BaseState.load_options(self, options)

        self._console = options.program.client.cli.console
        self._interactive = options.program.client.cli.interactive
        self._list_languages = options.program.client.cli.list_languages

        self._recursive = options.search.recursive

        self.set_subtitle_naming_strategy(options.download.naming_strategy)

    def get_console(self):
        return self._console

    def get_interactive(self):
        return self._interactive

    def get_list_languages(self):
        return self._list_languages

    def get_recursive(self):
        return self._recursive

    def set_recursive(self, recursive):
        self._recursive = recursive
