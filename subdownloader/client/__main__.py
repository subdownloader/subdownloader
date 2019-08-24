#!/usr/bin/env python3
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3
# PYTHON_ARGCOMPLETE_OK

import logging
import platform
import subprocess
import sys

from subdownloader.client import ClientType, IllegalArgumentException, add_client_module_dependencies
from subdownloader.client.state import BaseState, state_init
from subdownloader.client.configuration import Settings
from subdownloader.client.logger import logging_file_install, logging_install, logging_stream_install
from subdownloader.client.internationalization import i18n_install
from subdownloader.client.arguments import parse_arguments
from subdownloader.client.user_agent import user_agent_init
from subdownloader.project import PROJECT_TITLE


def emit_error_missing_pyqt():
    title = _('{} GUI needs {}').format(PROJECT_TITLE, 'PyQt5')
    short_msg = '{}.{{}}{}'.format(title, _('Please install {} and try again').format('PyQt5'))
    msg = '{}: {}'.format(_('Fatal error'), short_msg)
    sys.stderr.write('{}\n'.format(msg.format('\n')))

    if not sys.stderr.isatty():
        sent = False
        if platform.system() == 'Linux':
            try:
                subprocess.run(['notify-send', '-u', 'critical', '-a', PROJECT_TITLE,
                                '-c', 'ERROR', msg.format('\r')])
                sent = True
            except IOError:
                pass

            if not sent:
                try:
                    subprocess.run(['zenity', '--error', '--text={}'.format(msg.format('\n')),
                                    '--title={}'.format(_('Missing {}').format('PyQt5'))])
                    sent = True
                except IOError:
                    pass
        elif platform.system() == 'Windows':
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, short_msg.format('\n'), title, 0x10)
                sent = True
            except IOError:
                raise


def main(args=None):
    add_client_module_dependencies()
    logging_stream_install(logging.WARNING)
    state_init()
    logging_file_install(None)
    i18n_install()
    options = parse_arguments(args=args)
    settings = Settings(BaseState.get_default_settings_path())
    logging_install(options.program.log.level, options.program.log.path)
    user_agent_init()

    if options.program.client.type == ClientType.GUI:
        try:
            import subdownloader.client.gui
        except ImportError as e:
            if e.name.startswith('PyQt5'):
                emit_error_missing_pyqt()
                return 1
            else:
                raise
        runner = subdownloader.client.gui.run
    elif options.program.client.type == ClientType.CLI:
        import subdownloader.client.cli
        runner = subdownloader.client.cli.run
    else:
        print('{}: {}'.format(_('Invalid client type'), options.program.client_type))
        return 1

    try:
        return runner(options, settings)
    except IllegalArgumentException as e:
        sys.stderr.write(e.msg)
        print()
        return 1
    except (EOFError, KeyboardInterrupt):
        return 1


if __name__ == '__main__':
    sys.exit(main())
