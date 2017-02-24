# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

""" Create and launch the GUI """
import base64
import gettext
import locale
import os.path
import platform
import re
import sys
import time
import traceback
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

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QCoreApplication, QDir, \
    QEventLoop, QFileInfo, QItemSelection, QItemSelectionModel, QModelIndex, \
    QObject, QSettings, QSize, QTime
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QFileSystemModel, \
    QFileDialog, QHeaderView, QLabel, QMainWindow, QMenu, \
    QMessageBox, QProgressDialog, QPushButton

try:
    from PyQt5.QtCore import QString
except ImportError:
    QString = str

from subdownloader.callback import ProgressCallback
from subdownloader.client.gui.SplashScreen import SplashScreen
from subdownloader.client.internationalization import i18n_install
from subdownloader.FileManagement import get_extension, without_extension

# create splash screen and show messages to the user
app = QApplication(sys.argv)
splash = SplashScreen()
splash.showMessage("Loading...") #FIXME: add translation!
QCoreApplication.flush()

from subdownloader.languages import language
from subdownloader.provider.SDService import SDService, TimeoutFunctionException

from subdownloader.client.gui.uploadlistview import UploadListModel, UploadListView
from subdownloader.client.gui.videotreeview import VideoTreeModel

from subdownloader.client.gui.main_ui import Ui_MainWindow
from subdownloader.client.gui.imdbSearch import imdbSearchDialog
from subdownloader.client.gui.preferences import PreferencesDialog
from subdownloader.client.gui.about import AboutDialog

from subdownloader.client.gui.chooseLanguage import chooseLanguageDialog
from subdownloader.client.gui.login import LoginDialog
from subdownloader.FileManagement import FileScan, Subtitle
from subdownloader.project import PROJECT_TITLE, PROJECT_VERSION, WEBSITE_ISSUES, WEBSITE_MAIN, WEBSITE_TRANSLATE
from subdownloader.search import *
from subdownloader.videofile import VideoFile, VIDEOS_EXT
from subdownloader.subtitlefile import SubtitleFile, SUBTITLES_EXT

import logging
log = logging.getLogger("subdownloader.client.gui.main")
splash.showMessage(_("Building main dialog..."))

SELECT_SUBTITLES = _("Subtitle Files (*.%s)") % " *.".join(SUBTITLES_EXT)
SELECT_VIDEOS = _("Video Files (*.%s)") % " *.".join(VIDEOS_EXT)


