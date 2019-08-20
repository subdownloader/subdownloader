# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from pathlib import Path
import unittest

from subdownloader.client.configuration import Settings
from subdownloader.languages.language import Language, UnknownLanguage

from tests.util import create_temporary_file


class TestSettings(unittest.TestCase):
    def test_constructor_none(self):
        Settings(None)

    def test_string(self):
        with create_temporary_file() as f:
            f.file.close()
            s1 = Settings(f.name)
            s1.set_str(('section0', 'stringprop'), 'some_text')
            s1.write()
            del s1

            s2 = Settings(f.name)
            s2.reload()
            self.assertEqual('some_text', s2.get_str(('section0', 'stringprop'), None))

            self.assertEqual(None, s2.get_str(('s', 'k'), None))

    def test_path(self):
        with create_temporary_file() as f:
            f.file.close()
            s1 = Settings(f.name)
            s1.set_path(('section1', 'pathprop'), '/some/path')
            s1.write()
            del s1

            s2 = Settings(f.name)
            s2.reload()
            self.assertEqual(Path('/some/path'), s2.get_path(('section1', 'pathprop')))

            self.assertEqual(None, s2.get_path(('s', 'k'), None))

    def test_int(self):
        with create_temporary_file() as f:
            f.file.close()
            s1 = Settings(f.name)
            s1.set_int(('section2', 'intprop'), 1337)
            s1.write()
            del s1

            s2 = Settings(f.name)
            s2.reload()
            self.assertEqual(1337, s2.get_int(('section2', 'intprop'), None))

            self.assertEqual(None, s2.get_int(('s', 'k'), None))

    def test_language(self):
        with create_temporary_file() as f:
            f.file.close()
            s1 = Settings(f.name)
            s1.set_language(('section3', 'langprop'), Language.from_xxx('dut'))
            s1.write()
            del s1

            s2 = Settings(f.name)
            s2.reload()
            self.assertEqual(Language.from_xxx('dut'), s2.get_language(('section3', 'langprop')))

            self.assertEqual(None, s2.get_language(('s', 'k')))

    def test_languages(self):
        with create_temporary_file() as f:
            f.file.close()
            s1 = Settings(f.name)
            s1.set_languages(('section4', 'langsprop'), [Language.from_xxx('spa'), Language.from_xxx('eng')])
            s1.write()
            del s1

            s2 = Settings(f.name)
            s2.reload()
            self.assertListEqual([Language.from_xxx('spa'), Language.from_xxx('eng')], s2.get_languages(('section4', 'langsprop')))

            self.assertEqual(None, s2.get_languages(('s', 'k')))

    def test_clear(self):
        s = Settings(None)
        s.set_int(('section', 'key'), 1337)
        self.assertEqual(1337, s.get_int(('section', 'key'), None))
        s.clear()
        self.assertEqual(None, s.get_int(('section', 'key'), None))
