#!/usr/bin/env python
# Copyright (c) 2010 SubDownloader Developers - See COPYING - GPLv3

from PyQt4.QtCore import Qt, SIGNAL,  QCoreApplication, QEventLoop, QSettings
from PyQt4.Qt import QApplication, QFont, QAbstractListModel, \
                     QAbstractTableModel, QTableView, QListView, \
                     QLabel, QAbstractItemView, QPixmap, QIcon, QSize, \
                     QSpinBox, QPoint, QPainterPath, QItemDelegate, QPainter, \
                     QPen, QColor, QLinearGradient, QBrush, QStyle, \
                     QByteArray, QBuffer, QMimeData, \
                     QDrag, QRect

from PyQt4.QtGui import QItemSelection

from FileManagement import get_extension, clear_string, without_extension
import FileManagement.VideoTools as VideoTools
import FileManagement.Subtitle as Subtitle
import languages.Languages as languages

from modules.videofile import  *
from modules.subtitlefile import *

import logging
log = logging.getLogger("subdownloader.gui.uploadlistview")

class UploadListModel(QAbstractTableModel):

    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self._data = None
        self._subs = [None]
        self._videos = [None]
        self._headers = [_("Videofile"), _("Subtitle")]
        self._main = None
        self.rowsSelected = None

    def dropMimeData(self, data, action, row, column, parent):
        print(row,column)

    def flags(self, index):
        flags = QAbstractTableModel.flags(self, index)
        if index.isValid():
            if index.row() == 0:
                flags |= Qt.ItemIsDropEnabled
        return flags

    def addVideos(self,index,videos):
        for video in videos:
                if len(self._videos) <= index:
                        self._videos.insert(index,video)
                        self._subs.insert(index, None)
                else:
                        self._videos[index] = video

                if index == 0:
                        self._main.emit(SIGNAL('release_updated(QString)'),self.calculateReleaseName(video.getFilePath()))

                index += 1

    def calculateReleaseName(self, filepath):
        try:
            releaseName = os.path.split(os.path.dirname(filepath))[-1]
            if len(releaseName) > 9: # this way we avoid short names like CD1 or Videos, but we accept names like DVDRIP-aXXo , etc
                return releaseName
            else:
                return ""
        except:
            return ""

    def addSubs(self,index,subs ):
        for sub in subs:
                if len(self._subs) <= index:
                    self._subs.insert(index,sub)
                    self._videos.insert(index, None)
                else:
                    self._subs[index] = sub
                index += 1

    def validate(self):
        if not self.getTotalRows() or self.getTotalRows() == 1 and not self._subs[0] and not self._videos[0]:
            return False ,_('The list of video/subtitle is empty')

        valid_subs = []
        valid_videos = []
        for i in range(self.getTotalRows()):
            if self._subs[i]:
                if valid_subs.count(self._subs[i].getFilePath()) > 0:
                    return False ,_('Subtitle %s is repeated') % str(i +1)
                else:
                    valid_subs.append(self._subs[i].getFilePath())
            if self._videos[i]:
                if valid_videos.count(self._videos[i].getFilePath()) > 0:
                    return False ,_('Videofile %s is repeated') % str(i +1)
                else:
                    valid_videos.append(self._videos[i].getFilePath())

            if not self._subs[i] and not self._videos[i] :
               if i != self.getTotalRows()-1:
                    return False ,_('Some of the upload rows are empty')
               else:
                   return True, ""

            if not self._subs[i] or not self._videos[i]  and i != self.getTotalRows()-1:
                return False ,_('Some of the video/subtitles fields are empty')

        return True, ""

    def ObtainUploadInfo(self):
        #Trying to autodetect the imdb fro m the server
        videos = []
        for i, video in enumerate(self._videos):
            if self._videos[i] != None and self._subs[i] != None:
                tmp_video = VideoFile(video.getFilePath())
                tmp_video.setSubtitles([self._subs[i]])
                videos.append(tmp_video)
        if videos:
            results = self._main.OSDBServer.TryUploadSubtitles(videos, no_update = True)
            video_imdb = None
            if results['alreadyindb'] == 0 and results['data']:
                video_imdb =  self._main.OSDBServer.getBestImdbInfo(results['data'])
            elif results['alreadyindb'] == 1:
                #import pprint
                #pprint.pprint(results)
                video_imdb = {"IDMovieImdb": results['data']["IDMovieImdb"], "MovieName": results['data']["MovieName"]}
                if 'SubLanguageId' in results['data']:
                    xxx_lang = results['data']['SubLanguageID']
                    self._main.uploadLanguages.emit(SIGNAL('language_updated(QString,QString)'),xxx_lang, "database")
            if video_imdb:
                     self._main.emit(SIGNAL('imdbDetected(QString,QString,QString)'),video_imdb["IDMovieImdb"], video_imdb["MovieName"], "database")

        self.AutoDetectLangFromFileName()
        self.AutoDetectLangFromContent()

    def AutoDetectLangFromFileName(self):
        all_langs = []
        xxx_lang = ""
        for sub in self._subs:
            if sub:
                lang = sub.getLanguage()
                if lang == None:
                    lang = Subtitle.GetLangFromFilename(sub.getFilePath())
                    if len(lang)  == 2 and lang in languages.ListAll_xx():
                        all_langs.append(languages.xx2xxx(lang))
                    elif len(lang) == 3 and lang in languages.ListAll_xxx():
                        all_langs.append(lang)
                else:
                    all_langs.append(lang)

        max = 0
        max_lang = ""
        for lang in all_langs:
            if all_langs.count(lang) > max:
                max = all_langs.count(lang)
                max_lang = lang

        xxx_lang = max_lang
        log.debug("Majoritary Language Autodetected by filename = " + str(xxx_lang))
        if xxx_lang:
            self._main.uploadLanguages.emit(SIGNAL('language_updated(QString,QString)'),xxx_lang, "filename")

    def AutoDetectLangFromContent(self):
        all_langs = []
        for sub in self._subs:
            if sub:
                lang = sub.getLanguage()
                if lang == None:
                    lang = Subtitle.AutoDetectLang(sub.getFilePath())
                    sub.setLanguage(lang)
                all_langs.append(lang)
