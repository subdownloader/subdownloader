#/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import gettext
import os
from setuptools import find_packages, setup

gettext.NullTranslations().install()

import subdownloader.project
project_path = os.path.dirname(os.path.realpath(__file__))


def read(filename):
    return open(os.path.join(project_path, filename)).read()

install_requires = [
    "argparse >= 1.3.0",
    "argcomplete >= 1.7.0",
    "langdetect >= 1.0.7",
    "pyqt5 >= 5.0.0",
    "pymediainfo >= 2.1.6",
]

setup(
    name = subdownloader.project.PROJECT_TITLE,
    version = subdownloader.project.PROJECT_VERSION_STR,
    author = subdownloader.project.PROJECT_AUTHOR_COLLECTIVE,
    author_email = subdownloader.project.PROJECT_MAINTAINER_MAIL,
    description = subdownloader.project.get_description(),
    keywords = "download upload automatic subtitle download movie video film search",

    url = subdownloader.project.WEBSITE_MAIN,
    license="COPYING",
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
        "Topic :: Multimedia",
        "Topic :: Utilities",
        "Environment :: Console",
        "Environment :: X11 Applications :: Qt",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
    ],
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "subdownloader = subdownloader.client.__main__:main"
        ],
    },
    include_package_data=True,
)
