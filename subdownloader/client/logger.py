# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging
import logging.handlers
import os

from subdownloader import project
from subdownloader.client.configuration import configuration_get_default_folder

log = logging.getLogger('subdownloader.client.logger')
logging.getLogger().setLevel(logging.DEBUG)


"""
Handlers for the log file and stream.
"""
LOGGING_HANDLERS = {
    'file': None,
    'stream': None,
}


def logging_file_install(path):
    """
    Install logger that will write to file. If this function has already installed a handler, replace it.
    :param path: path to the log file, Use None for default file location.
    """
    if path is None:
        path = configuration_get_default_folder() / LOGGING_DEFAULTNAME

    if not path.parent.exists():
        log.error('File logger installation FAILED!')
        log.error('The directory of the log file does not exist.')
        return

    formatter = logging.Formatter(LOGGING_FORMAT)
    logger = logging.getLogger()

    logger.removeHandler(LOGGING_HANDLERS['file'])

    logFileHandler = logging.handlers.RotatingFileHandler(filename=str(path),
                                                          mode='a',
                                                          maxBytes=LOGGING_MAXBYTES,
                                                          backupCount=LOGGING_BACKUPCOUNT)
    logFileHandler.setLevel(logging.DEBUG)
    logFileHandler.setFormatter(formatter)

    LOGGING_HANDLERS['file'] = logFileHandler

    logger.addHandler(logFileHandler)


def logging_stream_install(loglevel):
    """
    Install logger that will output to stderr. If this function ha already installed a handler, replace it.
    :param loglevel: log level for the stream
    """
    formatter = logging.Formatter(LOGGING_FORMAT)
    logger = logging.getLogger()

    logger.removeHandler(LOGGING_HANDLERS['stream'])

    if loglevel == LOGGING_LOGNOTHING:
        streamHandler = None
    else:
        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(loglevel)
        streamHandler.setFormatter(formatter)

    LOGGING_HANDLERS['stream'] = streamHandler

    if streamHandler:
        logger.addHandler(streamHandler)


def logging_install(loglevel, filename):
    """
    Install stream and logfile loggers.
    The log file will always have DEBUG loglevel.
    :param loglevel: log level for the stream
    :param filename: filename of the log file
    """
    logging_file_install(filename)
    logging_stream_install(loglevel)


"""
Format of each log message.
"""
LOGGING_FORMAT = '[%(asctime)s] %(levelname)-s: %(name)-s # %(message)s'

"""
Constant to signal that no logging to stdout or stderr should be done.
"""
LOGGING_LOGNOTHING = -1

"""
Maximum number of rotating log filse.
"""
LOGGING_BACKUPCOUNT = 3

"""
Maximum file size for each log file.
"""
LOGGING_MAXBYTES = 1 * 1024 * 1024

"""
Default name of the log file.
"""
LOGGING_DEFAULTNAME = '{project}.log'.format(project=project.PROJECT_TITLE.lower())
