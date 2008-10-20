#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, SIGNAL
import PyQt4.QtCore as QtCore
from PyQt4.Qt import QApplication, QString, QFont, QAbstractListModel, \
                     QVariant, QAbstractTableModel, QTableView, QListView, \
                     QLabel, QAbstractItemView, QPixmap, QIcon, QSize, \
                     QSpinBox, QPoint, QPainterPath, QItemDelegate, QPainter, \
                     QPen, QColor, QLinearGradient, QBrush, QStyle, \
                     QByteArray, QBuffer, QMimeData, \
                     QDrag, QRect      

from modules.videofile import  VideoFile
from modules.subtitlefile import SubtitleFile
from modules.search import Movie

import languages.Languages as languages

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
    self.root=Node(QtCore.QVariant("")) 
    self.selectedNode = None
    self.languageFilter = None
    self.videoResultsBackup = None
    self.moviesResultsBackup = None
    #self.setupTree(self.root)

  def setVideos(self,videoResults,filter = None, append=False):
        log.debug("videotreeview::setVideos , len(videoResults) = %d " % len(videoResults))
        if append:
                self.videoResultsBackup += videoResults
        else:
                self.videoResultsBackup = videoResults
                
        if videoResults:
            for video in videoResults:
               videoNode = self.root.addChild(video)
               for sub in video._subs:
                   sub_lang_xxx =  sub.getLanguageXXX()
                   if (not filter) or (sub_lang_xxx in filter ) :    #Filter subtitles by Language
                       videoNode.addChild(sub)
                       
                       
  def setMovies(self,moviesResults,filter = None):
        self.moviesResultsBackup = moviesResults
            
        if moviesResults:
            for movie in moviesResults:
               movieNode = self.root.addChild(movie)
               if len(movie.subtitles): 
                    movieNode.data.totalSubs = 0 #We'll recount the number of subtitles after filtering
               for sub in movie.subtitles:
                   sub_lang_xxx =  sub.getLanguageXXX()
                   if (not filter) or (sub_lang_xxx in filter ) :    #Filter subtitles by Language
                       movieNode.addChild(sub)
                       movieNode.data.totalSubs +=  1
    
  def clearTree(self):
     log.debug("Clearing VideoTree")
     self.selectedNode = None
     self.languageFilter = None
     del self.root
     self.root=Node(QtCore.QVariant("")) 
     self.reset() #Better than emit the dataChanged signal
     
  def selectMostRatedSubtitles(self):
    for video in self.root.children:
          if len(video.children):
              subtitle = video.children[0] #We suppossed that the first subtitle is the most rated one
              subtitle.checked = True
              
  def unselectSubtitles(self):
      for video in self.root.children:
          for subtitle in video.children:
              subtitle.checked = False

  def setLanguageFilter(self, lang):
      #self.clearTree()
      self.languageFilter = lang
      if lang:
        lang = lang.split(",")
      if self.videoResultsBackup:
        self.setVideos(self.videoResultsBackup, lang)
      elif self.moviesResultsBackup:
        self.setMovies(self.moviesResultsBackup, lang)

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
        sub = data
        if role == QtCore.Qt.DecorationRole:
            if sub.isLocal():
                return QVariant(QIcon(':/images/flags/%s.png' % data.getLanguageXX()).pixmap(QSize(24, 24), QIcon.Disabled))
            else:
                return QVariant(QIcon(':/images/flags/%s.png' % data.getLanguageXX()).pixmap(QSize(24, 24), QIcon.Normal))
        
        if role == QtCore.Qt.ForegroundRole:
            if sub.isLocal():
                return QVariant(QColor(Qt.red))
        
        if role == QtCore.Qt.FontRole:
                return QVariant(QFont('Arial', 10, QFont.Bold)) 
            
        if role == QtCore.Qt.CheckStateRole:
            if index.internalPointer().checked:
                return  QVariant(Qt.Checked)
            else:
                return  QVariant(Qt.Unchecked)
            
        if role == QtCore.Qt.DisplayRole:
            uploader = data.getUploader()
            if not uploader : 
                uploader = 'Anonymous'
            if sub.isLocal():
                return QVariant(_("[%s]\t Rate: %s\t %s - (Already downloaded)") % (_(data.getLanguageName()) ,str(data.getRating()),   data.getFileName()))
            elif hasattr(sub, "_filename"): #Subtitle found from hash
                return QVariant(_("[%s]\t Rate: %s\t %s    - Uploader: %s") % (_(data.getLanguageName()) ,str(data.getRating()),   data.getFileName(), uploader))
            else: #Subtitle found from movie name
                return QVariant(_("[%s]\t Rate: %s\t Type: %s\t downloads: %d\t Cds = %d\tUploader: %s") % (_(sub.getLanguageName()),str(sub.getRating()),   sub.getExtraInfo('format').upper(),int(sub.getExtraInfo('totalDownloads')),int(sub.getExtraInfo('totalCDs')),  uploader))
        return QVariant()
    elif type(data)  == VideoFile: #It's a VIDEOFILE treeitem.
        if role == QtCore.Qt.ForegroundRole:
          return QVariant(QColor(Qt.blue))
        
        movie_info = data.getMovieInfo()
        if role == QtCore.Qt.DecorationRole:
            if movie_info :
                #TODO: Show this icon bigger.
                return QVariant(QIcon(':/images/imdb.png').pixmap(QSize(24, 24), QIcon.Normal))
            else:
                return QVariant()
        
        if role == QtCore.Qt.FontRole:
            return QVariant(QFont('Arial', 10, QFont.Bold)) 
            
        if role == QtCore.Qt.DisplayRole:
            if movie_info :
                #The ENGLISH Movie Name is priority, if not shown, then we show the original name.
                if movie_info["MovieNameEng"]:
                    movieName = movie_info["MovieNameEng"]
                else:
                    movieName = movie_info["MovieName"]
                    
                info = _("%s [%s] [IMDB rate=%s] - File: %s") %(movieName,  movie_info["MovieYear"], movie_info["MovieImdbRating"], data.getFileName())
                return QVariant(info)
            else:
                 return QVariant(data.getFileName())
                 
        return QVariant()
    elif type(data)  == Movie: #It's a MOVIE item
        if role == QtCore.Qt.ForegroundRole:
          return QVariant(QColor(Qt.blue))
        
        movie = data
        if role == QtCore.Qt.DecorationRole:
                return QVariant(QIcon(':/images/imdb.png'))
        
        if role == QtCore.Qt.FontRole:
            return QVariant(QFont('Arial', 10, QFont.Bold)) 
            
        if role == QtCore.Qt.DisplayRole:
            movieName = movie.MovieName
            info = _("%s [%s] - [IMDB rate=%s]  - (%d subs)") %(movie.MovieName,  movie.MovieYear, movie.IMDBRating, int(movie.totalSubs))
            if not len(movie.subtitles):
                pass #TODO: Show the PLUS icon to expand #info += " (Double Click here)"
            return QVariant(info)
           
        return QVariant()

  def flags(self, index):
    if not index.isValid():
      return Qt.ItemIsEnabled
    data = index.internalPointer().data
    if type(data)  == SubtitleFile: #It's a SUBTITLE treeitem.
        return Qt.ItemIsSelectable |Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
    elif type(data)  == VideoFile: #It's a VIDEO treeitem.
        return Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
    elif type(data)  == Movie: #It's a Movie  treeitem.
        return Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

  def getTopNodes(self):
      return [self.index(parentItem.row(), 0) for parentItem in self.root.children]
      
  def updateMovie(self, index, filter = None):
        movie = index.internalPointer().data
        movieNode = index.internalPointer()
        movieNode.children = []
        for sub in movie.subtitles:
            sub_lang_xxx =  sub.getLanguageXXX()
            if (not filter) or (filter == sub_lang_xxx) :    #Filter subtitles by Language
                   movieNode.addChild(sub)

  def getSelectedItem(self, index = None):
      if index == None: #We want to know the current Selected Item
        return self.selectedNode
        
      if not index.isValid():
            return None
      else:
            self.selectedNode = index.internalPointer()
            return index.internalPointer()
      
  def getCheckedSubtitles(self):
      checkedSubs = []
      for video in self.root.children:
          for subtitle in video.children:
                if subtitle.checked:
                    checkedSubs.append(subtitle.data)
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
    
    if row > len(parentItem.children) -1 :
      return QtCore.QModelIndex()
      
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
    #if parentItem == None:
        #return QtCore.QModelIndex()

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
    
    if type(parentItem.data)  == Movie:
        movie = parentItem.data
        if not len(movie.subtitles):
            if movie.totalSubs > 0: #To put a 0 in the future, the 1 is just to show it's working
                return 1 #movie.totalSubs (that way the scrollbar doesn't expand also)
            else:
                return 0
        return len(movie.subtitles)
    else:
        return len(parentItem.children)
