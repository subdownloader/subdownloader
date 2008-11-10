
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QVariant, QSize, QEventLoop, QString, \
                         QBuffer, QIODevice, QModelIndex,QDir
from PyQt4.QtGui import QPixmap, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel, QItemSelectionModel, QListWidgetItem
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical

from languages import Languages, autodetect_lang
from gui.chooseLanguage_ui import Ui_ChooseLanguageDialog
import logging
log = logging.getLogger("subdownloader.gui.chooseLanguage")

class chooseLanguageDialog(QtGui.QDialog): 
    def __init__(self, parent, user_locale):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_ChooseLanguageDialog()
        self.ui.setupUi(self)
        self._main  = parent
        settings = QSettings()
        QObject.connect(self.ui.languagesList, SIGNAL("activated(QModelIndex)"), self.onOkButton)
        QObject.connect(self.ui.OKButton, SIGNAL("clicked(bool)"), self.onOkButton)
        
        for lang_locale in self._main.interface_langs:
                languageName = Languages.locale2name(lang_locale)
                if not languageName:
                    languageName = lang_locale
                item = QListWidgetItem(languageName)
                item.setData(Qt.UserRole, QVariant(lang_locale))
                self.ui.languagesList.addItem(item)
                try:
                    if lang_locale == user_locale:
                            self.ui.languagesList.setCurrentItem(item,QItemSelectionModel.ClearAndSelect)
                except:
                    print "Warning: Please upgrade to a PyQT version >= 4.4"

    def onOkButton(self):
        if not self.ui.languagesList.currentItem():
                QMessageBox.about(self,"Alert","Please select a language")
        else:
                choosen_lang = str(self.ui.languagesList.currentItem().data(Qt.UserRole).toString().toUtf8())
                self._main.choosenLanguage = choosen_lang
                self.reject()

