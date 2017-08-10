#!/usr/bin/env python3
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

from subdownloader.project import PROJECT_TITLE, PROJECT_VERSION_STR

from subdownloader.provider import opensubtitles


def user_agent_init():
    opensubtitles.set_default_user_agent('{title} {version}'.format(title=PROJECT_TITLE, version=PROJECT_VERSION_STR))
