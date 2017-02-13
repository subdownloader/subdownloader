# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtCore import Qt, QItemSelectionModel, QSettings
from PyQt5.QtWidgets import QMessageBox, QDialog, QListWidgetItem

from subdownloader import Languages
from subdownloader.client.gui.chooseLanguage_ui import Ui_ChooseLanguageDialog

log = logging.getLogger("subdownloader.gui.chooseLanguage")


class chooseLanguageDialog(QDialog):

    def __init__(self, parent, user_locale):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_ChooseLanguageDialog()
        self.ui.setupUi(self)
        self._main = parent
        settings = QSettings()
        self.ui.languagesList.activated.connect(self.onOkButton)
        self.ui.OKButton.clicked.connect(self.onOkButton)

        for lang_locale in self._main.interface_langs:
            languageName = Languages.locale2name(lang_locale)
            if not languageName:
                languageName = lang_locale
            item = QListWidgetItem(languageName)
            item.setData(Qt.UserRole, lang_locale)
            self.ui.languagesList.addItem(item)
            try:
                if lang_locale == user_locale:
                    self.ui.languagesList.setCurrentItem(
                        item, QItemSelectionModel.ClearAndSelect)
            except:
                print("Warning: Please upgrade to a PyQT version >= 4.4")

    def onOkButton(self):
        if not self.ui.languagesList.currentItem():
            QMessageBox.about(self, "Alert", "Please select a language")
        else:
            choosen_lang = \
                self.ui.languagesList.currentItem().data(Qt.UserRole)
            self._main.choosenLanguage = choosen_lang
            self.reject()
