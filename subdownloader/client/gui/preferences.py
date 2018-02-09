# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
import platform
import webbrowser

from subdownloader.client.gui.generated.preferences_ui import Ui_PreferencesDialog
from subdownloader.languages.language import all_languages, Language, UnknownLanguage
from subdownloader.project import WEBSITE_TRANSLATE

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QDir, QSettings
from PyQt5.QtWidgets import QCheckBox, QCompleter, QDialog, QDirModel, QFileDialog, QMessageBox

log = logging.getLogger("subdownloader.client.gui.preferences")
# FIXME: add more logging


class PreferencesDialog(QDialog):

    def __init__(self, parent, state):
        QDialog.__init__(self, parent)

        self._state = state

        self._uploadLanguage = UnknownLanguage.create_generic()

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
            create_dlDestinationTypeChangedSlot(self.DLDESTINATIONTYPE_ASKUSER))
        self.ui.optionDlDestinationSame.toggled.connect(
            create_dlDestinationTypeChangedSlot(self.DLDESTINATIONTYPE_SAMEFOLDER))
        self.ui.optionDlDestinationUser.toggled.connect(
            create_dlDestinationTypeChangedSlot(self.DLDESTINATIONTYPE_PREDEFINEDFOLDER))

        self.dlDestinationTypeChanged.connect(self.onDlDestinationTypeChange)

        self.ui.optionDlDestinationUser.toggled.connect(
            self.ui.inputDlDestinationUser.setEnabled)
        self.ui.optionDlDestinationUser.toggled.connect(
            self.ui.buttonDlDestinationUser.setEnabled)
        self.ui.optionDlDestinationUser.toggled.emit(False)

        # Always contains a valid download destination folder
        self._dlDestinationPredefined = '' # FIXME: good default (USER HOME? USER DOWNLOADS?)

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
            create_dlSubtitleFileNameChangedSlot(self.DLSUBFN_SAME))
        self.ui.optionSubFnSameLang.toggled.connect(
            create_dlSubtitleFileNameChangedSlot(self.DLSUBFN_SAMELANG))
        self.ui.optionSubFnSameLangUploader.toggled.connect(
            create_dlSubtitleFileNameChangedSlot(self.DLSUBFN_SAMELANGUPLOADER))
        self.ui.optionSubFnOnline.toggled.connect(
            create_dlSubtitleFileNameChangedSlot(self.DLSUBFN_ONLINE))

        self.subtitleFilenameChanged.connect(self.onSubtitleFilenameChange)

        # 3. Upload tab

        # - Default Subtitle Language

        self._uploadLanguage = self.DEFAULT_UL_LANG

        self.ui.optionUlDefaultLanguage.set_unknown_text(_('Auto Detect'))
        self.ui.optionUlDefaultLanguage.set_selected_language(self._uploadLanguage)

        self.ui.optionUlDefaultLanguage.selected_language_changed.connect(self.onOptionUlDefaultLanguageChange)

        # 4. Network tab

        self.ui.inputProxyPort.setRange(0, 65535)

        # 5. Others tab

        # - Interface Language

        self._original_interface_language = UnknownLanguage.create_generic()
        self.ui.optionInterfaceLanguage.set_unknown_text(_('System Language'))
        self.ui.optionUlDefaultLanguage.set_selected_language(self.DEFAULT_INTERFACE_LANG)

        # - Video Application Location

        self.ui.buttonVideoAppLocationChoose.clicked.connect(
            self.onButtonVideoAppLocationChoose)
        self.ui.buttonHelpTranslation.clicked.connect(
            self.onHelpTranslate)

        self.settings = QSettings()  # FIXME: use config path

        self.readSettings()

    def readSettings(self):
        log.debug('readSettings: start')
        self.settings.sync()

        # 1. Search tab
        checked_languages_str = self.settings.value('options/filterSearchLang', [])
        if checked_languages_str:
            for lang_xxx in checked_languages_str.split(','):
                lang = Language.from_xxx(lang_xxx)
                if isinstance(lang, UnknownLanguage):
                    continue
                self._filterLanguageComboBoxes[lang].setChecked(True)

        # 2. Download tab

        # - Download Destination

        optionWhereToDownload = self.settings.value('options/whereToDownload', self.DLDESTINATIONTYPE_SAMEFOLDER)
        if optionWhereToDownload == self.DLDESTINATIONTYPE_ASKUSER:
            self.ui.optionDlDestinationAsk.setChecked(True)
        elif optionWhereToDownload == self.DLDESTINATIONTYPE_SAMEFOLDER:
            self.ui.optionDlDestinationSame.setChecked(True)
        elif optionWhereToDownload == self.DLDESTINATIONTYPE_PREDEFINEDFOLDER:
            self.ui.optionDlDestinationUser.setChecked(True)

        dlDestination = self.settings.value('options/whereToDownloadFolder', '')
        #self._dlDestinationPredefined = dlDestination if os.path.isdir(dlDestination) else ''
        self.ui.inputDlDestinationUser.setText(dlDestination)
        self.ui.inputDlDestinationUser.editingFinished.emit()

        # - Subtitle Filename

        optionSubtitleName = self.settings.value('options/subtitleName', self.DLSUBFN_SAME)
        if optionSubtitleName == self.DLSUBFN_SAME:
            self.ui.optionSubFnSame.setChecked(True)
        elif optionSubtitleName == self.DLSUBFN_SAMELANG:
            self.ui.optionSubFnSameLang.setChecked(True)
        elif optionSubtitleName == self.DLSUBFN_SAMELANGUPLOADER:
            self.ui.optionSubFnSameLangUploader.setChecked(True)
        elif optionSubtitleName == self.DLSUBFN_ONLINE:
            self.ui.optionSubFnOnline.setChecked(True)

        # 3. Upload tab

        # - Default Subtitle Language

        optionUploadLanguage = self.settings.value('options/uploadLanguage', self.DEFAULT_UL_LANG.xxx())
        self._uploadLanguage = Language.from_xxx(optionUploadLanguage)

        self.ui.optionUlDefaultLanguage.set_selected_language(self._uploadLanguage)

        # 4. Network tab

        self.ui.inputProxyHost.setText(
            self.settings.value("options/ProxyHost", ""))
        self.ui.inputProxyPort.setValue(int(
            self.settings.value("options/ProxyPort", 8080)))

        # 5. Others tab

        # - Interface Language

        optionInterfaceLanguage = self.settings.value('options/interfaceLang', self.DEFAULT_INTERFACE_LANG.locale())
        self._original_interface_language = Language.from_locale(optionInterfaceLanguage)
        self.ui.optionInterfaceLanguage.set_selected_language(self._original_interface_language)

        optionIntegrationExplorer = self.settings.value(
            "options/IntegrationExplorer", False)
        self.ui.optionIntegrationExplorer.setChecked(optionIntegrationExplorer)

        programPath = self.settings.value("options/VideoPlayerPath", "")
        parameters = self.settings.value("options/VideoPlayerParameters", "")
        self.ui.inputVideoAppLocation.setText(programPath)
        self.ui.inputVideoAppParams.setText(parameters)

        # Context menu for Explorer
        if platform.system() == "Linux":
            self.ui.optionIntegrationExplorer.setText(
                _("Enable in your Konqueror/Dolphin/Nautilus"))
            self.ui.optionIntegrationExplorer.setEnabled(False)
        elif platform.system() == "Windows":
            self.ui.optionIntegrationExplorer.setText(
                _("Enable in your Windows Explorer"))
            self.ui.optionIntegrationExplorer.setEnabled(False)
        else:
            self.ui.optionIntegrationExplorer.setText(
                _("Enable in your File Manager"))
            self.ui.optionIntegrationExplorer.setEnabled(False)

        log.debug('readSettings: finish')

    @pyqtSlot()
    def saveSettings(self):
        log.debug('saveSettings: start')

        # 1. Search tab

        checked_languages = [lang[0] for lang in filter(lambda x:x[1], self._search_languages.items())]
        checked_languages_str = ','.join([lang.xxx() for lang in checked_languages])
        self.settings.setValue("options/filterSearchLang", checked_languages_str)
        self.parent().permanent_language_filter_changed.emit(checked_languages)

        # 2. Downloads tab

        # - Download Destination

        self.settings.setValue('options/whereToDownload', self._dlDestinationType)
        self.settings.setValue('options/whereToDownloadFolder', self._dlDestinationPredefined)

        # - Subtitle Filename

        self.settings.setValue('options/subtitleName', self._subtitleFilename)

        # 3. Upload tab

        # - Default Subtitle Language

        self.settings.setValue('options/uploadLanguage', self._uploadLanguage.xxx())
        self.defaultUploadLanguageChanged.emit(self._uploadLanguage)

        # 5. Others tab

        # - Interface Language

        new_interface_language = self.ui.optionInterfaceLanguage.get_selected_language()
        self.settings.setValue('options/interfaceLang', new_interface_language.locale())
        if self._original_interface_language != new_interface_language:
            self._state.interface_language_changed.emit(new_interface_language)

        # Writing settings

        IEoldValue = self.settings.value(
            "options/IntegrationExplorer", False)
        IEnewValue = self.ui.optionIntegrationExplorer.isChecked()
        if IEoldValue != IEnewValue:
            if IEnewValue:
                log.debug('Installing the Integration Explorer feature')
                ok = self.actionContextMenu("install", platform.system())
            else:
                log.debug('Uninstalling the Integration Explorer feature')
                ok = self.actionContextMenu("uninstall", platform.system())
            if ok:
                self.settings.setValue("options/IntegrationExplorer", IEnewValue)

        newProxyHost = self.ui.inputProxyHost.text()
        newProxyPort = self.ui.inputProxyPort.value()
        oldProxyHost = self.settings.value("options/ProxyHost", "")
        oldProxyPort = int(self.settings.value("options/ProxyPort", 8080))
        if newProxyHost != oldProxyHost or newProxyPort != oldProxyPort:
            self.settings.setValue("options/ProxyHost", newProxyHost)
            self.settings.setValue("options/ProxyPort", newProxyPort)
            QMessageBox.about(self, _("Alert"), _(
                "Modified proxy settings will take effect after restarting the program"))

        programPath = self.ui.inputVideoAppLocation.text()
        parameters = self.ui.inputVideoAppParams.text()
        self.settings.setValue("options/VideoPlayerPath", programPath)
        self.settings.setValue("options/VideoPlayerParameters", parameters)
        self.settings.sync()
        log.debug('saveSettings: finish')

    # 0. Interface

    def validate(self):
        # Download Destination Validation
        dlDestinationUser = self.ui.inputDlDestinationUser.text()
        if self._dlDestinationType == self.DLDESTINATIONTYPE_PREDEFINEDFOLDER and not os.path.isdir(dlDestinationUser):
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

    dlDestinationTypeChanged = pyqtSignal(str)
    dlDestinationPredefinedChanged = pyqtSignal(str)

    DLDESTINATIONTYPE_ASKUSER = 'ASK_FOLDER'
    DLDESTINATIONTYPE_SAMEFOLDER = 'SAME_FOLDER'
    DLDESTINATIONTYPE_PREDEFINEDFOLDER = 'PREDEFINED_FOLDER'

    DEFAULT_DLDESTINATIONTYPE = DLDESTINATIONTYPE_SAMEFOLDER

    @pyqtSlot(str)
    def onDlDestinationTypeChange(self, dlDestinationType):
        self._dlDestinationType = dlDestinationType

    @pyqtSlot()
    def onButtonDlDestinationClicked(self):
        directory = QFileDialog.getExistingDirectory(self, _("Select a directory"), self._dlDestinationPredefined)
        if not directory:
            # Cancelled
            return
        if os.path.isdir(directory):
            self.ui.inputDlDestinationUser.setText(directory)
            self._dlDestinationPredefined = directory
            self.dlDestinationPredefinedChanged.emit(self._dlDestinationPredefined)
        else:
            QMessageBox.warning(self, _('Not a directory'), _('"{path}" is not a directory').format(path=directory))

    @pyqtSlot()
    def onInputDlDestinationEditingFinished(self):
        path = self.ui.inputDlDestinationUser.text()
        if os.path.isdir(path):
            self._dlDestinationPredefined = path

    def getDownloadDestinationPredefined(self):
        return self._dlDestinationPredefined

    # - Subtitle Filename

    subtitleFilenameChanged = pyqtSignal(str)

    DLSUBFN_SAME = 'SAME_VIDEO'
    DLSUBFN_SAMELANG = 'SAME_VIDEOPLUSLANG'
    DLSUBFN_SAMELANGUPLOADER = 'SAME_VIDEOPLUSLANGANDUPLOADER'
    DLSUBFN_ONLINE = 'SAME_ONLINE'

    DEFAULT_DLSUBFN = DLSUBFN_SAME

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

    DEFAULT_INTERFACE_LANG = UnknownLanguage.create_generic()

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
