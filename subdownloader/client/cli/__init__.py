# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3


def run(options):
    from subdownloader.client.cli.main import Main
    cli = Main(options)
    cli.start_session()
    return 0