class Main(QMainWindow):

    filterLangChangedPermanent = pyqtSignal(str)
    language_updated = pyqtSignal(str, str)
    imdbDetected = pyqtSignal(str, str, str)
    releaseUpdated = pyqtSignal(str)
    softwareUpdateDetected = pyqtSignal(str, str)
    loginStatusChanged = pyqtSignal(str)

    def __init__(self, parent, log_packets, options):
        QMainWindow.__init__(self, parent)

        self.setWindowTitle(PROJECT_TITLE)
        self.setWindowIcon(QIcon(":/icon"))

        self.ui = Ui_MainWindow()

        self.timeLastSearch = QTime.currentTime()

        self.log_packets = log_packets
        self.options = options
        self.upload_autodetected_lang = ""
        self.upload_autodetected_imdb = ""

        self.calculateProgramFolder()
        self.SetupInterfaceLang()
        self.ui.setupUi(self)
        self.closeEvent = self.close_event
        # Fill Out the Filters Language SelectBoxes
        self.filterLangChangedPermanent.connect(
            self.onFilterLangChangedPermanent)
        self.InitializeFilterLanguages()
        self.read_settings()
        # self.treeView.reset()
        self.ui.splitter.setSizes([600, 1000])

        # SETTING UP FOLDERVIEW
        model = QFileSystemModel(self)
        model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        self.ui.folderView.setModel(model)

        settings = QSettings()

        self.ui.folderView.header().hide()
        self.ui.folderView.hideColumn(3)
        self.ui.folderView.hideColumn(2)
        self.ui.folderView.hideColumn(1)
        self.ui.folderView.show()

        introduction = '<p align="center"><h2>{title}</h2></p>' \
            '<p><b>{tab1header}</b><br>{tab1content}</p>' \
            '<p><b>{tab2header}</b><br>{tab2content}</p>'\
            '<p><b>{tab3header}</b><br>{tab3content}</p>'.format(
                title=_("How To Use {title}").format(title=PROJECT_TITLE),
                tab1header=_("1st Tab:"),
                tab2header=_("2nd Tab:"),
                tab3header=_("3rd Tab:"),
                tab1content=_("Select, from the Folder Tree on the left, the folder which contains the videos "
                              "that need subtitles. {project} will then try to automatically find available "
                              "subtitles.").format(project=PROJECT_TITLE),
                tab2content=_("If you don't have the videos in your machine, ou can search subtitles by "
                               "introducing the title/name of the video."),
                tab3content=_("If you have found some subtitle somewhere else that is not in {project}'s database, "
                               "please upload those subtitles so next users will be able to "
                               "find them more easily.").format(project=PROJECT_TITLE))
        self.ui.introductionHelp.setHtml(introduction)

        self.ui.tabsMain.setCurrentIndex(0)
        self.showInstructions()

        # Loop to expand the current directory in the folderview.
        lastDir = \
            settings.value("mainwindow/workingDirectory", QDir.homePath())
        log.debug('Current directory: %s' % lastDir)
        model.setRootPath(lastDir)
        path = QDir(lastDir)
        while True:
            self.ui.folderView.expand(model.index(path.absolutePath()))
            if not path.cdUp():
                break

        self.ui.folderView.setSortingEnabled(True)
        self.ui.folderView.sortByColumn(0, 0)
        self.ui.folderView.scrollTo(model.index(lastDir))
        self.ui.folderView.clicked.connect(self.onFolderTreeClicked)
        self.ui.buttonFind.clicked.connect(self.onButtonFind)
        self.ui.buttonRefresh.clicked.connect(self.onButtonRefresh)

        # SETTING UP SEARCH_VIDEO_VIEW
        self.videoModel = VideoTreeModel(self)
        self.ui.videoView.setModel(self.videoModel)
        self.ui.videoView.activated.connect(self.onClickVideoTreeView)
        self.ui.videoView.clicked.connect(self.onClickVideoTreeView)
        self.ui.videoView.customContextMenuRequested.connect(self.onContext)
        self.videoModel.dataChanged.connect(self.subtitlesCheckedChanged)

        self.ui.buttonSearchSelectVideos.clicked.connect(
            self.onButtonSearchSelectVideos)
        self.ui.buttonSearchSelectFolder.clicked.connect(
            self.onButtonSearchSelectFolder)
        self.ui.buttonDownload.clicked.connect(self.onButtonDownload)
        self.ui.buttonPlay.clicked.connect(self.onButtonPlay)
        self.ui.buttonIMDB.clicked.connect(self.onViewOnlineInfo)
        self.ui.videoView.setContextMenuPolicy(Qt.CustomContextMenu)

        # Drag and Drop files to the videoView enabled
        self.ui.videoView.__class__.dragEnterEvent = self.dragEnterEvent
        self.ui.videoView.__class__.dragMoveEvent = self.dragEnterEvent
        self.ui.videoView.__class__.dropEvent = self.dropEvent
        self.ui.videoView.setAcceptDrops(1)

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

        self.softwareUpdateDetected.connect(self.OnSoftwareUpdateDetected)

        self.ui.label_autodetect_imdb.hide()
        self.ui.label_autodetect_lang.hide()
        # print self.ui.uploadView.sizeHint ()
        # self.ui.uploadView.adjustSize()
        # self.ui.groupBox_2.adjustSize()
        # self.ui.uploadDetailsGroupBox.adjustSize()
        # self.adjustSize()

        # Search by Name
        self.ui.buttonSearchByName.clicked.connect(self.onButtonSearchByTitle)
        self.ui.movieNameText.returnPressed.connect(self.onButtonSearchByTitle)
        self.ui.buttonDownloadByTitle.clicked.connect(
            self.onButtonDownloadByTitle)

        self.ui.buttonIMDBByTitle.clicked.connect(self.onViewOnlineInfo)
        self.moviesModel = VideoTreeModel(self)
        self.ui.moviesView.setModel(self.moviesModel)

        self.ui.videoView.clicked.connect(self.onClickMovieTreeView)
        self.ui.moviesView.clicked.connect(self.onClickMovieTreeView)
        self.moviesModel.dataChanged.connect(self.subtitlesMovieCheckedChanged)

        self.ui.moviesView.expanded.connect(self.onExpandMovie)
        self.ui.moviesView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.moviesView.customContextMenuRequested.connect(self.onContext)

        # Menu options
        self.ui.action_Quit.triggered.connect(self.onMenuQuit)
        self.ui.action_HelpHomepage.triggered.connect(self.onMenuHelpHomepage)
        self.ui.action_HelpAbout.triggered.connect(self.onMenuHelpAbout)
        self.ui.action_HelpBug.triggered.connect(self.onMenuHelpBug)
        self.ui.action_HelpTranslate.triggered.connect(self.onMenuHelpTranslate)
        #self.ui.action_HelpDonation.triggered.connect(self.onMenuHelpDonation)

        self.ui.action_ShowPreferences.triggered.connect(self.onMenuPreferences)
        self.loginStatusChanged.connect(self.onChangeLoginStatus)

        self.login_button = QPushButton(_("Not logged yet"), self.ui.statusbar)
        self.ui.action_Login.triggered.connect(self.onButtonLogin)
        self.login_button.clicked.connect(self.onButtonLogin)
        self.ui.action_LogOut.triggered.connect(self.onButtonLogOut)
        self.status_label = QLabel("v" + PROJECT_VERSION, self.ui.statusbar)
        self.status_label.setIndent(10)

        #self.donate_button = QPushButton(
        #    "   " + _("Help Us With 5 USD/EUR"))
        # self.donate_button.setIndent(10)

        #if platform.system() in ("Windows", "Microsoft"):
        #    iconpaypal = QIcon()
        #    iconpaypal.addPixmap(
        #        QPixmap(":/images/paypal.png"), QIcon.Normal, QIcon.On)
        #    self.donate_button.setIcon(iconpaypal)
        #    self.donate_button.setIconSize(QSize(50, 24))

        #self.donate_button.clicked.connect(self.onMenuHelpDonation)

        self.ui.statusbar.insertWidget(0, self.status_label)
        self.ui.statusbar.insertWidget(1, self.login_button)
        # self.statusbar.addPermanentWidget(self.donate_button, 0)
        # self.statusbar.addPermanentWidget(self.login_button,0)
        # self.statusbar.addPermanentItem(horizontalLayout_4,2)
        # self.status("")

        if not options.test:
            # print
            # self.OSDBServer.xmlrpc_server.GetTranslation(self.OSDBServer._token,
            # 'ar', 'po','subdownloader')
            self.setCursor(Qt.WaitCursor)
            # and self.OSDBServer.is_connected():
            if self.establishServerConnection():
                settings = QSettings()
                if options.username:
                    loginUsername = options.username
                    loginPassword = options.password
                else:
                    loginUsername = settings.value("options/LoginUsername", "")
                    loginPassword = settings.value("options/LoginPassword", "")
                self.login_user(loginUsername, loginPassword)
                # thread.start_new_thread(self.OSDBServer.NoOperation, (900, ))
                # #check expire session every 15min
            else:
                QMessageBox.about(self, _("Error"), _(
                    "Error contacting the server. Please try again later"))
            self.setCursor(Qt.ArrowCursor)
        QCoreApplication.processEvents()

        if options.videofile:
            if os.path.exists(options.videofile):
                self.SearchVideos(options.videofile)
            else:
                QMessageBox.about(
                    self, _("Error"), _("Unable to find %s") % options.videofile)

    def onButtonRefresh(self):
        settings = QSettings()
        lastDir = settings.value("mainwindow/workingDirectory", QDir.homePath())
        path = QDir(lastDir)
        model = QFileSystemModel(self)
        model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        model.setRootPath(lastDir)
        self.ui.folderView.setModel(model)

        self.ui.folderView.show()

        while True:
            self.ui.folderView.expand(model.index(path.absolutePath()))
            if not path.cdUp():
                break

    def SetupInterfaceLang(self):
        settings = QSettings()
        interface_locale = settings.value('options/interfaceLang', language.UnknownLanguage.create_generic().locale())
        interface_lang = language.Language.from_locale(interface_locale)

        if interface_lang.is_generic():
            interface_locale = None

        i18n_install(interface_locale)

    def chooseInterfaceLanguage(self, user_locale):
        self.choosenLanguage = 'en'  # By default
        dialog = chooseLanguageDialog(self, user_locale)
        dialog.show()
        ok = dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        return self.choosenLanguage

    def calculateProgramFolder(self):
        if os.path.isdir(sys.path[0]):  # for Linux is /program_folder/
            self.programFolder = sys.path[0]
        else:  # for Windows is the /program_folder/subdownloader.py
            self.programFolder = os.path.dirname(sys.path[0])

    def showInstructions(self):
        self.ui.stackedSearchResult.setCurrentWidget(self.ui.pageIntroduction)

    def hideInstructions(self):
        self.ui.stackedSearchResult.setCurrentWidget(self.ui.pageSearchResult)

    def openExternalUrl(self, url):
        webbrowser.open(str(url), new=2, autoraise=1)

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

    def onContext(self, point):  # Create a menu
        menu = QMenu("Menu", self)
        # Tab for SearchByHash TODO:replace this 0 by an ENUM value
        if self.ui.tabsMain.currentIndex() == 0:
            listview = self.ui.videoView
        else:
            listview = self.ui.moviesView
        index = listview.currentIndex()
        treeItem = listview.model().getSelectedItem(index)
        if treeItem != None:
            if type(treeItem.data) == VideoFile:
                video = treeItem.data
                movie_info = video.getMovieInfo()
                if movie_info:
                    subWebsiteAction = QAction(
                        QIcon(":/images/info.png"), _("View IMDB info"), self)
                    subWebsiteAction.triggered.connect(self.onViewOnlineInfo)
                else:
                    subWebsiteAction = QAction(
                        QIcon(":/images/info.png"), _("Set IMDB info..."), self)
                    subWebsiteAction.triggered.connect(self.onSetIMDBInfo)
                menu.addAction(subWebsiteAction)
            elif type(treeItem.data) == SubtitleFile:  # Subtitle
                treeItem.checked = True
                self.videoModel.dataChanged.emit(index, index)
                downloadAction = QAction(
                    QIcon(":/images/download.png"), _("Download"), self)
                # Video tab, TODO:Replace me with a enum
                if self.ui.tabsMain.currentIndex() == 0:
                    downloadAction.triggered.connect(self.onButtonDownload)
                    playAction = QAction(
                        QIcon(":/images/play.png"), _("Play video + subtitle"), self)
                    playAction.triggered.connect(self.onButtonPlay)
                    menu.addAction(playAction)
                else:
                    downloadAction.triggered.connect(
                        self.onButtonDownloadByTitle)
                subWebsiteAction = QAction(
                    QIcon(":/images/sites/opensubtitles.png"), _("View online info"), self)

                menu.addAction(downloadAction)
                subWebsiteAction.triggered.connect(self.onViewOnlineInfo)
                menu.addAction(subWebsiteAction)
            elif type(treeItem.data) == Movie:
                movie = treeItem.data
                subWebsiteAction = QAction(
                    QIcon(":/images/info.png"), _("View IMDB info"), self)
                subWebsiteAction.triggered.connect(self.onViewOnlineInfo)
                menu.addAction(subWebsiteAction)

        # Show the context menu.
        menu.exec_(listview.mapToGlobal(point))

    def onSetIMDBInfo(self):
        QMessageBox.about(
            self, _("Info"), "Not implemented yet. Sorry...")

    def onViewOnlineInfo(self):
        # Tab for SearchByHash TODO:replace this 0 by an ENUM value
        if self.ui.tabsMain.currentIndex() == 0:
            listview = self.ui.videoView
        else:
            listview = self.ui.moviesView
        index = listview.currentIndex()
        treeItem = listview.model().getSelectedItem(index)

        if type(treeItem.data) == VideoFile:
            video = self.videoModel.getSelectedItem().data
            movie_info = video.getMovieInfo()
            if movie_info:
                imdb = movie_info["IDMovieImdb"]
                if imdb:
                    webbrowser.open(
                        "http://www.imdb.com/title/tt%s" % imdb, new=2, autoraise=1)
        elif type(treeItem.data) == SubtitleFile:  # Subtitle
            sub = treeItem.data
            if sub.isOnline():
                webbrowser.open(
                    "http://www.opensubtitles.org/en/subtitles/%s/" % sub.getIdOnline(), new=2, autoraise=1)

        elif type(treeItem.data) == Movie:
            movie = self.moviesModel.getSelectedItem().data
            imdb = movie.IMDBId
            if imdb:
                webbrowser.open(
                    "http://www.imdb.com/title/tt%s" % imdb, new=2, autoraise=1)

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

    def OnSoftwareUpdateDetected(self, new_version, update_link):
        warningBox = QMessageBox(_("New Version Detected"),
                                 _("A new version of SubDownloader has been released.\n\nNew Version: %s\nCurrent Version: %s\n\n"
                                   "Would you like to download the new version now?") % (new_version, PROJECT_VERSION),
                                 QMessageBox.Information,
                                 QMessageBox.Yes | QMessageBox.Default,
                                 QMessageBox.Cancel | QMessageBox.Escape,
                                 QMessageBox.NoButton,
                                 self)
        answer = warningBox.exec_()
        if answer == QMessageBox.Yes:
            webbrowser.open(update_link, new=2, autoraise=1)
        elif answer == QMessageBox.Cancel:
            return

    def update_users(self, sleeptime=60):
        # REMARK: to be used by a thread
        while 1:
            self.status_label.setText(_("Users online: Updating..."))
            try:
                # we cant use the timeout class inherited in OSDBServer
                data = self.OSDBServer.ServerInfo()
                self.status_label.setText(
                    _("Users online: %s" % str(data["users_online_program"])))
            except:
                self.status_label.setText(_("Users online: ERROR"))
            time.sleep(sleeptime)

    def onButtonLogin(self):
        dialog = LoginDialog(self)
        ok = dialog.exec_()

    def login_user(self, username, password):
        #self.setLoginStatus.emit("Trying to login...")
        callback = self._get_callback(_("Authentication"), _("Logging in..."), "", cancellable=False)
        self.login_button.setText(_("Logging in..."))

        QCoreApplication.processEvents()
        try:
            if self.OSDBServer._login(username, password):
                if not username:
                    username = _('Anonymous')
                self.login_button.setText(_("Logged as %s") % username)
                callback.finish()
                self.login_button.setEnabled(False)
                self.ui.action_Login.setEnabled(False)
                self.ui.action_LogOut.setEnabled(True)
                return True
            # We try anonymous login in case the normal user login has failed
            elif username:
                self.login_button.setText(_("Login as %s: ERROR") % username)
                callback.finish()
                return False
        except Exception as e:
            self.login_button.setText(_("Login: ERROR"))
            traceback.print_exc(e)
            callback.finish()
            return False

    def onButtonLogOut(self):
        self.OSDBServer.logout()
        self.login_button.setText(_("Not logged yet"))
        self.login_button.setEnabled(True)
        self.ui.action_Login.setEnabled(True)
        self.ui.action_LogOut.setEnabled(False)

    def onMenuQuit(self):
        self.close()

    def setTitleBarText(self, text):
        self.setWindowTitle(
            _("SubDownloader %s - %s") % (PROJECT_VERSION, text))

    def onChangeTitleBarText(self, title):
        self.setTitleBarText(title)

    def onChangeLoginStatus(self, statusMsg):
        self.login_button.setText(statusMsg)
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
        self.ui.filterLanguageForVideo.addItem(_("All languages"), "")
        self.ui.filterLanguageForTitle.addItem(_("All languages"), "")
        for lang in language.legal_languages():
            self.ui.filterLanguageForVideo.addItem(
                _(lang.name()), lang.xxx())
            self.ui.filterLanguageForTitle.addItem(
                _(lang.name()), lang.xxx())
            self.ui.uploadLanguages.addItem(
                _(lang.name()), lang.xxx())

        settings = QSettings()
        optionUploadLanguage = settings.value("options/uploadLanguage", "eng")
        index = self.ui.uploadLanguages.findData(optionUploadLanguage)
        if index != -1:
            self.ui.uploadLanguages.setCurrentIndex(index)

        self.ui.filterLanguageForVideo.adjustSize()
        self.ui.filterLanguageForTitle.adjustSize()
        self.ui.uploadLanguages.adjustSize()

        optionFilterLanguage = settings.value("options/filterSearchLang", "")

        self.filterLangChangedPermanent.emit(optionFilterLanguage)

        self.ui.filterLanguageForVideo.currentIndexChanged.connect(
            self.onFilterLanguageVideo)
        self.ui.filterLanguageForTitle.currentIndexChanged.connect(
            self.onFilterLanguageSearchName)
        self.ui.uploadLanguages.activated.connect(
            self.onUploadSelectLanguage)
        self.language_updated.connect(
            self.onUploadLanguageDetection)

    def onFilterLanguageVideo(self, index):
        selectedLanguageXXX = self.ui.filterLanguageForVideo.itemData(index)
        log.debug("Filtering subtitles by language: %s" % selectedLanguageXXX)
        self.ui.videoView.clearSelection()

        # self.videoModel.layoutAboutToBeChanged.emit()
        self.videoModel.clearTree()
        # self.videoModel.layoutChanged.emit()
        # self.videoView.expandAll()
        if selectedLanguageXXX:
            self.videoModel.setLanguageFilter(selectedLanguageXXX)
            # Let's select by default the most rated subtitle for each video
            self.videoModel.selectMostRatedSubtitles()
            self.subtitlesCheckedChanged()
        else:
            self.videoModel.setLanguageFilter(None)
            self.videoModel.unselectSubtitles()
            self.subtitlesCheckedChanged()

        self.ui.videoView.expandAll()

    def subtitlesCheckedChanged(self):
        subs = self.videoModel.getCheckedSubtitles()
        if subs:
            self.ui.buttonDownload.setEnabled(True)
            self.ui.buttonPlay.setEnabled(True)
        else:
            self.ui.buttonDownload.setEnabled(False)
            self.ui.buttonPlay.setEnabled(False)

    def SearchVideos(self, path):
        self.ui.buttonFind.setEnabled(False)
        if not hasattr(self, 'OSDBServer') or not self.OSDBServer.is_connected():
            QMessageBox.about(self, _("Error"), _(
                "You are not connected to the server. Please reconnect first."))
        else:
            # Scan recursively the selected directory finding subtitles and
            # videos
            if not type(path) == list:
                path = [path]

            callback = self._get_callback(_("Scanning..."), _("Scanning files"), _("Scanning finished"))
            callback.set_range(0, 100)

            videos_found, subs_found = FileScan.ScanFilesFolders(
                path, callback=callback, recursively=True)

            log.debug("Videos found: %s" % videos_found)
            log.debug("Subtitles found: %s" % subs_found)
            callback.finish()
            self.hideInstructions()
            self.setCursor(Qt.ArrowCursor)
            # Populating the items in the VideoListView
            self.videoModel.clearTree()
            self.ui.videoView.expandAll()
            self.videoModel.setVideos(videos_found)
            self.ui.videoView.setModel(self.videoModel)
            self.videoModel.videoResultsBackup = []
            # This was a solution found to refresh the treeView
            self.ui.videoView.expandAll()
            # Searching our videohashes in the OSDB database
            QCoreApplication.processEvents()

            if not videos_found:
                QMessageBox.about(
                    self, _("Scan Results"), _("No video has been found!"))
            else:
                self.setCursor(Qt.WaitCursor)
                callback = self._get_callback(_("Asking Server..."), _("Searching subtitles..."), _("Search finished"),
                                              _("Searching subtitles ( %d / %d )"))
                i = 0
                total = len(videos_found)

                callback.set_range(0, total)
                # TODO: Hashes bigger than 12 MB not working correctly.
