#!/usr/bin/env python3
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3
# PYTHON_ARGCOMPLETE_OK

import logging
import sys

from subdownloader.client import ClientType, IllegalArgumentException, add_client_module_dependencies
from subdownloader.client.state import BaseState, state_init
from subdownloader.client.configuration import Settings
from subdownloader.client.logger import logging_file_install, logging_install, logging_stream_install
from subdownloader.client.internationalization import i18n_install
from subdownloader.client.arguments import parse_arguments
from subdownloader.client.user_agent import user_agent_init


def main(args=None):
    add_client_module_dependencies()
    logging_stream_install(logging.WARNING)
    state_init()
    logging_file_install(None)
    i18n_install()
    options = parse_arguments(args=args)
    settings = Settings(BaseState.get_default_settings_path())
    logging_install(options.program.log.level, options.program.log.path)
    user_agent_init()

    if options.program.client.type == ClientType.GUI:
        import subdownloader.client.gui
        runner = subdownloader.client.gui.run
    else:  # options.program.client.type == ClientType.CLI:
        import subdownloader.client.cli
        runner = subdownloader.client.cli.run

    try:
        return_code = runner(options, settings)
    except IllegalArgumentException as e:
        sys.stderr.write(e.msg)
        print()
        return_code = 1
    except (EOFError, KeyboardInterrupt):
        return_code = 1
    sys.exit(return_code)


if __name__ == "__main__":
    main()
