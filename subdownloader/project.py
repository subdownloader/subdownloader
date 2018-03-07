# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import os

"""
Name of the project.
Forks MUST change this to a non-ambiguous alternative.
"""
PROJECT_TITLE = "SubDownloader"

"""
Version of the project as a tuple.
"""
PROJECT_VERSION = (2, 1, 0)

"""
Full version of the project as a tuple.
"""
PROJECT_VERSION_FULL = PROJECT_VERSION + ('rc3', )

"""
Version of the project as a string.
"""
PROJECT_VERSION_STR = ".".join([str(i) for i in PROJECT_VERSION])

"""
Full version of the project as a string.
"""
PROJECT_VERSION_FULL_STR = PROJECT_VERSION_STR + PROJECT_VERSION_FULL[-1]

"""
License of the project
"""
PROJECT_LICENSE = "GPLv3"

"""
Year of last change.
"""
PROJECT_YEAR = 2018

"""
Author collective name
"""
PROJECT_AUTHOR_COLLECTIVE = "{title} Developers".format(title=PROJECT_TITLE)

"""
Maintainer e-mail address
"""
PROJECT_MAINTAINER_MAIL = "anonymous.maarten@gmail.com"


WEBSITE_MAIN = 'https://github.com/subdownloader/subdownloader'
WEBSITE_HELP = 'https://github.com/subdownloader/subdownloader'
WEBSITE_ISSUES = 'https://github.com/subdownloader/subdownloader/issues'
WEBSITE_RELEASES = 'https://github.com/subdownloader/subdownloader/releases'
WEBSITE_TRANSLATE = 'https://github.com/subdownloader/subdownloader-i18n'


def get_description():
    """
    Get description of the project.
    :return: description as a string
    """
    return _('{project} is a Free Open-Source tool written in PYTHON '
             'for automatic download/upload subtitles for videofiles '
             '(DIVX,MPEG,AVI,etc) and DVD\'s using fast hashing.'.format(project=PROJECT_TITLE))


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
