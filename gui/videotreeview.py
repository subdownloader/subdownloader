from PyQt4.QtCore import Qt, SIGNAL
import PyQt4.QtCore as QtCore
from PyQt4.Qt import QApplication, QString, QFont, QAbstractListModel, \
                     QVariant, QAbstractTableModel, QTableView, QListView, \
                     QLabel, QAbstractItemView, QPixmap, QIcon, QSize, \
                     QSpinBox, QPoint, QPainterPath, QItemDelegate, QPainter, \
                     QPen, QColor, QLinearGradient, QBrush, QStyle, \
                     QByteArray, QBuffer, QMimeData, \
                     QDrag, QRect      

import subdownloader.videofile as videofile

class Node:
  def __init__(self, data, parent=None):
    self.data=data
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
    self.setupTree(self.root)

  def setupTree(self, node):
    current=node.addChild([self.trUtf8("aa")])
    current=current.addChild([self.trUtf8("bb")])

    current.addChild([self.trUtf8("cc")])
    current.addChild([self.trUtf8("dd")])
    current.addChild([self.trUtf8("ee")])
    current.addChild([self.trUtf8("ff")])
   
  def clearTree(self):
     self.root.data = []
  def columnCount(self, parent):
    if parent.isValid():
      # parent.internalPointer()
      return len(parent.internalPointer().data)
    else:
      # header
      return len(self.root.data)

  def data(self, index, role):
    if not index.isValid():
      return QtCore.QVariant()

    if role != QtCore.Qt.DisplayRole:
      return QtCore.QVariant()

    return QtCore.QVariant(index.internalPointer().data[index.column()])

  def flags(self, index):
    if not index.isValid():
      return QtCore.Qt.ItemIsEnabled

    return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

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
