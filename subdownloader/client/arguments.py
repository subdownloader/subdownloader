# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from argcomplete import autocomplete
import argparse
from collections import namedtuple
import logging
from pathlib import Path

from subdownloader import project
from subdownloader.client import ClientType
from subdownloader.client.cli import CliAction
from subdownloader.client.logger import LOGGING_LOGNOTHING
from subdownloader.client.state import ProviderData, Proxy, SubtitleRenameStrategy
from subdownloader.languages.language import Language, NotALanguageException, UnknownLanguage


def parse_arguments(args=None):
    """
    Parse the program arguments.
    :return: argparse.Namespace object with the parsed arguments
    """
    parser = get_argument_parser()

    # Autocomplete arguments
    autocomplete(parser)

    ns = parser.parse_args(args=args)
    return ArgumentSettings(
        program=ArgumentProgramSettings(
            log=ArgumentLogSettings(
                path=None,
                level=ns.loglevel,
            ),
            settings=ArgumentSettingsSettings(
                path=ns.settings_path,
            ),
            client=ArgumentClientSettings(
                type=ns.client_type,
                cli=ArgumentClientCliSettings(
                    interactive=False,
                ),
                gui=ArgumentClientGuiSettings(
                ),
            ),
        ),
        search=ArgumentSearchSettings(
            recursive=ns.recursive,
            working_directory=ns.video_path,
        ),
        filter=FilterSettings(
            languages=ns.languages,
        ),
        download=DownloadSettings(
            rename_strategy=ns.rename_strategy,
        ),
        providers=ns.providers,
        proxy=ns.proxy,
        test=ns.test,
    )


def get_default_argument_settings(video_path, client):
    return ArgumentSettings(
        program=ArgumentProgramSettings(
            log=ArgumentLogSettings(
                path=None,
                level=logging.ERROR,
            ),
            settings=ArgumentSettingsSettings(
                path=None,
            ),
            client=client,
        ),
        search=ArgumentSearchSettings(
            recursive=True,
            working_directory=video_path,
        ),
        filter=FilterSettings(
            languages=[UnknownLanguage.create_generic()],
        ),
        download=DownloadSettings(
            rename_strategy=SubtitleRenameStrategy.ONLINE,
        ),
        providers=None,
        proxy=None,
        test=False,
    )


ArgumentSettings = namedtuple('ArgumentSettings', (
    'program',
    'search',
    'filter',
    'download',
    'providers',
    'proxy',
    'test',
))

ArgumentProgramSettings = namedtuple('ArgumentProgramSettings', (
    'log',
    'settings',
    'client',
))

ArgumentLogSettings = namedtuple('ArgumentLogSettings', (
    'path',
    'level',
))

ArgumentSettingsSettings = namedtuple('ArgumentSettingsSettings', (
    'path',
))

ArgumentClientSettings = namedtuple('ArgumentClientSettings', (
    'type',
    'cli',
    'gui',
))

ArgumentClientCliSettings = namedtuple('ArgumentClientCliSettings', (
    'interactive',
))

ArgumentClientGuiSettings = namedtuple('ArgumentClientGuiSettings', (
))

ArgumentSearchSettings = namedtuple('ArgumentSearchSettings', (
    'recursive',
    'working_directory',
))

FilterSettings = namedtuple('FilterSettings', (
    'languages',
))

DownloadSettings = namedtuple('DownloadSettings', (
    'rename_strategy',
))

class ProxyAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            [host, port] = values.split(':')
            setattr(namespace, self.dest, Proxy(host, int(port)))
        except ValueError:
            parser.error(_('Not a valid proxy address: "{}"').format(values))


class LanguagesAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            languages = [Language.from_unknown(value, xx=True, xxx=True, locale=True, name=True) for value in values]
            setattr(namespace, self.dest, languages)
        except NotALanguageException as e:
            parser.error(_('{lang_str} is an unknown language.').format(lang_str=e.value))


class PathsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        paths = [Path(value).expanduser().absolute() for value in values]
        setattr(namespace, self.dest, paths)


class ProviderAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        providers = getattr(namespace, self.dest)
        if providers is None:
            providers = {}
            setattr(namespace, self.dest, providers)
        provider_str = values[0]
        try:
            kwargs = providers[provider_str].kwargs
        except KeyError:
            kwargs = {}
        for value in values[1:]:
            try:
                k, v = value.split('=', 1)
                k, v = k.strip(), v.strip()
                if not k:
                    raise ValueError()
                if k in kwargs:
                    parser.error('Duplicate "{}"-provider key: {}'.format(provider_str, k))
                kwargs[k] = v
            except ValueError:
                parser.error('Illegal {} argument: {}'.format(option_string, value))

        providers[provider_str] = ProviderData(provider_str, kwargs)


