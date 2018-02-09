# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from subdownloader.client.state import BaseState, SubtitlePathStrategy


class CliState(BaseState):
    def __init__(self, options):
        BaseState.__init__(self, options=options, settings=None)
        self._interactive = options.program.client.cli.interactive,
        self._recursive = options.search.recursive

        self._cli_load_state()

        self.set_subtitle_rename_strategy(options.download.rename_strategy)
        self.set_subtitle_download_path_strategy(SubtitlePathStrategy.SAME)

        # FIXME: log state

    def is_interactive(self):
        return self._interactive

    def is_recursive(self):
        return self._recursive

    def set_recursive(self, recursive):
        self._recursive = True if recursive else False

    def _cli_load_state(self):
        pass
