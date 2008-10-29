
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QVariant, QSize, QEventLoop, QString, \
                         QBuffer, QIODevice, QModelIndex,QDir
from PyQt4.QtGui import QPixmap, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel, QItemSelectionModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical

from gui.preferences_ui import Ui_PreferencesDialog
import webbrowser
import languages.Languages as languages
import time, thread, platform
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
        self.ui.optionDefaultUploadLanguage.addItem(_("<AutoDetect>"), QVariant())
        for num, lang in enumerate(languages.LANGUAGES):
            lang_xxx = lang["SubLanguageID"]
            self.ui.optionDefaultUploadLanguage.addItem(_(lang["LanguageName"]), QVariant(lang_xxx))
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
                self.ui.optionInterfaceLanguage.addItem(_(languageName), QVariant(lang_locale))
            
        self.ui.optionDefaultUploadLanguage.adjustSize()
        self.ui.optionInterfaceLanguage.adjustSize()
        self.readOptionsSettings(settings)
        
        QObject.connect(self.ui.optionInterfaceLanguage, SIGNAL("currentIndexChanged(int)"), self.onOptionInterfaceLanguage)
        
    def onOptionHelpTranslateButton(self):
        webbrowser.open( "http://www.subdownloader.net/translate.html", new=2, autoraise=1)
        
    def onOptionButtonChooseFolder(self):
        directory=QtGui.QFileDialog.getExistingDirectory(None,_("Select a directory"),QString())
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
        optionWhereToDownload = settings.value("options/whereToDownload", QVariant("SAME_FOLDER"))
        if optionWhereToDownload == QVariant("ASK_FOLDER"):
            self.ui.optionDownloadFolderAsk.setChecked(True)
        elif optionWhereToDownload == QVariant("SAME_FOLDER"):
            self.ui.optionDownloadFolderSame.setChecked(True)
        elif optionWhereToDownload == QVariant("PREDEFINED_FOLDER"):
            self.ui.optionDownloadFolderPredefined.setChecked(True)
        
        folder = settings.value("options/whereToDownloadFolder", QVariant("")).toString()
        self.ui.optionPredefinedFolderText.setText(folder)
            
            
        optionSubtitleName = settings.value("options/subtitleName", QVariant("SAME_VIDEO"))
        if optionSubtitleName == QVariant("SAME_VIDEO"):
            self.ui.optionDownloadSameFilename.setChecked(True)
        elif optionSubtitleName == QVariant("SAME_VIDEOPLUSLANG"):
            self.ui.optionDownloadSameFilenamePlusLang.setChecked(True)
        elif optionSubtitleName == QVariant("SAME_ONLINE"):
            self.ui.optionDownloadOnlineSubName.setChecked(True)
            
        #Search
        optionFilterSearchLang = str(settings.value("options/filterSearchLang", QVariant("")).toString())
        for lang_xxx in optionFilterSearchLang.split(','):
            if self.filterLanguages.has_key(lang_xxx):
                self.filterLanguages[lang_xxx].setChecked(True)
            
        #Upload 
        optionUploadLanguage = settings.value("options/uploadLanguage", QVariant("eng"))
        index = self.ui.optionDefaultUploadLanguage.findData(optionUploadLanguage)
        if index != -1 :
            self.ui.optionDefaultUploadLanguage.setCurrentIndex (index)
            
        optionInterfaceLanguage = settings.value("options/interfaceLang", QVariant("en"))
        index = self.ui.optionInterfaceLanguage.findData(optionInterfaceLanguage)
        if index != -1 :
            self.ui.optionInterfaceLanguage.setCurrentIndex (index)
            
        optionIntegrationExplorer = settings.value("options/IntegrationExplorer", QVariant(False))
        self.ui.optionIntegrationExplorer.setChecked(optionIntegrationExplorer.toBool())

        self.ui.optionProxyHost.setText(settings.value("options/ProxyHost", QVariant()).toString())
        self.ui.optionProxyPort.setValue(settings.value("options/ProxyPort", QVariant(8080)).toInt()[0])
        
        programPath = settings.value("options/VideoPlayerPath", QVariant()).toString()
        parameters = settings.value("options/VideoPlayerParameters", QVariant()).toString()
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
        if self.ui.optionDownloadFolderPredefined.isChecked() and self.ui.optionPredefinedFolderText.text() == QString():
            QMessageBox.about(self,_("Error"),_("Predefined Folder cannot be empty"))
            return
        #Writting settings
        settings = QSettings()
        if self.ui.optionDownloadFolderAsk.isChecked():
            settings.setValue("options/whereToDownload", QVariant("ASK_FOLDER"))
        elif self.ui.optionDownloadFolderSame.isChecked():
            settings.setValue("options/whereToDownload", QVariant("SAME_FOLDER"))
        elif self.ui.optionDownloadFolderPredefined.isChecked():
            settings.setValue("options/whereToDownload", QVariant("PREDEFINED_FOLDER"))
            folder = self.ui.optionPredefinedFolderText.text()
            settings.setValue("options/whereToDownloadFolder", QVariant(folder))
            
        if self.ui.optionDownloadSameFilename.isChecked():
            settings.setValue("options/subtitleName", QVariant("SAME_VIDEO"))
        elif self.ui.optionDownloadSameFilenamePlusLang.isChecked():
            settings.setValue("options/subtitleName", QVariant("SAME_VIDEOPLUSLANG"))
        elif self.ui.optionDownloadOnlineSubName.isChecked():
            settings.setValue("options/subtitleName", QVariant("SAME_ONLINE"))
        
        #Search tab
        checked_languages = []
        for lang,checkbox in self.filterLanguages.items():
            if checkbox.isChecked():
                checked_languages.append(lang)
        settings.setValue("options/filterSearchLang", QVariant(",".join(checked_languages)))
        self._main.emit(SIGNAL('filterLangChangedPermanent(QString)'),",".join(checked_languages))
        
        #Upload tab
        optionUploadLanguage = self.ui.optionDefaultUploadLanguage.itemData(self.ui.optionDefaultUploadLanguage.currentIndex())
        settings.setValue("options/uploadLanguage", optionUploadLanguage)
        self._main.emit(SIGNAL('language_updated(QString,QString)'),optionUploadLanguage, "")
            
        optionInterfaceLanguage = self.ui.optionInterfaceLanguage.itemData(self.ui.optionInterfaceLanguage.currentIndex())
        settings.setValue("options/interfaceLang", optionInterfaceLanguage)
        
        IEoldValue = settings.value("options/IntegrationExplorer", QVariant(False)).toBool()
        IEnewValue = self.ui.optionIntegrationExplorer.isChecked()
        if  IEoldValue != IEnewValue:
           if IEnewValue:
               log.debug('Installing the Integration Explorer feature') 
               ok = self.actionContextMenu("install",platform.system())
           else:
               log.debug('Uninstalling the Integration Explorer feature')
               ok = self.actionContextMenu("uninstall",platform.system())
           if ok:
                settings.setValue("options/IntegrationExplorer", QVariant(IEnewValue))
        
        newProxyHost =  self.ui.optionProxyHost.text()
        newProxyPort = self.ui.optionProxyPort.value()
        oldProxyHost = settings.value("options/ProxyHost", QVariant()).toString()
        oldProxyPort = settings.value("options/ProxyPort", QVariant("8080")).toInt()[0]
        if newProxyHost != oldProxyHost or newProxyPort != oldProxyPort:
            settings.setValue("options/ProxyHost",QVariant(newProxyHost))
            settings.setValue("options/ProxyPort", QVariant(newProxyPort))
            QMessageBox.about(self,_("Alert"),_("Modified proxy settings will take effect after restarting the program"))
        
        programPath =  self.ui.optionVideoAppLocation.text()
        parameters =  self.ui.optionVideoAppParams.text()
        settings.setValue("options/VideoPlayerPath",QVariant(programPath))
        settings.setValue("options/VideoPlayerParameters",QVariant(parameters))
        
        #Closing the Preferences window
        self.reject()

    def actionContextMenu(self, action,os):
        pass
    def onOptionsButtonCancel(self):
        self.reject()

