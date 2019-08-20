# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from subdownloader.client import add_client_module_dependencies
from subdownloader.client.internationalization import i18n_install


def load_tests(loader, suite, pattern):
    add_client_module_dependencies()
    i18n_install()
    suite_add_tests(suite, loader)
    return suite


def suite_add_tests(suite, loader):
    import tests.test_cli
    import tests.test_filescan
    import tests.test_videofile
    import tests.test_settings
    import tests.test_state

    suite.addTests(loader.loadTestsFromModule(tests.test_filescan))
    suite.addTests(loader.loadTestsFromModule(tests.test_videofile))
    suite.addTests(loader.loadTestsFromModule(tests.test_settings))
    suite.addTests(loader.loadTestsFromModule(tests.test_state))
    suite.addTests(loader.loadTestsFromModule(tests.test_cli))
