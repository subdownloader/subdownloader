
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QVariant, QSize, QEventLoop, QString, \
                         QBuffer, QIODevice, QModelIndex,QDir
from PyQt4.QtGui import QPixmap, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel, QItemSelectionModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical

from subdownloader.gui.preferences_ui import Ui_PreferencesDialog
import webbrowser
import subdownloader.languages.Languages as languages
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
        
        self.onOptionDownloadFolderPredefined()
        
        for lang in languages.LANGUAGES:
            self.ui.optionDefaultUploadLanguage.addItem(QtGui.QApplication.translate("MainWindow", lang["LanguageName"], None, QtGui.QApplication.UnicodeUTF8), QVariant(lang["SubLanguageID"]))
            if lang["SubLanguageID"] == "eng": #For the moment interface is only in English
                self.ui.optionInterfaceLanguage.addItem(QtGui.QApplication.translate("MainWindow", lang["LanguageName"], None, QtGui.QApplication.UnicodeUTF8), QVariant(lang["SubLanguageID"]))
            
        self.ui.optionDefaultUploadLanguage.adjustSize()
        self.ui.optionInterfaceLanguage.adjustSize()
        self.readOptionsSettings(settings)
        
        QObject.connect(self.ui.optionInterfaceLanguage, SIGNAL("currentIndexChanged(int)"), self.onOptionInterfaceLanguage)
        
    def onOptionButtonChooseFolder(self):
        directory=QtGui.QFileDialog.getExistingDirectory(None,"Select a directory",QString())
        if directory:
            self.ui.optionPredefinedFolderText.setText(directory)
            
    def onOptionInterfaceLanguage(self, option):
        QMessageBox.about(self,"Alert","The new language will be displayed after restarting the application")
        
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
            
        
        optionUploadLanguage = settings.value("options/uploadLanguage", QVariant("eng"))
        index = self.ui.optionDefaultUploadLanguage.findData(optionUploadLanguage)
        if index != -1 :
            self.ui.optionDefaultUploadLanguage.setCurrentIndex (index)
            
        optionInterfaceLanguage = settings.value("options/interfaceLanguage", QVariant("eng"))
        index = self.ui.optionInterfaceLanguage.findData(optionInterfaceLanguage)
        if index != -1 :
            self.ui.optionInterfaceLanguage.setCurrentIndex (index)
            
        optionIntegrationExplorer = settings.value("options/IntegrationExplorer", QVariant(False))
        self.ui.optionIntegrationExplorer.setChecked(optionIntegrationExplorer.toBool())
        
        self.ui.optionLoginUsername.setText(settings.value("options/LoginUsername", QVariant()).toString())
        self.ui.optionLoginPassword.setText(settings.value("options/LoginPassword", QVariant()).toString())
        
        self.ui.optionProxyHost.setText(settings.value("options/ProxyHost", QVariant()).toString())
        self.ui.optionProxyPort.setValue(settings.value("options/ProxyPort", QVariant(8080)).toInt()[0])
        
        totalVideoPlayers = settings.beginReadArray("options/videoPlayers")
        for i in range(totalVideoPlayers):
            settings.setArrayIndex(i)
            programPath = settings.value("programPath").toString()
            parameters = settings.value("parameters").toString()
            name = settings.value("name").toString()
            self.ui.optionVideoAppCombo.addItem("%s" % (name), QVariant(name))
        settings.endArray()
        
        #Context menu for Explorer
        if platform.system() == "Linux":
            self.ui.optionIntegrationExplorer.setText("Enable in your Konqueror/Dolphin/Nautilus")
            self.ui.optionIntegrationExplorer.setEnabled(True)
        elif platform.system() == "Windows":
            self.ui.optionIntegrationExplorer.setText("Enable in your Windows Explorer")
            self.ui.optionIntegrationExplorer.setEnabled(True)
        else:
            self.ui.optionIntegrationExplorer.setText("Enable in your Explorer")
            self.ui.optionIntegrationExplorer.setEnabled(False)

        
        if totalVideoPlayers: 
            QObject.connect(self.ui.optionVideoAppCombo, SIGNAL("currentIndexChanged(int)"), self.onOptionVideoAppCombo)
        selectedVideoApp = settings.value("options/selectedVideoPlayer", QVariant()).toString()
        if selectedVideoApp != QString():
            index = self.ui.optionVideoAppCombo.findData(QVariant(selectedVideoApp))
            if index != -1 : 
                self.ui.optionVideoAppCombo.setCurrentIndex (index)
                self.onOptionVideoAppCombo(index)
        
    def onOptionVideoAppCombo(self, index):
        settings = QSettings()
        totalVideoPlayers = settings.beginReadArray("options/videoPlayers")
        settings.setArrayIndex(index)
        programPath = settings.value("programPath").toString()
        parameters = settings.value("parameters").toString()
        name = settings.value("name").toString()
        self.ui.optionVideoAppLocation.setText(programPath)
        self.ui.optionVideoAppParams.setText(parameters)
        settings.endArray()
        
    def onOptionsButtonApplyChanges(self):
        log.debug("Saving Options Settings")
        #Fields validation
        if self.ui.optionDownloadFolderPredefined.isChecked() and self.ui.optionPredefinedFolderText.text() == QString():
            QMessageBox.about(self,"Error","Predefined Folder cannot be empty")
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
        
        optionUploadLanguage = self.ui.optionDefaultUploadLanguage.itemData(self.ui.optionDefaultUploadLanguage.currentIndex())
        settings.setValue("options/uploadLanguage", optionUploadLanguage)
        index = self._main.uploadLanguages.findData(optionUploadLanguage)
        if index != -1 :
            self._main.uploadLanguages.setCurrentIndex (index)    
            
        optionInterfaceLanguage = self.ui.optionInterfaceLanguage.itemData(self.ui.optionInterfaceLanguage.currentIndex())
        settings.setValue("options/interfaceLanguage", optionInterfaceLanguage)
        
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
        
        newUsername =  self.ui.optionLoginUsername.text()
        newPassword = self.ui.optionLoginPassword.text()
        oldUsername = settings.value("options/LoginUsername", QVariant())
        oldPassword = settings.value("options/LoginPassword", QVariant())
        if newUsername != oldUsername.toString() or newPassword != oldPassword.toString():
            settings.setValue("options/LoginUsername",QVariant(newUsername))
            settings.setValue("options/LoginPassword", QVariant(newPassword))
            log.debug('Login credentials has changed. Trying to login.')
            thread.start_new_thread(self._main.login_user, (str(newUsername.toUtf8()),str(newPassword.toUtf8()),))
            
        newProxyHost =  self.ui.optionProxyHost.text()
        newProxyPort = self.ui.optionProxyPort.value()
        oldProxyHost = settings.value("options/ProxyHost", QVariant()).toString()
        oldProxyPort = settings.value("options/ProxyPort", QVariant("8080")).toInt()[0]
        if newProxyHost != oldProxyHost or newProxyPort != oldProxyPort:
            settings.setValue("options/ProxyHost",QVariant(newProxyHost))
            settings.setValue("options/ProxyPort", QVariant(newProxyPort))
            QMessageBox.about(self,"Alert","Modified proxy settings will take effect after restarting the program")
            
        
        totalVideoPlayers = settings.beginReadArray("options/videoPlayers")
        settings.endArray()
        if totalVideoPlayers:
            name = self.ui.optionVideoAppCombo.itemData(self.ui.optionVideoAppCombo.currentIndex())
            settings.setValue("options/selectedVideoPlayer", QVariant(name))
        
        #Closing the Preferences window
        self.reject()

    def actionContextMenu(self, action,os):
        pass
    def onOptionsButtonCancel(self):
        self.reject()

