#!/usr/bin/env python
# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

import logging
import os.path
from modules import progressbar
from modules import APP_TITLE
from modules import APP_VERSION

'''
Logging levels:
CRITICAL    50
ERROR       40
WARNING     30
INFO        20
DEBUG       10
NOTSET       0
'''

import argparse


class Terminal(object):

    @classmethod
    def populate_parser(cls, parser):
        parser.add_argument('--version', action='version', version=APP_VERSION)
        # internal application options
        parser.add_argument('-d', '--debug', dest='logging', default=logging.INFO,
                            action='store_const', const=logging.DEBUG,
                            help='Print debug messages to stdout and logfile')
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

        class proxyAction(argparse.Action):

            def __init__(self, *args, **kwargs):
                super(proxyAction, self).__init__(*args, **kwargs)

            def __call__(self, parser, options, value, switch):
                if value is None:
                    import random
                    value = General.default_proxy.format(random.randint(1, 3))
                setattr(options, self.dest, value)

        parser.add_argument('-P', '--proxy', dest='proxy', nargs='?', action=proxyAction,
                            help='Proxy to use on internet connections')

    progress_bar_style = [progressbar.Bar(
        left='[', right=']'), progressbar.Percentage(), ' ', progressbar.ETA()]


class General(object):
    name = APP_TITLE
    description = '%s is a Free Open-Source tool written in PYTHON '\
        'for automatic download/upload subtitles for videofiles '\
        '(DIVX,MPEG,AVI,etc) and DVD\'s using fast hashing.' % name
    version = '%s v%s' % (APP_TITLE, APP_VERSION)
    rpc_server = 'http://www.opensubtitles.org/xml-rpc'
    search_url = 'http://www.opensubtitles.org/en/search2/sublanguageid-%s/moviename-%s/xml'
    default_proxy = 'http://{}.hidemyass.com/'


class Logging(object):
    log_level = logging.DEBUG
    log_format = '[%(asctime)s] %(levelname)s::%(name)s # %(message)s'
    log_dir = os.path.expanduser('~')
    log_name = '%s.log' % General.name.lower()
    log_path = os.path.join(log_dir, log_name)
    log_mode = 'a'
