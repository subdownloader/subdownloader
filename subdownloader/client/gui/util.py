# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
from pathlib import Path
import sys

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from subdownloader.provider.provider import ProviderConnectionError
from subdownloader.client.callback import ProgressCallback
from subdownloader.client.gui.callback import ProgressCallbackWidget
from subdownloader.video2 import VideoFile

log = logging.getLogger(__name__)


class SubtitleDownloadProcess(object):
    def __init__(self, parent, rsubtitles, state, parent_add=False):
        self._parent = parent
        self._rsubtitles = rsubtitles
        self._downloaded_subtitles = []
        self._state = state
        self._curr_sub_i = 0
        self._callback = self._create_callback()
        self._parent_add = parent_add

        self._replace_all = False
        self._skip_all = False

    def __del__(self):
        self._callback.finish()

    def _create_callback(self):
        callback = ProgressCallbackWidget(self._parent)
        callback.set_title_text(_('Downloading...'))
        callback.set_label_text(_('Downloading files...'))
        callback.set_updated_text(_('Downloading subtitle {0} ({1}/{2})'))
        callback.set_finished_text(_('{0} from {1} subtitles downloaded successfully'))
        callback.set_block(True)
        callback.set_range(0, len(self._rsubtitles))

        callback.show()
        return callback

    def finished(self):
        return self._callback.canceled() or self._callback.finished() or self._curr_sub_i >= len(self._rsubtitles)

    def next_subtitle(self):
        self._curr_sub_i += 1

    def _create_choose_target_subtitle_path_cb(self):
        def callback(path, filename):
            selected_path = QFileDialog.getSaveFileName(self._parent, _('Choose the target filename'),
                                                        str(path / filename))
            if selected_path[0]:
                return Path(selected_path[0])
            else:
                return None

        return callback

    def info(self, title, msg):
        QMessageBox.information(self._parent, title, msg)

    def _download_current_subtitle(self):
        if self.finished():
            return
        rsub = self._rsubtitles[self._curr_sub_i]
        destinationPath = self._state.calculate_download_path(rsub, self._create_choose_target_subtitle_path_cb(),
                                                              conflict_free=False)
        if not destinationPath:
            self._callback.cancel()
            self.info(_('Download canceled'), _('Downloading has been canceled'))
            return

        log.debug('Trying to download subtitle "{}"'.format(destinationPath))

        while True:
            self._callback.update(self._curr_sub_i, destinationPath, self._curr_sub_i + 1, len(self._rsubtitles))
            if self.finished():
                break

            # Check for write access for file and folder
            if not os.access(str(destinationPath), os.W_OK) and not os.access(str(destinationPath.parent), os.W_OK):
                warningBox = QMessageBox(QMessageBox.Warning, _('Error write permission'),
                    _('{} cannot be saved.\nCheck that the folder exists and you have write-access permissions.').format(destinationPath),
                    QMessageBox.Retry | QMessageBox.Discard,
                    self._parent)

                saveAsButton = warningBox.addButton(
                    _('Save as...'), QMessageBox.ActionRole)
                boxExecResult = warningBox.exec_()
                if boxExecResult == QMessageBox.Retry:
                    continue
                elif boxExecResult == QMessageBox.Abort:
                    return
                else:
                    clickedButton = warningBox.clickedButton()
                    if clickedButton is None:
                        return
                    elif clickedButton == saveAsButton:
                        newFilePath, t = QFileDialog.getSaveFileName(
                            self._parent, _('Save subtitle as...'), str(destinationPath), 'All (*.*)')
                        if not newFilePath:
                            self._callback.cancel()
                            return
                        destinationPath = Path(newFilePath)
                        continue
                    else:
                        log.debug('Unknown button clicked: result={}, button={}, role: {}'.format(boxExecResult, clickedButton, warningBox.buttonRole(clickedButton)))
                        return

            if destinationPath.exists():
                if self._skip_all:
                    return
                elif self._replace_all:
                    pass
                else:
                    fileExistsBox = QMessageBox(QMessageBox.Warning, _('File already exists'),
                                                '{localLbl}: {local}\n\n{remoteLbl}: {remote}\n\n{question}'.format(
                                                    localLbl=_('Local'),
                                                    local=destinationPath,
                                                    remoteLbl=_('remote'),
                                                    remote=rsub.get_filename(),
                                                    question=_('How would you like to proceed?'),),
                                                QMessageBox.NoButton, self._parent)
                    skipButton = fileExistsBox.addButton(_('Skip'), QMessageBox.ActionRole)
                    skipAllButton = fileExistsBox.addButton(_('Skip all'), QMessageBox.ActionRole)
                    replaceButton = fileExistsBox.addButton(_('Replace'), QMessageBox.ActionRole)
                    replaceAllButton = fileExistsBox.addButton(_('Replace all'), QMessageBox.ActionRole)
                    saveAsButton = fileExistsBox.addButton(_('Save as...'), QMessageBox.ActionRole)
                    cancelButton = fileExistsBox.addButton(_('Cancel'), QMessageBox.ActionRole)
                    fileExecResult = fileExistsBox.exec_()

                    clickedButton = fileExistsBox.clickedButton()
                    if clickedButton == skipButton:
                        return
                    elif clickedButton == skipAllButton:
                        self._skip_all = True
                        return
                    elif clickedButton == replaceButton:
                        pass
                    elif clickedButton == replaceAllButton:
                        self._replace_all = True
                    elif clickedButton == saveAsButton:
                        suggestedDestinationPath = self._state.calculate_download_path(rsub, self._create_choose_target_subtitle_path_cb(), conflict_free=True)
                        fileName, t = QFileDialog.getSaveFileName(
                            None, _('Save subtitle as...'), str(suggestedDestinationPath), 'All (*.*)')
                        if not fileName:
                            return
                        destinationPath = Path(fileName)
                        continue
                    elif clickedButton == cancelButton:
                        self._callback.cancel()
                        return
                    else:
                        log.debug('Unknown button clicked: result={}, button={}, role: {}'.format(
                            fileExecResult, clickedButton, fileExistsBox.buttonRole(clickedButton)))
                        return
            break

        try:
            log.debug('Downloading subtitle to "{}"'.format(destinationPath))
            download_callback = ProgressCallback()  # FIXME
            local_sub = rsub.download(destinationPath,
                                      self._state.providers.get(rsub.get_provider()).provider, download_callback)

            if self._parent_add:
                super_parent = rsub.get_super_parent(VideoFile)
                if super_parent:
                    super_parent.add_subtitle(local_sub, priority=True)

            self._downloaded_subtitles.append(rsub)
        except ProviderConnectionError:
            log.debug('Unable to download subtitle "{}"'.format(rsub.get_filename()), exc_info=sys.exc_info())
            QMessageBox.about(self._parent, _('Error'), _('Unable to download subtitle "{subtitle}"').format(
                subtitle=rsub.get_filename()))
            self._callback.finish()

    def download_all(self):
        while not self.finished():
            self._download_current_subtitle()
            self._curr_sub_i += 1
        if not self._callback.finished():
            self._callback.finish(len(self._rsubtitles), len(self._rsubtitles))

    def downloaded_subtitles(self):
        return self._downloaded_subtitles
