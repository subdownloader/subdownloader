#!/usr/bin/env python3
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3
# PYTHON_ARGCOMPLETE_OK

import logging
import os
import sys

from subdownloader.client import ClientType, IllegalArgumentException
from subdownloader.client.configuration import configuration_init
from subdownloader.client.logger import logging_file_install, logging_install, logging_stream_install
from subdownloader.client.internationalization import i18n_install
from subdownloader.client.arguments import parse_arguments
from subdownloader.client.user_agent import user_agent_init

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules'))


def main(args=None):
    logging_stream_install(logging.WARNING)
    configuration_init()
    logging_file_install(None)
    i18n_install()
    options = parse_arguments(args=args)
    logging_install(options.program.log.level, options.program.log.path)
    user_agent_init()

    if options.program.client.type == ClientType.GUI:
        import subdownloader.client.gui
        runner = subdownloader.client.gui.run
    else:  # options.program.client.type == ClientType.CLI:
        import subdownloader.client.cli
        runner = subdownloader.client.cli.run

    try:
        return_code = runner(options)
    except IllegalArgumentException as e:
        sys.stderr.write(e.msg)
        print()
        return_code = 1
    except (EOFError, KeyboardInterrupt):
        return_code = 1
    sys.exit(return_code)


if __name__ == "__main__":
    main()
