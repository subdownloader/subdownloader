# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

""" Create and launch the GUI """
import base64
import os.path
import platform
import sys
import webbrowser
import zlib

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

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QCoreApplication, \
    QEventLoop, QFileInfo, QItemSelection, QItemSelectionModel, \
    QSettings, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QHeaderView, QMainWindow, QMessageBox, QProgressDialog

try:
    from PyQt5.QtCore import QString
except ImportError:
    QString = str

from subdownloader.callback import ProgressCallback
from subdownloader.client.internationalization import i18n_install

from subdownloader.languages import language

from subdownloader.client.gui.uploadlistview import UploadListModel, UploadListView
from subdownloader.client.gui.main_ui import Ui_MainWindow
from subdownloader.client.gui.imdbSearch import imdbSearchDialog
from subdownloader.client.gui.preferences import PreferencesDialog
from subdownloader.client.gui.about import AboutDialog
from subdownloader.client.gui.state import State
from subdownloader.client.gui.login import LoginDialog, login_parent_state

from subdownloader.FileManagement import FileScan, Subtitle
from subdownloader.project import PROJECT_TITLE, PROJECT_VERSION, WEBSITE_ISSUES, WEBSITE_MAIN, WEBSITE_TRANSLATE
from subdownloader.client.gui import SELECT_SUBTITLES, SELECT_VIDEOS
from subdownloader.videofile import VideoFile
from subdownloader.subtitlefile import SubtitleFile

import logging
log = logging.getLogger("subdownloader.client.gui.main")


