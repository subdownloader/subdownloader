from PyQt4.QtCore import Qt, SIGNAL
import PyQt4.QtCore as QtCore
from PyQt4.Qt import QApplication, QString, QFont, QAbstractListModel, \
                     QVariant, QAbstractTableModel, QTableView, QListView, \
                     QLabel, QAbstractItemView, QPixmap, QIcon, QSize, \
                     QSpinBox, QPoint, QPainterPath, QItemDelegate, QPainter, \
                     QPen, QColor, QLinearGradient, QBrush, QStyle, \
                     QByteArray, QBuffer, QMimeData, \
                     QDrag, QRect      

from subdownloader.videofile import  VideoFile
from subdownloader.subtitlefile import SubtitleFile
import images_rc
import logging
log = logging.getLogger("subdownloader.gui.videotreeview")

class Node:
  def __init__(self, data, parent=None):
    self.data=data
    self.checked = False
    self.parent=parent
    self.children=[]

  def addChild(self, data):
    node=Node(data, self)
    self.children.append(node)
    return node

  def row(self):
    if self.parent:
      return self.parent.children.index(self)
    else:
      return 0


class VideoTreeModel(QtCore.QAbstractItemModel):
  def __init__(self, parent=None):
    QtCore.QAbstractItemModel.__init__(self, parent)
    self.root=Node([QtCore.QVariant("")]) 
    self.checkedSubtitles = []
    #self.setupTree(self.root)

  def setVideos(self,videoResults):
    #TODO: Add context menus.
    for video in videoResults:
       videoNode = self.root.addChild(video)
       for sub in video._subs:
           videoNode.addChild(sub)
       
  def clearTree(self):
     log.debug("Clearing VideoTree")
     self.root.children = []

  def columnCount(self, parent):
    if parent.isValid():
      return 1 #Only 1 column
    else:
      # header
      return 1 #len(self.root.data) 

  def data(self, index, role):
    if not index.isValid():
      return QVariant()
    data = index.internalPointer().data
    
    if type(data)  == SubtitleFile: #It's a SUBTITLE treeitem.
        if role == QtCore.Qt.DecorationRole:
            return QVariant(QIcon(':/images/flags/%s.gif' % data.getLanguageXX() ))
            
        if role == QtCore.Qt.ForegroundRole:
            return QVariant(QColor(Qt.red))
            
        if role == QtCore.Qt.CheckStateRole:
            if index.internalPointer().checked:
                return  QVariant(Qt.Checked)
            else:
                return  QVariant(Qt.Unchecked)
            
        if role == QtCore.Qt.DisplayRole:
            return QVariant("[%s] %s" % (data.getLanguageName() ,  data.getFileName()))
            
        return QVariant()
    else: #It's a VIDEOFILE treeitem.
        if role == QtCore.Qt.FontRole:
          return QVariant(QFont('Arial', 10, QFont.Bold))
          
        if role == QtCore.Qt.DisplayRole:
            return QVariant(data.getFileName())
            
        return QVariant()

  def flags(self, index):
    if not index.isValid():
      return Qt.ItemIsEnabled

    return Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled

  def setData (self, index, value, role):
        #When user click to check the subtitle
        if role == Qt.CheckStateRole:
              node = index.internalPointer()
              if value == QVariant(Qt.Checked):
                 node.checked = True
              else:
                  node.checked = False
        else:
            print "Set data with no CheckStateRole"
        
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
        return True
   
  def getCheckedSubtitles(self):
      checkedSubs = []
      for video in self.root.children:
          for subtitle in video.children:
                if subtitle.checked:
                    log.debug("Checked = " + subtitle.data.getFileName() )
                    checkedSubs.append(subtitle.data)
      log.debug("Getting Checked Subtitles, total = %d" % len(checkedSubs))

      return checkedSubs
  def headerData(self, section, orientation, role):
  #  if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
     # return self.root.data[section]

    return QtCore.QVariant("") #Hide headers

  def index(self, row, column, parent):
    if row < 0 or column < 0 or row >= self.rowCount(parent) or column >= self.columnCount(parent):
      return QtCore.QModelIndex()

    if not parent.isValid():
      parentItem = self.root
    else:
      parentItem = parent.internalPointer()

    childItem = parentItem.children[row]
    if childItem:
      return self.createIndex(row, column, childItem)
    else:
      return QtCore.QModelIndex()

  def parent(self, index):
    if not index.isValid():
      return QtCore.QModelIndex()

    childItem = index.internalPointer()
    parentItem = childItem.parent

    if parentItem == self.root:
      return QtCore.QModelIndex()

    return self.createIndex(parentItem.row(), 0, parentItem)

  def rowCount(self, parent):
    if parent.column() > 0:
      return 0

    if not parent.isValid():
      parentItem = self.root
    else:
      parentItem = parent.internalPointer()

    return len(parentItem.children)
