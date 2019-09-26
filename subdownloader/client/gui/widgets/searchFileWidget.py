# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
from pathlib import Path
import sys
import tempfile
import webbrowser

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QDir, QFileInfo, QModelIndex, QSettings, \
    QSortFilterProxyModel, Qt, QTime
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog, QFileIconProvider, QFileSystemModel, QMenu, QMessageBox, QWidget

from subdownloader.callback import ProgressCallback
from subdownloader.filescan import scan_videopaths
from subdownloader.languages.language import Language, UnknownLanguage
from subdownloader.project import PROJECT_TITLE
from subdownloader.video2 import VideoFile
from subdownloader.subtitle2 import LocalSubtitleFile, RemoteSubtitleFile, SubtitleFile, SubtitleFileNetwork
from subdownloader.util import write_stream
from subdownloader.provider.SDService import ProviderConnectionError  # FIXME: move to provider

from subdownloader.client.gui import get_select_videos
from subdownloader.client.gui.callback import ProgressCallbackWidget
from subdownloader.client.gui.generated.searchFileWidget_ui import Ui_SearchFileWidget
from subdownloader.client.gui.state import State
from subdownloader.client.gui.models.searchFileModel import VideoModel

log = logging.getLogger('subdownloader.client.gui.searchFileWidget')
# FIXME: add logging


