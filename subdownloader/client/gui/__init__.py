# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
import sys

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication

from subdownloader.client.gui.splashScreen import SplashScreen

from subdownloader.project import PROJECT_TITLE
from subdownloader.videofile import VIDEOS_EXT
from subdownloader.subtitlefile import SUBTITLES_EXT

SELECT_SUBTITLES = _("Subtitle Files (*.%s)") % " *.".join(SUBTITLES_EXT)
SELECT_VIDEOS = _("Video Files (*.%s)") % " *.".join(VIDEOS_EXT)

log = logging.getLogger('subdownloader.client.gui')

def run(options):
    # create splash screen and show messages to the user
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName(PROJECT_TITLE)
    QCoreApplication.setApplicationName(PROJECT_TITLE)
    splash = SplashScreen()
    splash.showMessage(_("Loading...")) # FIXME: move main() function or Main class to separate file before including subdownloader and gui files.
    splash.show()
    app.processEvents()

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

    log.debug('Starting application event loop ...')
    res = app.exec_()
    return res
