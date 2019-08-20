#!/usr/bin/env python3

import unittest

from subdownloader.client.internationalization import i18n_install

i18n_install()

import tests

loader = unittest.TestLoader()
suite = unittest.TestSuite()

tests.suite_add_tests(suite, loader)

runner = unittest.TextTestRunner(verbosity=3)
result=runner.run(suite)
