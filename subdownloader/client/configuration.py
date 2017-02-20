# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import errno
import logging
import os
import platform

from subdownloader import project

log = logging.getLogger('subdownloader.client.configuration')


def configuration_get_folder():
    """
    Return the folder where user-specific data is stored.
    This depends of the system on which Python is running,
    :return: path to the user-specific configuration data folder
    """
    system = platform.system()
    if system == 'Linux':
        # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
        sys_config_path = os.getenv('XDG_CONFIG_HOME', os.path.expanduser("~/.config"))
    elif system == 'Windows':
        sys_config_path = os.getenv('APPDATA', '')
    else:
        log.error('Unknown system: "{system}" (using default configuration path)'.format(system=system))
        sys_config_path = ''
    log.debug('User-specific system configuration folder="{sys_config_path}"'.format(
        sys_config_path=sys_config_path))
    sys_config = os.path.join(sys_config_path, project.PROJECT_TITLE)
    log.debug('User-specific {project} configuration folder="{sys_config}"'.format(
        project=project.PROJECT_TITLE, sys_config=sys_config))
    return sys_config


"""
This variable holds the user-specific configuration data folder.
"""
CONFIGURATION_FOLDER = configuration_get_folder()


try:
    os.makedirs(CONFIGURATION_FOLDER)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
