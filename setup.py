#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import argparse
import gettext
from pathlib import Path
import sys
from setuptools import find_packages, setup

from sphinx.setup_command import BuildDoc

gettext.NullTranslations().install()

import subdownloader.project
project_path = Path(__file__).absolute().parent


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--no-gui', dest='with_gui', action='store_false')
ns, args = parser.parse_known_args()
sys.argv = [sys.argv[0]] + args


def read(filename):
    return (project_path / filename).read_text()


def get_requires(filepath):
    result = []
    with filepath.open("rt") as req_file:
        for line in req_file.read().splitlines():
            if not line.strip().startswith("#"):
                result.append(line)
    return result


requirements = get_requires(project_path / 'requirements.txt')
if ns.with_gui:
    requirements += get_requires(project_path / 'requirements_gui.txt')

setup(
    name=subdownloader.project.PROJECT_TITLE.lower(),
    version=subdownloader.project.PROJECT_VERSION_FULL_STR,
    author=subdownloader.project.PROJECT_AUTHOR_COLLECTIVE,
    author_email=subdownloader.project.PROJECT_MAINTAINER_MAIL,
    maintainer=subdownloader.project.PROJECT_AUTHOR_COLLECTIVE,
    maintainer_email=subdownloader.project.PROJECT_MAINTAINER_MAIL,
    description=subdownloader.project.get_description(),
    keywords=['download', 'upload', 'automatic', 'subtitle', 'movie', 'video', 'film', 'search'],
    license='GPL3',
    packages=find_packages(exclude=('tests', 'tests.*', )),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url=subdownloader.project.WEBSITE_MAIN,
    download_url=subdownloader.project.WEBSITE_RELEASES,
    project_urls={
        'Source Code': subdownloader.project.WEBSITE_MAIN,
        'Bug Tracker': subdownloader.project.WEBSITE_ISSUES,
        'Translations': subdownloader.project.WEBSITE_TRANSLATE,
    },
    classifiers=[
        'Topic :: Multimedia',
        'Topic :: Utilities',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.5, <4',
    provides=[
        'subdownloader'
    ],
    requires=requirements,
    entry_points={
        'console_scripts': [
            'subdownloader = subdownloader.client.__main__:main'
        ],
    },
    include_package_data=True,
    cmdclass={
        'build_sphinx': BuildDoc,
    },
    command_options={
        'build_sphinx': {
            'project': ('setup.py', subdownloader.project.PROJECT_TITLE, ),
            'version': ('setup.py', subdownloader.project.PROJECT_VERSION_STR, ),
            'release': ('setup.py', subdownloader.project.PROJECT_VERSION_FULL_STR, ),
            'builder': ('setup.py', 'man', ),
            'source_dir': ('setup.py', 'doc', ),
        },
    },
)
