# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging
import os.path
from pathlib import Path
import platform
import shutil
import sys
import webbrowser

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QEventLoop, QSettings, QSize, QTimer, Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from subdownloader.client.internationalization import i18n_install
from subdownloader.languages import language
from subdownloader.project import PROJECT_TITLE, PROJECT_VERSION_FULL_STR, WEBSITE_ISSUES, WEBSITE_MAIN,\
    WEBSITE_TRANSLATE

from subdownloader.client.gui.state import GuiState
from subdownloader.client.gui.generated.main_ui import Ui_MainWindow
from subdownloader.client.gui.widgets.preferences import PreferencesDialog
from subdownloader.client.gui.widgets.about import AboutDialog
from subdownloader.client.gui.state import State
from subdownloader.client.gui.widgets.login import LoginDialog, login_parent_state

log = logging.getLogger('subdownloader.client.gui.main')


class Main(QMainWindow):

    permanent_language_filter_changed = pyqtSignal(list)
    loginStatusChanged = pyqtSignal(str)

    def __init__(self, parent, log_packets, options, settings_new, options_new):
        QMainWindow.__init__(self, parent)

        self.setWindowTitle(PROJECT_TITLE)
        self.setWindowIcon(QIcon(':/icon'))

        self.ui = Ui_MainWindow()

        self._state = GuiState()
        self._settings = settings_new
        self._settings.reload()
        self._state.load_options(options_new)
        self._state.load_settings(settings_new)

        self._state_original = State(self, options)

        self.setup_ui()

        self.ui.tabSearchFile.set_state(self._state_original, self._state)
        self.ui.tabSearchName.set_state(self._state_original, self._state)
        self.ui.tabUpload.set_state(self._state_original, self._state)

        self._state_original.login_status_changed.connect(self.on_login_state_changed)

        self.log_packets = log_packets
        self.options = options

        self.closeEvent = self.close_event
        # Fill Out the Filters Language SelectBoxes
        self.permanent_language_filter_changed.connect(self.ui.tabSearchFile.on_permanent_language_filter_change)
        self.permanent_language_filter_changed.connect(self.ui.tabSearchName.on_permanent_language_filter_change)
        self.permanent_language_filter_changed.emit(self.get_state().get_permanent_language_filter())
        self.read_settings()

        QTimer.singleShot(0, self.on_event_loop_started)

    @pyqtSlot()
    def on_event_loop_started(self):
        if not self.options.test:
            login_parent_state(self, self.get_state())

        if self.options.search.working_directory:
            videos = [videopath for videopath in self.options.search.working_directory if videopath.exists()]
            self.ui.tabSearchFile.search_videos(videos)

    def setup_ui(self):
        self.calculateProgramFolder()
        self.setup_interface_language()
        self.ui.setupUi(self)
        self.ui.tabsMain.setCurrentWidget(self.ui.tabSearchFile)

        # Menu and button options
        self.ui.action_Login.triggered.connect(self.onButtonLogin)
        self.ui.button_login.clicked.connect(self.onButtonLogin)
        self.ui.action_LogOut.triggered.connect(self.onButtonLogOut)
        self.ui.action_Quit.triggered.connect(self.onMenuQuit)
        self.ui.action_ShowPreferences.triggered.connect(self.onMenuPreferences)
        self.ui.action_HelpHomepage.triggered.connect(self.onMenuHelpHomepage)
        self.ui.action_HelpAbout.triggered.connect(self.onMenuHelpAbout)
        self.ui.action_HelpBug.triggered.connect(self.onMenuHelpBug)
        self.ui.action_HelpTranslate.triggered.connect(self.onMenuHelpTranslate)

        self.ui.action_Quit.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Q))
        self.ui.action_Quit.setShortcutContext(Qt.ApplicationShortcut)

        self.loginStatusChanged.connect(self.onChangeLoginStatus)

        self.ui.label_version.setText(PROJECT_VERSION_FULL_STR)

        self._state_original.interface_language_changed.connect(self.on_interface_language_changed)

    def retranslate(self):
        pass

    @pyqtSlot(language.Language)
    def on_interface_language_changed(self, language):
        self.setup_interface_language()
        self.ui.retranslateUi(self)
        self.retranslate()

    def get_state(self):
        return self._state_original

    def get_search_file_widget(self):
        return self.ui.tabSearchFile

    def get_search_name_widget(self):
        return self.ui.tabSearchName

    def get_upload_widget(self):
        return self.ui.tabUpload

    @pyqtSlot(int, str)
    def on_login_state_changed(self, state, message):
        log.debug('on_login_state_changed(state={state}, message={message}'.format(state=state, message=message))
        self.ui.button_login.setText(message)
        if state == State.LOGIN_STATUS_LOGGED_OUT:
            self.ui.button_login.setEnabled(True)
            self.ui.action_Login.setEnabled(True)
            self.ui.action_LogOut.setEnabled(False)
        elif state == State.LOGIN_STATUS_BUSY:
            self.ui.button_login.setEnabled(False)
            self.ui.action_Login.setEnabled(False)
            self.ui.action_LogOut.setEnabled(False)
        elif state == State.LOGIN_STATUS_LOGGED_IN:
            self.ui.button_login.setEnabled(False)
            self.ui.action_Login.setEnabled(False)
            self.ui.action_LogOut.setEnabled(True)
        else:
            log.warning('unknown state')

    def setup_interface_language(self):
        interface_lang = self._state.get_interface_language()
        if interface_lang.is_generic():
            interface_locale = None
        else:
            interface_locale = interface_lang.locale()

        i18n_install(lc=interface_locale)

    def calculateProgramFolder(self):
        if os.path.isdir(sys.path[0]):  # for Linux is /program_folder/
            self.programFolder = sys.path[0]
        else:  # for Windows is the /program_folder/subdownloader.py
            self.programFolder = os.path.dirname(sys.path[0])

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain') or event.mimeData().hasFormat('text/uri-list'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # FIXME: test + add to SearchFileWidget?
        if event.mimeData().hasFormat('text/uri-list'):
            paths = [str(u.toLocalFile()) for u in event.mimeData().urls()]
            self.ui.tabSearchFile.search_videos(paths)

    def read_settings(self):
        settings = QSettings()
        size = settings.value('mainwindow/size', QSize(1000, 400))
        self.resize(size)
        # FIXME: default position?
        pos = settings.value('mainwindow/pos', '')
        if pos != '':
            self.move(pos)

        # programPath = settings.value('options/VideoPlayerPath', '')
        # if programPath == '':  # If not found videoplayer
        #     self.initializeVideoPlayer(settings)

    def write_settings(self):
        settings = QSettings()
        settings.setValue('mainwindow/size', self.size())
        settings.setValue('mainwindow/pos', self.pos())

    def close_event(self, e):
        self.write_settings()
        e.accept()

    def onButtonLogin(self):
        dialog = LoginDialog(self)
        ok = dialog.exec_()

    def onButtonLogOut(self):
        self.get_state().logout()
        self.ui.button_login.setText(_('Log In'))
        self.ui.button_login.setEnabled(True)
        self.ui.action_Login.setEnabled(True)
        self.ui.action_LogOut.setEnabled(False)

    def onMenuQuit(self):
        self.close()

    def onChangeLoginStatus(self, statusMsg):
        self.ui.button_login.setText(statusMsg)
        QCoreApplication.processEvents()

    @pyqtSlot()
    def onActivateMenu(self):
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    @pyqtSlot()
    def onMenuHelpAbout(self):
        dialog = AboutDialog(self)
        dialog.exec_()

    def onMenuHelpHomepage(self):
        webbrowser.open(WEBSITE_MAIN, new=2, autoraise=1)

    def onMenuHelpBug(self):
        webbrowser.open(WEBSITE_ISSUES, new=2, autoraise=1)

    def onMenuHelpTranslate(self):
        webbrowser.open(WEBSITE_TRANSLATE, new=2, autoraise=1)

    def onMenuPreferences(self):
        dialog = PreferencesDialog(self, state=self._state_original, state_new=self._state, settings_new=self._settings)
        dialog.defaultUploadLanguageChanged.connect(self.ui.tabUpload.on_default_upload_language_change)
        dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
