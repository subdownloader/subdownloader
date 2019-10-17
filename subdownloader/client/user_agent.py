# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from subdownloader.project import PROJECT_TITLE, PROJECT_VERSION_FULL_STR


def user_agent_init():
    from subdownloader.provider import opensubtitles
    opensubtitles.set_default_user_agent('{title} {version}'.format(title=PROJECT_TITLE, version=PROJECT_VERSION_FULL_STR))
