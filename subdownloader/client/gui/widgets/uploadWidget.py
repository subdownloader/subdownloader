# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging
from typing import Optional, Sequence

from PyQt5.QtCore import pyqtSlot, QAbstractListModel, QModelIndex, QObject, QSettings, Qt
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QMessageBox, QWidget

from subdownloader.identification import ImdbIdentity, VideoIdentity, ProviderIdentities, identificators_get
from subdownloader.languages import language
from subdownloader.movie import LocalMovie, VideoSubtitle
from subdownloader.provider.imdb import ImdbMovieMatch, ImdbHistory

from subdownloader.client.gui.widgets.imdbSearch import ImdbSearchDialog
from subdownloader.client.gui.widgets.preferences import PreferencesDialog
from subdownloader.client.gui.generated.uploadWidget_ui import Ui_UploadWidget

log = logging.getLogger('subdownloader.client.gui.widgets.uploadWidget')


class UploadWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self._state = None

        self._imdb_history_model = ImdbHistoryModel()
        self._upload_movie = LocalMovie()

        self.ui = Ui_UploadWidget()
        self.setup_ui()

    def set_state(self, state):
        self._state = state
        self._state.signals.interface_language_changed.connect(self.on_interface_language_changed)

        self._state.signals.login_status_changed.connect(self.on_login_status_changed)

        self.ui.comboProvider.set_state(self._state)
        self.ui.uploadView.set_local_movie(self._upload_movie)
        self._imdb_history_model.set_state(self._state)
        self.ui.uploadIMDB.setCurrentIndex(0)

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
        self.ui.uploadIMDB.currentIndexChanged.connect(self.onImdbComboIndexChanged)

        self.ui.uploadReleaseText.textChanged.connect(self.onReleaseNameChange)
        self.ui.uploadComments.textChanged.connect(self.onCommentsChange)
        self.ui.uploadTranslator.textChanged.connect(self.onTranslatorChange)

        self.ui.comboProvider.set_general_visible(True)
        self.ui.comboProvider.set_filter_enable(True)
        self.ui.comboProvider.selected_provider_state_changed.connect(self.onUploadProviderChanged)

        self.ui.comboHighDefinition.stateChanged.connect(self.onHighDefinitionChanged)
        self.ui.comboAutomaticTranslation.stateChanged.connect(self.onAutomaticTranslationChanged)
        self.ui.comboHearingImpaired.stateChanged.connect(self.onHearingImpairedChanged)

        self.on_reset()
        self.retranslate()

    def retranslate(self):
        self.ui.uploadLanguages.set_unknown_text(_('Unknown'))
        self.ui.uploadView.retranslate()

        self.ui.buttonUploadBrowseFolder.setToolTip(_('Load videos and subtitles from directory'))
        self.ui.buttonUploadDeleteAllRow.setToolTip(_('Reset videos and subtitles'))
        self.ui.buttonUploadPlusRow.setToolTip(_('Insert row above selected row'))
        self.ui.buttonUploadMinusRow.setToolTip(_('Remove table'))
        self.ui.buttonUploadUpRow.setToolTip(_('Move selected row up'))
        self.ui.buttonUploadDownRow.setToolTip(_('Move selected row down'))

        self.ui.comboProvider.set_general_text('({})'.format(_('none')))

    @pyqtSlot()
    def on_interface_language_changed(self):
        self.ui.retranslateUi(self)
        self.retranslate()

    def update_navigation_buttons(self):
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
    def on_login_status_changed(self):
        self.check_enable_upload_button()

    @pyqtSlot()
    def on_upload_data_changed(self):
        self.update_navigation_buttons()

        # FIXME: move to UploadDataCollection or more general place
        data_collection = self.ui.uploadView.get_data_collection()

        for identificator in identificators_get():
            videos_to_identify = []
            for video in data_collection.iter_videos():
                if identificator in video.get_identities():
                    continue
                videos_to_identify.append(video)
            identificator.identify_videos(videos_to_identify)

        if self.ui.uploadLanguages.get_selected_language().is_generic():
            language_nb = {}
            for subtitle in data_collection.iter_subtitles():
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

        self.check_enable_upload_button()

    def check_enable_upload_button(self):
        data_ok = self._upload_movie.check()
        providerState = self.ui.comboProvider.get_selected_provider_state()
        provider_ok = providerState is not None
        self.ui.buttonUpload.setEnabled(data_ok and provider_ok)

    @pyqtSlot()
    def on_selection_change(self):
        self.update_navigation_buttons()

    @pyqtSlot()
    def on_reset(self):
        self._upload_movie = LocalMovie()
        self.ui.uploadView.set_local_movie(self._upload_movie)
        self._upload_movie.set_data([VideoSubtitle() for _ in range(2)])

        self.ui.uploadReleaseText.clear()
        self.ui.uploadIMDB.setCurrentIndex(0)

        default_upload_language = self.get_default_upload_language()
        self.ui.uploadLanguages.set_selected_language(default_upload_language)
        self._upload_movie.set_language(self.ui.uploadLanguages.get_selected_language())

        self.ui.comboHighDefinition.setChecked(True if self._upload_movie.is_high_definition() else False)
        self.ui.comboHearingImpaired.setChecked(True if self._upload_movie.is_hearing_impaired() else False)
        self.ui.comboAutomaticTranslation.setChecked(True if self._upload_movie.is_automatic_translation() else False)

        self.ui.uploadTranslator.clear()
        self.ui.uploadComments.clear()
        self.ui.comboProvider.set_selected_provider(None)

        self.ui.uploadView.on_reset()

    @pyqtSlot(language.Language)
    def on_upload_language_change(self, language) -> None:
        self._upload_movie.set_language(language)
        self.check_enable_upload_button()
        # new_language = None
        # if lang.is_generic():
        #     self._default_language_selected = True
        #     default_upload_language = self._state.get_upload_language()
        #     if not default_upload_language.is_generic():
        #         new_language = default_upload_language
        # else:
        #     self._default_language_selected = False
        #     new_language = lang
        # if new_language:
        #     self._upload_movie.set_language(new_language)

    def get_default_upload_language(self):
        # FIXME: move to generalized position
        settings = QSettings()
        upload_language = language.Language.from_xxx(
            settings.value('options/uploadLanguage', PreferencesDialog.DEFAULT_UL_LANG))
        return upload_language

    @pyqtSlot()
    def on_find_imdb(self):
        imdb_dialog = ImdbSearchDialog(self)
        imdb_dialog.set_state(self._state)
        imdb_dialog.identity_selected.connect(self.on_imdb_selected)
        imdb_dialog.exec_()

    @pyqtSlot(ProviderIdentities)
    def on_imdb_selected(self, identity):
        if identity is None:
            return
        index_identity = self._imdb_history_model.add_imdb(identity)
        self.ui.uploadIMDB.setCurrentIndex(index_identity)

    def get_selected_imdb_identity(self):
        index_identity = self.ui.uploadIMDB.currentIndex()
        return self._imdb_history_model.index_to_identity(index_identity)

    @pyqtSlot(str)
    def onReleaseNameChange(self, name: str) -> None:
        self._upload_movie.set_release_name(name)
        self.check_enable_upload_button()

    @pyqtSlot(str)
    def onTranslatorChange(self, name: str) -> None:
        self._upload_movie.set_author(name)
        self.check_enable_upload_button()

    @pyqtSlot()
    def onCommentsChange(self) -> None:
        comments = self.ui.uploadComments.toPlainText()
        self._upload_movie.set_comments(comments)
        self.check_enable_upload_button()

    @pyqtSlot(int)
    def onImdbComboIndexChanged(self, index: int):
        imdb = self._imdb_history_model.index_to_identity(index)
        if imdb is None:
            imdb_id = None
            title = None
        else:
            imdb_id = imdb.imdb_id
            title = imdb.title
        self._upload_movie.set_imdb_id(imdb_id)
        self._upload_movie.set_movie_name(title)
        self.check_enable_upload_button()

    @pyqtSlot(int)
    def onHighDefinitionChanged(self, state: int) -> None:
        self._upload_movie.set_high_definition(state == Qt.Checked)
        self.check_enable_upload_button()

    @pyqtSlot(int)
    def onAutomaticTranslationChanged(self, state: int) -> None:
        self._upload_movie.set_automatic_translation(state == Qt.Checked)
        self.check_enable_upload_button()

    @pyqtSlot(int)
    def onHearingImpairedChanged(self, state: int) -> None:
        self._upload_movie.set_hearing_impaired(state == Qt.Checked)
        self.check_enable_upload_button()

    def onUploadProviderChanged(self) -> None:
        self.check_enable_upload_button()

    @pyqtSlot()
    def on_upload(self):
        providerState = self.ui.comboProvider.get_selected_provider_state()
        if providerState is None:
            QMessageBox.warning(self, _('Cannot upload'), _('No provider was selected.'))
            return

        upload_result = providerState.provider.upload_subtitles(self._upload_movie)
        if upload_result.ok:
            QMessageBox.information(self, _('Upload succeeded'), _('The upload was successful.'))
            self.ui.comboProvider.set_selected_provider(None)
        else:
            QMessageBox.warning(self, _('Upload failed'), '{}\n{}'.format(
                _('The upload failed.'), upload_result.reason))


