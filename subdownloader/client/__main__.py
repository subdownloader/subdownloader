#!/usr/bin/env python3
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3
# PYTHON_ARGCOMPLETE_OK

import os
import sys

from subdownloader.client.logger import logging_file_install, logging_install
from subdownloader.client.internationalization import i18n_install
from subdownloader.client.arguments import parse_arguments

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules'))


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    logging_file_install(None)
    i18n_install()
    options = parse_arguments(args=args)
    logging_install(options.loglevel, options.logfile)

    if options.mode == 'gui':
        import subdownloader.client.gui
        runner = subdownloader.client.gui.run
    elif options.mode == 'cli':
        import subdownloader.client.cli
        runner = subdownloader.client.cli.run

    return_code = runner(options)
    sys.exit(return_code)

if __name__ == "__main__":
    main()
