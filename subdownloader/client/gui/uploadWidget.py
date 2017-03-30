# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import base64
import logging
import os
try:
    import thread
except ImportError:
    import _thread as thread
import webbrowser
import zlib

from subdownloader.languages import language

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QEventLoop, QFileInfo, QItemSelection, QItemSelectionModel, QSettings
from PyQt5.QtWidgets import QFileDialog, QHeaderView, QMessageBox, QWidget

from subdownloader.FileManagement import FileScan, Subtitle
from subdownloader.client.gui import SELECT_SUBTITLES, SELECT_VIDEOS
from subdownloader.client.gui.imdbSearch import imdbSearchDialog
from subdownloader.client.gui.callback import ProgressCallbackWidget
from subdownloader.client.gui.uploadlistview import UploadListModel, UploadListView
from subdownloader.client.gui.uploadWidget_ui import Ui_UploadWidget
from subdownloader.client.gui.state import State
from subdownloader.FileManagement.videofile import VideoFile
from subdownloader.FileManagement.subtitlefile import SubtitleFile

log = logging.getLogger('subdownloader.client.gui.uploadWidget')


class UploadWidget(QWidget):

    imdbDetected = pyqtSignal(str, str, str)
    language_updated = pyqtSignal(str, str)
    releaseUpdated = pyqtSignal(str)

    def __init__(self):
        QWidget.__init__(self)

        self.upload_autodetected_lang = ""
        self.upload_autodetected_imdb = ""

        self._state = None

        self.ui = Ui_UploadWidget()
        self.setup_ui()

    def set_state(self, state):
        self._state = state
        self._state.login_status_changed.connect(self.on_login_state_changed)
        self._state.interface_language_changed.connect(self.on_interface_language_changed)

    def get_state(self):
        return self._state

    def setup_ui(self):
        self.ui.setupUi(self)
        self.initializeFilterLanguages()

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

        settings = QSettings()
        optionUploadLanguage = settings.value("options/uploadLanguage", "eng")
        index = self.ui.uploadLanguages.findData(optionUploadLanguage)
        if index != -1:
            self.ui.uploadLanguages.setCurrentIndex(index)

        self.ui.uploadLanguages.adjustSize()

        size = settings.beginReadArray("upload/imdbHistory")
        for i in range(size):
            settings.setArrayIndex(i)
            imdbId = settings.value("imdbId")
            title = settings.value("title")
            self.ui.uploadIMDB.addItem("%s : %s" % (imdbId, title), imdbId)
        settings.endArray()

    def retranslate(self):
        pass

    @pyqtSlot(language.Language)
    def on_interface_language_changed(self, language):
        self.ui.retranslateUi(self)
        self.retranslate()

    # UPLOAD METHODS

    @pyqtSlot(int, str)
    def on_login_state_changed(self, state, message):
        log.debug('on_login_state_changed(state={state}, message={message}'.format(state=state, message=message))
        if state in  (State.LOGIN_STATUS_LOGGED_OUT, State.LOGIN_STATUS_BUSY):
            pass
        elif state == State.LOGIN_STATUS_LOGGED_IN:
            pass

    def initializeFilterLanguages(self):
        for lang in language.legal_languages():
            self.ui.uploadLanguages.addItem(_(lang.name()), lang.xxx())

        self.language_updated.connect(
            self.onUploadLanguageDetection)

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
                callback = ProgressCallbackWidget(self)
                callback.set_title_text(_("Uploading..."))
                callback.set_label_text(_("Uploading subtitle"))
                callback.set_block(True)
                callback.set_cancellable(False)

                callback.show()

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
                        buf = open(curr_sub.getFilePath(), mode='rb').read()
                        curr_sub_content = base64.encodestring(zlib.compress(buf))
                        cd = "cd" + str(i)
                        movie_info[cd] = {'subhash': curr_sub.get_hash(), 'subfilename': curr_sub.get_filepath(), 'moviehash': curr_video.get_hash(), 'moviebytesize': curr_video.get_size(
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

    def uploadCleanWindow(self):
        self.ui.uploadReleaseText.setText("")
        self.ui.uploadComments.setText("")
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

    @pyqtSlot()
    def onButtonUploadFindIMDB(self):
        dialog = imdbSearchDialog(self)
        ok = dialog.exec_()
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    @pyqtSlot()
    def onUploadBrowseFolder(self):
        settings = QSettings()
        path = settings.value("mainwindow/workingDirectory", "")
        directory = QFileDialog.getExistingDirectory(
            self, _("Select a directory"), path)
        if directory:
            settings.setValue("mainwindow/workingDirectory", directory)
            videos_found, subs_found = FileScan.scan_folder(
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

    def onUploadSelectImdb(self, index):
        self.upload_autodetected_imdb = "selected"
        self.ui.label_autodetect_imdb.hide()

    def OnChangeReleaseName(self, name):
        self.ui.uploadReleaseText.setText(name)
