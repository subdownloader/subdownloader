# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

from enum import Enum

from subdownloader.client.cli.state import CliState


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
