# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import argparse
import gettext
import locale
import logging
import os
import platform
import sys

from subdownloader import project
from subdownloader.client import get_project_description, get_i18n_path


def install_i18n_early():
    """
    Install internationalization support for the clients.
    On failure, install a null translator.
    """
    lc, encoding = locale.getlocale()
    try:
        gettext.translation(
            domain='subdownloader', localedir=get_i18n_path(), languages=[lc], fallback=True).install()
    except IOError:
        gettext.NullTranslations().install()


def install_logger(level, filename):
    logging.basicConfig(level=level,
                        format=Logging.log_format,
                        datefmt='%H:%M',
                        filename=filename,
                        filemode='a',
                        )
    if platform.system() == "Windows":
        try:
            if os.path.isfile(sys.path[0]):
                subdownloader_folder = os.path.dirname(sys.path[0])
            else:
                subdownloader_folder = sys.path[0]
            sys.stderr = open(os.path.join(subdownloader_folder,
                                           "subdownloader.log"), "w")
            # The EXE file in windows will think that outputs here are errors,
            # and it will show annoying mesage about run.exe.log
        except:
            pass
            # Cannot write message into subdownloader.log,
            # that happens for example in Vista,
            # where SD does not have writer permission on its ProgramFiles folder.


def parse_args():
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

    return parser.parse_args()


def get_argument_parser():
    """
    Get a parser that is able to parse program arguments.
    :return: instance of arparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description=get_project_description())

    parser.add_argument('--version', action='version', version=project.VERSION)
    # internal application options
    parser.add_argument('-d', '--debug', dest='loglevel',
                        action='store_const', const=logging.DEBUG,
                        help='Print debug messages to stdout and logfile')
    parser.set_defaults(loglevel=logging.WARNING)

    parser.add_argument('-q', '--quiet', dest='verbose',
                        action='store_false', default=True,
                        help='Don\'t print status messages to stdout')

    guicli = parser.add_mutually_exclusive_group()
    guicli.add_argument('-g', '--gui', dest='mode',
                        action='store_const', const='gui',
                        help='Run application in GUI modei. This is the default')
    guicli.add_argument('-c', '--cli', dest='mode',
                        action='store_const', const='cli',
                        help='Run application in CLI mode')
    parser.set_defaults(mode='gui')

    parser.add_argument('-T', '--test', dest='test',
                        action='store_true', default=False,
                        help='Used by developers for testing')
    parser.add_argument('-H', '--human', dest='output',
                        action='store_const', const='human',
                        help='Print human readable messages. Default for CLI mode')
    parser.add_argument('-n', '--nerd', dest='output',
                        action='store_const', const='nerd', default='human',
                        help='Print messages with more details')
    parser.set_defaults(output='human')

    parser.add_argument('--log', dest='logfile', metavar='FILE',
                        nargs='?', const=Logging.log_name, default=None,
                        help='Log actions of subdownloader to file')

    # user application options
    updown = parser.add_mutually_exclusive_group()
    updown.add_argument('-D', '--download', dest='operation',
                        action='store_const', const='download',
                        help='Download a subtitle. Default for CLI mode')
    updown.add_argument('-U', '--upload', dest='operation',
                        action='store_const', const='upload', default='download',
                        help='Upload a subtitle')
    parser.set_defaults(operation='download')

    parser.add_argument('-L', '--list', dest='operation',
                        action='store_const', const='list', default='download',
                        help='List available subtitles without downloading')
    parser.add_argument('-V', '--video', dest='videofile',
                        metavar='FILE/DIR', default=None,
                        help='Full path to your video(s). Don\'t use "~"')
    parser.add_argument('-l', '--lang', dest='language', default='all',
                        help='Used in subtitle download and upload preferences')
    parser.add_argument('-i', '--interactive', dest='interactive',
                        action='store_true', default=False,
                        help='Prompt user when decisions need to be done')
    parser.add_argument('--rename-subs', dest='renaming',
                        action='store_true',
                        help='Rename subtitles to match movie file name')
    parser.add_argument('--keep-names', dest='renaming',
                        action='store_false', default=False,
                        help='Keep original subtitle names')
    parser.add_argument('--sol', dest='overwrite_local',
                        action='store_true',  # default=False,
                        help='"Server Over Local" overwrites local subtitle with one '
                             'from server. This is in cases when local subtitle isn\'t '
                             'found on server, but server has subtitles for the movie.')
    parser.add_argument('--los', dest='overwrite_local',
                        action='store_false', default=False,
                        help='"Local Over Server" keeps local subtitles, even if another'
                             'is found on server. This is the default')

    parser.add_argument('-u', '--user', dest='username', default='',
                        help='Opensubtitles.org username. Must be set in upload mode.'
                             'Default is blank (anonymous)')
    parser.add_argument('-p', '--password', dest='password', default='',
                        help='Opensubtitles.org password. Must be set in upload mode.'
                             'Default is blank (anonymous)')

    # misc options
    parser.add_argument('-s', '--server', dest='server', default=None,
                        help='Server address of Opensubtitles API')
    parser.add_argument("-P", "--proxy", dest="proxy", default=None,
                        help="Proxy to use on internet connections")

    return parser


class Logging(object):
    log_format = '[%(asctime)s] %(levelname)s::%(name)s # %(message)s'
    log_name = '%s.log' % project.TITLE.lower()