#                    if self.SDDBServer: #only sending those hashes bigger than 12MB
#                        videos_sddb = [video for video in videos_found if int(video.getSize()) > 12000000]
#                        if videos_sddb:
#                                thread.start_new_thread(self.SDDBServer.SearchSubtitles, ('',videos_sddb, ))
                while i < total:
                    videos_piece = videos_found[i:min(i + 10, total)]
                    callback.update(i, i+1, (i+1)/total)
                    if callback.canceled():
                        self.setCursor(Qt.ArrowCursor)
                        return
                    videoSearchResults = self.OSDBServer.SearchSubtitles(
                        "", videos_piece)
                    i += 10

                    if(videoSearchResults and subs_found):
                        hashes_subs_found = {}
                        # Hashes of the local subtitles
                        for sub in subs_found:
                            hashes_subs_found[
                                sub.get_hash()] = sub.get_filepath()

                        # are the online subtitles already in our folder?
                        for video in videoSearchResults:
                            for sub in video._subs:
                                if sub.get_hash() in hashes_subs_found:
                                    sub._path = hashes_subs_found[
                                        sub.get_hash()]
                                    sub._online = False

                    if videoSearchResults:
                        self.videoModel.setVideos(
                            videoSearchResults, filter=None, append=True)
                        self.onFilterLanguageVideo(
                            self.ui.filterLanguageForVideo.currentIndex())
                        # This was a solution found to refresh the treeView
                        self.ui.videoView.expandAll()
                    elif videoSearchResults == None:
                        QMessageBox.about(self, _("Error"), _(
                            "Error contacting the server. Please try again later"))
                        return

                    if 'videoSearchResults' in locals():
                        video_osdb_hashes = [
                            video.get_hash() for video in videoSearchResults]

                        video_filesizes = [video.get_size()
                                           for video in videoSearchResults]
                        video_movienames = [
                            video.getMovieName() for video in videoSearchResults]


