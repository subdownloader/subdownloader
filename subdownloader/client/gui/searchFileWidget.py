# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
from pathlib import Path
import platform
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
from subdownloader.provider.SDService import ProviderConnectionError #FIXME: move to provider

from subdownloader.client.gui import get_select_videos
from subdownloader.client.gui.callback import ProgressCallbackWidget
from subdownloader.client.gui.generated.searchFileWidget_ui import Ui_SearchFileWidget
from subdownloader.client.gui.state import State
from subdownloader.client.gui.searchFileModel import VideoModel

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

        self._state = None

        self.timeLastSearch = QTime.currentTime()

        self.ui = Ui_SearchFileWidget()
        self.setup_ui()

    def set_state(self, state):
        self._state = state
        self._state.login_status_changed.connect(self.on_login_state_changed)
        self._state.interface_language_changed.connect(self.on_interface_language_changed)

    def get_state(self):
        return self._state

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

        # Set up introduction
        self.showInstructions()

        # Set up video view
        self.ui.filterLanguageForVideo.set_unknown_text(_('All languages'))
        self.ui.filterLanguageForVideo.set_selected_language(UnknownLanguage.create_generic())
        self.ui.filterLanguageForVideo.selected_language_changed.connect(self.on_language_combobox_filter_change)

        self.videoModel = VideoModel(self)
        self.videoModel.connect_treeview(self.ui.videoView)
        self.ui.videoView.setHeaderHidden(True)
        self.ui.videoView.activated.connect(self.onClickVideoTreeView)
        self.ui.videoView.clicked.connect(self.onClickVideoTreeView)
        self.ui.videoView.customContextMenuRequested.connect(self.onContext)
        self.videoModel.dataChanged.connect(self.subtitlesCheckedChanged)
        self.language_filter_change.connect(self.videoModel.on_filter_languages_change)

        self.ui.buttonSearchSelectVideos.clicked.connect(self.onButtonSearchSelectVideos)
        self.ui.buttonSearchSelectFolder.clicked.connect(self.onButtonSearchSelectFolder)
        self.ui.buttonDownload.clicked.connect(self.onButtonDownload)
        self.ui.buttonPlay.clicked.connect(self.onButtonPlay)
        self.ui.buttonIMDB.clicked.connect(self.onViewOnlineInfo)
        self.ui.videoView.setContextMenuPolicy(Qt.CustomContextMenu)

        # Drag and Drop files to the videoView enabled
        self.ui.videoView.__class__.dragEnterEvent = self.dragEnterEvent
        self.ui.videoView.__class__.dragMoveEvent = self.dragEnterEvent
        self.ui.videoView.__class__.dropEvent = self.dropEvent
        self.ui.videoView.setAcceptDrops(1)

        # FIXME: ok to drop this connect?
        # self.ui.videoView.clicked.connect(self.onClickMovieTreeView)

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

    @pyqtSlot(Language)
    def on_language_combobox_filter_change(self, language):
        if language.is_generic():
            self.language_filter_change.emit(self.get_state().get_permanent_language_filter())
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
        settings = QSettings()
        folder_path = self.fileModel.filePath(index)
        settings.setValue('mainwindow/workingDirectory', folder_path)
        # self.ui.buttonFind.setEnabled(self.get_state().)

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
        settings = QSettings()
        path = settings.value('mainwindow/workingDirectory', QDir.homePath())
        folder_path = QFileDialog.getExistingDirectory(self, _('Select the directory that contains your videos'), path)
        if folder_path:
            settings.setValue('mainwindow/workingDirectory', folder_path)
            self.search_videos([Path(folder_path)])

    @pyqtSlot()
    def onButtonSearchSelectVideos(self):
        settings = QSettings()
        currentDir = settings.value('mainwindow/workingDirectory', QDir.homePath())
        fileNames, t = QFileDialog.getOpenFileNames(self, _('Select the video(s) that need subtitles'),
                                                    currentDir, get_select_videos())
        if fileNames:
            settings.setValue('mainwindow/workingDirectory', QFileInfo(fileNames[0]).absolutePath())
            self.search_videos([Path(filename) for filename in fileNames])

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
        callback.show()

        try:
            local_videos, local_subs = scan_videopaths(paths, callback=callback, recursive=True)
        except OSError:
            callback.cancel()
            QMessageBox.warning(self, _('Error'), _('Some directories are not accessible.'))

        if callback.canceled():
            return

        callback.finish()

        log.debug("Videos found: %s" % local_videos)
        log.debug("Subtitles found: %s" % local_subs)
        self.hideInstructions()

        QCoreApplication.processEvents()

        if not local_videos:
            QMessageBox.about(self, _("Scan Results"), _("No video has been found."))
            return

        total = len(local_videos)

        # FIXME: must pass mainwindow as argument to ProgressCallbackWidget
        # callback = ProgressCallbackWidget(self)
        # callback.set_title_text(_("Asking Server..."))
        # callback.set_label_text(_("Searching subtitles..."))
        # callback.set_updated_text(_("Searching subtitles ( %d / %d )"))
        # callback.set_finished_text(_("Search finished"))
        callback.set_block(True)
        callback.set_range(0, total)

        callback.show()

        callback.set_range(0, 2)

        download_callback = callback.get_child_progress(0, 1)
        # videoSearchResults = self.get_state().get_OSDBServer().SearchSubtitles("", videos_piece)
        remote_subs = self.get_state().get_OSDBServer().search_videos(videos=local_videos, callback=download_callback)

        self.videoModel.set_videos(local_videos)
        # self.onFilterLanguageVideo(self.ui.filterLanguageForVideo.get_selected_language())

        if remote_subs is None:
            QMessageBox.about(self, _("Error"), _(
                "Error contacting the server. Please try again later"))
        callback.finish()

        # TODO: CHECK if our local subtitles are already in the server, otherwise suggest to upload
        # self.OSDBServer.CheckSubHash(sub_hashes)

    @pyqtSlot()
    def onButtonPlay(self):
        settings = QSettings()
        programPath = settings.value('options/VideoPlayerPath', '')
        parameters = settings.value('options/VideoPlayerParameters', '')
        if programPath == '':
            QMessageBox.about(self, _('Error'), _(
                'No default video player has been defined in Settings.'))
            return

        selected_subtitle = self.get_current_selected_item_videomodel()
        if isinstance(selected_subtitle, SubtitleFileNetwork):
            selected_subtitle = selected_subtitle.get_subtitles()[0]

        if isinstance(selected_subtitle, LocalSubtitleFile):
            subtitle_file_path = selected_subtitle.get_filepath()
        elif isinstance(selected_subtitle, RemoteSubtitleFile):
            subtitle_file_path = QDir.temp().absoluteFilePath('subdownloader.tmp.srt')
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
                subtitle_stream = selected_subtitle.download(self.get_state().get_OSDBServer(), callback=callback)
            except ProviderConnectionError:
                log.debug('Unable to download subtitle "{}"'.format(selected_subtitle.get_filename()), exc_info=True)
                QMessageBox.about(self, _('Error'), _('Unable to download subtitle "{subtitle}"').format(
                    subtitle=selected_subtitle.get_filename()))
                callback.finish()
                return
            callback.finish()
            write_stream(subtitle_stream, subtitle_file_path)

        video = selected_subtitle.get_parent().get_parent().get_parent()

        def windows_escape(text):
            return'"{text}"'.format(text=text.replace('"', '\\"'))

        params = [windows_escape(programPath)]

        for param in parameters.split(' '):
            param = param.format(video.get_filepath(), subtitle_file_path)
            if platform.system() in ('Windows', 'Microsoft'):
                param = windows_escape(param)
            params.append(param)

        pid = None
        log.info('Running this command: {params}'.format(params=params))
        try:
            log.debug('Trying os.spawnvpe ...')
            pid = os.spawnvpe(os.P_NOWAIT, programPath, params, os.environ)
            log.debug('... SUCCESS. pid={pid}'.format(pid=pid))
        except AttributeError:
            log.debug('... FAILED', exc_info=True)
        except Exception as e:
            log.debug('... FAILED', exc_info=True)
        if pid is None:
            try:
                log.debug('Trying os.fork ...')
                pid = os.fork()
                if not pid:
                    log.debug('... SUCCESS. pid={pid}'.format(pid=pid))
                    os.execvpe(os.P_NOWAIT, programPath, params, os.environ)
            except:
                log.debug('... FAIL', exc_info=True)
        if pid is None:
            QMessageBox.about(
                self, _('Error'), _('Unable to launch videoplayer'))

    @pyqtSlot(QModelIndex)
    def onClickVideoTreeView(self, index):
        data_item = self.videoModel.getSelectedItem(index)

        if isinstance(data_item, SubtitleFile):
            self.ui.buttonPlay.setEnabled(True)
        else:
            self.ui.buttonPlay.setEnabled(False)

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

    def onButtonDownload(self):
        # We download the subtitle in the same folder than the video
        subs = self.videoModel.get_checked_subtitles()
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
        callback.set_title_text(_("Downloading..."))
        callback.set_label_text(_("Downloading files..."))
        callback.set_updated_text(_("Downloading subtitle {0} ({1}/{2})"))
        callback.set_finished_text(_("{0} from {1} subtitles downloaded successfully"))
        callback.set_block(True)
        callback.set_range(0, total_subs)

        callback.show()

        for i, sub in enumerate(subs):
            if callback.canceled():
                break
            destinationPath = self.get_state().getDownloadPath(self, sub)
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

            optionWhereToDownload = QSettings().value("options/whereToDownload", "SAME_FOLDER")
            # Check if doesn't exists already, otherwise show fileExistsBox
            # dialog
            if QFileInfo(destinationPath).exists() and not replace_all and not skip_all and optionWhereToDownload != "ASK_FOLDER":
                # The "remote filename" below is actually not the real filename. Real name could be confusing
                # since we always rename downloaded sub to match movie
                # filename.
                fileExistsBox = QMessageBox(
                    QMessageBox.Warning,
                    _("File already exists"),
                    _("Local: {local}\n\nRemote: {remote}\n\nHow would you like to proceed?").format(
                        local=destinationPath, remote=QFileInfo(destinationPath).fileName()),
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
                        sub.get_language().xxx() + suggFileExt
                    while (os.path.exists(suggestedFileName)):
                        fNameCtr += 1
                        suggestedFileName = suggBaseName + '.' + \
                            sub.get_language().xxx() + '-' + \
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
                    download_callback = ProgressCallback()  # FIXME
                    data_stream = sub.download(
                        provider_instance=self.get_state().get_OSDBServer(),
                        callback=download_callback,
                    )
                    write_stream(data_stream, destinationPath)
            except Exception as e:
                log.exception('Unable to Download subtitle {}'.format(sub.get_filename()))
                QMessageBox.about(self, _("Error"), _(
                    "Unable to download subtitle %s") % sub.get_filename())
        callback.finish(success_downloaded, total_subs)

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