#FIXME: Clean this code here and put it in a shared script for also CLI to use
        max = 0
        max_lang = ""
        for lang in all_langs:
            if all_langs.count(lang) > max:
                max = all_langs.count(lang)
                max_lang = lang

        xxx_lang = languages.name2xxx(max_lang)
        log.debug("Majoritary Language Autodetected by content = " + str(xxx_lang))
        if xxx_lang:
            self._main.uploadLanguages.emit(SIGNAL('language_updated(QString,QString)'),xxx_lang, "content")

    def getTotalRows(self):
        return self.rowCount(None)

    def rowCount(self, index):
           return max(len(self._subs), len(self._videos))

    def columnCount(self, parent):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return ""
        text = ""
        if orientation == Qt.Horizontal:
            text = self._headers[section]
            return text #self.trUtf8(text))
        else:
            return "CD" + str(1+section)

    def data(self, index, role):
        row, col = index.row(), index.column()

        if role == Qt.DisplayRole:
            text = None
            if   col == UploadListView.COL_VIDEO:
                if self._videos[row] == None:
                    text = _("Click here to select video...")
                else:
                        text = self._videos[row].getFileName()
            elif col == UploadListView.COL_SUB:
                if self._subs[row] == None:
                    text = _("Click here to select subtitle...")
                else:
                        text = self._subs[row].getFileName()
            if text == None:
                text = "Unknown"
            return text

        return None

    def onUploadButtonPlusRow(self, clicked):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        if(self.rowsSelected != None):
             self._videos.insert(self.rowsSelected[0] +1, None)
             self._subs.insert(self.rowsSelected[0] +1, None)
        else:
            self._videos.append(None)
            self._subs.append(None)
        self.emit(SIGNAL("layoutChanged()"))
        self._main.updateButtonsUpload()

    def onUploadButtonMinusRow(self, clicked):
         if self.rowsSelected != None:
            self.emit(SIGNAL("layoutAboutToBeChanged()"))

            rowsSelected = self.rowsSelected
            rowsSelected.sort(reverse=True)

            for row in rowsSelected:
                    try:
                        del self._videos[row]
                        del self._subs[row]
                    except:
                        pass
            self.emit(SIGNAL("layoutChanged()"))
            if self.rowsSelected[0] > 0:
                previousRowSelection = QItemSelection(self.createIndex(self.rowsSelected[0] -1, UploadListView.COL_VIDEO),self.createIndex(self.rowsSelected[0] -1, UploadListView.COL_SUB))
                self._main.uploadSelectionModel.select(previousRowSelection, self._main.uploadSelectionModel.ClearAndSelect)
            #elif not len(self._videos):
                #print "last row"

            self._main.updateButtonsUpload()

    def onUploadButtonUpRow(self, clicked):
        if self.rowsSelected != None:
            self.emit(SIGNAL("layoutAboutToBeChanged()"))
            rowSelected = self.rowsSelected[0]
            if rowSelected != 0:
                temp = self._videos[rowSelected]
                self._videos[rowSelected] = self._videos[rowSelected -1]
                self._videos[rowSelected - 1] = temp

                temp = self._subs[rowSelected]
                self._subs[rowSelected] = self._subs[rowSelected -1]
                self._subs[rowSelected - 1] = temp
            self.emit(SIGNAL("layoutChanged()"))
            previousRowSelection = QItemSelection(self.createIndex(rowSelected -1, UploadListView.COL_VIDEO),self.createIndex(rowSelected-1, UploadListView.COL_SUB))
            self._main.uploadSelectionModel.select(previousRowSelection, self._main.uploadSelectionModel.ClearAndSelect)

        self._main.updateButtonsUpload()

    def onUploadButtonDeleteAllRow(self):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.removeAll()
        self.emit(SIGNAL("layoutChanged()"))

    def onUploadButtonDownRow(self, clicked):
        if self.rowsSelected != None:
            self.emit(SIGNAL("layoutAboutToBeChanged()"))
            rowSelected = self.rowsSelected[0]
            if rowSelected != self.getTotalRows() -1:
                temp = self._videos[rowSelected]
                self._videos[rowSelected] = self._videos[rowSelected +1]
                self._videos[rowSelected + 1] = temp

                temp = self._subs[rowSelected]
                self._subs[rowSelected] = self._subs[rowSelected +1]
                self._subs[rowSelected + 1] = temp

            self.emit(SIGNAL("layoutChanged()"))
            nextRowSelection = QItemSelection(self.index(rowSelected +1 , UploadListView.COL_VIDEO),self.index(rowSelected +1, UploadListView.COL_SUB))
            self._main.uploadSelectionModel.select(nextRowSelection, self._main.uploadSelectionModel.ClearAndSelect)
        self._main.updateButtonsUpload()

    def removeAll(self):
         self._videos = [None, None]
         self._subs = [None, None]