#                                thread.start_new_thread(self.SDDBServer.sendHash, (video_hashes,video_movienames,  video_filesizes,  ))

                callback.finish()
                self.setCursor(Qt.ArrowCursor)
                self.ui.buttonFind.setEnabled(True)

            # TODO: CHECK if our local subtitles are already in the server, otherwise suggest to upload
            # self.OSDBServer.CheckSubHash(sub_hashes)

    def onClickVideoTreeView(self, index):
        treeItem = self.videoModel.getSelectedItem(index)
        if type(treeItem.data) == VideoFile:
            video = treeItem.data
            if video.getMovieInfo():
                self.ui.buttonIMDB.setEnabled(True)
                self.ui.buttonIMDB.setIcon(QIcon(":/images/info.png"))
                self.ui.buttonIMDB.setText(_("Movie Info"))
        else:
            treeItem.checked = not(treeItem.checked)
            self.videoModel.dataChanged.emit(index, index)
            self.ui.buttonIMDB.setEnabled(True)
            self.ui.buttonIMDB.setIcon(QIcon(":/images/sites/opensubtitles.png"))
            self.ui.buttonIMDB.setText(_("Sub Info"))

    def onClickMovieTreeView(self, index):
        treeItem = self.moviesModel.getSelectedItem(index)
        if type(treeItem.data) == Movie:
            movie = treeItem.data
            if movie.IMDBId:
                self.ui.buttonIMDBByTitle.setEnabled(True)
                self.ui.buttonIMDBByTitle.setIcon(QIcon(":/images/info.png"))
                self.ui.buttonIMDBByTitle.setText(_("Movie Info"))
        else:
            treeItem.checked = not(treeItem.checked)
            self.moviesModel.dataChanged.emit(
                index, index)
            self.ui.buttonIMDBByTitle.setEnabled(True)
            self.ui.buttonIMDBByTitle.setIcon(
                QIcon(":/images/sites/opensubtitles.png"))
            self.ui.buttonIMDBByTitle.setText(_("Sub Info"))

    @pyqtSlot()
    def onButtonFind(self):
        folder_path = None
        for index in self.ui.folderView.selectedIndexes():
            folder_path = str(self.ui.folderView.model().filePath(index))

        if not folder_path:
            QMessageBox.about(self, _("Info"), _("You must select a folder first"))
        else:
            settings = QSettings()
            settings.setValue("mainwindow/workingDirectory", folder_path)
            self.SearchVideos(folder_path)

    def onButtonSearchSelectVideos(self):
        if not hasattr(self, 'OSDBServer') or not self.OSDBServer.is_connected():
            QMessageBox.about(self, _("Error"), _(
                "You are not connected to the server. Please reconnect first."))
        else:
            settings = QSettings()
            currentDir = settings.value("mainwindow/workingDirectory", "")
            fileNames, t = QFileDialog.getOpenFileNames(None, _(
                "Select the video(s) that need subtitles"), currentDir, SELECT_VIDEOS)
            fileNames = [fileName for fileName in fileNames]
            if fileNames:
                settings.setValue(
                    "mainwindow/workingDirectory", QFileInfo(fileNames[0]).absolutePath())
                self.SearchVideos(fileNames)

    def onButtonSearchSelectFolder(self):
        if not hasattr(self, 'OSDBServer') or not self.OSDBServer.is_connected():
            QMessageBox.about(self, _("Error"), _(
                "You are not connected to the server. Please reconnect first."))
        else:
            settings = QSettings()
            path = settings.value("mainwindow/workingDirectory", "")
            directory = QFileDialog.getExistingDirectory(
                None, _("Select the directory that contains your videos"), path)
            if directory:
                settings.setValue("mainwindow/workingDirectory", directory)
                folder_path = directory
                self.SearchVideos(folder_path)

    """What to do when a Folder in the tree is clicked"""

    @pyqtSlot(QModelIndex)
    def onFolderTreeClicked(self, index):
        if index.isValid():
            now = QTime.currentTime()
            if now > self.timeLastSearch.addMSecs(500):
                if not self.ui.folderView.model().hasChildren(index):
                    settings = QSettings()
                    folder_path = self.ui.folderView.model().filePath(index)
                    settings.setValue(
                        "mainwindow/workingDirectory", folder_path)
                    self.SearchVideos(folder_path)
                    self.timeLastSearch = QTime.currentTime()
                self.ui.buttonFind.setEnabled(True)

    def onButtonPlay(self):
        settings = QSettings()
        programPath = settings.value("options/VideoPlayerPath", "")
        parameters = settings.value("options/VideoPlayerParameters", "")
        if programPath == '':
            QMessageBox.about(self, _("Error"), _(
                "No default video player has been defined in Settings."))
            return
        else:
            subtitle = self.videoModel.getSelectedItem().data
            moviePath = subtitle.getVideo().get_filepath()
            subtitleFileID = subtitle.getIdFileOnline()
            # This should work in all the OS, creating a temporary file
            tempSubFilePath = QDir.temp().absoluteFilePath("subdownloader.tmp.srt")
            log.debug(
                "Temporary subtitle will be downloaded into: %s" % tempSubFilePath)
            callback = self._get_callback(_("Playing video + sub"), _("Downloading files..."), "")
            self.setCursor(Qt.BusyCursor)
            callback.update(-1)
            try:
                ok = self.OSDBServer.DownloadSubtitles(
                    {subtitleFileID: tempSubFilePath})
                if not ok:
                    QMessageBox.about(self, _("Error"), _(
                        "Unable to download subtitle %s") % subtitle.get_filepath())
            except Exception as e:
                traceback.print_exc(e)
                QMessageBox.about(self, _("Error"), _(
                    "Unable to download subtitle %s") % subtitle.get_filepath())
            finally:
                callback.finish()
                self.setCursor(Qt.ArrowCursor)

            params = []

            for param in parameters.split(" "):
                if platform.system() in ("Windows", "Microsoft"):
                    param = param.replace('{0}', '"' + moviePath + '"')
                else:
                    param = param.replace('{0}', moviePath)
                param = param.replace('{1}',  tempSubFilePath)
                params.append(param)

            params.insert(0, '"' + programPath + '"')
            log.info("Running this command:\n%s %s" % (programPath, params))
            try:
                os.spawnvpe(os.P_NOWAIT, programPath, params, os.environ)
            except AttributeError:
                pid = os.fork()
                if not pid:
                    os.execvpe(os.P_NOWAIT, programPath, params, os.environ)
            except Exception as e:
                traceback.print_exc(e)
                QMessageBox.about(
                    self, _("Error"), _("Unable to launch videoplayer"))

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

    def onButtonDownload(self):
        # We download the subtitle in the same folder than the video
        subs = self.videoModel.getCheckedSubtitles()
        replace_all = False
        skip_all = False
        if not subs:
            QMessageBox.about(
                self, _("Error"), _("No subtitles selected to be downloaded"))
            return
        total_subs = len(subs)
        percentage = 100 / total_subs
        count = 0
        answer = None
        success_downloaded = 0

        callback = self._get_callback(_('Downloading...'),
                                      _("Downloading files..."),
                                      _("%d from %d subtitles downloaded successfully"),
                                      _("Downloading subtitle %s (%d/%d)"))
        callback.set_range(0, total_subs)
        for i, sub in enumerate(subs):
            if callback.canceled():
                break
            destinationPath = self.getDownloadPath(sub.getVideo(), sub)
            if not destinationPath:
                break
            log.debug("Trying to download subtitle '%s'" % destinationPath)
            callback.update(i, QFileInfo(destinationPath).fileName(), i + 1, total_subs)

            # Check if we have write permissions, otherwise show warning window
            while True:
                # If the file and the folder don't have write access.
                if not QFileInfo(destinationPath).isWritable() and not QFileInfo(QFileInfo(destinationPath).absoluteDir().path()).isWritable():
                    warningBox = QMessageBox(_("Error write permission"),
                                             _(
                                                 "%s cannot be saved.\nCheck that the folder exists and you have write-access permissions.") % destinationPath,
                                             QMessageBox.Warning,
                                             QMessageBox.Retry | QMessageBox.Default,
                                             QMessageBox.Discard | QMessageBox.Escape,
                                             QMessageBox.NoButton,
                                             self)

                    saveAsButton = warningBox.addButton(
                        _("Save as..."), QMessageBox.ActionRole)
                    answer = warningBox.exec_()
                    if answer == QMessageBox.Retry:
                        continue
                    elif answer == QMessageBox.Discard:
                        break  # Let's get out from the While true
                    # If we choose the SAVE AS
                    elif answer == QMessageBox.NoButton:
                        fileName, t = QFileDialog.getSaveFileName(
                            self, _("Save subtitle as..."), destinationPath, 'All (*.*)')
                        if fileName:
                            destinationPath = fileName
                else:  # If we have write access we leave the while loop.
                    break

            # If we have chosen Discard subtitle button.
            if answer == QMessageBox.Discard:
                count += percentage
                continue  # Continue the next subtitle

            optionWhereToDownload = \
                QSettings().value("options/whereToDownload", "SAME_FOLDER")
            # Check if doesn't exists already, otherwise show fileExistsBox
            # dialog
            if QFileInfo(destinationPath).exists() and not replace_all and not skip_all and optionWhereToDownload != "ASK_FOLDER":
                # The "remote filename" below is actually not the real filename. Real name could be confusing
                # since we always rename downloaded sub to match movie
                # filename.
                fileExistsBox = QMessageBox(
                    QMessageBox.Warning,
                    _("File already exists"),
                    _("Local: %s\n\nRemote: %s\n\nHow would you like to proceed?") % (destinationPath, QFileInfo(destinationPath).fileName()),
                    QMessageBox.NoButton,
                    self)
                skipButton = fileExistsBox.addButton(
                    _("Skip"), QMessageBox.ActionRole)
