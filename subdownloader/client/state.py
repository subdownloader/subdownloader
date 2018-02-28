# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from collections import namedtuple
from enum import Enum
import logging
import os.path
from pathlib import Path

from subdownloader.client import ClientType, IllegalArgumentException
from subdownloader.client.configuration import Settings, configuration_get_default_file
from subdownloader.client.internationalization import i18n_system_locale, i18n_locale_fallbacks_calculate
from subdownloader.languages.language import Language, NotALanguageException, UnknownLanguage
from subdownloader.provider.factory import NoProviderException, ProviderFactory

log = logging.getLogger('subdownloader.client.state')


Proxy = namedtuple('Proxy', ('host', 'port'))

ProviderData = namedtuple('ProviderData', ('provider', 'kwargs'))


def filter_providers(providers_cls, providers_data):
    map_provider_settings = {}

    for provider_data_name, provider_data in providers_data.items():
        provider_data_name = provider_data_name.lower()
        for provider_cls in providers_cls:
            if provider_data_name == provider_cls.get_name().lower():
                map_provider_settings[provider_cls] = provider_data
                break
        else:
            raise IllegalArgumentException(_('Unknown provider "{}"').format(provider_data_name))

    return map_provider_settings


class SubtitleRenameStrategy(Enum):
    VIDEO = 'SAME_VIDEO'
    VIDEO_LANG = 'SAME_VIDEOPLUSLANG'
    VIDEO_LANG_UPLOADER = 'SAME_VIDEOPLUSLANGANDUPLOADER'
    ONLINE = 'SAME_ONLINE'


class SubtitlePathStrategy(Enum):
    ASK = 'ASK_FOLDER'
    SAME = 'SAME_FOLDER'
    PREDEFINED = 'PREDEFINED_FOLDER'

# FIXME: add more logging


