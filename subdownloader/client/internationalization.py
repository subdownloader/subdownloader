# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import gettext
import locale
import logging
import os
import platform

from subdownloader import project
from subdownloader.client import client_get_path

log = logging.getLogger('subdownloader.client.internationalization')


def i18n_install(lc=None):
    """
    Install internationalization support for the clients using the specified locale.
    If there is no support for the locale, the default locale will be used.
    As last resort, a null translator will be installed.
    :param lc: locale to install. If None, the system default locale will be used.
    """
    log.debug('i18n_install( {lc} ) called.'.format(lc=lc))
    if lc is None:
        lc, encoding = locale.getlocale()
        log.debug('locale.getlocale() = (lc="{lc}", encoding="{encoding}).'.format(lc=lc, encoding=encoding))
    if lc is None:
        lc, encoding = locale.getdefaultlocale()
        log.debug('locale.getdefaultlocale() = (lc="{lc}", encoding="{encoding}).'.format(lc=lc, encoding=encoding))
    if lc is None:
        log.debug('i18n_install(): installing NullTranslator')
        gettext.NullTranslations().install()
    else:
        child_locales = i18n_support_locale(lc)  # Call i18n_support_locale to log the supported locales
        # child_locales = i18n_locale_fallbacks_calculate(lc)

        log.debug('i18n_install(): installing gettext.translation(domain={domain}, localedir={localedir}, '
                  'languages={languages}, fallback={fallback})'.format(domain=project.PROJECT_TITLE.lower(),
                                                                       localedir=i18n_get_path(),
                                                                       languages=child_locales,
                                                                       fallback=True))
        gettext.translation(
            domain=project.PROJECT_TITLE.lower(), localedir=i18n_get_path(),
            languages=child_locales, fallback=True).install()


def i18n_locale_fallbacks_calculate(lc):
    """
    Calculate all child locales from a locale.
    e.g. for locale="pt_BR.us-ascii", returns ["pt_BR.us-ascii", "pt_BR.us", "pt_BR", "pt"]
    :param lc: locale for which the child locales are needed
    :return: all child locales (including the parameter lc)
    """
    log.debug('i18n_locale_fallbacks_calculate( locale="{locale}" ) called'.format(locale=lc))
    locales = []
    lc_original = lc
    while lc:
        locales.append(lc)
        rindex = max([lc.rfind(separator) for separator in ['@', '_', '-', '.']])
        if rindex == -1:
            break
        lc = lc[:rindex]
    log.debug('i18n_locale_fallbacks_calculate( lc="{lc}" ) = {locales}'.format(lc=lc_original, locales=locales))
    return locales


def i18n_support_locale(lc_parent):
    """
    Find out whether lc is supported. Returns all child locales (and eventually lc) which do have support.
    :param lc: Locale for which we want to know the child locales that are supported
    :return: list of supported locales
    """
    log.debug('i18n_support_locale( locale="{locale}" ) called'.format(locale=lc_parent))
    lc_childs = i18n_locale_fallbacks_calculate(lc_parent)
    locales = []

    locale_dir = i18n_get_path()
    mo_file = '{project}.mo'.format(project=project.PROJECT_TITLE.lower())

    for lc in lc_childs:
        locale_path = os.path.join(locale_dir, lc, 'LC_MESSAGES')
        log.debug('Locale data in "{locale_path}"?'.format(locale_path=locale_path))
        if os.path.isdir(locale_path) and mo_file in os.listdir(locale_path):
            log.debug('Found! "{locale_path}" contains {mo_file}.'.format(locale_path=locale_path, mo_file=mo_file))
            locales.append(lc)

    log.debug('i18n_support_locale( lc="{lc}" ) = {locales}'.format(lc=lc, locales=locales))
    return locales


def i18n_get_path():
    """
    Get path to the internationalization data.
    :return: path as a string
    """
    local_locale_path = os.path.join(client_get_path(), 'locale')
    if platform.system() == 'Linux':
        if os.path.exists(local_locale_path):
            return local_locale_path
        else:
            return '/usr/share/locale'
    else:
        return local_locale_path


def i18n_get_supported_locales():
    """
    List all locales that have internationalization data for this program
    :return: List of locales
    """
    locale_dir = i18n_get_path()
    log.debug('Scanning translation files .mo in locale folder: {}'.format(locale_dir))
    langs = []
    mo_file = '{project}.mo'.format(project=project.PROJECT_TITLE.lower())
    for lc in os.listdir(locale_dir):
        if os.path.isdir(os.path.join(locale_dir, lc)):
            try:
                locale_path = os.path.join(locale_dir, lc, 'LC_MESSAGES')
                if mo_file in os.listdir(locale_path):
                    langs.append(lc)
            except OSError:
                pass
    log.debug('Detected: {langs}'.format(langs=langs))
    return langs
