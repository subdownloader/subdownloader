# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import os.path
import platform
import sys
import webbrowser

try:
    import thread
except ImportError:
    import _thread as thread

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

try:
    from commands import getstatusoutput
except ImportError:
    from subprocess import getstatusoutput

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QEventLoop, QSettings, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QProgressDialog

from subdownloader.callback import ProgressCallback
from subdownloader.client.internationalization import i18n_install

from subdownloader.languages import language

from subdownloader.client.gui.main_ui import Ui_MainWindow
from subdownloader.client.gui.preferences import PreferencesDialog
from subdownloader.client.gui.about import AboutDialog
from subdownloader.client.gui.state import State
from subdownloader.client.gui.login import LoginDialog, login_parent_state

from subdownloader.project import PROJECT_TITLE, PROJECT_VERSION, WEBSITE_ISSUES, WEBSITE_MAIN, WEBSITE_TRANSLATE

import logging
log = logging.getLogger("subdownloader.client.gui.main")


class Main(QMainWindow):

    filterLangChangedPermanent = pyqtSignal(str)
    loginStatusChanged = pyqtSignal(str)

    def __init__(self, parent, log_packets, options):
        QMainWindow.__init__(self, parent)

        self.setWindowTitle(PROJECT_TITLE)
        self.setWindowIcon(QIcon(":/icon"))

        self.ui = Ui_MainWindow()
        self.calculateProgramFolder()
        self.SetupInterfaceLang()
        self.ui.setupUi(self)

        self._state = State(self, options)

        self.ui.tabSearchFile.set_state(self._state)
        self.ui.tabSearchName.set_state(self._state)
        self.ui.tabUpload.set_state(self._state)

        self._state.login_status_changed.connect(self.on_login_state_changed)

        self.log_packets = log_packets
        self.options = options

        self.closeEvent = self.close_event
        # Fill Out the Filters Language SelectBoxes
        self.filterLangChangedPermanent.connect(self.ui.tabSearchFile.onFilterLangChangedPermanent)
        self.filterLangChangedPermanent.connect(self.ui.tabSearchName.onFilterLangChangedPermanent)
        self.InitializeFilterLanguages()
        self.read_settings()

        self.ui.tabsMain.setCurrentWidget(self.ui.tabSearchFile)




        # Menu options
        self.ui.action_Quit.triggered.connect(self.onMenuQuit)
        self.ui.action_HelpHomepage.triggered.connect(self.onMenuHelpHomepage)
        self.ui.action_HelpAbout.triggered.connect(self.onMenuHelpAbout)
        self.ui.action_HelpBug.triggered.connect(self.onMenuHelpBug)
        self.ui.action_HelpTranslate.triggered.connect(self.onMenuHelpTranslate)
        #self.ui.action_HelpDonation.triggered.connect(self.onMenuHelpDonation)

        self.ui.action_ShowPreferences.triggered.connect(self.onMenuPreferences)
        self.loginStatusChanged.connect(self.onChangeLoginStatus)

        # self.ui.button_login = QPushButton(_("Not logged yet"), self.ui.statusbar)
        self.ui.action_Login.triggered.connect(self.onButtonLogin)
        self.ui.button_login.clicked.connect(self.onButtonLogin)
        self.ui.action_LogOut.triggered.connect(self.onButtonLogOut)

        self.ui.label_version.setText(PROJECT_VERSION)

        QCoreApplication.processEvents()

        if options.videofile:
            if os.path.exists(options.videofile):
                self.SearchVideos(options.videofile)
            else:
                QMessageBox.about(
                    self, _("Error"), _("Unable to find %s") % options.videofile)

    def get_state(self):
        return self._state

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

    def SetupInterfaceLang(self):
        settings = QSettings()
        interface_locale = settings.value('options/interfaceLang', language.UnknownLanguage.create_generic().locale())
        interface_lang = language.Language.from_locale(interface_locale)

        if interface_lang.is_generic():
            interface_locale = None

        i18n_install(interface_locale)

    def calculateProgramFolder(self):
        if os.path.isdir(sys.path[0]):  # for Linux is /program_folder/
            self.programFolder = sys.path[0]
        else:  # for Windows is the /program_folder/subdownloader.py
            self.programFolder = os.path.dirname(sys.path[0])

    def log_in_default(self):
        return login_parent_state(self, self.get_state())

    def dragEnterEvent(self, event):
        # print event.mimeData().formats().join(" ")
        if event.mimeData().hasFormat("text/plain") or event.mimeData().hasFormat("text/uri-list"):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            paths = [str(u.toLocalFile()) for u in event.mimeData().urls()]
            self.ui.tabSearchFile.SearchVideos(paths)

    def read_settings(self):
        settings = QSettings()
        size = settings.value("mainwindow/size", QSize(1000, 400))
        self.resize(size)
        # FIXME: default position?
        pos = settings.value("mainwindow/pos", "")
        if pos != "":
            self.move(pos)

        programPath = settings.value("options/VideoPlayerPath", "")
        if programPath == "":  # If not found videoplayer
            self.initializeVideoPlayer(settings)

    def write_settings(self):
        settings = QSettings()
        settings.setValue("mainwindow/size", self.size())
        settings.setValue("mainwindow/pos", self.pos())

    def close_event(self, e):
        self.write_settings()
        e.accept()

    def onButtonLogin(self):
        dialog = LoginDialog(self)
        ok = dialog.exec_()

    def onButtonLogOut(self):
        self.get_state().logout()
        self.ui.button_login.setText(_("Log in"))
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
        dialog = PreferencesDialog(self)
        ok = dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def InitializeFilterLanguages(self):
        settings = QSettings()

        optionFilterLanguage = settings.value("options/filterSearchLang", "")

        self.filterLangChangedPermanent.emit(optionFilterLanguage)

    def showErrorConnection(self):
        QMessageBox.about(self, _("Alert"), _(
            "www.opensubtitles.org is not responding\nIt might be overloaded, try again in a few moments."))




    def initializeVideoPlayer(self, settings):
        predefinedVideoPlayer = None
        if platform.system() == "Linux":
            linux_players = [{'executable': 'mplayer', 'parameters': '{0} -sub {1}'},
                             {'executable': 'vlc',
                                 'parameters': '{0} --sub-file {1}'},
                             {'executable': 'xine', 'parameters': '{0}#subtitle:{1}'}]
            for player in linux_players:
                # 1st video player to find
                status, path = getstatusoutput(
                    "which %s" % player["executable"])
                if status == 0:
                    predefinedVideoPlayer = {
                        'programPath': path,  'parameters': player['parameters']}
                    break

        elif platform.system() in ("Windows", "Microsoft"):
            import _winreg
            windows_players = [{'regRoot': _winreg.HKEY_LOCAL_MACHINE, 'regFolder': 'SOFTWARE\\VideoLan\\VLC', 'regKey': '', 'parameters': '{0} --sub-file {1}'},
                               {'regRoot': _winreg.HKEY_LOCAL_MACHINE, 'regFolder': 'SOFTWARE\\Gabest\\Media Player Classic', 'regKey': 'ExePath', 'parameters': '{0} /sub {1}'}]

            for player in windows_players:
                try:
                    registry = _winreg.OpenKey(
                        player['regRoot'],  player["regFolder"])
                    path, type = _winreg.QueryValueEx(
                        registry, player["regKey"])
                    log.debug("Video Player found at: %s" % repr(path))
                    predefinedVideoPlayer = {
                        'programPath': path,  'parameters': player['parameters']}
                    break
                except (WindowsError, OSError) as e:
                    log.debug("Cannot find registry for %s" %
                              player['regRoot'])
        elif platform.system() == "Darwin":  # MACOSX
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
                "options/VideoPlayerPath", predefinedVideoPlayer['programPath'])
            settings.setValue(
                "options/VideoPlayerParameters", predefinedVideoPlayer['parameters'])

    def onUploadSelectLanguage(self, index):
        self.upload_autodetected_lang = "selected"
        self.ui.label_autodetect_lang.hide()

    def onUpgradeDetected(self):
        QMessageBox.about(
            self, _("A new version of SubDownloader has been released."))

    def _get_callback(self, titleMsg, labelMsg, finishedMsg, updatedMsg=None, cancellable=True):
        class GuiProgressCallback(ProgressCallback):
            def __init__(self, parent, titleMsg, labelMsg, finishedMsg, updatedMsg, cancellable):
                ProgressCallback.__init__(self)
                self.status_progress = QProgressDialog(labelMsg, _("&Cancel"), 0, 1, parent)
                self.status_progress.setWindowTitle(titleMsg)
                self._finishedMsg = finishedMsg
                self._updatedMsg = updatedMsg

                self._cancelled = False
                if not cancellable:
                    self.status_progress.setCancelButton(None)
                self.status_progress.canceled.connect(self.on_cancel)

                self.set_range(0, 1)

                self.status_progress.show()

            def on_update(self, value, *args, **kwargs):
                self.status_progress.setValue(value)
                if self._updatedMsg:
                    # FIXME: let the caller format the strings
                    updatedMsg = self._updatedMsg.__mod__(args)
                    self.status_progress.setLabelText(updatedMsg)
                QCoreApplication.processEvents()

            def on_finish(self, *args, **kwargs):
                # FIXME: let the caller format the strings
                windowTitle = self._finishedMsg.__mod__(args)
                self.status_progress.setWindowTitle(windowTitle)
                self.status_progress.close()
                QCoreApplication.processEvents()

            def on_rangeChange(self, minimum, maximum):
                self.status_progress.setMinimum(minimum)
                self.status_progress.setMaximum(maximum)
                QCoreApplication.processEvents()

            def on_cancel(self):
                self._cancelled = True

            def canceled(self):
                return self._cancelled

        return GuiProgressCallback(self, titleMsg, labelMsg, finishedMsg, updatedMsg, cancellable)