class ImdbHistoryModel(QAbstractListModel):
    def __init__(self, parent: QObject=None):
        QAbstractListModel.__init__(self, parent)
        self._imdb_history = ImdbHistory()

    def rowCount(self, parent: QModelIndex=None) -> int:
        return 1 + len(self._imdb_history)

    def data(self, index: QModelIndex, role: int=None) -> Optional[str]:
        row, col = index.row(), index.column()
        if role == Qt.DisplayRole:
            if row == 0:
                return _('Click on the "Find" button to identify the movie')

            row -= 1

            imdb = self._imdb_history[row]
            return '{} : {}'.format(imdb.imdb_id, imdb.title_year)

        return None

    MAX_IMDB_HISTORY = 20

    def add_imdb(self, new_imdb: ImdbMovieMatch) -> int:
        self.beginResetModel()
        index = self._imdb_history.insert_unique(0, new_imdb)
        self.endResetModel()
        self._imdb_history.limit(self.MAX_IMDB_HISTORY)
        return 1 + index

    def set_state(self, state) -> None:
        self.beginResetModel()
        self._imdb_history = state.get_imdb_history()
        self.endResetModel()

    def index_to_identity(self, index: int) -> Optional[ImdbMovieMatch]:
        if index <= 0:
            return None
        return self._imdb_history[index - 1]