class UploadListView(QTableView):
    COL_VIDEO = 0
    COL_SUB = 1
    def __init__(self, parent):
        QTableView.__init__(self, parent)
        self.setAcceptDrops(True)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("text/plain")  or event.mimeData().hasFormat("text/uri-list"):
                event.accept()
        else:
                event.ignore()
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/plain")  or event.mimeData().hasFormat("text/uri-list"):
                event.accept()
        else:
                event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            paths = [str(u.toLocalFile().toUtf8()) for u in event.mimeData().urls()]
            fileName = paths[0] #If we drop many files, only the first one will be take into acount
            index = self.indexAt(event.pos())
            row, col = index.row(), index.column()
            settings = QSettings()
            if col == UploadListView.COL_VIDEO:
                if(VideoTools.isVideofile(fileName)):
                    settings.setValue("mainwindow/workingDirectory", fileName)
                    video = VideoFile(fileName)
                    self.model().emit(SIGNAL("layoutAboutToBeChanged()"))
                    self.model().addVideos(row, [video])
                    subtitle = Subtitle.AutoDetectSubtitle(video.getFilePath())
                    if subtitle:
                        sub = SubtitleFile(False,subtitle)
                        self.model().addSubs(row, [sub])
                        thread.start_new_thread(self.uploadModel.ObtainUploadInfo, ())
                    self.resizeRowsToContents()
                    self.model().emit(SIGNAL("layoutChanged()"))
            else: #if it's the column in SUBTITLES
                print(fileName)
                if(Subtitle.isSubtitle(fileName)):
                    settings.setValue("mainwindow/workingDirectory", fileName)
                    sub = SubtitleFile(False, fileName)
                    self.model().emit(SIGNAL("layoutAboutToBeChanged()"))
                    self.model().addSubs(row, [sub])
                    self.resizeRowsToContents()
                    self.model().emit(SIGNAL("layoutChanged()"))
                    thread.start_new_thread(self.uploadModel.ObtainUploadInfo, ())
