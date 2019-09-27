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


def _create_choose_target_subtitle_path_cb(parent):
    def callback(path, filename):
        selected_path = QFileDialog.getSaveFileName(parent, _('Choose the target filename'),
                                                    str(path / filename))
        if selected_path[0]:
            return Path(selected_path[0])
        else:
            return None

    return callback


def download_subtitles_gui(parent, state, subs, parent_add=False):
    callback = ProgressCallbackWidget(parent)
    callback.set_title_text(_('Downloading...'))
    callback.set_label_text(_('Downloading files...'))
    callback.set_updated_text(_('Downloading subtitle {0} ({1}/{2})'))
    callback.set_finished_text(_('{0} from {1} subtitles downloaded successfully'))
    callback.set_block(True)
    callback.set_range(0, len(subs))

    callback.show()

    replace_all = False
    skip_all = False
    downloaded_subtitles = []

    for i, sub in enumerate(subs):
        if callback.canceled():
            break
        destinationPath = state.calculate_download_path(sub, _create_choose_target_subtitle_path_cb(parent),
                                                        conflict_free=False)
        if not destinationPath:
            callback.cancel()
            QMessageBox.information(parent, _('Download canceled'),_('Downloading has been canceled'))
            break
        log.debug('Trying to download subtitle "{}"'.format(destinationPath))
        callback.update(i, destinationPath.name, i + 1, len(subs))

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
                    parent)

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
                            parent, _("Save subtitle as..."), str(destinationPath), 'All (*.*)')
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
                                                QMessageBox.NoButton, parent)
                    skipButton = fileExistsBox.addButton(_('Skip'), QMessageBox.ActionRole)
                    skipAllButton = fileExistsBox.addButton(_('Skip all'), QMessageBox.ActionRole)
                    replaceButton = fileExistsBox.addButton(_('Replace'), QMessageBox.ActionRole)
                    replaceAllButton = fileExistsBox.addButton(_('Replace all'), QMessageBox.ActionRole)
                    saveAsButton = fileExistsBox.addButton(_('Save as...'), QMessageBox.ActionRole)
                    cancelButton = fileExistsBox.addButton(_('Cancel'), QMessageBox.ActionRole)
                    fileExecResult = fileExistsBox.exec_()

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
                        suggestedDestinationPath = state.calculate_download_path(sub, _create_choose_target_subtitle_path_cb(parent), conflict_free=True)
                        fileName, t = QFileDialog.getSaveFileName(
                            None, _('Save subtitle as...'), str(suggestedDestinationPath), 'All (*.*)')
                        if not fileName:
                            skipSubtitle = True
                        destinationPath = Path(fileName)
                    elif clickedButton == cancelButton:
                        callback.cancel()
                        continue
                    else:
                        log.debug('Unknown button clicked: result={}, button={}, role: {}'.format(
                            fileExecResult, clickedButton, fileExistsBox.buttonRole(clickedButton)))
                        skipSubtitle = True
                        continue
            break

        if skipSubtitle:
            continue

        if callback.canceled():
            break

        # FIXME: redundant update?
        callback.update(i, destinationPath, i + 1, len(subs))

        try:
            log.debug('Downloading subtitle "{}"'.format(destinationPath))
            download_callback = ProgressCallback()  # FIXME
            local_sub = sub.download(destinationPath, state.providers.get(sub.get_provider()).provider, download_callback)

            if parent_add:
                super_parent = sub.get_super_parent(VideoFile)
                if super_parent:
                    super_parent.add_subtitle(local_sub, priority=True)

            downloaded_subtitles.append(sub)
        except ProviderConnectionError:
            log.debug('Unable to download subtitle "{}"'.format(sub.get_filename()), exc_info=sys.exc_info())
            QMessageBox.about(parent, _('Error'), _('Unable to download subtitle "{subtitle}"').format(
                subtitle=sub.get_filename()))
            callback.finish()
            return downloaded_subtitles

    callback.finish(len(downloaded_subtitles), len(subs))
    return downloaded_subtitles
