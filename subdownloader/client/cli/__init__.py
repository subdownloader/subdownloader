# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from enum import Enum


def get_default_options():
    from subdownloader.client.arguments import get_argument_options, ArgumentClientSettings, \
        ArgumentClientCliSettings, ClientType
    return get_argument_options(
        client=ArgumentClientSettings(
            type=ClientType.CLI,
            cli=ArgumentClientCliSettings(
                console=False,
                interactive=None,
                list_languages=False,
            ),
            gui=None,
        )
    )


class CliAction(Enum):
    DOWNLOAD = 'download'
    UPLOAD = 'upload'
    # LIST = 'list'


def run(options, settings):
    from subdownloader.client.cli.cli import CliCmd

    cmd = CliCmd(options=options, settings=settings)
    try:
        cmd.run()
    except (EOFError, KeyboardInterrupt):
        cmd.cleanup()
        raise
    # FIXME; do actions depending on options.operation

    return cmd.return_code
