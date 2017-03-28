# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import argparse
import logging

from subdownloader import project
from subdownloader.client.logger import LOGGING_LOGNOTHING


def parse_arguments(args):
    """
    Parse the program arguments.
    :return: argparse.Namespace object with the parsed arguments
    """
    parser = get_argument_parser()

    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    return parser.parse_args(args=args)


def get_argument_parser():
    """
    Get a parser that is able to parse program arguments.
    :return: instance of arparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description=project.get_description())

    parser.add_argument('--version', action='version',
                        version='{project} {version}'.format(project=project.PROJECT_TITLE,
                                                             version=project.PROJECT_VERSION_STR))

    # internal application options

    interfaceGroup = parser.add_argument_group(_('interface'), _('Change settings of the interface'))
    guicli = interfaceGroup.add_mutually_exclusive_group()
    guicli.add_argument('-g', '--gui', dest='mode',
                        action='store_const', const='gui',
                        help=_('Run application in GUI mode. This is the default.'))
    guicli.add_argument('-c', '--cli', dest='mode',
                        action='store_const', const='cli',
                        help=_('Run application in CLI mode.'))
    parser.set_defaults(mode='gui')

    interfaceGroup.add_argument('-T', '--test', dest='test',
                                action='store_true', default=False,
                                help=_('Used by developers for testing. (unsupported)'))
    interfaceGroup.add_argument('-V', '--video', dest='videofile',
                                metavar='PATH', default=None,
                                help=_('Full path to your video(s). Don\'t use "~".'))  # FIXME: allow ~
    interfaceGroup.add_argument('-l', '--lang', dest='language', default='all',
                                help=_('Set the language of the subtitle for download and upload.'))

    # logger options
    loggroup = parser.add_argument_group(_('logging'), _('Change the amount of logging done.'))
    loglvlex = loggroup.add_mutually_exclusive_group()
    loglvlex.add_argument('--debug', dest='loglevel',
                          action='store_const', const=logging.DEBUG,
                          help=_('Print log messages of debug severity and higher to stderr.'))
    loglvlex.add_argument('--warning', dest='loglevel',
                          action='store_const', const=logging.WARNING,
                          help=_('Print log messages of warning severity and higher to stderr. This is the default.'))
    loglvlex.add_argument('--error', dest='loglevel',
                          action='store_const', const=logging.ERROR,
                          help=_('Print log messages of error severity and higher to stderr.'))
    loglvlex.add_argument('--quiet', dest='loglevel',
                          action='store_const', const=LOGGING_LOGNOTHING,
                          help=_('Don\'t log anything to stderr or stdout'))
    loggroup.set_defaults(loglevel=logging.WARNING)

    loggroup.add_argument('--log', dest='logfile', metavar='FILE',
                          default=None, help=_('Path name of the log file.'))

    # cli options
    cliGroup = parser.add_argument_group(_('cli'), _('Change the behavior of the command line interface.'))
    cliGroup.add_argument('-i', '--interactive', dest='interactive',
                          action='store_true', default=False,
                          help=_('Prompt user when decisions need to be done.'))

    overwriteGroup = cliGroup.add_mutually_exclusive_group()
    overwriteGroup.add_argument('--los', dest='overwrite_local', action='store_false',
                                help=_('"Local Over Server" policy. '
                                     'Give priority of local subtitles over subtitles on server. This is the default.'))
    overwriteGroup.add_argument('--sol', dest='overwrite_local', action='store_true',
                                help=_('"Server Over Local" policy. '
                                       'Give priority of subtitles on server over local subtitles.'))
    parser.set_defaults(overwrite_local=False)

    operationGroup = cliGroup.add_mutually_exclusive_group()
    operationGroup.add_argument('-D', '--download', dest='operation', action='store_const', const='download',
                                help=_('Download a subtitle. This is the default.'))
    operationGroup.add_argument('-U', '--upload', dest='operation', action='store_const', const='upload',
                                help=_('Upload a subtitle.'))
    operationGroup.add_argument('-L', '--list', dest='operation', action='store_const', const='list',
                                help=_('List available subtitles without downloading.'))
    parser.set_defaults(operation='download')

    renameGroup = cliGroup.add_mutually_exclusive_group()
    renameGroup.add_argument('--keep-names', dest='renaming', action='store_false',
                             help=_('Keep original subtitle names. This is the default.'))
    renameGroup.add_argument('--rename-subs', dest='renaming', action='store_true',
                             help=_('Rename subtitles to match the movie file name.'))
    parser.set_defaults(renaming=False)

    # online options
    onlineGroup = parser.add_argument_group('online', 'Change parameters related to the online provider.')
    onlineGroup.add_argument("-P", "--proxy", dest="proxy", default=None,
                             help=_('Proxy to use on internet connections.'))

    onlineGroup.add_argument('-u', '--user', dest='username', default='',
                             help=_('Opensubtitles.org username. Must be set in upload mode. '
                                    'Default is blank (anonymous).'))
    onlineGroup.add_argument('-p', '--password', dest='password', default='',
                             help=_('Opensubtitles.org password. Must be set in upload mode. '
                                    'Default is blank (anonymous).'))

    return parser
