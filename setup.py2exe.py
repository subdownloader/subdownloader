#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    PySlovar - Dictionary written in Python
#    Copyright (C) 2006  Matjaž Drolc
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from distutils.core import setup
import py2exe
	
import glob
setup(name='PySlovar',
	version='0.0.2.9',
	description='Dictionary viever and editor',
	author='Matjaz Drolc',
	author_email='mdrolc@gmail.com',
	url='http://www.pyslovar.org',
	packages=['psctrl', 'pscore', 'psui', 'psui.psWx'],
	package_dir={'psctrl':'psctrl'},
	icon='psctrl/data/pyslovar/icon.ico',
	data_files=[
	('data/pyslovar', glob.glob('psctrl/data/pyslovar/*.html')+['psctrl/data/pyslovar/icon.ico', 'psctrl/data/pyslovar/logo.png']),
	('data/pyslovar/locale', ['psctrl/data/pyslovar/locale/pyslovar.pot']),
	('data/pyslovar/locale/sl/LC_MESSAGES', ['psctrl/data/pyslovar/locale/sl/LC_MESSAGES/pyslovar.po', 'psctrl/data/pyslovar/locale/sl/LC_MESSAGES/pyslovar.mo']),
	('', ['COPYING'])
	],
	windows=[{'script':'pyslovar.py', 'icon_resources':[(1, 'psctrl/data/pyslovar/icon.ico')]}]
	)
