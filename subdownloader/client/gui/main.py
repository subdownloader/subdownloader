# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging
import os.path
import platform
from subprocess import getstatusoutput
import sys
import webbrowser

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QEventLoop, QSettings, QSize, QTimer, Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QMainWindow

from subdownloader.client.internationalization import i18n_install
from subdownloader.languages import language
from subdownloader.project import PROJECT_TITLE, PROJECT_VERSION_STR, WEBSITE_ISSUES, WEBSITE_MAIN, WEBSITE_TRANSLATE

from subdownloader.client.gui.generated.main_ui import Ui_MainWindow
from subdownloader.client.gui.preferences import PreferencesDialog
from subdownloader.client.gui.about import AboutDialog
from subdownloader.client.gui.state import State
from subdownloader.client.gui.login import LoginDialog, login_parent_state

log = logging.getLogger('subdownloader.client.gui.main')


class Main(QMainWindow):

    permanent_language_filter_changed = pyqtSignal(list)
    loginStatusChanged = pyqtSignal(str)

    def __init__(self, parent, log_packets, options):
        QMainWindow.__init__(self, parent)

        self.setWindowTitle(PROJECT_TITLE)
        self.setWindowIcon(QIcon(':/icon'))

        self.ui = Ui_MainWindow()

        self._state = State(self, options)

        self.setup_ui()

        self.ui.tabSearchFile.set_state(self._state)
        self.ui.tabSearchName.set_state(self._state)
        self.ui.tabUpload.set_state(self._state)

        self._state.login_status_changed.connect(self.on_login_state_changed)

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

        self.ui.label_version.setText(PROJECT_VERSION_STR)

        self._state.interface_language_changed.connect(self.on_interface_language_changed)

    def retranslate(self):
        pass

    @pyqtSlot(language.Language)
    def on_interface_language_changed(self, language):
        self.setup_interface_language()
        self.ui.retranslateUi(self)
        self.retranslate()

    def get_state(self):
        return self._state

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

    @staticmethod
    def setup_interface_language():
        settings = QSettings()
        interface_locale = settings.value('options/interfaceLang', language.UnknownLanguage.create_generic().locale())
        interface_lang = language.Language.from_locale(interface_locale)

        if interface_lang.is_generic():
            interface_locale = None

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

        programPath = settings.value('options/VideoPlayerPath', '')
        if programPath == '':  # If not found videoplayer
            self.initializeVideoPlayer(settings)

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
        dialog = PreferencesDialog(self, state=self._state)
        dialog.defaultUploadLanguageChanged.connect(self.ui.tabUpload.on_default_upload_language_change)
        dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def initializeVideoPlayer(self, settings):
        predefinedVideoPlayer = None
        if platform.system() == 'Linux':
            linux_players = [{'executable': 'mplayer', 'parameters': '{0} -sub {1}'},
                             {'executable': 'vlc',
                                 'parameters': '{0} --sub-file {1}'},
                             {'executable': 'xine', 'parameters': '{0}#subtitle:{1}'}]
            for player in linux_players:
                # 1st video player to find
                status, path = getstatusoutput(
                    'which "{executable}"'.format(executable=player["executable"]))
                if status == 0:
                    predefinedVideoPlayer = {
                        'programPath': path,  'parameters': player['parameters']}
                    break

        elif platform.system() in ('Windows', 'Microsoft'):
            import _winreg
            windows_players = [{'regRoot': _winreg.HKEY_LOCAL_MACHINE, 'regFolder': 'SOFTWARE\\VideoLan\\VLC', 'regKey': '', 'parameters': '{0} --sub-file {1}'},
                               {'regRoot': _winreg.HKEY_LOCAL_MACHINE, 'regFolder': 'SOFTWARE\\Gabest\\Media Player Classic', 'regKey': 'ExePath', 'parameters': '{0} /sub {1}'}]

            for player in windows_players:
                try:
                    registry = _winreg.OpenKey(
                        player['regRoot'],  player['regFolder'])
                    path, type = _winreg.QueryValueEx(
                        registry, player['regKey'])
                    log.debug('Video Player found at: {path}'.format(path=repr(path)))
                    predefinedVideoPlayer = {
                        'programPath': path,  'parameters': player['parameters']}
                    break
                except (WindowsError, OSError) as e:
                    log.debug('Cannot find registry for {regRoot}'.format(regRoot=player['regRoot']))
        elif platform.system() == 'Darwin':  # MACOSX
            macos_players = [{'path': '/usr/bin/open', 'parameters': '-a /Applications/VLC.app {0} --sub-file {1}'},
                             {'path': '/Applications/MPlayer OSX.app/Contents/MacOS/MPlayer OSX',
                                 'parameters': '{0} -sub {1}'},
                             {'path': '/Applications/MPlayer OS X 2.app/Contents/MacOS/MPlayer OS X 2', 'parameters': '{0} -sub {1}'}]
            for player in macos_players:
                if os.path.exists(player['path']):
                    predefinedVideoPlayer = {
                        'programPath': player['path'],  'parameters': player['parameters']}

        if predefinedVideoPlayer:
            settings.setValue(
                'options/VideoPlayerPath', predefinedVideoPlayer['programPath'])
            settings.setValue(
                'options/VideoPlayerParameters', predefinedVideoPlayer['parameters'])
