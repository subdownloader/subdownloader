# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
import platform
import traceback
import webbrowser

from PyQt5.QtCore import pyqtSlot, QCoreApplication, QDir, QFileInfo, QModelIndex, QSettings, \
    QSortFilterProxyModel, Qt, QTime
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractItemView, QAction, QFileDialog, QFileIconProvider, QFileSystemModel, \
    QMenu, QMessageBox, QWidget

from subdownloader.FileManagement import FileScan
from subdownloader.FileManagement.videofile import VideoFile
from subdownloader.FileManagement.search import Movie
from subdownloader.FileManagement.subtitlefile import SubtitleFile
from subdownloader.languages import language
from subdownloader.project import PROJECT_TITLE

from subdownloader.client.gui import SELECT_VIDEOS
from subdownloader.client.gui.callback import ProgressCallbackWidget
from subdownloader.client.gui.searchFileWidget_ui import Ui_SearchFileWidget
from subdownloader.client.gui.state import State
from subdownloader.client.gui.videotreeview import VideoTreeModel

log = logging.getLogger('subdownloader.client.gui.searchFileWidget')
# FIXME: add logging


class SearchFileWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.ui = Ui_SearchFileWidget()

        self._refreshing = False

        self.fileModel = None
        self.proxyFileModel = None
        self.videoModel = None

        self.setupUi()

        self._state = None
        self.timeLastSearch = QTime.currentTime()

    def set_state(self, state):
        self._state = state
        self._state.login_status_changed.connect(self.on_login_state_changed)

    def get_state(self):
        return self._state

    def setupUi(self):
        self.ui.setupUi(self)
        settings = QSettings()

        self.ui.splitter.setSizes([600, 1000])
        self.ui.splitter.setChildrenCollapsible(False)

        # Set up folder view

        lastDir = settings.value("mainwindow/workingDirectory", QDir.homePath())
        log.debug('Current directory: {currentDir}'.format(currentDir=lastDir))

        self.fileModel = QFileSystemModel(self)
        self.fileModel.setFilter(QDir.AllDirs | QDir.Dirs | QDir.Drives | QDir.NoDotAndDotDot | QDir.Readable | QDir.Executable | QDir.Writable)
        self.fileModel.iconProvider().setOptions(QFileIconProvider.DontUseCustomDirectoryIcons)
        self.fileModel.setRootPath(QDir.rootPath())
        self.fileModel.directoryLoaded.connect(self.onFileModelDirectoryLoaded)

        self.proxyFileModel = QSortFilterProxyModel(self)
        self.proxyFileModel.setSortRole(Qt.DisplayRole)
        self.proxyFileModel.setSourceModel(self.fileModel)
        self.proxyFileModel.sort(0, Qt.AscendingOrder)
        self.proxyFileModel.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.ui.folderView.setModel(self.proxyFileModel)

        self.ui.folderView.setHeaderHidden(True)
        self.ui.folderView.hideColumn(3)
        self.ui.folderView.hideColumn(2)
        self.ui.folderView.hideColumn(1)

        index = self.fileModel.index(lastDir)
        proxyIndex = self.proxyFileModel.mapFromSource(index)
        self.ui.folderView.scrollTo(proxyIndex)

        self.ui.folderView.expanded.connect(self.onFolderViewExpanded)
        self.ui.folderView.clicked.connect(self.onFolderTreeClicked)
        self.ui.buttonFind.clicked.connect(self.onButtonFind)
        self.ui.buttonRefresh.clicked.connect(self.onButtonRefresh)

        # Set up introduction

        introduction = '<p align="center"><h2>{title}</h2></p>' \
            '<p><b>{tab1header}</b><br>{tab1content}</p>' \
            '<p><b>{tab2header}</b><br>{tab2content}</p>'\
            '<p><b>{tab3header}</b><br>{tab3content}</p>'.format(
                title=_('How To Use {title}').format(title=PROJECT_TITLE),
                tab1header=_('1st Tab:'),
                tab2header=_('2nd Tab:'),
                tab3header=_('3rd Tab:'),
                tab1content=_('Select, from the Folder Tree on the left, the folder which contains the videos '
                              'that need subtitles. {project} will then try to automatically find available '
                              'subtitles.').format(project=PROJECT_TITLE),
                tab2content=_('If you don\'t have the videos in your machine, you can search subtitles by '
                              'introducing the title/name of the video.').format(project=PROJECT_TITLE),
                tab3content=_('If you have found some subtitle somewhere else that is not in {project}\'s database, '
                              'please upload those subtitles so next users will be able to '
                              'find them more easily.').format(project=PROJECT_TITLE))
        self.ui.introductionHelp.setHtml(introduction)

        self.showInstructions()

        # SETTING UP SEARCH_VIDEO_VIEW

        self.initializeFilterLanguages()
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

        # FIXME: ok to drop this conect?
        # self.ui.videoView.clicked.connect(self.onClickMovieTreeView)

    @pyqtSlot(str)
    def onFileModelDirectoryLoaded(self, path):
        settings = QSettings()
        lastDir = settings.value('mainwindow/workingDirectory', QDir.homePath())
        qDirLastDir = QDir(lastDir)
        qDirLastDir.cdUp()
        if qDirLastDir.path() == path:
            index = self.fileModel.index(lastDir)
            proxyIndex = self.proxyFileModel.mapFromSource(index)
            self.ui.folderView.scrollTo(proxyIndex)#, QAbstractItemView.PositionAtBottom)
            self.ui.folderView.setCurrentIndex(proxyIndex)

    @pyqtSlot(int, str)
    def on_login_state_changed(self, state, message):
        log.debug('on_login_state_changed(state={state}, message={message}'.format(state=state, message=message))
        if state in  (State.LOGIN_STATUS_LOGGED_OUT, State.LOGIN_STATUS_BUSY):
            self.ui.buttonSearchSelectFolder.setEnabled(False)
            self.ui.buttonSearchSelectVideos.setEnabled(False)
            self.ui.buttonFind.setEnabled(False)
        elif state == State.LOGIN_STATUS_LOGGED_IN:
            self.ui.buttonSearchSelectFolder.setEnabled(True)
            self.ui.buttonSearchSelectVideos.setEnabled(True)
            self.ui.buttonFind.setEnabled(self.get_current_selected_folder() is not None)
        else:
            log.warning('unknown state')

    def initializeFilterLanguages(self):
        self.ui.filterLanguageForVideo.set_unknown_text(_('All languages'))

        self.ui.filterLanguageForVideo.selected_language_changed.connect(
            self.onFilterLanguageVideo)

    @pyqtSlot(list)
    def onFilterLangChangedPermanent(self, languages):
        if len(languages) > 0:
            lang = languages[0]
            self.ui.filterLanguageForVideo.set_selected_language(lang)

    @pyqtSlot(language.Language)
    def onFilterLanguageVideo(self, lang):
        log.debug('Filtering subtitles by language: {}'.format(lang))

        self.ui.videoView.clearSelection()
        self.videoModel.clearTree()

        if isinstance(lang, language.UnknownLanguage):
            self.videoModel.setLanguageFilter(None)
            self.videoModel.unselectSubtitles()
        else:
            self.videoModel.setLanguageFilter(lang)
            self.videoModel.selectMostRatedSubtitles()

        self.subtitlesCheckedChanged()
        self.ui.videoView.expandAll()

    @pyqtSlot()
    def subtitlesCheckedChanged(self):
        subs = self.videoModel.getCheckedSubtitles()
        if subs:
            self.ui.buttonDownload.setEnabled(True)
            self.ui.buttonPlay.setEnabled(True)
        else:
            self.ui.buttonDownload.setEnabled(False)
            self.ui.buttonPlay.setEnabled(False)

    def showInstructions(self):
        self.ui.stackedSearchResult.setCurrentWidget(self.ui.pageIntroduction)

    def hideInstructions(self):
        self.ui.stackedSearchResult.setCurrentWidget(self.ui.pageSearchResult)

    @pyqtSlot(QModelIndex)
    def onFolderTreeClicked(self, proxyIndex):
        """What to do when a Folder in the tree is clicked"""
        if not proxyIndex.isValid():
            return

        index = self.proxyFileModel.mapToSource(proxyIndex)
        settings = QSettings()
        folder_path = self.fileModel.filePath(index)
        settings.setValue('mainwindow/workingDirectory', folder_path)
        # self.ui.buttonFind.setEnabled(self.get_state().)

    def get_current_selected_folder(self):
        proxyIndex = self.ui.folderView.currentIndex()
        index = self.proxyFileModel.mapToSource(proxyIndex)
        folder_path = self.fileModel.filePath(index)
        if not folder_path:
            return None
        return folder_path

    @pyqtSlot()
    def onButtonFind(self):
        now = QTime.currentTime()
        if now < self.timeLastSearch.addMSecs(500):
            return
        folder_path = self.get_current_selected_folder()

        settings = QSettings()
        settings.setValue('mainwindow/workingDirectory', folder_path)
        self.search_videos([folder_path])

        self.timeLastSearch = QTime.currentTime()

    @pyqtSlot()
    def onButtonRefresh(self):
        currentPath = self.get_current_selected_folder()
        if not currentPath:
            settings = QSettings()
            currentPath = settings.value('mainwindow/workingDirectory', QDir.homePath())

        self._refreshing = True

        self.ui.folderView.collapseAll()

        currentPath = self.get_current_selected_folder()
        if not currentPath:
            settings = QSettings()
            currentPath = settings.value('mainwindow/workingDirectory', QDir.homePath())

        index = self.fileModel.index(currentPath)

        self.ui.folderView.scrollTo(self.proxyFileModel.mapFromSource(index))

    @pyqtSlot(QModelIndex)
    def onFolderViewExpanded(self, proxyIndex):
        if self._refreshing:
            expandedPath = self.fileModel.filePath(self.proxyFileModel.mapToSource(proxyIndex))
            if expandedPath == QDir.rootPath():
                currentPath = self.get_current_selected_folder()
                if not currentPath:
                    settings = QSettings()
                    currentPath = settings.value('mainwindow/workingDirectory', QDir.homePath())

                index = self.fileModel.index(currentPath)

                self.ui.folderView.scrollTo(self.proxyFileModel.mapFromSource(index))
                self._refreshing = False

    @pyqtSlot()
    def onButtonSearchSelectFolder(self):
        settings = QSettings()
        path = settings.value('mainwindow/workingDirectory', QDir.homePath())
        folder_path = QFileDialog.getExistingDirectory(self, _('Select the directory that contains your videos'), path)
        if folder_path:
            settings.setValue('mainwindow/workingDirectory', folder_path)
            self.search_videos([folder_path])

    @pyqtSlot()
    def onButtonSearchSelectVideos(self):
        settings = QSettings()
        currentDir = settings.value('mainwindow/workingDirectory', QDir.homePath())
        fileNames, t = QFileDialog.getOpenFileNames(self, _('Select the video(s) that need subtitles'),
                                                    currentDir, SELECT_VIDEOS)
        if fileNames:
            settings.setValue('mainwindow/workingDirectory', QFileInfo(fileNames[0]).absolutePath())
            self.search_videos(fileNames)

    def search_videos(self, paths):
        if not self.get_state().connected():
            QMessageBox.about(self, _("Error"), _('You are not connected to the server. Please reconnect first.'))
            return
        self.ui.buttonFind.setEnabled(False)
        self._search_videos_raw(paths)
        self.ui.buttonFind.setEnabled(True)

    def _search_videos_raw(self, paths):
        # FIXME: must pass mainwindow as argument to ProgressCallbackWidget
        callback = ProgressCallbackWidget(self)
        callback.set_title_text(_("Scanning..."))
        callback.set_label_text(_("Scanning files"))
        callback.set_finished_text(_("Scanning finished"))
        callback.set_block(True)

        try:
            videos_found, subs_found = FileScan.scan_paths(paths, callback=callback, recursively=True)
        except OSError:
            callback.cancel()
            QMessageBox.warning(self, _('Error'), _('Some directories are not accessible.'))

        if callback.canceled():
            return

        callback.finish()

        log.debug("Videos found: %s" % videos_found)
        log.debug("Subtitles found: %s" % subs_found)
        self.hideInstructions()

        # Populating the items in the VideoListView
        self.videoModel.clearTree()
        self.ui.videoView.expandAll()
        self.videoModel.setVideos(videos_found)
        self.videoModel.videoResultsBackup = []
        # This was a solution found to refresh the treeView
        self.ui.videoView.expandAll()
        # Searching our videohashes in the OSDB database
        QCoreApplication.processEvents()

        if not videos_found:
            QMessageBox.about(self, _("Scan Results"), _("No video has been found!"))
            return

        i = 0
        total = len(videos_found)

        # FIXME: must pass mainwindow as argument to ProgressCallbackWidget
        callback = ProgressCallbackWidget(self)
        callback.set_title_text(_("Asking Server..."))
        callback.set_label_text(_("Searching subtitles..."))
        callback.set_updated_text(_("Searching subtitles ( %d / %d )"))
        callback.set_finished_text(_("Search finished"))
        callback.set_block(True)
        callback.set_range(0, total)

        callback.show()

        # TODO: Hashes bigger than 12 MB not working correctly.
        #                    if self.SDDBServer: #only sending those hashes bigger than 12MB
        #                        videos_sddb = [video for video in videos_found if int(video.getSize()) > 12000000]
        #                        if videos_sddb:
        #                                thread.start_new_thread(self.SDDBServer.SearchSubtitles, ('',videos_sddb, ))
        while i < total:
            if callback.canceled():
                break
            videos_piece = videos_found[i:min(i + 10, total)]
            callback.update(i, i + 1, total)
            videoSearchResults = self.get_state().get_OSDBServer().SearchSubtitles("", videos_piece)
            i += 10

            if (videoSearchResults and subs_found):
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
                self.videoModel.setVideos(videoSearchResults, filter=None, append=True)
                self.onFilterLanguageVideo(self.ui.filterLanguageForVideo.get_selected_language())
                # This was a solution found to refresh the treeView
                self.ui.videoView.expandAll()
            elif videoSearchResults == None:
                QMessageBox.about(self, _("Error"), _(
                    "Error contacting the server. Please try again later"))
                break

            if 'videoSearchResults' in locals():
                video_osdb_hashes = [
                    video.get_hash() for video in videoSearchResults]

                video_filesizes = [video.get_size()
                                   for video in videoSearchResults]
                video_movienames = [
                    video.getMovieName() for video in videoSearchResults]

        callback.finish()

        # TODO: CHECK if our local subtitles are already in the server, otherwise suggest to upload
        # self.OSDBServer.CheckSubHash(sub_hashes)

    @pyqtSlot()
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

            # FIXME: must pass mainwindow as argument to ProgressCallbackWidget
            callback = ProgressCallbackWidget(self)
            callback.set_title_text(_("Playing video + sub"))
            callback.set_label_text(_("Downloading files..."))
            callback.set_finished_text(_("Downloading finished"))
            callback.set_block(True)
            callback.set_range(0, 100)

            callback.show()

            callback.update(-1)
            try:
                ok = self.get_state().get_OSDBServer().DownloadSubtitles(
                    {subtitleFileID: tempSubFilePath})
                if not ok:
                    QMessageBox.about(self, _("Error"), _(
                        "Unable to download subtitle %s") % subtitle.get_filepath())
            except Exception as e:
                log.exception('Unable to download subtitle {}'.format(subtitle.get_filepath()))
                QMessageBox.about(self, _("Error"), _(
                    "Unable to download subtitle %s") % subtitle.get_filepath())
            finally:
                callback.finish()

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
                log.exception('Unable to launch videoplayer')
                QMessageBox.about(
                    self, _("Error"), _("Unable to launch videoplayer"))

    @pyqtSlot(QModelIndex)
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

    def onContext(self, point):
        # FIXME: code duplication with Main.onContext and/or SearchNameWidget and/or SearchFileWidget
        menu = QMenu("Menu", self)

        listview = self.ui.videoView

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

                downloadAction.triggered.connect(self.onButtonDownload)
                playAction = QAction(
                    QIcon(":/images/play.png"), _("Play video + subtitle"), self)
                playAction.triggered.connect(self.onButtonPlay)
                menu.addAction(playAction)

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
        answer = None
        success_downloaded = 0

        # FIXME: must pass mainwindow as argument to ProgressCallbackWidget
        callback = ProgressCallbackWidget(self)
        callback.set_title_text(_('Downloading...'))
        callback.set_label_text(_("Downloading files..."))
        callback.set_updated_text(_("Downloading subtitle %s (%d/%d)"))
        callback.set_finished_text(_("%d from %d subtitles downloaded successfully"))
        callback.set_block(True)
        callback.set_range(0, total_subs)

        callback.show()

        for i, sub in enumerate(subs):
            if callback.canceled():
                break
            destinationPath = self.get_state().getDownloadPath(sub.getVideo(), sub)
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
                        # Skip this particular file if no filename chosen
                        continue
                elif answer == skipButton:
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
                    if self.get_state().get_OSDBServer().DownloadSubtitles({sub.getIdFileOnline(): destinationPath}):
                        success_downloaded += 1
                    else:
                        QMessageBox.about(self, _("Error"), _(
                            "Unable to download subtitle %s") % sub.get_filepath())
            except Exception as e:
                log.exception('Unable to Download subtitle {}'.format(sub.get_filepath()))
                QMessageBox.about(self, _("Error"), _(
                    "Unable to download subtitle %s") % sub.get_filepath())
        callback.finish(success_downloaded, total_subs)

    def onViewOnlineInfo(self):
        # FIXME: code duplication with Main.onContext and/or SearchNameWidget and/or SearchFileWidget
        # Tab for SearchByHash TODO:replace this 0 by an ENUM value
        listview = self.ui.videoView
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
    @pyqtSlot()
    def onSetIMDBInfo(self):
        #FIXME: DUPLICATED WITH SEARCHNAMEWIDGET
        QMessageBox.about(
            self, _("Info"), "Not implemented yet. Sorry...")
