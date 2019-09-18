# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
from pathlib import Path
import platform
import webbrowser

from subdownloader.client.state import SubtitlePathStrategy, SubtitleNamingStrategy
from subdownloader.client.player import VideoPlayer
from subdownloader.client.gui.generated.preferences_ui import Ui_PreferencesDialog
from subdownloader.languages.language import all_languages, Language, UnknownLanguage
from subdownloader.project import WEBSITE_TRANSLATE
from subdownloader.provider.provider import ProviderSettingsType

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QDir
from PyQt5.QtWidgets import QCheckBox, QCompleter, QDialog, QDirModel, QFileDialog, QFormLayout, QLineEdit, \
    QMessageBox, QWidget

log = logging.getLogger("subdownloader.client.gui.preferences")
# FIXME: add more logging


class PreferencesDialog(QDialog):

    def __init__(self, parent, state, settings):
        QDialog.__init__(self, parent)

        self._state = state
        self._settings = settings

        self._uploadLanguage = UnknownLanguage.create_generic()

        self.providers_ui = dict()

        self.ui = Ui_PreferencesDialog()
        self.setup_ui()

    def setup_ui(self):
        self.ui.setupUi(self)

        # 0. Dialog

        self.ui.buttonApplyChanges.clicked.connect(
            self.onApplyChanges)
        self.ui.buttonCancel.clicked.connect(
            self.onCancel)
        self.ui.tabsPreferences.setCurrentIndex(0)

        # 1. Search tab

        # - Filter languages

        self._filterLanguageComboBoxes = {}

        self._search_languages = {lang: False for lang in all_languages()}
        nb_columns_languages = 4
        for lang_i, lang in enumerate(all_languages()):
            row = lang_i // nb_columns_languages
            column = lang_i % nb_columns_languages

            checkBox = QCheckBox(_(lang.generic_name()), self.ui.scrollAreaWidgetSearch)

            def createSearchLangSlot(lang):
                @pyqtSlot(bool)
                def onSearchLangCheckBoxToggled(toggled):
                    self.searchLanguageChanged.emit(lang, toggled)
                return onSearchLangCheckBoxToggled

            checkBox.toggled.connect(createSearchLangSlot(lang))
            checkBox.setChecked(self._search_languages[lang])

            self._filterLanguageComboBoxes[lang] = checkBox
            self.ui.scrollAreaWidgetLayoutSearch.addWidget(checkBox, row, column)

        self.searchLanguageChanged.connect(self.onSearchLanguageChanged)
        fontSearchItem = self._filterLanguageComboBoxes[UnknownLanguage.create_generic()].font()
        fontSearchItem.setItalic(True)
        self._filterLanguageComboBoxes[UnknownLanguage.create_generic()].setFont(fontSearchItem)

        # 2. Download tab

        # - Download Destination

        self._dlDestinationType = self.DEFAULT_DLDESTINATIONTYPE

        def create_dlDestinationTypeChangedSlot(dlDestinationType):
            @pyqtSlot(bool)
            def dlDestinationTypeChanged(toggled):
                if toggled:
                    self.dlDestinationTypeChanged.emit(dlDestinationType)
            return dlDestinationTypeChanged

        self.ui.optionDlDestinationAsk.toggled.connect(
            create_dlDestinationTypeChangedSlot(SubtitlePathStrategy.ASK))
        self.ui.optionDlDestinationSame.toggled.connect(
            create_dlDestinationTypeChangedSlot(SubtitlePathStrategy.SAME))
        self.ui.optionDlDestinationUser.toggled.connect(
            create_dlDestinationTypeChangedSlot(SubtitlePathStrategy.PREDEFINED))

        self.dlDestinationTypeChanged.connect(self.onDlDestinationTypeChange)

        self.ui.optionDlDestinationUser.toggled.connect(
            self.ui.inputDlDestinationUser.setEnabled)
        self.ui.optionDlDestinationUser.toggled.connect(
            self.ui.buttonDlDestinationUser.setEnabled)
        self.ui.optionDlDestinationUser.toggled.emit(False)

        # Always contains a valid download destination folder
        self._dlDestinationPredefined = Path()

        dlDestinationCompleter = QCompleter()
        dlDestinationCompleter.setModel(QDirModel([], QDir.Dirs | QDir.NoDotAndDotDot, QDir.Name, dlDestinationCompleter))
        self.ui.inputDlDestinationUser.setCompleter(dlDestinationCompleter)
        self.ui.inputDlDestinationUser.editingFinished.connect(
            self.onInputDlDestinationEditingFinished)

        self.ui.buttonDlDestinationUser.clicked.connect(
            self.onButtonDlDestinationClicked)

        # - Subtitle Filename

        self._subtitleFilename = self.DEFAULT_DLSUBFN

        def create_dlSubtitleFileNameChangedSlot(subtitleFilename):
            @pyqtSlot(bool)
            def subtitleFileNameChanged(toggled):
                if toggled:
                    self.subtitleFilenameChanged.emit(subtitleFilename)
            return subtitleFileNameChanged

        self.ui.optionSubFnSame.toggled.connect(
            create_dlSubtitleFileNameChangedSlot(SubtitleNamingStrategy.VIDEO))
        self.ui.optionSubFnSameLang.toggled.connect(
            create_dlSubtitleFileNameChangedSlot(SubtitleNamingStrategy.VIDEO_LANG))
        self.ui.optionSubFnSameLangUploader.toggled.connect(
            create_dlSubtitleFileNameChangedSlot(SubtitleNamingStrategy.VIDEO_LANG_UPLOADER))
        self.ui.optionSubFnOnline.toggled.connect(
            create_dlSubtitleFileNameChangedSlot(SubtitleNamingStrategy.ONLINE))

        self.subtitleFilenameChanged.connect(self.onSubtitleFilenameChange)

        # 3. Upload tab

        # - Default Subtitle Language

        self._uploadLanguage = self.DEFAULT_UL_LANG

        self.ui.optionUlDefaultLanguage.set_unknown_text(_('Auto Detect'))
        self.ui.optionUlDefaultLanguage.set_selected_language(self._uploadLanguage)

        self.ui.optionUlDefaultLanguage.selected_language_changed.connect(self.onOptionUlDefaultLanguageChange)

        # 4. Providers tab

        for provider in self._state.providers.iter():
            provider_name = provider.get_name()
            self.ui.providerComboBox.addItem(provider_name, provider)
            providerWidget = QWidget()
            providerLayout = QFormLayout()
            ui_items = {
                '_enabled': QCheckBox(),
            }
            providerLayout.addRow(_('enabled').capitalize(), ui_items['_enabled'])

            for key, key_type in provider.get_settings().key_types().items():
                if key_type == ProviderSettingsType.String:
                    widget = QLineEdit()
                elif key_type == ProviderSettingsType.Password:
                    widget = QLineEdit()
                    widget.setEchoMode(QLineEdit.Password)
                else:
                    # FIXME: generalize this warning about possible warnings?
                    log.error('Unknown provider settings type: {}: {} -> {}'.format(provider_name, key, key_type))
                    QMessageBox.warning(self, _('Unknown provider settings type'),
                                        '\n'.join((_('An unknown settings type has been passed.'),
                                                   _('Please open an issue'))))
                    continue
                providerLayout.addRow(key.capitalize(), widget)
                ui_items[provider_name] = widget
            providerWidget.setLayout(providerLayout)
            self.ui.providerStack.addWidget(providerWidget)
            self.providers_ui[provider_name] = ui_items

        # 5. Others tab

        # - Interface Language

        self._original_interface_language = UnknownLanguage.create_generic()
        self.ui.optionInterfaceLanguage.set_unknown_text(_('System Language'))
        self.ui.optionUlDefaultLanguage.set_selected_language(self._original_interface_language)

        # - Video Application Location

        self.ui.buttonVideoAppLocationChoose.clicked.connect(
            self.onButtonVideoAppLocationChoose)
        self.ui.buttonHelpTranslation.clicked.connect(
            self.onHelpTranslate)

        self.readSettings()

    def readSettings(self):
        log.debug('readSettings: start')

        # 1. Search tab
        checked_languages = self._state.get_download_languages()
        for checked_language in checked_languages:
            self._filterLanguageComboBoxes[checked_language].setChecked(True)

        # 2. Download tab

        # - Download Destination

        optionWhereToDownload = self._state.get_subtitle_download_path_strategy()
        if optionWhereToDownload == SubtitlePathStrategy.ASK:
            self.ui.optionDlDestinationAsk.setChecked(True)
        elif optionWhereToDownload == SubtitlePathStrategy.SAME:
            self.ui.optionDlDestinationSame.setChecked(True)
        elif optionWhereToDownload == SubtitlePathStrategy.PREDEFINED:
            self.ui.optionDlDestinationUser.setChecked(True)

        dlDestination = self._state.get_default_download_path()
        self.ui.inputDlDestinationUser.setText(str(dlDestination))
        self.ui.inputDlDestinationUser.editingFinished.emit()

        # - Subtitle Filename

        optionSubtitleName = self._state.get_subtitle_naming_strategy()
        if optionSubtitleName == SubtitleNamingStrategy.VIDEO:
            self.ui.optionSubFnSame.setChecked(True)
        elif optionSubtitleName == SubtitleNamingStrategy.VIDEO_LANG:
            self.ui.optionSubFnSameLang.setChecked(True)
        elif optionSubtitleName == SubtitleNamingStrategy.VIDEO_LANG_UPLOADER:
            self.ui.optionSubFnSameLangUploader.setChecked(True)
        elif optionSubtitleName == SubtitleNamingStrategy.ONLINE:
            self.ui.optionSubFnOnline.setChecked(True)

        # 3. Upload tab

        # - Default Subtitle Language

        self._uploadLanguage = self._state.get_upload_language()
        self._originalUploadLanguage = self._uploadLanguage
        self.ui.optionUlDefaultLanguage.set_selected_language(self._uploadLanguage)

        # 4. Providers' tab
        for provider in self._state.providers.iter():
            # FIXME: read providers data
            pass

        # 5. Others tab

        # - Interface Language

        optionInterfaceLanguage = self._state.get_interface_language()
        self._original_interface_language = optionInterfaceLanguage
        self.ui.optionInterfaceLanguage.set_selected_language(optionInterfaceLanguage)

        playerPath = self._state.get_videoplayer().get_path()
        playerParams = self._state.get_videoplayer().get_command()
        self.ui.inputVideoAppLocation.setText(str(playerPath))
        self.ui.inputVideoAppParams.setText(playerParams)

        log.debug('readSettings: finish')

    @pyqtSlot()
    def saveSettings(self):
        log.debug('saveSettings: start')

        # 1. Search tab

        checked_languages = [lang[0] for lang in filter(lambda x:x[1], self._search_languages.items())]
        self._state.set_download_languages(checked_languages)

        # 2. Downloads tab

        # - Download Destination

        self._state.set_subtitle_download_path_strategy(self._dlDestinationType)
        self._state.set_default_download_path(self._dlDestinationPredefined)

        # - Subtitle Filename

        self._state.set_subtitle_naming_strategy(self._subtitleFilename)

        # 3. Upload tab

        # - Default Subtitle Language

        self._state.set_upload_language(self._uploadLanguage)
        if self._uploadLanguage != self._originalUploadLanguage:
            self.defaultUploadLanguageChanged.emit(self._uploadLanguage)

        # 4. Providers' tab
        for provider in self._state.providers.iter():
            # FIXME: write providers data
            pass

        # 5. Others tab

        # - Interface Language

        new_interface_language = self.ui.optionInterfaceLanguage.get_selected_language()
        self._state.set_interface_language(new_interface_language)
        if self._original_interface_language != new_interface_language:
            self._state.signals.interface_language_changed.emit(new_interface_language)

        # - video player

        playerPath = Path(self.ui.inputVideoAppLocation.text())
        playerParams = self.ui.inputVideoAppParams.text()
        videoPlayer = VideoPlayer(playerPath, playerParams)
        self._state.set_videoplayer(videoPlayer)

        # Finally, write to disk

        self._state.save_settings(self._settings)
        log.debug('saveSettings: finish')

    # 0. Interface

    def validate(self):
        # Download Destination Validation
        dlDestinationUser = self.ui.inputDlDestinationUser.text()
        if self._dlDestinationType == SubtitlePathStrategy.PREDEFINED and not os.path.isdir(dlDestinationUser):
            QMessageBox.about(
                self, _("Error"), _("Predefined Folder is invalid"))
            return False
        return True

    @pyqtSlot()
    def onApplyChanges(self):
        if self.validate():
            self.saveSettings()
            self.close()

    @pyqtSlot()
    def onCancel(self):
        self.reject()

    # 1. Search tab

    searchLanguageChanged = pyqtSignal(Language, bool)

    @pyqtSlot(Language, bool)
    def onSearchLanguageChanged(self, lang, toggled):
        self._search_languages[lang] = toggled

    # 2. Downloads tab

    # - Download destination

    dlDestinationTypeChanged = pyqtSignal(SubtitlePathStrategy)
    dlDestinationPredefinedChanged = pyqtSignal(Path)

    DEFAULT_DLDESTINATIONTYPE = SubtitlePathStrategy.SAME

    @pyqtSlot(SubtitlePathStrategy)
    def onDlDestinationTypeChange(self, dlDestinationType):
        self._dlDestinationType = dlDestinationType

    @pyqtSlot()
    def onButtonDlDestinationClicked(self):
        directory = QFileDialog.getExistingDirectory(self, _("Select a directory"), str(self._dlDestinationPredefined))
        if not directory:
            # Cancelled
            return
        if os.path.isdir(directory):
            self.ui.inputDlDestinationUser.setText(directory)
            self._dlDestinationPredefined = Path(directory)
            self.dlDestinationPredefinedChanged.emit(self._dlDestinationPredefined)
        else:
            QMessageBox.warning(self, _('Not a directory'), _('"{path}" is not a directory').format(path=directory))

    @pyqtSlot()
    def onInputDlDestinationEditingFinished(self):
        path = self.ui.inputDlDestinationUser.text()
        if os.path.isdir(path):
            self._dlDestinationPredefined = Path(path)

    def getDownloadDestinationPredefined(self):
        return self._dlDestinationPredefined

    # - Subtitle Filename

    subtitleFilenameChanged = pyqtSignal(SubtitleNamingStrategy)

    DEFAULT_DLSUBFN = SubtitleNamingStrategy.VIDEO

    def onSubtitleFilenameChange(self, subtitleFilename):
        self._subtitleFilename = subtitleFilename

    # 3. Upload tab

    # - Default Subtitle Language

    defaultUploadLanguageChanged = pyqtSignal(Language)

    DEFAULT_UL_LANG = UnknownLanguage.create_generic()

    @pyqtSlot(Language)
    def onOptionUlDefaultLanguageChange(self, lang):
        self._uploadLanguage = lang

    # 5. Others tab

    interfaceLanguageChange = pyqtSignal(Language)

    def actionContextMenu(self, action, os):
        pass

    @pyqtSlot()
    def onHelpTranslate(self):
        webbrowser.open(WEBSITE_TRANSLATE, new=2, autoraise=1)

    @pyqtSlot()
    def onButtonVideoAppLocationChoose(self):
        extensions = ""
        if platform.system == "Windows":
            extensions = "*.exe"

        fileName, t = QFileDialog.getOpenFileName(
            self, _("Select the Video Player executable file"), "", extensions)
        if fileName:
            self.ui.inputVideoAppLocation.setText(fileName)
