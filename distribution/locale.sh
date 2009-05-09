#!/bin/sh

#    Copyright (C) 2007-2009 Ivan Garcia capiscuas@gmail.com
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    see <http://www.gnu.org/licenses/>.

NEW_LANGUAGES=`ls /tmp/launchpad-export/po/ | cut -d '-' -f 2 | cut -d '.' -f 1`
for lang in $NEW_LANGUAGES; do \
  localedir=../locale/$lang/LC_MESSAGES; \
  mkdir -p $localedir
  str_1='/tmp/launchpad-export/po/subdownloader-'
  str_2='.po'
  cp $str_1$lang$str_2 $localedir/subdownloader.po
done

LANGUAGES=`find ../locale/ -maxdepth 1 -mindepth 1 -type d -not -name \.svn -printf "%f "`
for lang in $LANGUAGES; do \
                localedir=../locale/$lang/LC_MESSAGES; \
                msgfmt --directory=../locale $lang/LC_MESSAGES/subdownloader.po --output-file=$localedir/subdownloader.mo; \
done
