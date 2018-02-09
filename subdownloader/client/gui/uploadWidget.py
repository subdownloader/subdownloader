# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtCore import pyqtSlot, QAbstractListModel, QModelIndex, QSettings, Qt
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QMessageBox, QWidget

from subdownloader.identification import ImdbIdentity, VideoIdentity, ProviderIdentities, identificators_get
from subdownloader.languages import language
from subdownloader.movie import LocalMovie

from subdownloader.client.gui.imdbSearch import ImdbSearchDialog
from subdownloader.client.gui.preferences import PreferencesDialog
from subdownloader.client.gui.generated.uploadWidget_ui import Ui_UploadWidget

log = logging.getLogger('subdownloader.client.gui.uploadWidget')


class UploadWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self._state = None
        self._default_language_selected = False

        self._imdb_history_model = ImdbHistoryModel()

        self.ui = Ui_UploadWidget()
        self.setup_ui()

    def set_state(self, state):
        self._state = state
        self._state.interface_language_changed.connect(self.on_interface_language_changed)

        self._state.login_status_changed.connect(self.on_upload_data_changed)

    def get_state(self):
        return self._state

    def setup_ui(self):
        self.ui.setupUi(self)

        self.ui.uploadView.selectionModel().selectionChanged.connect(self.on_selection_change)

        self.ui.uploadView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.uploadView.setAlternatingRowColors(True)
        self.ui.uploadView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.uploadView.setGridStyle(Qt.DotLine)

        self.ui.buttonUploadBrowseFolder.clicked.connect(self.ui.uploadView.on_browse_folder)

        self.ui.buttonUploadPlusRow.clicked.connect(self.ui.uploadView.on_add_row)
        self.ui.buttonUploadMinusRow.clicked.connect(self.ui.uploadView.on_remove_selection)

        self.ui.buttonUploadDeleteAllRow.clicked.connect(self.ui.uploadView.on_reset)
        self.ui.buttonUploadDeleteAllRow.clicked.connect(self.on_reset)

        self.ui.buttonUploadDownRow.clicked.connect(self.ui.uploadView.on_move_selection_down)
        self.ui.buttonUploadUpRow.clicked.connect(self.ui.uploadView.on_move_selection_up)

        self.ui.uploadLanguages.set_unknown_visible(True)
        self.ui.uploadLanguages.selected_language_changed.connect(self.on_upload_language_change)

        self.ui.buttonUpload.setEnabled(False)
        self.ui.buttonUpload.clicked.connect(self.on_upload)

        self.ui.buttonUploadFindIMDB.clicked.connect(self.on_find_imdb)
        self.ui.uploadView.upload_data_changed.connect(self.on_upload_data_changed)

        self.ui.uploadIMDB.setModel(self._imdb_history_model)
        self.ui.uploadIMDB.currentIndexChanged.connect(self.on_upload_data_changed)

        self.ui.uploadReleaseText.textChanged.connect(self.on_upload_data_changed)

        self.on_reset()
        self.retranslate()

    def retranslate(self):
        self.ui.uploadLanguages.set_unknown_text(_('Unknown'))
        self.ui.uploadView.retranslate()

    @pyqtSlot()
    def on_interface_language_changed(self):
        self.ui.retranslateUi(self)
        self.retranslate()

    def update_buttons(self):
        selected = self.ui.uploadView.selectionModel().selectedRows()
        if len(selected) == 0:
            self.ui.buttonUploadDownRow.setEnabled(False)
            self.ui.buttonUploadUpRow.setEnabled(False)
            self.ui.buttonUploadMinusRow.setEnabled(False)
        else:
            rows = [s.row() for s in selected]
            min_selected = min(rows)
            max_selected = max(rows)
            self.ui.buttonUploadDownRow.setEnabled(max_selected < len(self.ui.uploadView.get_data_collection()) - 1)
            self.ui.buttonUploadUpRow.setEnabled(min_selected > 0)
            self.ui.buttonUploadMinusRow.setEnabled(True)

    @pyqtSlot()
    def on_upload_data_changed(self):
        self.update_buttons()

        # FIXME: move to UploadDataCollection or more general place
        data = self.ui.uploadView.get_data_collection()

        for identificator in identificators_get():
            videos_to_identify = []
            for video in data.iter_videos():
                if identificator in video.get_identities():
                    continue
                videos_to_identify.append(video)
            identificator.identify_videos(videos_to_identify)

        # merged_identity = ProviderIdentities()
        # for video in data.iter_videos():
        #     merged_identity.merge(video.get_identities())
        # self.on_imdb_selected.emit(merged_identity)

        if self._default_language_selected or self.ui.uploadLanguages.get_selected_language().is_generic():
            language_nb = {}
            for subtitle in data.iter_subtitles():
                lang = subtitle.get_language()
                if not lang.is_generic():
                    language_nb[lang] = language_nb.get(lang, 0) + 1
                    continue

                lang = language.Language.from_file(subtitle.get_filepath())
                if not lang.is_generic():
                    subtitle.set_language(lang)
                    language_nb[lang] = language_nb.get(lang, 0) + 1
            try:
                lang_popular, lang_nb = max(language_nb.items(), key=lambda x: x[1])
            except ValueError:
                lang_popular = self.get_default_upload_language()
            self.ui.uploadLanguages.set_selected_language(lang_popular)

        self.ui.buttonUpload.setEnabled(self.can_upload())

    @pyqtSlot()
    def on_selection_change(self):
        self.update_buttons()

    @pyqtSlot(language.Language)
    def on_default_upload_language_change(self, upload_language):
        if self._default_language_selected:
            self.ui.uploadLanguages.set_selected_language(upload_language)
            self._default_language_selected = True

    @pyqtSlot()
    def on_reset(self):
        default_upload_language = self.get_default_upload_language()
        self.ui.uploadLanguages.set_selected_language(default_upload_language)
        self._default_language_selected = True

        self.ui.uploadIMDB.setCurrentIndex(0)

        self.ui.uploadReleaseText.clear()
        self.ui.uploadComments.clear()

    @pyqtSlot(language.Language)
    def on_upload_language_change(self, lang):
        self._default_language_selected = lang.is_generic()

    def get_default_upload_language(self):
        # FIXME: move to generalized position
        settings = QSettings()
        upload_language = language.Language.from_xxx(
            settings.value('options/uploadLanguage', PreferencesDialog.DEFAULT_UL_LANG))
        return upload_language

    @pyqtSlot()
    def on_find_imdb(self):
        imdb_dialog = ImdbSearchDialog(self)
        imdb_dialog.identity_selected.connect(self.on_imdb_selected)
        imdb_dialog.exec_()

    @pyqtSlot(ProviderIdentities)
    def on_imdb_selected(self, identity):
        if identity is None:
            return
        index_identity = self._imdb_history_model.add_identity(identity)
        self.ui.uploadIMDB.setCurrentIndex(index_identity)

    def get_selected_imdb_identity(self):
        index_identity = self.ui.uploadIMDB.currentIndex()
        return self._imdb_history_model.index_to_identity(index_identity)

    def can_upload(self):
        if not self._state.connected():
            return False
        if not self.ui.uploadReleaseText.text().strip():
            return False
        if self.get_selected_imdb_identity() is None:
            return False
        data_collection = self.ui.uploadView.get_data_collection()
        if not data_collection.is_valid():
            return False
        return True

    @pyqtSlot()
    def on_upload(self):
        local_movie = LocalMovie()

        identity = self.get_selected_imdb_identity()
        local_movie.set_movie_name(identity.video_identity.get_name())
        local_movie.set_imdb_id(identity.imdb_identity.get_imdb_id())
        local_movie.set_release_name(self.ui.uploadReleaseText.text())
        local_movie.set_comments(self.ui.uploadComments.toPlainText())

        data = self.ui.uploadView.get_data_collection()
        for video, subtitle in zip(data.iter_videos(), data.iter_subtitles()):
            local_movie.add_video_subtitle(video, subtitle)
        success = self.get_state().upload(local_movie)
        if success:
            QMessageBox.information(self, _('Upload succeeded'), _('The upload was successful.'))
            self.on_reset()
        else:
            QMessageBox.warning(self, _('Upload failed'), _('The upload failed.'))


