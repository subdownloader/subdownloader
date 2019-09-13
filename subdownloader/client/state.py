# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from collections import namedtuple
from enum import Enum
import logging
import os.path
from pathlib import Path
import platform

from subdownloader.client import ClientType, IllegalArgumentException
from subdownloader.client.internationalization import i18n_system_locale, i18n_locale_fallbacks_calculate
from subdownloader.client.configuration import Settings
from subdownloader.project import PROJECT_TITLE
from subdownloader.languages.language import Language, NotALanguageException, UnknownLanguage
from subdownloader.provider.factory import NoProviderException, ProviderFactory
from subdownloader.provider.provider import SubtitleProvider

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


class SubtitleNamingStrategy(Enum):
    VIDEO = 'SAME_VIDEO'
    VIDEO_LANG = 'SAME_VIDEOPLUSLANG'
    VIDEO_LANG_UPLOADER = 'SAME_VIDEOPLUSLANGANDUPLOADER'
    ONLINE = 'SAME_ONLINE'

    @classmethod
    def from_str(cls, s):
        try:
            return next(c for c in cls if s == c.value)
        except StopIteration:
            raise ValueError(s)


class SubtitlePathStrategy(Enum):
    ASK = 'ASK_FOLDER'
    SAME = 'SAME_FOLDER'
    PREDEFINED = 'PREDEFINED_FOLDER'

    @classmethod
    def from_str(cls, s):
        try:
            return next(c for c in cls if s == c.value)
        except StopIteration:
            raise ValueError(s)


class StateConfigKey(Enum):
    VIDEO_PATH = ('mainwindow', 'workingDirectory', )
    FILTER_LANGUAGES = ('options', 'filterSearchLang', )
    UPLOAD_LANGUAGE = ('options', 'uploadLanguage', )
    SUBTITLE_PATH_STRATEGY = ('options', 'whereToDownload', )
    SUBTITLE_NAMING_STRATEGY = ('options', 'subtitleName',)
    DOWNLOAD_PATH = ('options', 'whereToDownloadFolder', )
    PROXY_HOST = ('options', 'ProxyHost', )
    PROXY_PORT = ('options', 'ProxyPort', )


# FIXME: add more logging


class ProvidersState(object):
    def __init__(self):
        self._providers = []

    def load_settings(self, settings):
        for provider in self._providers:
            self._load_provider_settings(provider, settings)

    def save_settings(self, settings):
        for provider in self._providers:
            raise NotImplementedError('TODO!')

    def load_options(self, options):
        providers_cls = ProviderFactory.list()
        if options.providers:
            map_provider_data = filter_providers(providers_cls, options.providers)
        else:
            map_provider_data = {provider_cls: ProviderData(provider_cls.get_name(), dict()) for provider_cls in providers_cls}
        self._providers = [provider_cls() for provider_cls in map_provider_data.keys()]

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

    def _load_provider_settings(self, provider, settings):
        section = 'provider_{name}'.format(name=provider.get_name())
        provider_settings = provider.get_settings()
        new_provider_data = {}
        for k, v in provider_settings.as_dict().items():
            d = settings.get_str((section, k), v)
            new_provider_data[k] = d
        new_data = provider_settings.load(**new_provider_data)
        provider.set_settings(new_data)

    def iter(self):
        return iter(self._providers)

    def find(self, item):
        def _find_provider(provider, item):
            if isinstance(item, str):
                return provider.get_name() == item
            elif isinstance(item, type) and issubclass(item, SubtitleProvider):
                return type(provider) == item
            else:
                return provider == item
        try:
            provider = next(provider for provider in self._providers if _find_provider(provider, item))
        except StopIteration:
            return None
        return provider
    def _item_to_providers(self, item):
        if item is None:
            providers = self._providers
        else:
            provider = self.find(item)
            if provider is None:
                raise IndexError()
            providers = (provider, )
        return providers

    def add_name(self, name, settings):
        for provider in self._providers:
            if provider.get_name() == name:
                log.debug('Provider "{}" already added'.format(name))
                return False
        try:
            providers_cls = ProviderFactory.local_search(name)
            if len(providers_cls) != 1:
                log.warning('More than one provider matched "{}". Ignoring.'.format(name))
                return False
            provider_cls = providers_cls[0]
        except NoProviderException:
            return False

        provider = provider_cls()
        self._load_provider_settings(provider, settings)
        self._providers.append(provider)
        return True

    def remove(self, item):
        provider = self.find(item)
        if provider is None:
            return False
        self._providers.remove(provider)
        return True

    def get(self, index):
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

    def query_text_all(self, text):
        from subdownloader.query import SubtitlesTextQuery
        query = SubtitlesTextQuery(text=text)
        query.search_init(self.iter())
        return query


