# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from enum import Enum

from subdownloader.client.cli.state import CliState


def get_default_settings(video_path=None):
    from subdownloader.client.arguments import get_default_argument_settings, ArgumentClientSettings, ArgumentClientCliSettings, ClientType
    return get_default_argument_settings(
        video_path=video_path,
        client=ArgumentClientSettings(
            type=ClientType.GUI,
            cli=ArgumentClientCliSettings(
                interactive=False,
            ),
            gui=None,
        )
    )

class CliAction(Enum):
    DOWNLOAD = 'download'
    UPLOAD = 'upload'
    # LIST = 'list'


def run(options):
    from subdownloader.client.cli.cli import CliCmd

    state = CliState(options)

    cmd = CliCmd(state=state)
    try:
        cmd.cmdloop()
    except (EOFError, KeyboardInterrupt):
        state.logout()
        raise
    # FIXME; do actions depending on options.operation

    return cmd.return_code
