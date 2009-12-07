#!/bin/sh

# Copyright (c) 2009 SubDownloader Developers - See COPYING - GPLv3

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
