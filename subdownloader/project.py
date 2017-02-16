# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import os

TITLE = 'SubDownloader'
VERSION = '2.0.19'


WEBSITE_MAIN = 'https://github.com/subdownloader/subdownloader'
WEBSITE_HELP = 'https://github.com/subdownloader/subdownloader'
WEBSITE_ISSUES = 'https://github.com/subdownloader/subdownloader/issues'
WEBSITE_RELEASES = 'https://github.com/subdownloader/subdownloader/releases'
WEBSITE_TRANSLATE = 'http://www.subdownloader.net/translate.html'


class Author(object):
    def __init__(self, name, mail):
        self._name = name
        self._mail = mail

    def name(self):
        return self._name

    def mail(self):
        return self._mail

    def __repr__(self):
        return '{name} ({mail})'.format(
            name=self.name(),
            mail=self.mail()
        )


def subdownloader_path():
    """
    Get the path of the subdownloader library
    :return: string of the path
    """
    return os.path.dirname(os.path.realpath(__file__))


def read_authors():
    result = []
    authormails_str = open(os.path.join(subdownloader_path(), 'AUTHORS'), 'r').read()
    for authormail_str in authormails_str.split('\n'):
        try:
            name, mail = authormail_str.split(':')
            result.append(Author(name, mail))
        except ValueError:
            pass
    return result
