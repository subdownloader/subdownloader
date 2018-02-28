# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import configparser
import logging
import os
from pathlib import Path
import platform

from subdownloader.languages.language import Language, UnknownLanguage
from subdownloader.project import PROJECT_TITLE

log = logging.getLogger('subdownloader.client.configuration')


class Settings(object):
    def __init__(self, path):
        self.path = path
        self.cfg = configparser.ConfigParser()
        self.dirty = None

    def get_str(self, section, option, default):
        try:
            return self.cfg.get(section, option)
        except (configparser.NoOptionError, configparser.NoSectionError):
            return default

    def set_str(self, section, option, value):
        try:
            self.cfg.add_section(section)
        except configparser.DuplicateSectionError:
            pass
        self.cfg.set(section, option, value)
        self.dirty = True

    def get_language(self, section, option):
        xxx = self.get_str(section, option, UnknownLanguage.create_generic())
        return Language.from_xxx(xxx)

    def set_language(self, section, option, lang):
        self.set_str(section, option, lang.xxx())

    def get_languages(self, section, option):
        xxxs = self.get_str(section, option, None)
        if xxxs is None:
            return []
        return [Language.from_xxx(lang_str) for lang_str in xxxs.split(',') if lang_str]

    def set_languages(self, section, option, langs):
        self.set_str(section, option, ','.join(l.xxx() for l in langs))

    def get_int(self, section, option, default=None):
        return int(self.get_str(section, option, default))

    def set_int(self, section, option, value):
        self.set_str(section, option, str(value))

    def get_path(self, section, option, default=Path()):
        return Path(self.get_str(section, option, default))

    def set_path(self, section, option, value):
        self.set_str(section, option, str(value))

    def read(self):
        try:
            log.debug('Reading settings from {} ...'.format(self.path))
            self.cfg.read(str(self.path))
            log.debug('... reading finished')
        except configparser.ParsingError:
            log.warning('... Failed to parse settings from "{}". Assuming defaults.'.format(self.path))
        except OSError:  # FileNotFoundError:
            log.debug('... File not found. Assuming defaults.')
        self.dirty = False

    def write(self):
        try:
            log.debug('Writing settings to {} ...'.format(self.path))
            with open(str(self.path), 'w') as f:
                self.cfg.write(f)
            log.debug('... writing finished')
        except PermissionError:
            log.warning('... Writing failed. No permission.')
        self.dirty = False


def configuration_get_default_file():
    """
    Return the default file where user-specific data is stored.
    This depends of the system on which Python is running,
    :return: path to the user-specific configuration data folder
    """
    return (configuration_get_default_folder() / PROJECT_TITLE).with_suffix('.conf')


def configuration_get_default_folder():
    """
    Return the default folder where user-specific data is stored.
    This depends of the system on which Python is running,
    :return: path to the user-specific configuration data folder
    """
    system = platform.system()
    if system == 'Linux':
        # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
        sys_config_path = Path(os.getenv('XDG_CONFIG_HOME', os.path.expanduser("~/.config")))
    elif system == 'Windows':
        sys_config_path = Path(os.getenv('APPDATA', ''))
    else:
        log.error('Unknown system: "{system}" (using default configuration path)'.format(system=system))
        sys_config_path = Path()
    log.debug('User-specific system configuration folder="{sys_config_path}"'.format(
        sys_config_path=sys_config_path))
    sys_config = sys_config_path / PROJECT_TITLE
    log.debug('User-specific {project} configuration folder="{sys_config}"'.format(
        project=PROJECT_TITLE, sys_config=sys_config))
    return sys_config


def configuration_init():
    config_path = configuration_get_default_folder()
    config_path.mkdir(exist_ok=True)
