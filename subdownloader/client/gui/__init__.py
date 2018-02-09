# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging
import signal
import sys

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication

from subdownloader.subtitle2 import SUBTITLES_EXT
from subdownloader.video2 import VIDEOS_EXT
from subdownloader.client.gui.splashScreen import SplashScreen
from subdownloader.project import PROJECT_TITLE

from subdownloader.client.gui.generated.images_rc import qInitResources, qCleanupResources

log = logging.getLogger('subdownloader.client.gui')


def get_default_settings(video_path=None):
    from subdownloader.client.arguments import get_default_argument_settings, ArgumentClientSettings, ArgumentClientGuiSettings, ClientType
    return get_default_argument_settings(
        video_path=video_path,
        client=ArgumentClientSettings(
            type=ClientType.GUI,
            cli=None,
            gui=ArgumentClientGuiSettings(
            ),
        )
    )


def get_select_subtitles():
    return _("Subtitle Files (*.%s)") % " *.".join(SUBTITLES_EXT)


def get_select_videos():
    return _("Video Files (*.%s)") % " *.".join(VIDEOS_EXT)


def run(options):
    # create splash screen and show messages to the user
    app = QApplication(sys.argv)

    qInitResources()

    QCoreApplication.setOrganizationName(PROJECT_TITLE)
    QCoreApplication.setApplicationName(PROJECT_TITLE)
    splash = SplashScreen()
    splash.showMessage(_("Loading...")) # FIXME: move main() function or Main class to separate file before including subdownloader and gui files.
    # splash.show()

    from subdownloader.client.gui.main import Main

    QCoreApplication.flush()

    splash.showMessage(_("Building main dialog..."))
    log.debug('Building main dialog ...')

    main_window = Main(None, "", options)

    log.debug('... Building FINISHED')

    log.debug('Showing main window')
    main_window.show()
    log.debug('Finishing splash screen0')
    splash.finish(main_window)
    main_window.raise_()

    log.debug('Starting application event loop ...')

    # restore default interrupt handler for signal interrupt (CTRL+C interrupt)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    res = app.exec_()

    qCleanupResources()

    return res