class BaseState(object):
    def __init__(self, options, settings=None):
        settings_path = options.program.settings.path if options.program.settings.path else configuration_get_default_file()

        if settings is None:
            settings = Settings(path=settings_path)
        self.settings = settings

        self._video_paths = None

        self._upload_language = None
        self._download_languages = None

        self._rename_strategy = None
        self._download_path_strategy = None
        self._default_download_path = None

        self._proxy = None
        providers_cls = ProviderFactory.list()
        if options.providers:
            map_provider_data = filter_providers(providers_cls, options.providers)
        else:
            map_provider_data = {provider_cls: ProviderData(provider_cls.get_name(), dict()) for provider_cls in providers_cls}
        self._providers = [provider_cls() for provider_cls in map_provider_data.keys()]

        self._client_load_state()

        if options.search.working_directory:
            self.set_video_paths(options.search.working_directory)
        elif options.program.client.type == ClientType.CLI:
            self.set_video_paths([Path().absolute()])

        if not options.filter.languages[0].is_generic():
            self.set_upload_language(options.filter.languages[0])
            self.set_download_languages(options.filter.languages)

        if options.proxy:
            self.set_proxy(options.proxy)

        for provider in self._providers:
            provider_settings = provider.get_settings()
            dict_settings = provider_settings.as_dict()
            dict_settings.update(map_provider_data[type(provider)].kwargs)
            try:
                new_settings = provider_settings.load(**dict_settings)
            except TypeError:
                raise IllegalArgumentException(_('Provider "{}" received an unsupported keyword.').format(
                    provider.get_name()))
            provider.set_settings(new_settings)

    def _client_load_state(self):
        self.settings.read()

        self._video_paths = [self.settings.get_path('mainwindow', 'workingDirectory', Path().absolute())]

        self._upload_language = self.settings.get_language('options', 'uploadLanguage')
        self._download_languages = self.settings.get_languages('options', 'filterSearchLang')

        self._rename_strategy = SubtitleRenameStrategy.VIDEO
        strategy_str = self.settings.get_str('options', 'subtitleName', SubtitleRenameStrategy.VIDEO.value).upper()
        for strategy in SubtitleRenameStrategy:
            if strategy_str == strategy.value.upper():
                self._rename_strategy = strategy

        self._download_path_strategy = SubtitlePathStrategy.SAME
        strategy_str = self.settings.get_str('options', 'whereToDownload', SubtitlePathStrategy.SAME.value).upper()
        for strategy in SubtitlePathStrategy:
            if strategy_str == strategy.value.upper():
                self._download_path_strategy = strategy

        self._default_download_path = self.settings.get_path('options', 'whereToDownloadFolder')

        for provider in self._providers:
            self._client_load_provider(provider)
        
        proxy_host = self.settings.get_str('options', 'ProxyHost', None)
        if proxy_host is not None:
            proxy_port = self.settings.get_int('options', 'ProxyPort', 8080)
            self._proxy = Proxy(proxy_host, proxy_port)

        # FIXME: log state

    def _client_load_provider(self, provider):
        section = 'provider_{name}'.format(name=provider.get_name())
        provider_settings = provider.get_settings()
        new_provider_data = {}
        for k, v in provider_settings.as_dict().items():
            d = self.settings.get_str(section, k, None)
            if d is None:
                d = v
            new_provider_data[k] = d
        new_data = provider_settings.load(**new_provider_data)
        provider.set_settings(new_data)

    def save_state(self):
        self.settings.write()

    def get_providers(self):
        return self._providers

    def _item_to_providers(self, item):
        if item is None:
            providers = self._providers
        else:
            provider = self.provider_search(item)
            if provider is None:
                raise IndexError()
            providers = (provider, )
        return providers

    def provider_search(self, item=None):
        if isinstance(item, str):
            def condition(provider, name):
                return provider.get_name() == name
        else:
            def condition(provider, other):
                return provider == other
        try:
            provider = next(provider for provider in self._providers if condition(provider, item))
        except StopIteration:
            return None
        return provider

    def provider_add(self, name):
        for provider in self._providers:
            if provider.get_name() == name:
                return False
        try:
            providers_cls = ProviderFactory.local_search(name)
            if len(providers_cls) != 1:
                return False
            provider_cls = providers_cls[0]
        except NoProviderException:
            return False

        provider = provider_cls()
        self._client_load_provider(provider)
        self._providers.append(provider)
        return True

    def provider_remove(self, item):
        provider = self.provider_search(item)
        if provider is None:
            return False
        self._providers.remove(provider)
        return True

    def provider_get(self, index):
        if isinstance(index, str):
            try:
                return next(provider for provider in self._providers if provider.get_name().lower() == index.lower())
            except StopIteration:
                raise IndexError()
        else:
            try:
                return next(provider for provider in self._providers if type(provider) == index)
            except StopIteration:
                raise IndexError()

    def connect(self, item=None):
        for provider in self._item_to_providers(item):
            provider.connect()

    def disconnect(self, item=None):
        for provider in self._item_to_providers(item):
            provider.disconnect()

    def login(self, item=None):
        for provider in self._item_to_providers(item):
            provider.login()

    def logout(self, item=None):
        for provider in self._item_to_providers(item):
            provider.logout()

    def ping(self, item=None):
        for provider in self._item_to_providers(item):
            provider.ping()

    def search_videos_all(self, videos, callback):
        callback.set_range(0, len(self._providers))
        prov_rsubs = {}
        for provider_i, provider in enumerate(self._providers):
            download_callback = callback.get_child_progress(provider_i, provider_i+1)
            prov_rsubs[provider] = provider.search_videos(videos=videos, callback=download_callback)
        return prov_rsubs

    def query_text_all(self, text):
        from subdownloader.query import SubtitlesTextQuery
        query = SubtitlesTextQuery(text=text)
        query.search_init(self._providers)
        return query

    def get_video_paths(self):
        return self._video_paths

    def set_video_paths(self, video_paths, write=False):
        self._video_paths = video_paths
        if write:
            self.settings.set_path('mainwindow', 'workingDirectory', video_paths[0])

    # FIXME: change to filter languages?
    def get_download_languages(self):
        return self._download_languages

    def set_download_languages(self, langs, write=False):
        self._download_languages = langs
        if write:
            self.settings.set_languages('options', 'filterSearchLang', langs)

    def get_upload_language(self):
        return self._upload_language

    def set_upload_language(self, lang, write=False):
        self._upload_language = lang
        if write:
            self.settings.set_language('options', 'uploadLanguage', lang)

    def get_proxy(self):
        return self._proxy

    def set_proxy(self, proxy, write=False):
        self._proxy = proxy
        if write:
            self.settings.set_str('options', 'ProxyHost', proxy.host)
            self.settings.set_int('options', 'ProxyPort', proxy.port)

    def get_subtitle_rename_strategy(self):
        return self._rename_strategy

    def set_subtitle_rename_strategy(self, strategy, write=False):
        self._rename_strategy = strategy
        if write:
            self.settings.set_str('options', 'subtitleName', strategy.value)

    def get_subtitle_download_path_strategy(self):
        return self._download_path_strategy

    def set_subtitle_download_path_strategy(self, strategy, write=False):
        self._download_path_strategy = strategy
        if write:
            self.settings.set_str('options', 'whereToDownload', strategy.value)

    def get_default_download_path(self):
        return self._default_download_path

    def set_default_download_path(self, path, write=False):
        self._default_download_path = path
        if write:
            self.settings.set_path('options', 'whereToDownloadFolder', path)

    @staticmethod
    def get_system_language():
        locale = i18n_system_locale()
        for lc_fallback in i18n_locale_fallbacks_calculate(locale):
            try:
                language = Language.from_unknown(lc_fallback, locale=True)
                return language
            except NotALanguageException:
                continue
        return UnknownLanguage.create_generic()

    # FIXME: this does not belong here
    def calculate_subtitle_filename(self, subtitle):
        # FIXME: add accessibility method in subtitle?
        video = subtitle.get_parent().get_parent().get_parent()

        sub_stem, sub_extension = os.path.splitext(subtitle.get_filename())
        video_path = video.get_filepath()

        suffix_start_counter = 0

        while True:
            suffix_start = '.{}'.format(suffix_start_counter) if suffix_start_counter else ''
            rename_strategy = self.get_subtitle_rename_strategy()
            if rename_strategy == SubtitleRenameStrategy.VIDEO:
                new_ext = suffix_start + sub_extension
                sub_filepath = video_path.with_suffix(new_ext)
            elif rename_strategy == SubtitleRenameStrategy.VIDEO_LANG:
                new_ext = '{ss}.{xx}{ext}'.format(xx=subtitle.get_language().xx(), ss=suffix_start, ext=sub_extension)
                sub_filepath = video_path.with_suffix(new_ext)
            elif rename_strategy == SubtitleRenameStrategy.VIDEO_LANG_UPLOADER:
                new_ext = '.{upl}{ss}.{xx}{ext}'.format(xx=subtitle.get_language().xx(), upl=subtitle.get_uploader(), ss=suffix_start, ext=sub_extension)
                sub_filepath = video_path.with_suffix(new_ext)
            else:  # if rename_strategy == SubtitleRename.ONLINE:
                sub_filepath = video_path.parent / subtitle.get_filename()
                sub_filepath = sub_filepath.with_suffix(suffix_start + sub_filepath.suffix)

            suffix_start_counter += 1
            if not sub_filepath.exists():
                break

        return sub_filepath.name

    def calculate_download_path(self, subtitle, file_save_as_cb):
        video = subtitle.get_parent().get_parent().get_parent()

        sub_filename = self.calculate_subtitle_filename(subtitle)

        location_strategy = self.get_subtitle_download_path_strategy()
        if location_strategy == SubtitlePathStrategy.ASK:
            download_path = file_save_as_cb(path=video.get_folderpath(), filename=sub_filename)  # How to cancel? None?
        elif location_strategy == SubtitlePathStrategy.SAME:
            download_path = video.get_folderpath() / sub_filename
        else:  # location_strategy == SubtitlePath.PREDEFINED:
            download_path = self.get_default_download_path() / sub_filename
        log.debug('Downloading to {}'.format(download_path))

        return download_path

    def calculate_subtitle_query_filename(self, subtitle):
        sub_stem, sub_extension = os.path.splitext(subtitle.get_filename())

        suffix_start_counter = 0

        while True:
            suffix_start = '.{}'.format(suffix_start_counter) if suffix_start_counter else ''
            rename_strategy = self.get_subtitle_rename_strategy()
            if rename_strategy == SubtitleRenameStrategy.VIDEO:
                new_ext = suffix_start + sub_extension
            elif rename_strategy == SubtitleRenameStrategy.VIDEO_LANG:
                new_ext = '{ss}.{xx}{ext}'.format(xx=subtitle.get_language().xx(), ss=suffix_start, ext=sub_extension)
            elif rename_strategy == SubtitleRenameStrategy.VIDEO_LANG_UPLOADER:
                new_ext = '.{upl}{ss}.{xx}{ext}'.format(
                    xx=subtitle.get_language().xx(), upl=subtitle.get_uploader(), ss=suffix_start, ext=sub_extension)
            else:  # if rename_strategy == SubtitleRename.ONLINE:
                new_ext = suffix_start + sub_extension
            sub_filepath = sub_stem + new_ext

            suffix_start_counter += 1
            if not os.path.exists(sub_filepath):
                break

        return sub_filepath

    def calculate_download_query_path(self, subtitle, file_save_as_cb):
        sub_filename = self.calculate_subtitle_query_filename(subtitle)

        location_strategy = self.get_subtitle_download_path_strategy()
        if location_strategy == SubtitlePathStrategy.ASK:
            download_path = file_save_as_cb(path=os.getcwd(), filename=sub_filename)  # How to cancel? None?
        elif location_strategy == SubtitlePathStrategy.SAME:
            download_path = Path(os.getcwd()) / sub_filename
        else:  # location_strategy == SubtitlePath.PREDEFINED:
            download_path = self.get_default_download_path() / sub_filename
        log.debug('Downloading to {}'.format(download_path))

        return download_path
