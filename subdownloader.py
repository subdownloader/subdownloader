#!/usr/bin/env python
# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3
# PYTHON_ARGCOMPLETE_OK

import os
import sys

from subdownloader.client.configuration import install_i18n_early, install_logger, parse_args

sys.path.append(os.path.join(sys.path[0], 'modules'))

install_i18n_early()
options = parse_args()
install_logger(options.loglevel, options.logfile)

if options.mode == 'gui':
    import subdownloader.client.gui.main
    subdownloader.client.gui.main.main(options)
elif options.mode == 'cli':
    import subdownloader.client.cli.main
    cli = subdownloader.client.cli.main.Main(options)
    cli.start_session()