class Main(QMainWindow):

    filterLangChangedPermanent = pyqtSignal(str)
    language_updated = pyqtSignal(str, str)
    imdbDetected = pyqtSignal(str, str, str)
    releaseUpdated = pyqtSignal(str)
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

        self._state.login_status_changed.connect(self.on_login_state_changed)

        self.log_packets = log_packets
        self.options = options
        self.upload_autodetected_lang = ""
        self.upload_autodetected_imdb = ""

        self.closeEvent = self.close_event
        # Fill Out the Filters Language SelectBoxes
        self.filterLangChangedPermanent.connect(self.ui.tabSearchFile.onFilterLangChangedPermanent)
        self.filterLangChangedPermanent.connect(self.ui.tabSearchName.onFilterLangChangedPermanent)
        self.InitializeFilterLanguages()
        self.read_settings()

        self.ui.tabsMain.setCurrentWidget(self.ui.tabSearchFile)

        # SETTING UP UPLOAD_VIEW
        self.uploadModel = UploadListModel(self)
        self.ui.uploadView.setModel(self.uploadModel)
        # FIXME: This connection should be cleaner.
        self.uploadModel._main = self

        # Resizing the headers to take all the space(50/50) in the TableView
        header = self.ui.uploadView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.ui.buttonUploadBrowseFolder.clicked.connect(
            self.onUploadBrowseFolder)
        self.ui.uploadView.activated.connect(self.onUploadClickViewCell)
        self.ui.uploadView.clicked.connect(self.onUploadClickViewCell)

        self.ui.buttonUpload.clicked.connect(self.onUploadButton)

        self.ui.buttonUploadUpRow.clicked.connect(
            self.uploadModel.onUploadButtonUpRow)
        self.ui.buttonUploadDownRow.clicked.connect(
            self.uploadModel.onUploadButtonDownRow)
        self.ui.buttonUploadPlusRow.clicked.connect(
            self.uploadModel.onUploadButtonPlusRow)
        self.ui.buttonUploadMinusRow.clicked.connect(
            self.uploadModel.onUploadButtonMinusRow)
        self.ui.buttonUploadDeleteAllRow.clicked.connect(
            self.uploadModel.onUploadButtonDeleteAllRow)

        self.ui.buttonUploadFindIMDB.clicked.connect(
            self.onButtonUploadFindIMDB)
        self.ui.uploadIMDB.activated.connect(self.onUploadSelectImdb)

        self.uploadSelectionModel = QItemSelectionModel(self.uploadModel)
        self.ui.uploadView.setSelectionModel(self.uploadSelectionModel)
        self.uploadSelectionModel.selectionChanged.connect(
            self.onUploadChangeSelection)

        self.imdbDetected.connect(self.onUploadIMDBNewSelection)

        self.releaseUpdated.connect(self.OnChangeReleaseName)

        self.ui.label_autodetect_imdb.hide()
        self.ui.label_autodetect_lang.hide()
        # print self.ui.uploadView.sizeHint ()
        # self.ui.uploadView.adjustSize()
        # self.ui.groupBox_2.adjustSize()
        # self.ui.uploadDetailsGroupBox.adjustSize()
        # self.adjustSize()


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
        # self.ui.label_status.setIndent(10)
        # self.status_label.setIndent(10)

        # self.ui.statusbar.addWidget(self.status_label)
        # self.ui.statusbar.addWidget(self.ui.button_login)

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
            paths = [str(u.toLocalFile())
                     for u in event.mimeData().urls()]
            self.SearchVideos(paths)

    def read_settings(self):
        settings = QSettings()
        size = settings.value("mainwindow/size", QSize(1000, 400))
        self.resize(size)
        # FIXME: default position?
        pos = settings.value("mainwindow/pos", "")
        if pos != "":
            self.move(pos)

        size = settings.beginReadArray("upload/imdbHistory")
        for i in range(size):
            settings.setArrayIndex(i)
            imdbId = settings.value("imdbId")
            title = settings.value("title")
            self.ui.uploadIMDB.addItem("%s : %s" % (imdbId, title), imdbId)
        settings.endArray()

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
        for lang in language.legal_languages():
            self.ui.uploadLanguages.addItem(
                _(lang.name()), lang.xxx())

        settings = QSettings()
        optionUploadLanguage = settings.value("options/uploadLanguage", "eng")
        index = self.ui.uploadLanguages.findData(optionUploadLanguage)
        if index != -1:
            self.ui.uploadLanguages.setCurrentIndex(index)

        self.ui.uploadLanguages.adjustSize()

        optionFilterLanguage = settings.value("options/filterSearchLang", "")

        self.filterLangChangedPermanent.emit(optionFilterLanguage)

        self.language_updated.connect(
            self.onUploadLanguageDetection)

    def showErrorConnection(self):
        QMessageBox.about(self, _("Alert"), _(
            "www.opensubtitles.org is not responding\nIt might be overloaded, try again in a few moments."))

    # UPLOAD METHODS

    def onButtonUploadFindIMDB(self):
        dialog = imdbSearchDialog(self)
        ok = dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def onUploadBrowseFolder(self):
        settings = QSettings()
        path = settings.value("mainwindow/workingDirectory", "")
        directory = QFileDialog.getExistingDirectory(
            None, _("Select a directory"), path)
        if directory:
            settings.setValue("mainwindow/workingDirectory", directory)
            videos_found, subs_found = FileScan.ScanFolder(
                directory, callback=None, recursively=False)
            log.info("Videos found: %i Subtitles found: %i" %
                     (len(videos_found), len(subs_found)))
            self.uploadModel.layoutAboutToBeChanged.emit()
            for row, video in enumerate(videos_found):
                self.uploadModel.addVideos(row, [video])
                subtitle = Subtitle.AutoDetectSubtitle(video.get_filepath())
                if subtitle:
                    sub = SubtitleFile(False, subtitle)
                    self.uploadModel.addSubs(row, [sub])
            if not len(videos_found):
                for row, sub in enumerate(subs_found):
                    self.uploadModel.addSubs(row, [sub])
            self.ui.uploadView.resizeRowsToContents()
            self.uploadModel.layoutChanged.emit()
            thread.start_new_thread(self.AutoDetectNFOfile, (directory, ))
            thread.start_new_thread(self.uploadModel.ObtainUploadInfo, ())

    def AutoDetectNFOfile(self, folder):
        imdb_id = FileScan.AutoDetectNFOfile(folder)
        if imdb_id:
            results = self.get_state().get_OSDBServer().GetIMDBMovieDetails(imdb_id)
            if results['title']:
                self.imdbDetected.emit(imdb_id, results['title'],  "nfo")

    def onUploadButton(self, clicked):
        ok, error = self.uploadModel.validate()
        if not ok:
            QMessageBox.about(self, _("Error"), error)
            return
        else:
            imdb_id = self.ui.uploadIMDB.itemData(self.ui.uploadIMDB.currentIndex())
            if imdb_id is None:  # No IMDB
                QMessageBox.about(
                    self, _("Error"), _("Please identify the movie."))
                return
            else:
                #def _get_callback(self, titleMsg, labelMsg, finishedMsg, updatedMsg=None, cancellable=True):
                callback = self._get_callback(_("Uploading..."), _("Uploading subtitle"), "")
                self.setCursor(Qt.WaitCursor)

                log.debug("Compressing subtitle...")
                details = {}
                details['IDMovieImdb'] = imdb_id
                lang_xxx = self.ui.uploadLanguages.itemData(
                        self.ui.uploadLanguages.currentIndex())
                details['sublanguageid'] = lang_xxx
                details['movieaka'] = ''
                details['moviereleasename'] = self.ui.uploadReleaseText.text()
                comments = self.ui.uploadComments.toPlainText()
                details['subauthorcomment'] = comments

                movie_info = {}
                movie_info['baseinfo'] = {'idmovieimdb': details['IDMovieImdb'], 'moviereleasename': details['moviereleasename'], 'movieaka': details[
                    'movieaka'], 'sublanguageid': details['sublanguageid'], 'subauthorcomment': details['subauthorcomment']}

                nb = self.uploadModel.getTotalRows()
                callback.set_range(0, nb)
                for i in range(nb):
                    curr_sub = self.uploadModel._subs[i]
                    curr_video = self.uploadModel._videos[i]
                    if curr_sub:  # Make sure is not an empty row with None
                        buf = open(curr_sub.get_filepath(), mode='rb').read()
                        curr_sub_content = base64.encodestring(zlib.compress(buf))
                        cd = "cd" + str(i)
                        movie_info[cd] = {'subhash': curr_sub.get_hash(), 'subfilename': curr_sub.get_filepath(), 'moviehash': curr_video.calculateOSDBHash(), 'moviebytesize': curr_video.get_size(
                        ), 'movietimems': curr_video.get_time_ms(), 'moviefps': curr_video.get_fps(), 'moviefilename': curr_video.get_filepath(), 'subcontent': curr_sub_content}
                    callback.update(i)

                try:
                    info = self.get_state().upload(movie_info)
                    callback.finish()
                    if info['status'] == "200 OK":
                        successBox = QMessageBox(_("Successful Upload"),
                                                 _(
                                                     "Subtitles successfully uploaded.\nMany Thanks!"),
                                                 QMessageBox.Information,
                                                 QMessageBox.Ok | QMessageBox.Default | QMessageBox.Escape,
                                                 QMessageBox.NoButton,
                                                 QMessageBox.NoButton,
                                                 self)

                        saveAsButton = successBox.addButton(
                            _("View Subtitle Info"), QMessageBox.ActionRole)
                        answer = successBox.exec_()
                        if answer == QMessageBox.NoButton:
                            webbrowser.open(info['data'], new=2, autoraise=1)
                        self.uploadCleanWindow()
                    else:
                        QMessageBox.about(self, _("Error"), _(
                            "Problem while uploading...\nError: %s") % info['status'])
                except:
                    callback.finish()
                    QMessageBox.about(self, _("Error"), _(
                        "Error contacting the server. Please restart or try later"))
                self.setCursor(Qt.ArrowCursor)

    def uploadCleanWindow(self):
        self.uploadReleaseText.setText("")
        self.uploadComments.setText("")
        self.upload_autodetected_lang = ""
        self.upload_autodetected_imdb = ""
        # Note: We don't reset the language
        self.uploadModel.layoutAboutToBeChanged.emit()
        self.uploadModel.removeAll()
        self.uploadModel.layoutChanged.emit()
        self.ui.label_autodetect_imdb.hide()
        self.ui.label_autodetect_lang.hide()
        index = self.ui.uploadIMDB.findData("")
        if index != -1:
            self.ui.uploadIMDB.setCurrentIndex(index)

    @pyqtSlot(str, str, str)
    def onUploadIMDBNewSelection(self, id, title, origin=""):
        log.debug(
            "onUploadIMDBNewSelection, id: %s, title: %s, origin: %s" % (id, title, origin))
        if origin == "nfo" and not self.upload_autodetected_imdb or self.upload_autodetected_imdb == "nfo":
            self.ui.label_autodetect_imdb.setText(
                _(u'↓ Movie autodetected from .nfo file'))
            self.ui.label_autodetect_imdb.show()
        elif origin == "database" and not self.upload_autodetected_imdb:
            self.ui.label_autodetect_imdb.setText(
                _(u'↓ Movie autodetected from database'))
            self.ui.label_autodetect_imdb.show()
        else:
            self.ui.label_autodetect_imdb.hide()

        # Let's select the item with that id.
        index = self.ui.uploadIMDB.findData(id)
        if index != -1:
            self.ui.uploadIMDB.setCurrentIndex(index)
        else:
            self.ui.uploadIMDB.addItem("%s : %s" % (id, title), id)
            index = self.ui.uploadIMDB.findData(id)
            self.ui.uploadIMDB.setCurrentIndex(index)

            # Adding the new IMDB in our settings historial
            settings = QSettings()
            size = settings.beginReadArray("upload/imdbHistory")
            settings.endArray()
            settings.beginWriteArray("upload/imdbHistory")
            settings.setArrayIndex(size)
            settings.setValue("imdbId", id)
            settings.setValue("title", title)
            settings.endArray()

            #imdbHistoryList = settings.value("upload/imdbHistory", []).toList()
            # print imdbHistoryList
            #imdbHistoryList.append({'id': id,  'title': title})
            #settings.setValue("upload/imdbHistory", imdbHistoryList)
            # print id
            # print title

    @pyqtSlot(str, str)
    def onUploadLanguageDetection(self, lang_xxx, origin=""):
        settings = QSettings()
        origin = origin
        optionUploadLanguage = settings.value("options/uploadLanguage", "")
        if optionUploadLanguage != "":
            self.ui.label_autodetect_lang.hide()
        else:  # if we have selected <Autodetect> in preferences
            if origin == "database" and self.upload_autodetected_lang != "filename" and self.upload_autodetected_lang != "selected":
                self.ui.label_autodetect_lang.setText(
                    _(u'↑ Language autodetected from database'))
                self.ui.label_autodetect_lang.show()
                self.upload_autodetected_lang = origin
            elif origin == "filename" and self.upload_autodetected_lang != "selected":
                self.ui.label_autodetect_lang.setText(
                    _(u"↑ Language autodetected from subtitle's filename"))
                self.ui.label_autodetect_lang.show()
                self.upload_autodetected_lang = origin
            elif origin == "content" and not self.upload_autodetected_lang or self.upload_autodetected_lang == "content":
                self.ui.label_autodetect_lang.setText(
                    _(u"↑ Language autodetected from subtitle's content"))
                self.ui.label_autodetect_lang.show()
                self.upload_autodetected_lang = origin
            elif not origin:
                self.ui.label_autodetect_lang.hide()
            # Let's select the item with that id.
            index = self.uploadLanguages.findData(lang_xxx)
            if index != -1:
                self.uploadLanguages.setCurrentIndex(index)
                return

    def updateButtonsUpload(self):
        self.ui.uploadView.resizeRowsToContents()
        selected = self.uploadSelectionModel.selection()
        total_selected = selected.count()
        if total_selected == 1:
            self.uploadModel.rowsSelected = [
                selected.last().bottomRight().row()]
            self.ui.buttonUploadMinusRow.setEnabled(True)
            if self.uploadModel.rowsSelected[0] != self.uploadModel.getTotalRows() - 1:
                self.ui.buttonUploadDownRow.setEnabled(True)
            else:
                self.ui.buttonUploadDownRow.setEnabled(False)

            if self.uploadModel.rowsSelected[0] != 0:
                self.ui.buttonUploadUpRow.setEnabled(True)
            else:
                self.ui.buttonUploadUpRow.setEnabled(False)

        elif total_selected > 1:
            self.ui.buttonUploadDownRow.setEnabled(False)
            self.ui.buttonUploadUpRow.setEnabled(False)
            self.ui.buttonUploadMinusRow.setEnabled(True)
            self.uploadModel.rowsSelected = []
            for range in selected:
                self.uploadModel.rowsSelected.append(range.bottomRight().row())
        else:  # nothing selected
            self.uploadModel.rowsSelected = None
            self.ui.buttonUploadDownRow.setEnabled(False)
            self.ui.buttonUploadUpRow.setEnabled(False)
            self.ui.buttonUploadMinusRow.setEnabled(False)

    @pyqtSlot(QItemSelection, QItemSelection)
    def onUploadChangeSelection(self, selected, unselected):
        self.updateButtonsUpload()

    def onUploadClickViewCell(self, index):
        row, col = index.row(), index.column()
        settings = QSettings()
        currentDir = settings.value("mainwindow/workingDirectory", '')

        if col == UploadListView.COL_VIDEO:
            fileName, t = QFileDialog.getOpenFileName(
                self, _("Browse video..."), currentDir, SELECT_VIDEOS)
            if fileName:
                settings.setValue(
                    "mainwindow/workingDirectory", QFileInfo(fileName).absolutePath())
                video = VideoFile(fileName)
                self.uploadModel.layoutAboutToBeChanged.emit()
                self.uploadModel.addVideos(row, [video])
                subtitle = Subtitle.AutoDetectSubtitle(video.get_filepath())
                if subtitle:
                    sub = SubtitleFile(False, subtitle)
                    self.uploadModel.addSubs(row, [sub])
                    thread.start_new_thread(
                        self.uploadModel.ObtainUploadInfo, ())
                self.ui.uploadView.resizeRowsToContents()
                self.uploadModel.layoutChanged.emit()
                thread.start_new_thread(
                    self.AutoDetectNFOfile, (os.path.dirname(fileName), ))

        else:
            fileName, t = QFileDialog.getOpenFileName(
                self, _("Browse subtitle..."), currentDir, SELECT_SUBTITLES)
            if fileName:
                settings.setValue(
                    "mainwindow/workingDirectory", QFileInfo(fileName).absolutePath())
                sub = SubtitleFile(False, fileName)
                self.uploadModel.layoutAboutToBeChanged.emit()
                self.uploadModel.addSubs(row, [sub])
                self.ui.uploadView.resizeRowsToContents()
                self.uploadModel.layoutChanged.emit()
                thread.start_new_thread(self.uploadModel.ObtainUploadInfo, ())

    def OnChangeReleaseName(self, name):
        self.ui.uploadReleaseText.setText(name)

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

    def onUploadSelectImdb(self, index):
        self.upload_autodetected_imdb = "selected"
        self.ui.label_autodetect_imdb.hide()

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