class SearchFileWidget(QWidget):

    language_filter_change = pyqtSignal(list)

    def __init__(self):
        QWidget.__init__(self)

        self._refreshing = False

        self.fileModel = None
        self.proxyFileModel = None
        self.videoModel = None

        self._state_old = None  # FIXME: Remove
        self._state = None

        self.timeLastSearch = QTime.currentTime()

        self.ui = Ui_SearchFileWidget()
        self.setup_ui()

    def set_state(self, state_old, state):
        self._state_old = state_old  # FIXME: Remove
        self._state = state
        self._state.signals.interface_language_changed.connect(self.on_interface_language_changed)
        self._state.signals.login_status_changed.connect(self.on_login_state_changed)

    def get_state(self):
        return self._state_old

    def setup_ui(self):
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

        index = self.fileModel.index(str(lastDir))
        proxyIndex = self.proxyFileModel.mapFromSource(index)
        self.ui.folderView.scrollTo(proxyIndex)

        self.ui.folderView.expanded.connect(self.onFolderViewExpanded)
        self.ui.folderView.clicked.connect(self.onFolderTreeClicked)
        self.ui.buttonFind.clicked.connect(self.onButtonFind)
        self.ui.buttonRefresh.clicked.connect(self.onButtonRefresh)

        # Setup and disable buttons
        self.ui.buttonFind.setEnabled(False)
        self.ui.buttonSearchSelectFolder.setEnabled(False)
        self.ui.buttonSearchSelectVideos.setEnabled(False)

        # Set up introduction
        self.showInstructions()

        # Set up video view
        self.ui.filterLanguageForVideo.set_unknown_text(_('All languages'))
        self.ui.filterLanguageForVideo.set_selected_language(UnknownLanguage.create_generic())
        self.ui.filterLanguageForVideo.selected_language_changed.connect(self.on_language_combobox_filter_change)

        self.videoModel = VideoModel(self)
        self.videoModel.connect_treeview(self.ui.videoView)
        self.ui.videoView.setHeaderHidden(True)
        self.ui.videoView.clicked.connect(self.onClickVideoTreeView)
        self.ui.videoView.selectionModel().currentChanged.connect(self.onSelectVideoTreeView)
        self.ui.videoView.customContextMenuRequested.connect(self.onContext)
        self.videoModel.dataChanged.connect(self.subtitlesCheckedChanged)
        self.language_filter_change.connect(self.videoModel.on_filter_languages_change)

        self.ui.buttonSearchSelectVideos.clicked.connect(self.onButtonSearchSelectVideos)
        self.ui.buttonSearchSelectFolder.clicked.connect(self.onButtonSearchSelectFolder)
        self.ui.buttonDownload.clicked.connect(self.onButtonDownload)
        self.ui.buttonPlay.clicked.connect(self.onButtonPlay)
        self.ui.buttonIMDB.clicked.connect(self.onViewOnlineInfo)
        self.ui.videoView.setContextMenuPolicy(Qt.CustomContextMenu)

        self.ui.buttonPlay.setEnabled(False)

        # Drag and Drop files to the videoView enabled
        # FIXME: enable drag events for videoView (and instructions view)
        self.ui.videoView.__class__.dragEnterEvent = self.dragEnterEvent
        self.ui.videoView.__class__.dragMoveEvent = self.dragEnterEvent
        self.ui.videoView.__class__.dropEvent = self.dropEvent
        self.ui.videoView.setAcceptDrops(1)

        self.retranslate()

    def retranslate(self):
        introduction = '<p align="center"><h2>{title}</h2></p>' \
            '<p><b>{tab1header}</b><br/>{tab1content}</p>' \
            '<p><b>{tab2header}</b><br/>{tab2content}</p>'\
            '<p><b>{tab3header}</b><br/>{tab3content}</p>'.format(
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

    @pyqtSlot(Language)
    def on_interface_language_changed(self, language):
        self.ui.retranslateUi(self)
        self.retranslate()

    @pyqtSlot(str)
    def onFileModelDirectoryLoaded(self, path):
        settings = QSettings()
        lastDir = settings.value('mainwindow/workingDirectory', QDir.homePath())
        qDirLastDir = QDir(lastDir)
        qDirLastDir.cdUp()
        if qDirLastDir.path() == path:
            index = self.fileModel.index(lastDir)
            proxyIndex = self.proxyFileModel.mapFromSource(index)
            self.ui.folderView.scrollTo(proxyIndex)
            self.ui.folderView.setCurrentIndex(proxyIndex)

    @pyqtSlot()
    def on_login_state_changed(self):
        log.debug('on_login_state_changed()')
        nb_connected = self._state.providers.get_number_connected_providers()
        if nb_connected:
            self.ui.buttonSearchSelectFolder.setEnabled(True)
            self.ui.buttonSearchSelectVideos.setEnabled(True)
            self.ui.buttonFind.setEnabled(self.get_current_selected_folder() is not None)
        else:
            self.ui.buttonSearchSelectFolder.setEnabled(False)
            self.ui.buttonSearchSelectVideos.setEnabled(False)
            self.ui.buttonFind.setEnabled(False)

    @pyqtSlot(Language)
    def on_language_combobox_filter_change(self, language):
        if language.is_generic():
            self.language_filter_change.emit(self._state.get_download_languages())
        else:
            self.language_filter_change.emit([language])

    def on_permanent_language_filter_change(self, languages):
        selected_language = self.ui.filterLanguageForVideo.get_selected_language()
        if selected_language.is_generic():
            self.language_filter_change.emit(languages)

    @pyqtSlot()
    def subtitlesCheckedChanged(self):
        subs = self.videoModel.get_checked_subtitles()
        if subs:
            self.ui.buttonDownload.setEnabled(True)
        else:
            self.ui.buttonDownload.setEnabled(False)

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
        folder_path = self.fileModel.filePath(index)
        self._state.set_video_paths([folder_path])

    def get_current_selected_folder(self):
        proxyIndex = self.ui.folderView.currentIndex()
        index = self.proxyFileModel.mapToSource(proxyIndex)
        folder_path = Path(self.fileModel.filePath(index))
        if not folder_path:
            return None
        return folder_path

    def get_current_selected_item_videomodel(self):
        current_index = self.ui.videoView.currentIndex()
        return self.videoModel.getSelectedItem(current_index)

    @pyqtSlot()
    def onButtonFind(self):
        now = QTime.currentTime()
        if now < self.timeLastSearch.addMSecs(500):
            return
        folder_path = self.get_current_selected_folder()

        settings = QSettings()
        settings.setValue('mainwindow/workingDirectory', str(folder_path))
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

        index = self.fileModel.index(str(currentPath))

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

                index = self.fileModel.index(str(currentPath))

                self.ui.folderView.scrollTo(self.proxyFileModel.mapFromSource(index))
                self._refreshing = False

    @pyqtSlot()
    def onButtonSearchSelectFolder(self):
        paths = self._state.get_video_paths()
        path = paths[0] if paths else Path()
        selected_path = QFileDialog.getExistingDirectory(self, _('Select the directory that contains your videos'), str(path))
        if selected_path:
            selected_paths = [Path(selected_path)]
            self._state.set_video_paths(selected_paths)
            self.search_videos(selected_paths)

    @pyqtSlot()
    def onButtonSearchSelectVideos(self):
        paths = self._state.get_video_paths()
        path = paths[0] if paths else Path()
        selected_files, t = QFileDialog.getOpenFileNames(self, _('Select the video(s) that need subtitles'),
                                                    str(path), get_select_videos())
        if selected_files:
            selected_files = list(Path(f) for f in selected_files)
            selected_dirs = list(set(p.parent for p in selected_files))
            self._state.set_video_paths(selected_dirs)
            self.search_videos(selected_files)

    def search_videos(self, paths):
        if not self._state.providers.get_number_connected_providers():
            QMessageBox.about(self, _('Error'), _('You are not connected to a server. Please connect first.'))
            return
        self.ui.buttonFind.setEnabled(False)
        self._search_videos_raw(paths)
        self.ui.buttonFind.setEnabled(True)

    def _search_videos_raw(self, paths):
        # FIXME: must pass mainwindow as argument to ProgressCallbackWidget
        callback = ProgressCallbackWidget(self)
        callback.set_title_text(_('Scanning...'))
        callback.set_label_text(_('Scanning files'))
        callback.set_finished_text(_('Scanning finished'))
        callback.set_block(True)
        callback.show()

        try:
            local_videos, local_subs = scan_videopaths(paths, callback=callback, recursive=True)
        except OSError:
            callback.cancel()
            QMessageBox.warning(self, _('Error'), _('Some directories are not accessible.'))

        if callback.canceled():
            return

        callback.finish()

        log.debug('Videos found: {}'.format(local_videos))
        log.debug('Subtitles found: {}'.format(local_subs))

        self.hideInstructions()

        if not local_videos:
            QMessageBox.information(self, _('Scan Results'), _('No video has been found.'))
            return

        total = len(local_videos)

        # FIXME: must pass mainwindow as argument to ProgressCallbackWidget
        # callback = ProgressCallbackWidget(self)
        # callback.set_title_text(_('Asking Server...'))
        # callback.set_label_text(_('Searching subtitles...'))
        # callback.set_updated_text(_('Searching subtitles ( %d / %d )'))
        # callback.set_finished_text(_('Search finished'))
        callback.set_block(True)
        callback.set_range(0, total)

        callback.show()

        try:
            remote_subs = self._state.search_videos(local_videos, callback)
        except ProviderConnectionError:
                log.debug('Unable to search for subtitles of videos: videos={}'.format(list(v.get_filename() for v in local_videos)))
                QMessageBox.about(self, _('Error'), _('Unable to search for subtitles'))
                callback.finish()
                return

        self.videoModel.set_videos(local_videos)

        if remote_subs is None:
            QMessageBox.about(self, _('Error'), _(
                'Error contacting the server. Please try again later'))
        callback.finish()

        # TODO: CHECK if our local subtitles are already in the server, otherwise suggest to upload

    @pyqtSlot()
    def onButtonPlay(self):
        selected_item = self.get_current_selected_item_videomodel()
        log.debug('Trying to play selected item: {}'.format(selected_item))

        if selected_item is None:
            QMessageBox.warning(self, _('No subtitle selected'), _('Select a subtitle and try again'))
            return

        if isinstance(selected_item, SubtitleFileNetwork):
            selected_item = selected_item.get_subtitles()[0]

        if isinstance(selected_item, VideoFile):
            subtitle_file_path = None
            video = selected_item
        elif isinstance(selected_item, LocalSubtitleFile):
            subtitle_file_path = selected_item.get_filepath()
            video = selected_item.get_super_parent(VideoFile)
        elif isinstance(selected_item, RemoteSubtitleFile):
            video = selected_item.get_super_parent(VideoFile)
            subtitle_file_path = Path(tempfile.gettempdir()) / 'subdownloader.tmp.srt'
            log.debug('tmp path is {}'.format(subtitle_file_path))
            log.debug('Temporary subtitle will be downloaded into: {temp_path}'.format(temp_path=subtitle_file_path))
            # FIXME: must pass mainwindow as argument to ProgressCallbackWidget
            callback = ProgressCallbackWidget(self)
            callback.set_title_text(_('Playing video + sub'))
            callback.set_label_text(_('Downloading files...'))
            callback.set_finished_text(_('Downloading finished'))
            callback.set_block(True)
            callback.set_range(0, 100)
            callback.show()

            try:
                selected_item.download(subtitle_file_path, self._state.providers.get(selected_item.get_provider), callback)
            except ProviderConnectionError:
                log.debug('Unable to download subtitle "{}"'.format(selected_item.get_filename()), exc_info=sys.exc_info())
                QMessageBox.about(self, _('Error'), _('Unable to download subtitle "{subtitle}"').format(
                    subtitle=selected_item.get_filename()))
                callback.finish()
                return
            callback.finish()
        else:
            QMessageBox.about(self, _('Error'), '{}\n{}'.format(_('Unknown Error'), _('Please submit bug report')))
            return

        # video = selected_item.get_parent().get_parent().get_parent()
        # FIXME: download subtitle with provider + use returned localSubtitleFile instead of creating one here
        if subtitle_file_path:
            local_subtitle = LocalSubtitleFile(subtitle_file_path)
        else:
            local_subtitle = None
        try:
            player = self._state.get_videoplayer()
            player.play_video(video, local_subtitle)
        except RuntimeError as e:
            QMessageBox.about(self, _('Error'), e.args[0])

    @pyqtSlot(QModelIndex)
    def onClickVideoTreeView(self, index):
        data_item = self.videoModel.getSelectedItem(index)

        if isinstance(data_item, VideoFile):
            video = data_item
            if True: # video.getMovieInfo():
                self.ui.buttonIMDB.setEnabled(True)
                self.ui.buttonIMDB.setIcon(QIcon(':/images/info.png'))
                self.ui.buttonIMDB.setText(_('Movie Info'))
        elif isinstance(data_item, RemoteSubtitleFile):
            self.ui.buttonIMDB.setEnabled(True)
            self.ui.buttonIMDB.setIcon(QIcon(':/images/sites/opensubtitles.png'))
            self.ui.buttonIMDB.setText(_('Subtitle Info'))
        else:
            self.ui.buttonIMDB.setEnabled(False)

    @pyqtSlot(QModelIndex)
    def onSelectVideoTreeView(self, index):
        data_item = self.videoModel.getSelectedItem(index)

        self.ui.buttonPlay.setEnabled(True)
        # if isinstance(data_item, SubtitleFile):
        #     self.ui.buttonPlay.setEnabled(True)
        # else:
        #     self.ui.buttonPlay.setEnabled(False)

    def onContext(self, point):
        # FIXME: code duplication with Main.onContext and/or SearchNameWidget and/or SearchFileWidget
        menu = QMenu('Menu', self)

        listview = self.ui.videoView

        index = listview.currentIndex()
        data_item = listview.model().getSelectedItem(index)
        if data_item is not None:
            if isinstance(data_item, VideoFile):
                video = data_item
                video_identities = video.get_identities()
                if any(video_identities.iter_imdb_identity()):
                    online_action = QAction(QIcon(":/images/info.png"), _("View IMDb info"), self)
                    online_action.triggered.connect(self.onViewOnlineInfo)
                else:
                    online_action = QAction(QIcon(":/images/info.png"), _("Set IMDb info..."), self)
                    online_action.triggered.connect(self.on_set_imdb_info)
                menu.addAction(online_action)
            elif isinstance(data_item, SubtitleFile):
                play_action = QAction(QIcon(":/images/play.png"), _("Play video + subtitle"), self)
                play_action.triggered.connect(self.onButtonPlay)
                menu.addAction(play_action)

                if isinstance(data_item, RemoteSubtitleFile):
                    download_action = QAction(QIcon(":/images/download.png"), _("Download"), self)
                    download_action.triggered.connect(self.onButtonDownload)
                    menu.addAction(download_action)

                    online_action = QAction(QIcon(":/images/sites/opensubtitles.png"), _("View online info"), self)
                    online_action.triggered.connect(self.onViewOnlineInfo)
                    menu.addAction(online_action)

        # Show the context menu.
        menu.exec_(listview.mapToGlobal(point))

    def _create_choose_target_subtitle_path_cb(self):
        def callback(path, filename):
            selected_path = QFileDialog.getSaveFileName(self, _('Choose the target filename'),
                                                        str(path / filename))
            return selected_path
        return callback

    def onButtonDownload(self):
        # We download the subtitle in the same folder than the video
        subs = self.videoModel.get_checked_subtitles()
        replace_all = False
        skip_all = False
        if not subs:
            QMessageBox.about(
                self, _('Error'), _('No subtitles selected to be downloaded'))
            return
        total_subs = len(subs)
        success_downloaded = 0

        # FIXME: must pass mainwindow as argument to ProgressCallbackWidget
        callback = ProgressCallbackWidget(self)
        callback.set_title_text(_('Downloading...'))
        callback.set_label_text(_('Downloading files...'))
        callback.set_updated_text(_('Downloading subtitle {0} ({1}/{2})'))
        callback.set_finished_text(_('{0} from {1} subtitles downloaded successfully'))
        callback.set_block(True)
        callback.set_range(0, total_subs)

        callback.show()

        for i, sub in enumerate(subs):
            if callback.canceled():
                break
            destinationPath = self._state.calculate_download_path(sub, self._create_choose_target_subtitle_path_cb(),
                                                                  conflict_free=False)
            if not destinationPath:
                QMessageBox.information(self, _('Download canceled'),_('Downloading has been canceled'))
                break
            log.debug('Trying to download subtitle "{}"'.format(destinationPath))
            callback.update(i, destinationPath.name, i + 1, total_subs)

            skipSubtitle = False

            # Check if we have write permissions, otherwise show warning window
            while not skipSubtitle:

                if callback.canceled():
                    break

                # If the file and the folder don't have write access.
                if not os.access(str(destinationPath), os.W_OK) and not os.access(str(destinationPath.parent), os.W_OK):
                    warningBox = QMessageBox(
                        QMessageBox.Warning,
                        _("Error write permission"),
                        _("{} cannot be saved.\nCheck that the folder exists and you have write-access permissions.").format(destinationPath),
                        QMessageBox.Retry | QMessageBox.Discard,
                        self)

                    saveAsButton = warningBox.addButton(
                        _("Save as..."), QMessageBox.ActionRole)
                    boxExecResult = warningBox.exec_()
                    if boxExecResult == QMessageBox.Retry:
                        continue
                    elif boxExecResult == QMessageBox.Abort:
                        skipSubtitle = True
                        continue
                    else:
                        clickedButton = warningBox.clickedButton()
                        if clickedButton is None:
                            skipSubtitle = True
                            continue
                        elif clickedButton == saveAsButton:
                            newFilePath, t = QFileDialog.getSaveFileName(
                                self, _("Save subtitle as..."), str(destinationPath), 'All (*.*)')
                            if not newFilePath:
                                skipSubtitle = True
                                continue
                            destinationPath = Path(newFilePath)
                        else:
                            log.debug('Unknown button clicked: result={}, button={}, role: {}'.format(boxExecResult, clickedButton, warningBox.buttonRole(clickedButton)))
                            skipSubtitle = True
                            continue

                if skipSubtitle:
                    break

                if destinationPath.exists():
                    if skip_all:
                        skipSubtitle = True
                        continue
                    elif replace_all:
                        pass
                    else:
                        fileExistsBox = QMessageBox(QMessageBox.Warning, _('File already exists'),
                                                    '{localLbl}: {local}\n\n{remoteLbl}: {remote}\n\n{question}'.format(
                                                        localLbl=_('Local'),
                                                        local=destinationPath,
                                                        remoteLbl=_('remote'),
                                                        remote=sub.get_filename(),
                                                        question=_('How would you like to proceed?'),),
                                                    QMessageBox.NoButton, self)
                        skipButton = fileExistsBox.addButton(_('Skip'), QMessageBox.ActionRole)
                        skipAllButton = fileExistsBox.addButton(_('Skip all'), QMessageBox.ActionRole)
                        replaceButton = fileExistsBox.addButton(_('Replace'), QMessageBox.ActionRole)
                        replaceAllButton = fileExistsBox.addButton(_('Replace all'), QMessageBox.ActionRole)
                        saveAsButton = fileExistsBox.addButton(_('Save as...'), QMessageBox.ActionRole)
                        cancelButton = fileExistsBox.addButton(_('Cancel'), QMessageBox.ActionRole)
                        fileExistsBox.exec_()

                        clickedButton = fileExistsBox.clickedButton()
                        if clickedButton == skipButton:
                            skipSubtitle = True
                            continue
                        elif clickedButton == skipAllButton:
                            skipSubtitle = True
                            skip_all = True
                            continue
                        elif clickedButton == replaceButton:
                            pass
                        elif clickedButton == replaceAllButton:
                            replace_all = True
                        elif clickedButton == saveAsButton:
                            suggestedDestinationPath = self._state.calculate_download_path(sub, self._create_choose_target_subtitle_path_cb(), conflict_free=True)
                            fileName, t = QFileDialog.getSaveFileName(
                                None, _('Save subtitle as...'), str(suggestedDestinationPath), 'All (*.*)')
                            if not fileName:
                                skipSubtitle = True
                            destinationPath = Path(fileName)
                        elif clickedButton == cancelButton:
                            callback.cancel()
                            continue
                        else:
                            log.debug('Unknown button clicked: result={}, button={}, role: {}'.format(boxExecResult, clickedButton, warningBox.buttonRole(clickedButton)))
                            skipSubtitle = True
                            continue
                break

            if skipSubtitle:
                continue

            if callback.canceled():
                break

            # FIXME: redundant update?
            callback.update(i, destinationPath, i + 1, total_subs)

            try:
                log.debug('Downloading subtitle "{}"'.format(destinationPath))
                download_callback = ProgressCallback()  # FIXME
                sub.download(destinationPath, self._state.providers.get(sub.get_provider), download_callback)
                self.videoModel.uncheck_subtitle(sub)
            except ProviderConnectionError:
                log.debug('Unable to download subtitle "{}"'.format(sub.get_filename()), exc_info=sys.exc_info())
                QMessageBox.about(self, _('Error'), _('Unable to download subtitle "{subtitle}"').format(
                    subtitle=sub.get_filename()))
                callback.finish()
                return
        callback.finish(success_downloaded, total_subs)
        self.videoModel.underlying_data_changed()

    def onViewOnlineInfo(self):
        # FIXME: code duplication with Main.onContext and/or SearchNameWidget and/or SearchFileWidget
        # Tab for SearchByHash TODO:replace this 0 by an ENUM value
        listview = self.ui.videoView
        index = listview.currentIndex()
        data_item = self.videoModel.getSelectedItem(index)

        if isinstance(data_item, VideoFile):
            video = data_item
            video_identities = video.get_identities()
            if any(video_identities.iter_imdb_identity()):
                imdb_identity = next(video_identities.iter_imdb_identity())
                webbrowser.open(imdb_identity.get_imdb_url(), new=2, autoraise=1)

        elif isinstance(data_item, RemoteSubtitleFile):
            sub = data_item
            webbrowser.open(sub.get_link(), new=2, autoraise=1)

    @pyqtSlot()
    def on_set_imdb_info(self):
        #FIXME: DUPLICATED WITH SEARCHNAMEWIDGET
        QMessageBox.about(
            self, _("Info"), "Not implemented yet. Sorry...")
