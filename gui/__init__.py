#!/usr/bin/env python
# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

""" The GUI to libprs500. Also has ebook library management features. """
__docformat__ = "epytext"
__author__ = "Ivan Garcia <contact@ivangarcia.org>"

import sys
import os
import re
import traceback
from modules import APP_TITLE, APP_VERSION, SDService, subtitlefile, videofile


error_dialog = None


def extension(path):
    return os.path.splitext(path)[1][1:].lower()


def installErrorHandler(dialog):
    global error_dialog
    error_dialog = dialog
    error_dialog.resize(600, 400)
    error_dialog.setWindowTitle(APP_TITLE + " - Error")
    error_dialog.setModal(True)


def Error(msg, e):
    if error_dialog:
        if e:
            msg += "<br>" + traceback.format_exc(e)
        msg = re.sub("Traceback", "<b>Traceback</b>", msg)
        msg = re.sub(r"\n", "<br>", msg)
        error_dialog.showMessage(msg)
        error_dialog.show()
