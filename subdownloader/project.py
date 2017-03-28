# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import os

"""
Name of the project.
Forks MUST change this to a non-ambiguous alternative namex.
"""
PROJECT_TITLE = 'SubDownloader'


"""
Tuple, containing the version of the project.
"""
PROJECT_VERSION = (2, 0, 19)

"""
String, containing the version of the project.
"""
PROJECT_VERSION_STR = ".".join([str(i) for i in PROJECT_VERSION])

"""
Year of last change.
"""
PROJECT_YEAR = 2017


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

DEVELOPERS = [
    Author('Ivan Garcia', 'ivangarcia@subdownloader.net'),
    Author('Marco Ferreira', 'mferreira@subdownloader.net'),
    Author('Marco Rodrigues', 'gothicx@gmail.com'),
    Author('Anonymous Maarten', 'anonymous.maarten@gmail.com'),
    Author('Sergio Basto', 'sergio@serjux.com'),
    ]

TRANSLATORS = [
]

def subdownloader_path():
    """
    Get the path of the subdownloader library
    :return: string of the path
    """
    return os.path.dirname(os.path.realpath(__file__))
