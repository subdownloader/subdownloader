from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.Qt import QApplication, QString, QFont, QAbstractListModel, \
                     QVariant, QAbstractTableModel, QTableView, QListView, \
                     QLabel, QAbstractItemView, QPixmap, QIcon, QSize, \
                     QSpinBox, QPoint, QPainterPath, QItemDelegate, QPainter, \
                     QPen, QColor, QLinearGradient, QBrush, QStyle, \
                     QByteArray, QBuffer, QMimeData, \
                     QDrag, QRect      

import subdownloader.videofile as videofile
import subdownloader.languages.Languages as languages

class SubOsdbListModel(QAbstractTableModel):
    
    TIME_READ_FMT = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self._subs = []
        self._headers = ["Language","SubFile"]  
    
    def setSubs(self,subs):
        self._subs = subs

    def dropMimeData(self, data, action, row, column, parent):
        print row,column 
    
    def rowCount(self, parent): 
        return len(self._subs)
        
    def columnCount(self, parent): 
        return len(self._headers)
    
    def headerData(self, section, orientation, role): 
        if role != Qt.DisplayRole:
            return QVariant()
        text = ""
        if orientation == Qt.Horizontal:      
            text = self._headers[section]
            return QVariant(self.trUtf8(text))
        return QVariant()
    
    def id_from_index(self, index): return self._subs[index.row()]
    def getSubFromRow(self, row): return self._subs[row]

    def flags(self, index):
        flags = QAbstractTableModel.flags(self, index)   
        return flags
    
    def data(self, index, role):
        row, col = index.row(), index.column()
        
        COL_LANG = 0
        COL_NAME = 1
        
        if role == Qt.DisplayRole:      
            text = None
            sub = self._subs[row]
            
            if col == COL_LANG:
                lang_xx= languages.xxx2xx(sub.getLanguage())
                lang_name = languages.xxx2name(sub.getLanguage())
            
        #image_file = lang_xx + '.gif'
        #icon = QtGui.QIcon(":/images/flags/" + image_file)
        #item_sub.setIcon(0,icon)
        
                text = lang_name
            if col == COL_NAME:
                text = sub.getFileName()
            if text == None: 
                text = "Unknown"
            return QVariant(text)
        
        elif role == Qt.ToolTipRole and index.isValid():
                if index.column() in [0,1]:
                    edit = "<b>COMMENTS</b> here.<br>"
                return QVariant(edit)
            
        return QVariant()
    
class SubOsdbListView(QTableView):
    def __init__(self, parent):    
        QTableView.__init__(self, parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        #self.setSortingEnabled(True)
        #self.setItemDelegate(LibraryDelegate(self, rating_column=4))
    
    #def dragEnterEvent(self, event):
        #print event.mimeData()
    
    def dropEvent(self, event):
        #event.setDropAction(Qt.IgnoreAction)
        #event.accept()
        md = event.mimeData()
        if md.hasFormat('application/x-qabstractitemmodeldatalist'):
            index = self.indexAt(event.pos())
            if index.isValid():
                a = md.data('application/x-qabstractitemmodeldatalist')
                print index.row(), index.column()
        
        
    def start_drag(self, pos):    
        index = self.indexAt(pos)
        if index.isValid():
            print index
            #rows = frozenset([ index.row() for index in self.selectedIndexes()])
            #files = self.model().extract_formats(rows)            
            #drag = self.drag_object_from_files(files)
            #if drag:
                #ids = [ str(self.model().id_from_row(row)) for row in rows ]
                #drag.mimeData().setData("application/x-libprs500-id", \
                        #QByteArray("\n".join(ids)))
                #drag.start()
    
    
    def files_dropped(self, files, event):
        if not files: return
        index = self.indexAt(event.pos())    
        if index.isValid():
            self.model().add_formats(files, index)      
        else: self.emit(SIGNAL('books_dropped'), files)      