class ImdbHistoryModel(QAbstractListModel):
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self._item_identities = []
        self.read_settings()

    def set_imdb_data(self, imdb_data):
        self.beginResetModel()
        self._item_identities = [data for data in imdb_data]
        self.endResetModel()

    def rowCount(self, parent=None):
        return 1 + len(self._item_identities)

    def data(self, index, role=None):
        row, col = index.row(), index.column()
        if role == Qt.DisplayRole:
            if row is 0:
                return _('Click on the "Find" button to identify the movie')

            row -= 1

            provider_identity = self._item_identities[row]

            imdb_identity = provider_identity.imdb_identity
            imdb_id = imdb_identity.get_imdb_id()

            video_identity = provider_identity.video_identity
            name = video_identity.get_name()

            return '{imdb_id} : {name}'.format(imdb_id=imdb_id, name=name)

        return None

    MAX_IMDB_HISTORY = 20

    def add_identity(self, new_identity):
        new_imdb_id = new_identity.imdb_identity.get_imdb_id()
        parent = QModelIndex()
        for identity_i, identity in enumerate(self._item_identities):
            imdb_id = identity.imdb_identity.get_imdb_id()
            if new_imdb_id == imdb_id:
                move_valid = self.beginMoveRows(parent, identity_i, identity_i, parent, 0)
                if not move_valid:
                    return 1
                del self._item_identities[identity_i]
                self._item_identities.insert(0, identity)
                self.endMoveRows()
                self.write_settings()
                return 1
        identities = [new_identity]
        identities.extend(self._item_identities)
        self.beginInsertRows(parent, 0, 0)
        self._item_identities.insert(0, new_identity)
        self.endInsertRows()
        if len(self._item_identities) > self.MAX_IMDB_HISTORY:
            self.beginRemoveRows(parent, self.MAX_IMDB_HISTORY, len(self._item_identities))
            del self._item_identities[self.MAX_IMDB_HISTORY:]
            self.endRemoveRows()

        self.write_settings()
        return 1

    def read_settings(self):
        identities = []
        settings = QSettings()
        size = settings.beginReadArray('upload/imdbHistory')
        for identity_i in range(size):
            settings.setArrayIndex(identity_i)
            imdb_id = settings.value('imdbId')
            imdb_identity = ImdbIdentity(imdb_id=imdb_id, imdb_rating=None)
            name = settings.value('title')
            video_identity = VideoIdentity(name=name, year=None)
            identities.append(ProviderIdentities(video_identity=video_identity, imdb_identity=imdb_identity,
                                                 provider=self))
        settings.endArray()

        self.set_imdb_data(identities)

    def write_settings(self):
        settings = QSettings()
        settings.beginWriteArray('upload/imdbHistory', size=len(self._item_identities))
        settings.setValue("imdbId", id)
        for identity_i, identity in enumerate(self._item_identities):
            settings.setArrayIndex(identity_i)
            imdb_identity = identity.imdb_identity
            settings.setValue('imdbId', imdb_identity.get_imdb_id())
            video_identity = identity.video_identity
            settings.setValue('title', video_identity.get_name())
        settings.endArray()

    def index_to_identity(self, index):
        if index == 0:
            return None
        return self._item_identities[index - 1]
