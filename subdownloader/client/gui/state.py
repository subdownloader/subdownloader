# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging
from pathlib import Path

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QDir, QObject, QSettings
from PyQt5.QtWidgets import QFileDialog

from subdownloader.callback import ProgressCallback
from subdownloader.identification import identificator_add
from subdownloader.languages.language import Language

from subdownloader.provider.SDService import ProviderConnectionError, SDService, TimeoutFunctionException

log = logging.getLogger('subdownloader.client.gui.state')

#FIXME: add logging!!


class State(QObject):

    interface_language_changed = pyqtSignal(Language)

    def __init__(self, parent, options):
        QObject.__init__(self, parent)

        self._proxy = options.proxy
        self._OSDBServer = SDService(proxy=self._proxy)
        identificator_add(self._OSDBServer)

        self.read_settings()

    def read_settings(self):
        settings = QSettings()

        # If no proxy settings were passed on the command line, use the one in the settings
        if not self._proxy:
            proxy_host = settings.value("options/ProxyHost", "")
            proxy_port = int(settings.value("options/ProxyPort", 8080))
            if proxy_host:
                self._proxy = '{proxy_host}:{proxy_port}'.format(proxy_host=proxy_host, proxy_port=proxy_port)

    def get_permanent_language_filter(self):
        settings = QSettings()

        languages_str = settings.value('options/filterSearchLang', '')
        if languages_str:
            languages = [Language.from_xxx(lang_str) for lang_str in languages_str.split(',')]
            return languages
        else:
            return []

    def connected(self):
        return self._OSDBServer.logged_in()

    def get_OSDBServer(self):
        # FIXME: method MUST disappear
        return self._OSDBServer

    @pyqtSlot()
    def connect_server(self, callback=None):
        # FIXME: start timer. To avoid timeout. Ping server, every XX seconds.

        if callback is None:
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
            connect_res = self._OSDBServer.connect()
            callback.finish()
            return connect_res
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
                    callback.show()
                    username = ''
                    password = ''
                    login_result = self._OSDBServer._login(username, password)
                    callback.finish()

            if not login_result:
                self.login_status_changed.emit(self.LOGIN_STATUS_LOGGED_OUT, _("Login: ERROR"))
                return False

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

    def upload(self, local_movie):
        # FIXME: define interface for successful/failed upload
        can_upload = self._OSDBServer.can_upload_subtitles(local_movie)
        if not can_upload:
            return False
        try:
            self._OSDBServer.upload_subtitles(local_movie)
        except ProviderConnectionError:
            return False

        return True

    def getDownloadPath(self, parent, subtitle):
        video = subtitle.get_parent().get_parent().get_parent()
        downloadFullPath = ""
        settings = QSettings()

        # Creating the Subtitle Filename
        optionSubtitleName = settings.value('options/subtitleName', 'SAME_VIDEO')
        sub_extension = Path(subtitle.get_filename()).suffix
        if optionSubtitleName == 'SAME_VIDEO':
            subFilePath = video.get_filepath().with_suffix(sub_extension)
        elif optionSubtitleName == 'SAME_VIDEOPLUSLANG':
            subFilePath = video.get_filepath().with_suffix("." + subtitle.get_language().xxx() + sub_extension)
        elif optionSubtitleName == 'SAME_VIDEOPLUSLANGANDUPLOADER':
            subFilePath = video.get_filepath().with_suffix("." + subtitle.get_language().xxx() + "." + subtitle.get_uploader() + sub_extension)
        else:  # if optionSubtitleName == 'SAME_ONLINE':
            subFilePath = video.get_filepath().parent / subtitle.get_filename()

        # Creating the Folder Destination
        optionWhereToDownload =  settings.value('options/whereToDownload', 'SAME_FOLDER')
        if optionWhereToDownload == 'ASK_FOLDER':
            folderPath = video.get_folderpath()
            downloadFullPath = folderPath / subFilePath.name
            downloadFullPath, t = QFileDialog.getSaveFileName(
                parent, _("Save as..."), str(downloadFullPath), sub_extension)
            log.debug('Downloading to: %r' % downloadFullPath)
        elif optionWhereToDownload == 'SAME_FOLDER':
            folderPath = video.get_folderpath()
            downloadFullPath = folderPath / subFilePath.name
            log.debug('Downloading to: %r' % downloadFullPath)
        else:  # if optionWhereToDownload == 'PREDEFINED_FOLDER':
            folderPath = Path(settings.value("options/whereToDownloadFolder", ""))
            downloadFullPath = folderPath / subFilePath.name
            log.debug('Downloading to: %r' % downloadFullPath)

        return str(downloadFullPath)