class BaseState(object):
    def __init__(self):
        self._providersState = ProvidersState()

        self._recursive = False
        self._video_paths = []

        self._upload_language = None
        self._download_languages = []

        self._naming_strategy = SubtitleNamingStrategy.ONLINE
        self._download_path_strategy = SubtitlePathStrategy.PREDEFINED
        self._default_download_path = Path().resolve()

        self._proxy = None

    @property
    def providers(self):
        return self._providersState

    def load_options(self, options):
        self._providersState.load_options(options)

        self.set_recursive(options.search.recursive)
        if options.search.working_directory is not None:
            self.set_video_paths(options.search.working_directory)
        else:
            self.set_video_paths([Path(os.getcwd())])

        if options.filter.languages:
            self.set_upload_language(options.filter.languages[0])
            self.set_download_languages(options.filter.languages)

        subtitle_naming_strategy = options.download.naming_strategy
        if subtitle_naming_strategy is not None:
            self.set_subtitle_naming_strategy(subtitle_naming_strategy)

        if options.proxy is not None:
            self.set_proxy(options.proxy)

        # FIXME: log state

    def load_settings(self, settings):
        self._providersState.load_settings(settings)

        upload_language = settings.get_language(StateConfigKey.UPLOAD_LANGUAGE.value)
        if upload_language is not None:
            self.set_upload_language(upload_language)

        download_languages = settings.get_languages(StateConfigKey.FILTER_LANGUAGES.value)
        if download_languages is not None:
            self.set_download_languages(download_languages)

        naming_strategy_str = settings.get_str(StateConfigKey.SUBTITLE_NAMING_STRATEGY.value, None)
        if naming_strategy_str:
            self.set_subtitle_naming_strategy(SubtitleNamingStrategy.from_str(naming_strategy_str))

        download_path_strategy_str = settings.get_str(StateConfigKey.SUBTITLE_PATH_STRATEGY.value, None)
        if download_path_strategy_str:
            self.set_subtitle_download_path_strategy(SubtitlePathStrategy.from_str(download_path_strategy_str))

        proxy_host = settings.get_str(StateConfigKey.PROXY_HOST.value, None)
        proxy_port = settings.get_int(StateConfigKey.PROXY_PORT.value, None)
        if None not in (proxy_host, proxy_port):
            proxy = Proxy(proxy_host, proxy_port)
            self.set_proxy(proxy)

    def save_settings(self, settings):
        self._providersState.save_settings(settings)

        if self._video_paths:
            settings.set_path(StateConfigKey.VIDEO_PATH.value, self._video_paths[0])
        else:
            settings.remove_key(StateConfigKey.VIDEO_PATH.value)

        settings.set_str(StateConfigKey.SUBTITLE_NAMING_STRATEGY.value, self.get_subtitle_naming_strategy().value)
        settings.set_str(StateConfigKey.SUBTITLE_PATH_STRATEGY.value, self.get_subtitle_download_path_strategy().value)

        settings.set_languages(StateConfigKey.FILTER_LANGUAGES.value, self.get_download_languages())
        settings.set_language(StateConfigKey.UPLOAD_LANGUAGE.value, self.get_upload_language())

        proxy = self.get_proxy()
        if proxy:
            settings.set_str(StateConfigKey.PROXY_HOST.value, proxy.host)
            settings.set_int(StateConfigKey.PROXY_PORT.value, proxy.port)
        else:
            settings.remove_key(StateConfigKey.PROXY_HOST.value)
            settings.remove_key(StateConfigKey.PROXY_PORT.value)

        settings.write()

    def search_videos_all(self, videos, callback):
        providers = list(self._providersState.iter())
        callback.set_range(0, len(providers))
        prov_rsubs = {}
        for provider_i, provider in enumerate(providers):
            download_callback = callback.get_child_progress(provider_i, provider_i+1)
            prov_rsubs[provider] = provider.search_videos(videos=videos, callback=download_callback)
        return prov_rsubs

    def get_recursive(self):
        return self._recursive

    def set_recursive(self, recursive):
        log.debug('set_recursive({})'.format(recursive))
        self._recursive = recursive

    def get_video_paths(self):
        if self._video_paths is None:
            return []
        return self._video_paths

    def set_video_paths(self, video_paths):
        log.debug('set_video_paths({})'.format(video_paths))
        self._video_paths = video_paths

    # FIXME: change to filter languages
    def get_download_languages(self):
        return self._download_languages

    def set_download_languages(self, langs):
        log.debug('set_download_languages({})'.format(langs))
        self._download_languages = langs

    def get_upload_language(self):
        return self._upload_language

    def set_upload_language(self, lang):
        self._upload_language = lang

    def get_proxy(self):
        return self._proxy

    def set_proxy(self, proxy):
        log.debug('set_proxy({})'.format(proxy))
        self._proxy = proxy

    def get_subtitle_naming_strategy(self):
        return self._naming_strategy

    def set_subtitle_naming_strategy(self, strategy):
        log.debug('set_subtitle_naming_strategy({})'.format(strategy))
        self._naming_strategy = strategy

    def get_subtitle_download_path_strategy(self):
        return self._download_path_strategy

    def set_subtitle_download_path_strategy(self, strategy, write=False):
        log.debug('set_subtitle_download_path_strategy({})'.format(strategy))
        self._download_path_strategy = strategy

    def get_default_download_path(self):
        return self._default_download_path

    def set_default_download_path(self, path, write=False):
        log.debug('set_default_download_path({})'.format(path))
        self._default_download_path = path

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
            naming_strategy = self.get_subtitle_naming_strategy()
            if naming_strategy == SubtitleNamingStrategy.VIDEO:
                new_ext = suffix_start + sub_extension
                sub_filepath = video_path.with_suffix(new_ext)
            elif naming_strategy == SubtitleNamingStrategy.VIDEO_LANG:
                new_ext = '{ss}.{xx}{ext}'.format(xx=subtitle.get_language().xx(), ss=suffix_start, ext=sub_extension)
                sub_filepath = video_path.with_suffix(new_ext)
            elif naming_strategy == SubtitleNamingStrategy.VIDEO_LANG_UPLOADER:
                new_ext = '.{upl}{ss}.{xx}{ext}'.format(xx=subtitle.get_language().xx(), upl=subtitle.get_uploader(), ss=suffix_start, ext=sub_extension)
                sub_filepath = video_path.with_suffix(new_ext)
            else:  # if naming_strategy == SubtitleNamingStrategy.ONLINE:
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
            naming_strategy = self.get_subtitle_naming_strategy()
            if naming_strategy == SubtitleNamingStrategy.VIDEO:
                new_ext = suffix_start + sub_extension
            elif naming_strategy == SubtitleNamingStrategy.VIDEO_LANG:
                new_ext = '{ss}.{xx}{ext}'.format(xx=subtitle.get_language().xx(), ss=suffix_start, ext=sub_extension)
            elif naming_strategy == SubtitleNamingStrategy.VIDEO_LANG_UPLOADER:
                new_ext = '.{upl}{ss}.{xx}{ext}'.format(
                    xx=subtitle.get_language().xx(), upl=subtitle.get_uploader(), ss=suffix_start, ext=sub_extension)
            else:  # if naming_strategy == SubtitleRename.ONLINE:
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

    @classmethod
    def get_default_settings_path(cls):
        """
        Return the default file where user-specific data is stored.
        This depends of the system on which Python is running,
        :return: path to the user-specific configuration data folder
        """
        return (cls.get_default_settings_folder() / PROJECT_TITLE).with_suffix('.conf')

    @staticmethod
    def get_default_settings_folder():
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


class GuiState(BaseState):  # FIXME: move to gui/state.py
    def __init__(self):
        BaseState.__init__(self)

    def load_settings(self, settings):
        BaseState.load_settings(settings)

        self.set_video_paths([settings.get_path(StateConfigKey.VIDEO_PATH.value, Path().resolve())])


def state_init():
    config_path = BaseState.get_default_settings_folder()
    config_path.mkdir(exist_ok=True)