#                    skipAllButton = fileExistsBox.addButton(_("Skip all"), QMessageBox.ActionRole)
                replaceButton = fileExistsBox.addButton(
                    _("Replace"), QMessageBox.ActionRole)
                replaceAllButton = fileExistsBox.addButton(
                    _("Replace all"), QMessageBox.ActionRole)
                saveAsButton = fileExistsBox.addButton(
                    _("Save as..."), QMessageBox.ActionRole)
                cancelButton = fileExistsBox.addButton(
                    _("Cancel"), QMessageBox.ActionRole)
                fileExistsBox.exec_()
                answer = fileExistsBox.clickedButton()
                if answer == replaceAllButton:
                    # Don't ask us again (for this batch of files)
                    replace_all = True
                elif answer == saveAsButton:
                    # We will find a uniqiue filename and suggest this to user.
                    # add .<lang> to (inside) the filename. If that is not enough, start adding numbers.
                    # There should also be a preferences setting "Autorename
                    # files" or similar ( =never ask) FIXME
                    suggBaseName, suggFileExt = os.path.splitext(
                        destinationPath)
                    fNameCtr = 0  # Counter used to generate a unique filename
                    suggestedFileName = suggBaseName + '.' + \
                        sub.getLanguage().xxx() + suggFileExt
                    while (os.path.exists(suggestedFileName)):
                        fNameCtr += 1
                        suggestedFileName = suggBaseName + '.' + \
                            sub.getLanguage().xxx() + '-' + \
                            str(fNameCtr) + suggFileExt
                    fileName, t = QFileDialog.getSaveFileName(
                        None, _("Save subtitle as..."), suggestedFileName, 'All (*.*)')
                    if fileName:
                        destinationPath = fileName
                    else:
                        count += percentage
                        # Skip this particular file if no filename chosen
                        continue
                elif answer == skipButton:
                    count += percentage
                    continue  # Skip this particular file
