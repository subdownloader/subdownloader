# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
import os
import platform
import webbrowser

from subdownloader.languages import language

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QDir, QSettings, Qt
from PyQt5.QtWidgets import QCheckBox, QCompleter, QDialog, QDirModel, QFileDialog, QMessageBox

from subdownloader.client.gui.preferences_ui import Ui_PreferencesDialog

log = logging.getLogger("subdownloader.client.gui.preferences")
#FIXME: add more logging


class PreferencesDialog(QDialog):

    def __init__(self, parent, main):
        QDialog.__init__(self, parent)

        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)

        self._main = main

        # 0. Dialog

        self.ui.buttonApplyChanges.clicked.connect(
            self.onApplyChanges)
        self.ui.buttonCancel.clicked.connect(
            self.onCancel)

        # 1. Search tab

        # - Filter languages

        self._filterLanguageComboBoxes = {}

        self._search_languages = {lang: False for lang in language.languages()}
        nb_columns_languages = 4
        for lang_i, lang in enumerate(language.languages()):
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
        fontSearchItem = self._filterLanguageComboBoxes[language.UnknownLanguage.create_generic()].font()
        fontSearchItem.setItalic(True)
        self._filterLanguageComboBoxes[language.UnknownLanguage.create_generic()].setFont(fontSearchItem)

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

        self._uploadLanguage = self.DEFAULT_ULFN

        ulItalicFont = self.ui.optionUlDefaultLanguage.font()
        ulItalicFont.setItalic(True)

        for lang in language.languages():
            # FIXME: don't add language as UserData
            # FIXME: create LanguageComboBox
            self.ui.optionUlDefaultLanguage.addItem(_(lang.generic_name()), lang)

        self.ui.optionUlDefaultLanguage.setItemText(0, _('Auto Detect'))
        self.ui.optionUlDefaultLanguage.setItemData(0, ulItalicFont, Qt.FontRole)
        self.ui.optionUlDefaultLanguage.adjustSize()

        self.ui.optionUlDefaultLanguage.currentIndexChanged.connect(self.onOptionUlDefaultLanguageIndexChange)

        # 4. Network tab

        self.ui.inputProxyPort.setRange(0, 65535)

        # 5. Others tab
        self.ui.optionInterfaceLanguage.addItem(_('<system_locale>'))
        for lang_locale in self._main.interface_langs:
            languageName = language.locale2name(lang_locale)
            if not languageName:
                languageName = lang_locale
            self.ui.optionInterfaceLanguage.addItem(
                _(languageName), lang_locale)
        self.ui.optionInterfaceLanguage.adjustSize()

        self.ui.buttonVideoAppLocationChoose.clicked.connect(
            self.onButtonVideoAppLocationChoose)
        self.ui.buttonHelpTranslation.clicked.connect(
            self.onHelpTranslate)

        self.settings = QSettings()  # FIXME: use config path

        self.readSettings()

        self.ui.optionInterfaceLanguage.currentIndexChanged.connect(
            self.onOptionInterfaceLanguage)

    def readSettings(self):
        log.debug('Reading Options Settings')
        self.settings.sync()

        # 1. Search tab
        checked_languages_str = self.settings.value('options/filterSearchLang', [])
        if checked_languages_str:
            for lang_xxx in checked_languages_str.split(','):
                try:
                    lang = language.Language.from_xxx(lang_xxx)
                    self._filterLanguageComboBoxes[lang].setChecked(True)
                except language.NotALanguageException:
                    pass

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

        optionUploadLanguage = self.settings.value('options/uploadLanguage', self.DEFAULT_ULFN.xxx())
        uploadLanguage = language.Language.from_xxx(optionUploadLanguage)

        index = self.ui.optionUlDefaultLanguage.findData(uploadLanguage)
        if index != -1:
            self.ui.optionUlDefaultLanguage.setCurrentIndex(index)

        for index in range(self.ui.optionUlDefaultLanguage.count()):
            if self.ui.optionUlDefaultLanguage.itemData(index, Qt.UserRole) == uploadLanguage:
                self.ui.optionUlDefaultLanguage.setCurrentIndex(index)
                break



        optionInterfaceLanguage = self.settings.value("options/interfaceLang", "en")
        index = self.ui.optionInterfaceLanguage.findData(optionInterfaceLanguage)
        if index != -1:
            self.ui.optionInterfaceLanguage.setCurrentIndex(index)

        optionIntegrationExplorer = self.settings.value(
            "options/IntegrationExplorer", False)
        self.ui.optionIntegrationExplorer.setChecked(optionIntegrationExplorer)

        # 4. Network tab
        self.ui.inputProxyHost.setText(
            self.settings.value("options/ProxyHost", ""))
        self.ui.inputProxyPort.setValue(int(
            self.settings.value("options/ProxyPort", 8080)))

        programPath = self.settings.value("options/VideoPlayerPath", "")
        parameters = self.settings.value("options/VideoPlayerParameters", "")
        self.ui.inputVideoAppLocation.setText(programPath)
        self.ui.inputVideoAppParams.setText(parameters)

        # 5. Others tab

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

    @pyqtSlot()
    def saveSettings(self):
        log.debug("Saving Options Settings")

        # 1. Search tab

        checked_languages = [lang[0].xxx() for lang in filter(lambda x:x[1], self._search_languages.items())]
        checked_languages_str = ','.join(checked_languages)
        self.settings.setValue("options/filterSearchLang", checked_languages_str)
        self._main.filterLangChangedPermanent.emit(checked_languages_str)

        # 2. Downloads tab

        # - Download Destination

        # Predefined Download Destination Validation
        if self.ui.optionDlDestinationUser.isChecked() and self.ui.inputDlDestinationUser.text() == "":
            QMessageBox.about(
                self, _("Error"), _("Predefined Folder cannot be empty"))
            return False

        self.settings.setValue('options/whereToDownload', self._dlDestinationType)
        self.settings.setValue('options/whereToDownloadFolder', self._dlDestinationPredefined)

        # - Subtitle Filename

        self.settings.setValue('options/subtitleName', self._subtitleFilename)

        # 3. Upload tab

        # - Default Subtitle Language

        self.settings.setValue('options/uploadLanguage', self._uploadLanguage.xxx())
        self._main.language_updated.emit(self._uploadLanguage.xxx(), "")

        # Writing settings

        optionInterfaceLanguage = self.ui.optionInterfaceLanguage.itemData(
            self.ui.optionInterfaceLanguage.currentIndex())
        self.settings.setValue("options/interfaceLang", optionInterfaceLanguage)

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
        return True

    # 0. Interface

    def validate(self):
        # Download Destination Validation
        dlDestinationUser = self.ui.inputDlDestinationUser.text()
        if self._dlDestinationType is self.DLDESTINATIONTYPE_PREDEFINEDFOLDER and not os.path.isdir(dlDestinationUser):
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

    searchLanguageChanged = pyqtSignal(language.Language, bool)

    @pyqtSlot(language.Language, bool)
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

    defaultUploadLanguageChanged = pyqtSignal(language.Language)

    DEFAULT_ULFN = language.UnknownLanguage.create_generic()

    @pyqtSlot(int)
    def onOptionUlDefaultLanguageIndexChange(self, index):
        self._uploadLanguage = self.ui.optionUlDefaultLanguage.itemData(index, Qt.UserRole)
        self.defaultUploadLanguageChanged.emit(self._uploadLanguage)

    def actionContextMenu(self, action, os):
        pass

    @pyqtSlot()
    def onHelpTranslate(self):
        webbrowser.open(
            "http://www.subdownloader.net/translate.html", new=2, autoraise=1)

    @pyqtSlot()
    def onButtonVideoAppLocationChoose(self):
        extensions = ""
        if platform.system == "Windows":
            extensions = "*.exe"

        fileName, t = QFileDialog.getOpenFileName(
            self, _("Select the Video Player executable file"), "", extensions)
        if fileName:
            self.ui.inputVideoAppLocation.setText(fileName)

    @pyqtSlot(int)
    def onOptionInterfaceLanguage(self, option):
        QMessageBox.about(self, _('Alert'), _(
            'The new language will be displayed after restarting the program.'))
