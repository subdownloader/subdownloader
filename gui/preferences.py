#!/usr/bin/env python
# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QSize, QEventLoop, \
                         QBuffer, QIODevice, QModelIndex,QDir
from PyQt4.QtGui import QPixmap, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel, QItemSelectionModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical

from .main import toString, toInteger

from gui.preferences_ui import Ui_PreferencesDialog
import webbrowser
import languages.Languages as languages
import time, platform
import logging
log = logging.getLogger("subdownloader.gui.preferences")

class preferencesDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)
        self._main  = parent
        settings = QSettings()
        #OPTIONS events
        QObject.connect(self.ui.optionsButtonApplyChanges, SIGNAL("clicked(bool)"), self.onOptionsButtonApplyChanges)
        QObject.connect(self.ui.optionsButtonCancel, SIGNAL("clicked(bool)"), self.onOptionsButtonCancel)
        QObject.connect(self.ui.optionButtonChooseFolder, SIGNAL("clicked(bool)"), self.onOptionButtonChooseFolder)
        QObject.connect(self.ui.optionDownloadFolderPredefined, SIGNAL("toggled(bool)"), self.onOptionDownloadFolderPredefined)
        QObject.connect(self.ui.optionVideoAppChooseLocation, SIGNAL("clicked(bool)"), self.onOptionVideoAppChooseLocation)
        QObject.connect(self.ui.helpTranslateButton, SIGNAL("clicked(bool)"), self.onOptionHelpTranslateButton)

        self.onOptionDownloadFolderPredefined()
        self.filterLanguages = {}
        self.ui.optionDefaultUploadLanguage.addItem(_("<AutoDetect>"), "")
        for num, lang in enumerate(languages.LANGUAGES):
            lang_xxx = lang["SubLanguageID"]
            self.ui.optionDefaultUploadLanguage.addItem(_(lang["LanguageName"]), lang_xxx)
            #Adding checkboxes for the Search...Filter by ...
            self.filterLanguages[lang_xxx] = QtGui.QCheckBox(_(lang["LanguageName"]), self.ui.scrollAreaWidgetContents)
            if num % 4 == 1:
                self.ui.optionFilterLangLayout_1.addWidget(self.filterLanguages[lang_xxx] )
            elif num % 4 == 2:
                self.ui.optionFilterLangLayout_2.addWidget(self.filterLanguages[lang_xxx] )
            elif num % 4 == 3:
                self.ui.optionFilterLangLayout_3.addWidget(self.filterLanguages[lang_xxx] )
            else:
                self.ui.optionFilterLangLayout_4.addWidget(self.filterLanguages[lang_xxx] )

        for lang_locale in self._main.interface_langs:
                languageName = languages.locale2name(lang_locale)
                if not languageName:
                    languageName = lang_locale
                self.ui.optionInterfaceLanguage.addItem(_(languageName), lang_locale)

        self.ui.optionDefaultUploadLanguage.adjustSize()
        self.ui.optionInterfaceLanguage.adjustSize()
        self.readOptionsSettings(settings)

        QObject.connect(self.ui.optionInterfaceLanguage, SIGNAL("currentIndexChanged(int)"), self.onOptionInterfaceLanguage)

    def onOptionHelpTranslateButton(self):
        webbrowser.open( "http://www.subdownloader.net/translate.html", new=2, autoraise=1)

    def onOptionButtonChooseFolder(self):
        directory = QtGui.QFileDialog.getExistingDirectory(None, _("Select a directory"), "")
        if directory:
            self.ui.optionPredefinedFolderText.setText(directory)

    def onOptionVideoAppChooseLocation(self):
        extensions = ""
        if platform.system == "Windows":
            extensions  = "*.exe"

        fileName = QFileDialog.getOpenFileName(None, _("Select the Video Player executable file"), "", extensions)
        if fileName:
            self.ui.optionVideoAppLocation.setText(fileName)

    def onOptionInterfaceLanguage(self, option):
        QMessageBox.about(self,_("Alert"),_("The new language will be displayed after restarting the program."))

    def onOptionDownloadFolderPredefined(self):
        if self.ui.optionDownloadFolderPredefined.isChecked():
            self.ui.optionPredefinedFolderText.setEnabled(True)
            self.ui.optionButtonChooseFolder.setEnabled(True)
        else:
            self.ui.optionPredefinedFolderText.setEnabled(False)
            self.ui.optionButtonChooseFolder.setEnabled(False)

    def readOptionsSettings(self, settings):
        log.debug("Reading Options Settings")
        optionWhereToDownload = toString(settings.value("options/whereToDownload", "SAME_FOLDER"))
        if optionWhereToDownload == "ASK_FOLDER":
            self.ui.optionDownloadFolderAsk.setChecked(True)
        elif optionWhereToDownload == "SAME_FOLDER":
            self.ui.optionDownloadFolderSame.setChecked(True)
        elif optionWhereToDownload == "PREDEFINED_FOLDER":
            self.ui.optionDownloadFolderPredefined.setChecked(True)

        folder = toString(settings.value("options/whereToDownloadFolder", ""))
        self.ui.optionPredefinedFolderText.setText(folder)


        optionSubtitleName = toString(settings.value("options/subtitleName", "SAME_VIDEO"))
        if optionSubtitleName == "SAME_VIDEO":
            self.ui.optionDownloadSameFilename.setChecked(True)
        elif optionSubtitleName == "SAME_VIDEOPLUSLANG":
            self.ui.optionDownloadSameFilenamePlusLang.setChecked(True)
        elif optionSubtitleName == "SAME_VIDEOPLUSLANGANDUPLOADER":
            self.ui.optionDownloadSameFilenamePlusLangAndUploader.setChecked(True)
        elif optionSubtitleName == "SAME_ONLINE":
            self.ui.optionDownloadOnlineSubName.setChecked(True)

        #Search
        optionFilterSearchLang = toString(settings.value("options/filterSearchLang", ""))
        for lang_xxx in optionFilterSearchLang.split(','):
            if lang_xxx in self.filterLanguages:
                self.filterLanguages[lang_xxx].setChecked(True)

        #Upload
        optionUploadLanguage = toString(settings.value("options/uploadLanguage", "eng"))
        index = self.ui.optionDefaultUploadLanguage.findData(optionUploadLanguage)
        if index != -1 :
            self.ui.optionDefaultUploadLanguage.setCurrentIndex (index)

        optionInterfaceLanguage = toString(settings.value("options/interfaceLang", "en"))
        index = self.ui.optionInterfaceLanguage.findData(optionInterfaceLanguage)
        if index != -1 :
            self.ui.optionInterfaceLanguage.setCurrentIndex (index)

        optionIntegrationExplorer = settings.value("options/IntegrationExplorer", False).toBool()
        self.ui.optionIntegrationExplorer.setChecked(optionIntegrationExplorer)

        self.ui.optionProxyHost.setText(toString(settings.value("options/ProxyHost", "")))
        self.ui.optionProxyPort.setValue(toInteger(settings.value("options/ProxyPort", 8080)))

        programPath = toString(settings.value("options/VideoPlayerPath", ""))
        parameters = toString(settings.value("options/VideoPlayerParameters", ""))
        self.ui.optionVideoAppLocation.setText(programPath)
        self.ui.optionVideoAppParams.setText(parameters)

        #Context menu for Explorer
        if platform.system() == "Linux":
            self.ui.optionIntegrationExplorer.setText(_("Enable in your Konqueror/Dolphin/Nautilus"))
            self.ui.optionIntegrationExplorer.setEnabled(False)
        elif platform.system() == "Windows":
            self.ui.optionIntegrationExplorer.setText(_("Enable in your Windows Explorer"))
            self.ui.optionIntegrationExplorer.setEnabled(False)
        else:
            self.ui.optionIntegrationExplorer.setText(_("Enable in your File Manager"))
            self.ui.optionIntegrationExplorer.setEnabled(False)


    def onOptionsButtonApplyChanges(self):
        log.debug("Saving Options Settings")
        #Fields validation
        if self.ui.optionDownloadFolderPredefined.isChecked() and toString(self.ui.optionPredefinedFolderText.text()) == "":
            QMessageBox.about(self,_("Error"),_("Predefined Folder cannot be empty"))
            return
        #Writting settings
        settings = QSettings()
        if self.ui.optionDownloadFolderAsk.isChecked():
            settings.setValue("options/whereToDownload", "ASK_FOLDER")
        elif self.ui.optionDownloadFolderSame.isChecked():
            settings.setValue("options/whereToDownload", "SAME_FOLDER")
        elif self.ui.optionDownloadFolderPredefined.isChecked():
            settings.setValue("options/whereToDownload", "PREDEFINED_FOLDER")
            folder = self.ui.optionPredefinedFolderText.text()
            settings.setValue("options/whereToDownloadFolder", folder)

        if self.ui.optionDownloadSameFilename.isChecked():
            settings.setValue("options/subtitleName", "SAME_VIDEO")
        elif self.ui.optionDownloadSameFilenamePlusLang.isChecked():
            settings.setValue("options/subtitleName", "SAME_VIDEOPLUSLANG")
        elif self.ui.optionDownloadSameFilenamePlusLangAndUploader.isChecked():
            settings.setValue("options/subtitleName", "SAME_VIDEOPLUSLANGANDUPLOADER")
        elif self.ui.optionDownloadOnlineSubName.isChecked():
            settings.setValue("options/subtitleName", "SAME_ONLINE")

        #Search tab
        checked_languages = []
        for lang,checkbox in self.filterLanguages.items():
            if checkbox.isChecked():

                checked_languages.append(lang)

        settings.setValue("options/filterSearchLang", ",".join(checked_languages))
        self._main.emit(SIGNAL('filterLangChangedPermanent(QString)'),",".join(checked_languages))

        #Upload tab
        optionUploadLanguage = self.ui.optionDefaultUploadLanguage.itemData(self.ui.optionDefaultUploadLanguage.currentIndex())
        settings.setValue("options/uploadLanguage", optionUploadLanguage)
        self._main.emit(SIGNAL('language_updated(QString,QString)'),optionUploadLanguage, "")

        optionInterfaceLanguage = self.ui.optionInterfaceLanguage.itemData(self.ui.optionInterfaceLanguage.currentIndex())
        settings.setValue("options/interfaceLang", optionInterfaceLanguage)

        IEoldValue = settings.value("options/IntegrationExplorer", False).toBool()
        IEnewValue = self.ui.optionIntegrationExplorer.isChecked()
        if  IEoldValue != IEnewValue:
           if IEnewValue:
               log.debug('Installing the Integration Explorer feature')
               ok = self.actionContextMenu("install",platform.system())
           else:
               log.debug('Uninstalling the Integration Explorer feature')
               ok = self.actionContextMenu("uninstall",platform.system())
           if ok:
                settings.setValue("options/IntegrationExplorer", IEnewValue)

        newProxyHost =  self.ui.optionProxyHost.text()
        newProxyPort = self.ui.optionProxyPort.value()
        oldProxyHost = settings.value("options/ProxyHost", "")
        oldProxyPort = settings.value("options/ProxyPort", "8080").toInt()
        if newProxyHost != oldProxyHost or newProxyPort != oldProxyPort:
            settings.setValue("options/ProxyHost", newProxyHost)
            settings.setValue("options/ProxyPort", newProxyPort)
            QMessageBox.about(self,_("Alert"),_("Modified proxy settings will take effect after restarting the program"))

        programPath =  self.ui.optionVideoAppLocation.text()
        parameters =  self.ui.optionVideoAppParams.text()
        settings.setValue("options/VideoPlayerPath", programPath)
        settings.setValue("options/VideoPlayerParameters", parameters)

        #Closing the Preferences window
        self.reject()

    def actionContextMenu(self, action,os):
        pass

    def onOptionsButtonCancel(self):
        self.reject()