#                    elif answer == skipAllButton:
#                        count += percentage
#                        skip_all = True # Skip all files already downloaded
#                        continue
                elif answer == cancelButton:
                    break  # Break out of DL loop - cancel was pushed
            QCoreApplication.processEvents()
            # FIXME: redundant update?
            callback.update(i, QFileInfo(destinationPath).fileName(), i + 1, total_subs)
            try:
                if not skip_all:
                    log.debug("Downloading subtitle '%s'" % destinationPath)
                    if self.OSDBServer.DownloadSubtitles({sub.getIdFileOnline(): destinationPath}):
                        success_downloaded += 1
                    else:
                        QMessageBox.about(self, _("Error"), _(
                            "Unable to download subtitle %s") % sub.get_filepath())
            except Exception as e:
                traceback.print_exc(e)
                QMessageBox.about(self, _("Error"), _(
                    "Unable to download subtitle %s") % sub.get_filepath())
            finally:
                count += percentage
        callback.finish(success_downloaded, total_subs)

    def showErrorConnection(self):
        QMessageBox.about(self, _("Alert"), _(
            "www.opensubtitles.org is not responding\nIt might be overloaded, try again in a few moments."))

    def establishServerConnection(self):
        # def _get_callback(self, titleMsg, labelMsg, finishedMsg, updatedMsg=None, cancellable=True):
        if self.options.proxy:
            updatedMsg = _("Connecting to server using proxy %s") % self.options.proxy
        else:
            updatedMsg = ""
        callback = self._get_callback(_('Connecting'), _("Connecting to server..."), _("Connected successfully"),
                                      updatedMsg, cancellable=False)
        callback.set_range(0, 1)

        settings = QSettings()
        settingsProxyHost = settings.value("options/ProxyHost", "")
        settingsProxyPort = int(settings.value("options/ProxyPort", 8080))
        # If we are not defining the proxy from command line
        if not self.options.proxy:
            # Let's see if we have defined a proxy in our Settings
            if settingsProxyHost:
                self.options.proxy = str(
                    settingsProxyHost + ":" + str(settingsProxyPort))

        try:
            self.OSDBServer = SDService(
                'osdb', server=self.options.server, proxy=self.options.proxy)
            callback.finish()
            return True
        except TimeoutFunctionException:
            # FIXME: callback finish should display a failed message on exception
            callback.finish()
            self.showErrorConnection()
            QCoreApplication.processEvents() # FIXME: needed?
            return False

        except Exception as e:
            traceback.print_exc()#(e)
            # FIXME: callback finish should display a failed message on exception
            callback.finish()
            # replace by a dialog with button.
            QCoreApplication.processEvents()
            return False

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
            results = self.OSDBServer.GetIMDBMovieDetails(imdb_id)
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
                    info = self.OSDBServer.UploadSubtitles(movie_info)
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

    def onButtonSearchByTitle(self):
        if not self.ui.movieNameText.text().strip():
            QMessageBox.about(self, _("Info"), _(
                "You must enter at least one character in movie name"))

        else:
            self.ui.buttonSearchByName.setEnabled(False)
            callback = self._get_callback(_('Search'), _("Searching..."), "")
            self.setCursor(Qt.WaitCursor)
            self.moviesModel.clearTree()
            # This was a solution found to refresh the treeView
            self.ui.moviesView.expandAll()
            QCoreApplication.processEvents()
            s = SearchByName()
            selectedLanguageXXX = self.ui.filterLanguageForTitle.itemData(self.ui.filterLanguageForTitle.currentIndex())
            search_text = self.ui.movieNameText.text()
            # Fix for user entering "'" in search field. If we find more chars that breaks things we'll handle this in a better way,
            # like a string of forbidden chars (pr the other way around, string
            # of good chars)
            search_text = re.sub('\'', '', search_text)
            callback.update(0)
            # This should be in a thread to be able to Cancel
            movies = s.search_movie(search_text, 'all')
            if movies == 2:
                QMessageBox.about(self, _("Info"), _(
                    "The server is momentarily unavailable. Please try later."))
                sys.exit(1)
            self.moviesModel.setMovies(movies, selectedLanguageXXX)
            if len(movies) == 1:
                self.ui.moviesView.expandAll()
            else:
                self.ui.moviesView.collapseAll()
            QCoreApplication.processEvents()
            self.setCursor(Qt.ArrowCursor)
            callback.finish()
            self.ui.buttonSearchByName.setEnabled(True)

    @pyqtSlot(str)
    def onFilterLangChangedPermanent(self, languages):
        languages_array = languages.split(",")

        if len(languages_array) > 1:
            index = self.ui.filterLanguageForTitle.findData(languages)
            if index == -1:
                self.ui.filterLanguageForVideo.addItem(languages, languages)
                self.ui.filterLanguageForTitle.addItem(languages, languages)
        index = self.ui.filterLanguageForTitle.findData(languages)
        if index != -1:
            self.ui.filterLanguageForTitle.setCurrentIndex(index)

        index = self.ui.filterLanguageForVideo.findData(languages)
        if index != -1:
            self.ui.filterLanguageForVideo.setCurrentIndex(index)

    def onFilterLanguageSearchName(self, index):
        selectedLanguageXXX = self.ui.filterLanguageForTitle.itemData(index)
        log.debug("Filtering subtitles by language: %s" % selectedLanguageXXX)
        self.ui.moviesView.clearSelection()
        self.moviesModel.clearTree()
        self.moviesModel.setLanguageFilter(selectedLanguageXXX)
        self.ui.moviesView.expandAll()

    def onUploadSelectLanguage(self, index):
        self.upload_autodetected_lang = "selected"
        self.ui.label_autodetect_lang.hide()

    def onUploadSelectImdb(self, index):
        self.upload_autodetected_imdb = "selected"
        self.ui.label_autodetect_imdb.hide()

    def subtitlesMovieCheckedChanged(self):
        subs = self.moviesModel.getCheckedSubtitles()
        if subs:
            self.ui.buttonDownloadByTitle.setEnabled(True)
        else:
            self.ui.buttonDownloadByTitle.setEnabled(False)

    def onButtonDownloadByTitle(self):
        subs = self.moviesModel.getCheckedSubtitles()
        total_subs = len(subs)
        if not subs:
            QMessageBox.about(
                self, _("Error"), _("No subtitles selected to be downloaded"))
            return
        answer = None
        success_downloaded = 0

        settings = QSettings()
        path = settings.value("mainwindow/workingDirectory", "")
        zipDestDir = QFileDialog.getExistingDirectory(
            None, _("Select the directory where to save the subtitle(s)"), path)
        if not zipDestDir:
            return
        if zipDestDir:
            settings.setValue("mainwindow/workingDirectory", zipDestDir)

        callback = self._get_callback(_('Downloading'), _("Downloading files..."), "",
                                      updatedMsg=_("Downloading %s to %s"))
        callback.set_range(0, len(subs))