def get_argument_parser():
    """
    Get a parser that is able to parse program arguments.
    :return: instance of arparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description=project.get_description(),
                                     epilog=_('Visit us at {website}.').format(website=project.WEBSITE_MAIN))

    parser.add_argument('--version', action='version',
                        version='{project} {version}'.format(project=project.PROJECT_TITLE,
                                                             version=project.PROJECT_VERSION_STR))
    parser.add_argument('-T', '--test', dest='test',
                        action='store_true', default=False,
                        help=argparse.SUPPRESS)
    parser.add_argument('-V', '--video', dest='video_path', default=None, metavar='PATH',
                        nargs=argparse.ONE_OR_MORE, action=PathsAction,
                        help=_('Full path to your video(s).'))
    parser.add_argument('-s', '--settings', dest='settings_path', type=Path, default=None, metavar='FILE',
                        help=_('Set the settings file.'))
    parser.add_argument('-l', '--lang', dest='languages', metavar='LANGUAGE',
                        default=[UnknownLanguage.create_generic()],
                        nargs=argparse.ONE_OR_MORE, action=LanguagesAction,
                        help=_('Set the preferred subtitle language(s) for download and upload.'))

    # interface options
    interface_group = parser.add_argument_group(_('interface'), _('Change settings of the interface'))
    guicli = interface_group.add_mutually_exclusive_group()
    guicli.add_argument('-g', '--gui', dest='client_type',
                        action='store_const', const=ClientType.GUI,
                        help=_('Run application in GUI mode. This is the default.'))
    guicli.add_argument('-c', '--cli', dest='client_type',
                        action='store_const', const=ClientType.CLI,
                        help=_('Run application in CLI mode.'))
    parser.set_defaults(client_type=ClientType.GUI)

    # logger options
    loggroup = parser.add_argument_group(_('logging'), _('Change the amount of logging done.'))
    loglvlex = loggroup.add_mutually_exclusive_group()
    loglvlex.add_argument('-d', '--debug', dest='loglevel',
                          action='store_const', const=logging.DEBUG,
                          help=_('Print log messages of debug severity and higher to stderr.'))
    loglvlex.add_argument('-w', '--warning', dest='loglevel',
                          action='store_const', const=logging.WARNING,
                          help=_('Print log messages of warning severity and higher to stderr. This is the default.'))
    loglvlex.add_argument('-e', '--error', dest='loglevel',
                          action='store_const', const=logging.ERROR,
                          help=_('Print log messages of error severity and higher to stderr.'))
    loglvlex.add_argument('-q', '--quiet', dest='loglevel',
                          action='store_const', const=LOGGING_LOGNOTHING,
                          help=_('Don\'t log anything to stderr.'))
    loggroup.set_defaults(loglevel=logging.WARNING)

    loggroup.add_argument('--log', dest='logfile', metavar='FILE', type=Path,
                          default=None, help=_('Path name of the log file.'))

    # cli options
    cli_group = parser.add_argument_group(_('cli'), _('Change the behavior of the command line interface.'))
    cli_group.add_argument('-i', '--interactive', dest='interactive',
                           action='store_true', default=False,
                           help=_('Prompt user when decisions need to be done.'))
    cli_group.add_argument('-r', '--recursive', dest='recursive',
                           action='store_true', default=False,
                           help=_('Search for subtitles recursively.'))

    operation_group = cli_group.add_mutually_exclusive_group()
    operation_group.add_argument('-D', '--download', dest='operation', action='store_const', const=CliAction.DOWNLOAD,
                                 help=_('Download subtitle(s). This is the default.'))
    operation_group.add_argument('-U', '--upload', dest='operation', action='store_const', const=CliAction.UPLOAD,
                                 help=_('Upload subtitle(s).'))
    # operation_group.add_argument('-L', '--list', dest='operation', action='store_const', const=CliAction.LIST,
    #                              help=_('List available subtitle(s) without downloading.'))
    parser.set_defaults(operation=CliAction.DOWNLOAD)

    rename_group = cli_group.add_mutually_exclusive_group()
    rename_group.add_argument('--rename-online', dest='rename_strategy', action='store_const',
                              const=SubtitleRenameStrategy.ONLINE,
                              help=_('Use the on-line subtitle filename as name for the downloaded subtitles. '
                                     'This is the default.'))
    rename_group.add_argument('--rename-video', dest='rename_strategy', action='store_const',
                              const=SubtitleRenameStrategy.VIDEO,
                              help=_('Use the local video filename as name for the downloaded subtitle.'))
    rename_group.add_argument('--rename-lang', dest='rename_strategy', action='store_const',
                              const=SubtitleRenameStrategy.VIDEO_LANG,
                              help=_('Use the local video filename + language as name for the downloaded subtitle.'))
    rename_group.add_argument('--rename-uploader', dest='rename_strategy', action='store_const',
                              const=SubtitleRenameStrategy.VIDEO_LANG_UPLOADER,
                              help=_('Use the local video filename + uploader + language '
                                     'as name for the downloaded subtitle.'))
    parser.set_defaults(rename_strategy=SubtitleRenameStrategy.ONLINE)

    # online options
    online_group = parser.add_argument_group('online', 'Change parameters related to the online provider.')
    online_group.add_argument('-P', '--proxy', dest='proxy', default=None, action=ProxyAction,
                              help=_('Proxy to use on internet connections.'))
    online_group.add_argument('--provider', dest='providers', metavar='NAME [KEY1=VALUE1 [KEY2=VALUE2 [...]]]',
                              nargs=argparse.ONE_OR_MORE, default=None, action=ProviderAction,
                              help=_('Enable and configure a provider.'))

    return parser
