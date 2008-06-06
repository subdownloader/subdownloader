#!/usr/bin/env python
# -*- coding: utf8 -*-

##    Copyright (C) 2007 Ivan Garcia contact@ivangarcia.org
##    This program is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License along
##    with this program; if not, write to the Free Software Foundation, Inc.,
##    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from distutils.core import setup
#import py2exe
    
import glob
setup(name='SubDownloader',
    version='2.0.1',
    description='Find Subtitles for your Videos',
    author='Ivan Garcia',
    author_email='contact@ivangarcia.org',
    url='http://www.subdownloader.net',
    packages=['ola'],
    #packages=['FileManagement', 'cli', 'gui', 'languages', 'modules'],
    package_dir={'subdownloader':'.'},
    #icon='psctrl/data/pyslovar/icon.ico',
    data_files=[
    ('gui/images', glob.glob('gui/images/*.png')+glob.glob('gui/images/*.ico')+glob.glob('gui/images/*.jpg')+['gui/images/subd_splash.gif']),
    ('gui/images/flags', glob.glob('gui/images/flags/*.gif')),
    ('languages/lm', glob.glob('languages/lm/*.lm')),
    ('', ['README'])
    ],
    #windows=[{'script':'run.py', 'icon_resources':[(1, 'psctrl/data/pyslovar/icon.ico')]}]
    )
