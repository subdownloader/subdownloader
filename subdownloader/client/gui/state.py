# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
import os

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QDir, QObject, QSettings
from PyQt5.QtWidgets import QFileDialog

from subdownloader.callback import ProgressCallback

from subdownloader.FileManagement import get_extension, without_extension
from subdownloader.provider.SDService import SDService, TimeoutFunctionException

log = logging.getLogger('subdownloader.client.gui.state')

#FIXME: add logging!!


class State(QObject):
    def __init__(self, parent, options):
        QObject.__init__(self, parent)

        self._OSDBServer = None

        self._proxy = options.proxy

        self.read_settings()

    def read_settings(self):
        settings = QSettings()

        # If no proxy settings were passed on the command line, use the one in the settings
        if not self._proxy:
            proxy_host = settings.value("options/ProxyHost", "")
            proxy_port = int(settings.value("options/ProxyPort", 8080))
            if proxy_host:
                self._proxy = '{proxy_host}:{proxy_port}'.format(proxy_host=proxy_host, proxy_port=proxy_port)

    def connected(self):
        return self._OSDBServer is not None

    def get_OSDBServer(self):
        # FIXME: method MUST disappear
        return self._OSDBServer

    @pyqtSlot()
    def connect_server(self, callback=None):
        # FIXME: start timer. To avoid timeout. Ping server, every XX seconds.

        if not callback:
            callback = ProgressCallback()

        if self._proxy:
            updated_text = _('Connecting to server using proxy {proxy}').format(proxy=self._proxy)
        else:
            updated_text = ''

        callback.set_title_text(_('Connecting'))
        callback.set_label_text(_('Connecting to server...'))
        callback.set_finished_text(_('Connected successfully'))
        callback.set_updated_text(updated_text)
        callback.set_cancellable(False)

        callback.set_range(0, 1)

        callback.show()

        try:
            self._OSDBServer = SDService(proxy=self._proxy)
            # self._OSDBServer.connect() # FIXME: separate provider creation and connection
            callback.finish()
            return True
        except TimeoutFunctionException:
            # FIXME get rid of TimeoutFunctionException
            # FIXME: callback finish should display a failed message on exception
            callback.finish()
            self.showErrorConnection()
            QCoreApplication.processEvents() # FIXME: needed?
            return False

        except:
            log.exception('An exception was thrown during connecting.')
            # FIXME: callback finish should display a failed message on exception
            callback.finish()
            # replace by a dialog with button.
            QCoreApplication.processEvents()
            return False

    login_status_changed = pyqtSignal(int, str)

    LOGIN_STATUS_LOGGED_OUT = 0
    LOGIN_STATUS_LOGGED_IN = 1
    LOGIN_STATUS_BUSY = 2

    DEFAULT_USERNAME = ''
    DEFAULT_PASSWORD = ''

    @pyqtSlot(str, str)
    def login_user(self, username=None, password=None, callback=None):
        # FIXME: add logging!
        if not callback:
            callback = ProgressCallback()

        if not username:
            settings = QSettings()
            username = settings.value('options/LoginUsername', self.DEFAULT_USERNAME)
            password = settings.value('options/LoginPassword', self.DEFAULT_PASSWORD)

        if not password:
            password = self.DEFAULT_PASSWORD

        if self._proxy:
            updated_text = _('Connecting to server using proxy {proxy}').format(proxy=self._proxy)
        else:
            updated_text = ''

        callback.set_title_text(_("Authentication"))
        callback.set_label_text(_("Logging in..."))
        callback.set_finished_text(_('Authenticated successfully'))
        callback.set_cancellable(False)
        callback.set_range(0, 1)
        callback.show()

        self.login_status_changed.emit(self.LOGIN_STATUS_BUSY, _("Logging in..."))

        try:
            login_result = self._OSDBServer._login(username, password)
            callback.finish()

            if not login_result:
                # We try anonymous login in case the normal user login has failed
                if username:
                    callback.reinit()
                    callback.show()
                    username = ''
                    password = ''
                    login_result = self._OSDBServer._login(username, password)
                    callback.finish()

            if not login_result:
                self.login_status_changed.emit(self.LOGIN_STATUS_LOGGED_OUT, _("Login: ERROR"))

            username_display = username if username else _('Anonymous')
            message = _("Logged in as {username}").format(username=username_display)

            self.login_status_changed.emit(self.LOGIN_STATUS_LOGGED_IN, message)
            return True
        except:
            self.login_status_changed.emit(self.LOGIN_STATUS_LOGGED_OUT, _("Login: ERROR"))
            log.exception('An exception was thrown during logging in')
            callback.finish()
            return False

    @pyqtSlot()
    def logout(self):
        self._OSDBServer.logout()
        self.login_status_changed.emit(self.LOGIN_STATUS_LOGGED_OUT, _('Log in'))

    def get_users_online(self):
        try:
            data = self._OSDBServer.ServerInfo()
            return int(data["users_online_program"])
        except:
            return -1

    def download_subtitles(self, data):
        # FIXME: define interface
        return self._OSDBServer.DownloadSubtitles(data)

    def upload(self, data):
        # FIXME: define interface!
        return self._OSDBServer.UploadSubtitles(data)

    def getDownloadPath(self, video, subtitle):
        downloadFullPath = ""
        settings = QSettings()

        # Creating the Subtitle Filename
        optionSubtitleName = \
            settings.value("options/subtitleName", "SAME_VIDEO")
        sub_extension = get_extension(subtitle.get_filepath().lower())
        if optionSubtitleName == "SAME_VIDEO":
            subFileName = without_extension(
                video.get_filepath()) + "." + sub_extension
        elif optionSubtitleName == "SAME_VIDEOPLUSLANG":
            subFileName = without_extension(
                video.get_filepath()) + "." + subtitle.getLanguage().xxx() + "." + sub_extension
        elif optionSubtitleName == "SAME_VIDEOPLUSLANGANDUPLOADER":
            subFileName = without_extension(video.get_filepath(
            )) + "." + subtitle.getLanguage().xxx() + "." + subtitle.getUploader() + "." + sub_extension
        elif optionSubtitleName == "SAME_ONLINE":
            subFileName = subtitle.get_filepath()

        # Creating the Folder Destination
        optionWhereToDownload = \
            settings.value("options/whereToDownload", "SAME_FOLDER")
        if optionWhereToDownload == "ASK_FOLDER":
            folderPath = video.get_folderpath()
            dir = QDir(folderPath)
            downloadFullPath = dir.filePath(subFileName)
            downloadFullPath, t = QFileDialog.getSaveFileName(
                None, _("Save as..."), downloadFullPath, sub_extension).__str__()
            log.debug("Downloading to: %r" % downloadFullPath)
        elif optionWhereToDownload == "SAME_FOLDER":
            folderPath = video.get_folderpath()
            dir = QDir(folderPath)
            downloadFullPath = os.path.join(folderPath, subFileName)
            log.debug("Downloading to: %r" % downloadFullPath)
        elif optionWhereToDownload == "PREDEFINED_FOLDER":
            folderPath = settings.value("options/whereToDownloadFolder", "")
            dir = QDir(folderPath)
            downloadFullPath = dir.filePath(subFileName).__str__()
            log.debug("Downloading to: %r" % downloadFullPath)

        return downloadFullPath
