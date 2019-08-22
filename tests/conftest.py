# -*- coding: utf-8 -*-

from subdownloader.client import add_client_module_dependencies
from subdownloader.client.internationalization import i18n_install


def pytest_sessionstart(session):
    add_client_module_dependencies()
    i18n_install()
