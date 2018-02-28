# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import importlib
import logging
from pathlib import Path

from subdownloader.provider.provider import SubtitleProvider

log = logging.getLogger('subdownloader.provider.factory')


class NoProviderException(Exception):
    pass


# FIXME: list available providers
class ProviderFactory(object):
    def __init__(self):
        pass

    @classmethod
    def local_search(cls, provider):
        try:
            module_name = 'subdownloader.provider.{provider}'.format(provider=provider)
            log.debug('Attempting to import "{}"...'.format(module_name))
            provider_module = importlib.import_module(module_name)
            log.debug('... OK')
        except ImportError:
            log.debug('... FAILED')
            raise NoProviderException('Unknown provider "{}"'.format(provider))
        try:
            log.debug('Attempting to get "providers" from module...')
            provider_classes = provider_module.providers
            log.debug('... OK')
        except AttributeError:
            log.debug('... FAILED')
            raise NoProviderException('"{}" must provide a "providers" attribute'.format(provider))
        log.debug('Checking provider types:')
        for provider_class in provider_classes:
            log.debug('- {}:'.format(provider_class))
            if not issubclass(provider_class, SubtitleProvider):
                log.debug('... FAILED: not a SubtitleProvider')
                raise NoProviderException('Provider must subclass SubtitleProvider')
            log.debug('... OK')
        return provider_classes

    @classmethod
    def list(cls):
        providers = []
        provider_path = Path(__file__).parent
        for file in provider_path.iterdir():
            if file.suffix != '.py':
                continue
            try:
                providers.extend(cls.local_search(file.stem))
            except NoProviderException:
                continue
        return providers
