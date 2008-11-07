
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QObject, QCoreApplication, \
                         QSettings, QVariant, QSize, QEventLoop, QString, \
                         QBuffer, QIODevice, QModelIndex,QDir
from PyQt4.QtGui import QPixmap, QErrorMessage, QLineEdit, \
                        QMessageBox, QFileDialog, QIcon, QDialog, QInputDialog,QDirModel, QItemSelectionModel
from PyQt4.Qt import qDebug, qFatal, qWarning, qCritical

from gui.expiration_ui import Ui_ExpirationDialog
import logging
import webbrowser
from modules import APP_TITLE, APP_VERSION
log = logging.getLogger("subdownloader.gui.expiration")

from datetime import date , timedelta
import time

DAYS_TRIAL = 30
def GetFirstRunDate():
    return date.today() - timedelta(days=0)
    
def calculateDaysLeft(SDDBServer):
        log.debug('Calculating the days left for expiration')
        server_time = SDDBServer.xmlrpc_server.GetTimeStamp()
        server_date = date.fromtimestamp(server_time)
        first_run_date = GetFirstRunDate()
        daysLeft =  first_run_date + timedelta(days=DAYS_TRIAL) - server_date

        print "Days Left = %d" % daysLeft.days
        if daysLeft.days <= 0:
            return 0
        return daysLeft.days
        
class expirationDialog(QtGui.QDialog): 
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_ExpirationDialog()
        self.ui.setupUi(self)
        self._main  = parent
        settings = QSettings()
        QObject.connect(self.ui.buttonCancel, SIGNAL("clicked(bool)"), self.onButtonCancel)
        QObject.connect(self.ui.buttonRegister, SIGNAL("clicked(bool)"), self.onButtonRegister)
        QObject.connect(self.ui.buttonActivate, SIGNAL("clicked(bool)"), self.onButtonActivate)
        QObject.connect(self.ui.activation_email, SIGNAL("textChanged()"), self.onFieldsChanged)
        QObject.connect(self.ui.activation_fullname, SIGNAL("textChanged()"), self.onFieldsChanged)
        QObject.connect(self.ui.activation_licensekey, SIGNAL("textChanged()"), self.onFieldsChanged)
        
        
    def onButtonCancel(self):
        self.reject()
        
    def onButtonRegister(self):
        webbrowser.open( "http://www.subdownloader.net/", new=2, autoraise=1)
        
    def onFieldsChanged(self):
        if len(self.ui.activation_email.text()) and len(self.ui.activation_fullname.text()) and len(self.ui.activation_licensekey.text()):
            self.ui.buttonActivate.setEnabled(True)
        else:
            self.ui.buttonActivate.setEnabled(False)
    def onButtonActivate(self):
        email = unicode(self.ui.activation_email.text().toString())
        fullname = unicode(self.ui.activation_fullname.text().toString())
        licensekey  = unicode(self.ui.activation_licensekey.text().toString())
        self.window.setCursor(Qt.BusyCursor)
        result = self._main.SDDBServer.xmlrpc_server.CheckLicense(APP_VERSION,email, fullname, licensekey)
        self.window.setCursor(Qt.NormalCursor)