# Download and unzip files automatically. We might want to move this to an
# external module, perhaps?
        unzipedOK = 0
        dlOK = 0

        for i, sub in enumerate(subs):
            # Skip rest of loop if Abort was pushed in progress bar
            if callback.canceled():
                break

            try:
                url = sub.getExtraInfo("downloadLink")
                log.debug("sub.getExtraInfo downloadLink  %s " % (url))
            except:
                url = Link().OneLink(0)
                log.debug("Link().OneLink downloadLink  %s " % (url))
#                webbrowser.open( url, new=2, autoraise=1)
            zipFileID = re.search("(\/.*\/)(.*)\Z", url).group(2)
            zipFileName = "sub-" + zipFileID + ".srt"

            try:
                zipDestFile = os.path.join(zipDestDir, zipFileName).decode(
                    sys.getfilesystemencoding())
            except:
                zipDestFile = (zipDestDir + '/' + zipFileName)
            log.debug("About to download %s %s to %s" % (i, sub.__repr__, zipDestFile))
            log.debug("IdFileOnline: %s" % (sub.getIdFileOnline()))
            callback.update(i, sub.getIdFileOnline(), zipDestDir)

            # Download the file from opensubtitles.org
            # Note that we take for granted it will be in .zip format! Might not be so for other sites
            # This should be tested for when more sites are added or find
            # true filename like browser does FIXME
            try:
                if self.OSDBServer.DownloadSubtitles({sub.getIdFileOnline(): zipDestFile}):
                    dlOK += 1
                else:
                    QMessageBox.about(self, _("Error"), _(
                        "Unable to download subtitle %s") % sub.get_filepath())
            except Exception as e:
                log.debug(e)
                QMessageBox.about(self, _("Error"), _(
                    "Unable to download subtitle %s") % sub.get_filepath())
                QMessageBox.critical(self, _("Error"), _(
                    "An error occured downloading %s:\nError:%s") % (url, e), QMessageBox.Abort)
            QCoreApplication.processEvents()
        callback.finish()
        if (dlOK > 0):
            QMessageBox.about(self, _("%d subtitles downloaded successfully") % (unzipedOK), _(
                "The downloaded subtitle(s) may not be in sync with your video file(s), please check this manually.\n\nIf there is no sync problem, please consider re-uploading using subdownloader. This will automate the search for other users!"))

    def onExpandMovie(self, index):
        if index.internalPointer() is None:
            return
        movie = index.internalPointer().data
        if type(movie) == Movie and not movie.subtitles and movie.totalSubs:
            callback = self._get_callback(_('Search'), _("Searching..."), "")
            self.setCursor(Qt.WaitCursor)

            s = SearchByName()
            selectedLanguageXXX = self.ui.filterLanguageForTitle.itemData(
                self.ui.filterLanguageForTitle.currentIndex())
            callback.update(0)
            temp_movie = s.search_movie(
                None, 'all', MovieID_link=movie.MovieSiteLink)
            # The internal results are not filtered by language, so in case we change the filter, we don't need to request again.
            # print temp_movie
            try:
                movie.subtitles = temp_movie[0].subtitles
            except IndexError:
                QMessageBox.about(
                    self, _("Info"), _("This is a TV series and it cannot be handled."))
                self.setCursor(Qt.ArrowCursor)
                callback.finish()
                return
            except AttributeError:
                # this means only one subtitle was returned
                movie.subtitles = [temp_movie[1]]
            # The treeview is filtered by language
            self.moviesModel.updateMovie(index, selectedLanguageXXX)
            self.ui.moviesView.collapse(index)
            self.ui.moviesView.expand(index)
            self.setCursor(Qt.ArrowCursor)
            callback.finish()


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


def main(options):
    global app
    log.debug("Building main dialog")
#    app = QApplication(sys.argv)
#    splash = SplashScreen()
#    splash.showMessage(QApplication.translate("subdownloader", "Building main dialog..."))
    window = QMainWindow()
    QCoreApplication.setOrganizationName("SubDownloader")
    QCoreApplication.setApplicationName(PROJECT_TITLE)

    splash.finish(window)

    log.debug('Building main window ...')
    main_window = Main(None, "", options)
    log.debug('... Building FINISHED')

    log.debug('Showing main window')
    main_window.show()

    log.debug('Starting application event loop ...')
    res = app.exec_()
    app = None
    return res
