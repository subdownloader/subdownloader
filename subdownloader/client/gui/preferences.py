# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging
import platform
import webbrowser

from subdownloader.languages import language

from PyQt5.QtCore import pyqtSlot, QSettings
from PyQt5.QtWidgets import QCheckBox, QDialog, QFileDialog, QMessageBox

from subdownloader.client.gui.preferences_ui import Ui_PreferencesDialog

log = logging.getLogger("subdownloader.client.gui.preferences")


class PreferencesDialog(QDialog):

    def __init__(self, parent, main):
        QDialog.__init__(self, parent)

        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)

        self._main = main

        # 0. Preferences dialog
        self.ui.buttonApplyChanges.clicked.connect(
            self.onApplyChanges)
        self.ui.buttonCancel.clicked.connect(
            self.onCancel)

        # 1. Search tab
        self.filterLanguages = {}
        nb_columns_languages = 4
        for num, lang in enumerate(language.legal_languages()):
            row = num // nb_columns_languages
            column = num % nb_columns_languages

            lang_xxx = lang["LanguageID"][0]
            self.ui.optionUlDefaultLanguage.addItem(
                _(lang["LanguageName"][0]), lang_xxx)
            # Adding checkboxes for the Search...Filter by ...
            self.filterLanguages[lang_xxx] = QCheckBox(
                _(lang["LanguageName"][0]), self.ui.scrollAreaWidgetSearch)
            self.ui.scrollAreaWidgetLayoutSearch.addWidget(self.filterLanguages[lang_xxx], row, column)

        # 2. Download tab
        self.ui.optionDlDestinationUser.toggled.connect(
            self.ui.textDlDestinationUser.setEnabled)
        self.ui.optionDlDestinationUser.toggled.connect(
            self.ui.buttonDlDestinationUser.setEnabled)
        self.ui.optionDlDestinationUser.toggled.emit(False)

        self.ui.buttonDlDestinationUser.clicked.connect(
            self.onDlDestinationUser)

        # 5. Others tab
        self.ui.buttonVideoAppLocationChoose.clicked.connect(
            self.onOptionVideoAppChooseLocation)
        self.ui.buttonHelpTranslation.clicked.connect(
            self.onHelpTranslate)

        self.ui.optionUlDefaultLanguage.addItem(_("<AutoDetect>"), "")


        self.ui.optionInterfaceLanguage.addItem(_('<system_locale>'), "")
        for lang_locale in self._main.interface_langs:
            languageName = language.locale2name(lang_locale)
            if not languageName:
                languageName = lang_locale
            self.ui.optionInterfaceLanguage.addItem(
                _(languageName), lang_locale)

        self.ui.optionUlDefaultLanguage.adjustSize()
        self.ui.optionInterfaceLanguage.adjustSize()
        self.readOptionsSettings()

        self.ui.optionInterfaceLanguage.currentIndexChanged.connect(
            self.onOptionInterfaceLanguage)

    @pyqtSlot()
    def onHelpTranslate(self):
        webbrowser.open(
            "http://www.subdownloader.net/translate.html", new=2, autoraise=1)

    @pyqtSlot()
    def onDlDestinationUser(self):
        directory = QFileDialog.getExistingDirectory(
            None, _("Select a directory"), "")
        if directory:
            self.ui.textDlDestinationUser.setText(directory)

    @pyqtSlot()
    def onOptionVideoAppChooseLocation(self):
        extensions = ""
        if platform.system == "Windows":
            extensions = "*.exe"

        fileName, t = QFileDialog.getOpenFileName(
            None, _("Select the Video Player executable file"), "", extensions)
        if fileName:
            self.ui.optionVideoAppLocation.setText(fileName)

    @pyqtSlot(int)
    def onOptionInterfaceLanguage(self, option):
        QMessageBox.about(self, _("Alert"), _(
            "The new language will be displayed after restarting the program."))

    def readOptionsSettings(self):
        log.debug("Reading Options Settings")
        settings = QSettings()
        optionWhereToDownload = \
            settings.value("options/whereToDownload", "SAME_FOLDER")
        if optionWhereToDownload == "ASK_FOLDER":
            self.ui.optionDlDestinationAsk.setChecked(True)
        elif optionWhereToDownload == "SAME_FOLDER":
            self.ui.optionDlDestinationSame.setChecked(True)
        elif optionWhereToDownload == "PREDEFINED_FOLDER":
            self.ui.optionDlDestinationUser.setChecked(True)

        folder = settings.value("options/whereToDownloadFolder", "")
        self.ui.textDlDestinationUser.setText(folder)

        optionSubtitleName = \
            settings.value("options/subtitleName", "SAME_VIDEO")
        if optionSubtitleName == "SAME_VIDEO":
            self.ui.optionSubFnSame.setChecked(True)
        elif optionSubtitleName == "SAME_VIDEOPLUSLANG":
            self.ui.optionSubFnSameLang.setChecked(True)
        elif optionSubtitleName == "SAME_VIDEOPLUSLANGANDUPLOADER":
            self.ui.optionSubFnSameLangUploader.setChecked(
                True)
        elif optionSubtitleName == "SAME_ONLINE":
            self.ui.optionSubFnOnline.setChecked(True)

        # Search
        optionFilterSearchLang = \
            settings.value("options/filterSearchLang", "")
        for lang_xxx in optionFilterSearchLang.split(','):
            if lang_xxx in self.filterLanguages:
                self.filterLanguages[lang_xxx].setChecked(True)

        # Upload
        optionUploadLanguage = \
            settings.value("options/uploadLanguage", "eng")
        index = self.ui.optionUlDefaultLanguage.findData(
            optionUploadLanguage)
        if index != -1:
            self.ui.optionUlDefaultLanguage.setCurrentIndex(index)

        optionInterfaceLanguage = \
            settings.value("options/interfaceLang", "en")
        index = self.ui.optionInterfaceLanguage.findData(
            optionInterfaceLanguage)
        if index != -1:
            self.ui.optionInterfaceLanguage.setCurrentIndex(index)

        optionIntegrationExplorer = settings.value(
            "options/IntegrationExplorer", False)
        self.ui.optionIntegrationExplorer.setChecked(optionIntegrationExplorer)

        self.ui.optionProxyHost.setText(
            settings.value("options/ProxyHost", ""))
        self.ui.optionProxyPort.setValue(int(
            settings.value("options/ProxyPort", 8080)))

        programPath = settings.value("options/VideoPlayerPath", "")
        parameters = settings.value("options/VideoPlayerParameters", "")
        self.ui.optionVideoAppLocation.setText(programPath)
        self.ui.optionVideoAppParams.setText(parameters)

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
    def onApplyChanges(self):
        log.debug("Saving Options Settings")
        # Fields validation
        if self.ui.optionDlDestinationUser.isChecked() and self.ui.textDlDestinationUser.text() == "":
            QMessageBox.about(
                self, _("Error"), _("Predefined Folder cannot be empty"))
            return
        # Writing settings
        settings = QSettings()
        if self.ui.optionDlDestinationAsk.isChecked():
            settings.setValue("options/whereToDownload", "ASK_FOLDER")
        elif self.ui.optionDlDestinationSame.isChecked():
            settings.setValue("options/whereToDownload", "SAME_FOLDER")
        elif self.ui.optionDlDestinationUser.isChecked():
            settings.setValue("options/whereToDownload", "PREDEFINED_FOLDER")
            folder = self.ui.textDlDestinationUser.text()
            settings.setValue("options/whereToDownloadFolder", folder)

        if self.ui.optionSubFnSame.isChecked():
            settings.setValue("options/subtitleName", "SAME_VIDEO")
        elif self.ui.optionSubFnSameLang.isChecked():
            settings.setValue("options/subtitleName", "SAME_VIDEOPLUSLANG")
        elif self.ui.optionSubFnSameLangUploader.isChecked():
            settings.setValue(
                "options/subtitleName", "SAME_VIDEOPLUSLANGANDUPLOADER")
        elif self.ui.optionSubFnSameLangUploader.isChecked():
            settings.setValue("options/subtitleName", "SAME_ONLINE")

        # Search tab
        checked_languages = []
        for lang, checkbox in self.filterLanguages.items():
            if checkbox.isChecked():

                checked_languages.append(lang)

        settings.setValue(
            "options/filterSearchLang", ",".join(checked_languages))
        self._main.filterLangChangedPermanent.emit(",".join(checked_languages))

        # Upload tab
        optionUploadLanguage = self.ui.optionUlDefaultLanguage.itemData(
            self.ui.optionUlDefaultLanguage.currentIndex())
        settings.setValue("options/uploadLanguage", optionUploadLanguage)
        self._main.language_updated.emit(optionUploadLanguage, "")

        optionInterfaceLanguage = self.ui.optionInterfaceLanguage.itemData(
            self.ui.optionInterfaceLanguage.currentIndex())
        settings.setValue("options/interfaceLang", optionInterfaceLanguage)

        IEoldValue = settings.value(
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
                settings.setValue("options/IntegrationExplorer", IEnewValue)

        newProxyHost = self.ui.optionProxyHost.text()
        newProxyPort = self.ui.optionProxyPort.value()
        oldProxyHost = settings.value("options/ProxyHost", "")
        oldProxyPort = int(settings.value("options/ProxyPort", 8080))
        if newProxyHost != oldProxyHost or newProxyPort != oldProxyPort:
            settings.setValue("options/ProxyHost", newProxyHost)
            settings.setValue("options/ProxyPort", newProxyPort)
            QMessageBox.about(self, _("Alert"), _(
                "Modified proxy settings will take effect after restarting the program"))

        programPath = self.ui.optionVideoAppLocation.text()
        parameters = self.ui.optionVideoAppParams.text()
        settings.setValue("options/VideoPlayerPath", programPath)
        settings.setValue("options/VideoPlayerParameters", parameters)

        # Closing the Preferences window
        self.reject()

    def actionContextMenu(self, action, os):
        pass

    @pyqtSlot()
    def onCancel(self):
        self.reject()
