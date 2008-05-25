#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Copyright (C) 2007 Ivan Garcia <contact@ivangarcia.org>
##    This program is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License along
##    with this program; if not, write to the Free Software Foundation, Inc.,
##    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import urllib2
from xml.dom import minidom
import xml.parsers.expat
#from subdownloader.modules import configuration

class SearchByName(object):
    
    def __init__(self):
        pass
        
    def search_movie(self, moviename, sublanguageid="eng"):
        #xml_url = configuration.General.search_url % (sublanguageid, moviename)
        xml_url = "http://www.opensubtitles.com/en/search2/sublanguageid-%s/moviename-%s/xml"% (sublanguageid, moviename)
        xml_page = urllib2.urlopen(xml_url)
        try:
            search = self.parse_results(xml_page.read())
        except xml.parsers.expat.ExpatError: # this will happen when only one result is found
            search = self.parse_results(urllib2.urlopen(xml_page.url + "/xml").read())
        if not search:
            search = self.subtitle_info(urllib2.urlopen(xml_page.url + "/xml").read())
            
        return search
        
    def subtitle_info(self, raw_xml):
        dom = minidom.parseString(raw_xml) #Make the dom from raw xml
        entries=dom.getElementsByTagName('opensubtitles') #Pull out all entry's
        subtitle_entries=[] #Make an empty container to fill up and return
        data=None
        for entry in entries:
            if entry.getElementsByTagName('SubBrowse'):
                for result in entry.getElementsByTagName('SubBrowse'):
                    if result.getElementsByTagName('Subtitle'):
                        data = result.getElementsByTagName('Subtitle')
                        break
                break
        #print "data=", data
        if not data:
            return []
        # catch subtitle information
        for entry in data:
            sub = {}
            if entry.getElementsByTagName('LinkDetails'):
                sub['LinkDetails'] = entry.getElementsByTagName('LinkDetails')[0].firstChild.data
            if entry.getElementsByTagName('IDSubtitle'):
                sub['IDSubtitle'] = { 'IDSubtitle': entry.getElementsByTagName('IDSubtitle')[0].firstChild.data, 
                                                    'Link': entry.getElementsByTagName('IDSubtitle')[0].getAttribute('Link'), 
                                                }
            if entry.getElementsByTagName('MovieReleaseName'):
                sub['MovieReleaseName'] = entry.getElementsByTagName('MovieReleaseName')[0].firstChild.data
            if entry.getElementsByTagName('SubFormat'):
                sub['SubFormat'] = entry.getElementsByTagName('SubFormat')[0].firstChild.data
            if entry.getElementsByTagName('SubSumCD'):
                sub['SubSumCD'] = entry.getElementsByTagName('SubSumCD')[0].firstChild.data
            if entry.getElementsByTagName('SubAuthorComment'):
                sub['SubAuthorComment'] = entry.getElementsByTagName('SubAuthorComment')[0].firstChild.data
            if entry.getElementsByTagName('SubAddDate'):
                sub['SubAddDate'] = entry.getElementsByTagName('SubAddDate')[0].firstChild.data
            if entry.getElementsByTagName('SubSumVotes'):
                sub['SubSumVotes'] = entry.getElementsByTagName('SubSumVotes')[0].firstChild.data
            if entry.getElementsByTagName('SubRating'):
                sub['SubRating'] = entry.getElementsByTagName('SubRating')[0].firstChild.data
            if entry.getElementsByTagName('SubDownloadsCnt'):
                sub['SubDownloadsCnt'] = entry.getElementsByTagName('SubDownloadsCnt')[0].firstChild.data
            if entry.getElementsByTagName('UserNickName'):
                sub['UserNickName'] = entry.getElementsByTagName('UserNickName')[0].firstChild.data
            if entry.getElementsByTagName('LanguageName'):
                sub['LanguageName'] = entry.getElementsByTagName('LanguageName')[0].firstChild.data
                
            if entry.getElementsByTagName('SubtitleFile'):
                SubtitleFile = {}
                _SubtitleFile = entry.getElementsByTagName('SubtitleFile')[0]
                _File = _SubtitleFile.getElementsByTagName('File')[0]
                SubtitleFile['File'] = {'ID': _SubtitleFile.getElementsByTagName('File')[0].getAttribute('ID'), 
                                                'SubActualCD': {'SubActualCD':_File.getElementsByTagName('SubActualCD')[0].firstChild.data, 
                                                                        'SubSize': _File.getElementsByTagName('SubActualCD')[0].getAttribute('Link'), 
                                                                        'MD5': _File.getElementsByTagName('SubActualCD')[0].getAttribute('MD5'), 
                                                                        'SubFileName': _File.getElementsByTagName('SubActualCD')[0].getAttribute('SubFileName'), 
                                                                        'DownloadLink': _File.getElementsByTagName('SubActualCD')[0].getAttribute('DownloadLink'),  
                                                                        }, 
                                                'SubPreview': _File.getElementsByTagName('SubPreview')[0].firstChild.data
                                                }
                SubtitleFile['Download'] = {'Download': _SubtitleFile.getElementsByTagName('Download')[0].firstChild.data, 
                                                        'DownloadLink': _SubtitleFile.getElementsByTagName('Download')[0].getAttribute('DownloadLink'),  
                                                        }
                sub['SubtitleFile'] = SubtitleFile
            if entry.getElementsByTagName('FullName'):
                sub['FullName'] = entry.getElementsByTagName('FullName')[0].firstChild.data
            if entry.getElementsByTagName('ReportLink'):
                sub['ReportLink'] = entry.getElementsByTagName('ReportLink')[0].firstChild.data
            # just s shortcut
            sub['DownloadLink'] = sub['SubtitleFile']['File']['SubActualCD']['DownloadLink']
            print sub
            
            if sub:
                subtitle_entries.append(sub)
        return subtitle_entries
            
    def parse_results(self, raw_xml):
        """Parse the xml and return a list of dictionaries like:
            [   {'IDSubtitle': 'foo', 
                    'LinkUseNext': 'foo', 
                    'MovieName': 'foo_movie',
                    ...
                }, 
                {'IDSubtitle': 'foo', 
                    'LinkUseNext': 'foo', 
                    'MovieName': 'foo_movie',
                    ...
                }, 
                ...]
        """
        dom = minidom.parseString(raw_xml) #Make the dom from raw xml
        entries=dom.getElementsByTagName('opensubtitles') #Pull out all entry's
        result_entries=[] #Make an empty container to fill up and return
        data = None
        # fetch the wanted result xml node
        for entry in entries:
            if len(entry.getElementsByTagName('results')) > 0:
                for result in entry.getElementsByTagName('results'):
                    if len(result.getElementsByTagName('subtitle')) > 0:
                        data = result.getElementsByTagName('subtitle')
                        break
                break
        #print "data=", data
        if not data:
            return []
        # catch all subtitles information
        for entry in data:
            try:
                sub = {}
                if entry.getElementsByTagName('IDSubtitle'):
                    sub['IDSubtitle'] = { 'IDSubtitle': entry.getElementsByTagName('IDSubtitle')[0].firstChild.data, 
                                                        'Link': entry.getElementsByTagName('IDSubtitle')[0].getAttribute('Link'), 
                                                        'LinkImdb': entry.getElementsByTagName('IDSubtitle')[0].getAttribute('LinkImdb'), 
                                                        'DownloadLink': entry.getElementsByTagName('IDSubtitle')[0].getAttribute('DownloadLink'), 
                                                        'uuid': entry.getElementsByTagName('IDSubtitle')[0].getAttribute('uuid'), 
                                                    }
                if entry.getElementsByTagName('MovieID'):
                    sub['MovieID'] = entry.getElementsByTagName('MovieID')[0].firstChild.data
                if entry.getElementsByTagName('MovieThumb'):
                    sub['MovieThumb'] = entry.getElementsByTagName('MovieThumb')[0].firstChild.data
                if entry.getElementsByTagName('LinkUseNext'):
                    sub['LinkUseNext'] = entry.getElementsByTagName('LinkUseNext')[0].firstChild.data
                if entry.getElementsByTagName('LinkZoozle'):
                    sub['LinkZoozle'] = entry.getElementsByTagName('LinkZoozle')[0].firstChild.data
                if entry.getElementsByTagName('LinkTorrentbar'):
                    sub['LinkTorrentbar'] = entry.getElementsByTagName('LinkTorrentbar')[0].firstChild.data
                if entry.getElementsByTagName('LinkBoardreader'):
                    sub['LinkBoardreader'] = entry.getElementsByTagName('LinkBoardreader')[0].firstChild.data
                if entry.getElementsByTagName('MovieName'):
                    sub['MovieName'] = entry.getElementsByTagName('MovieName')[0].firstChild.data
                if entry.getElementsByTagName('MovieYear'):
                    sub['MovieYear'] = entry.getElementsByTagName('MovieYear')[0].firstChild.data
                if entry.getElementsByTagName('MovieImdbRating'):
                    sub['MovieImdbRating'] = entry.getElementsByTagName('MovieImdbRating')[0].firstChild.data
                if entry.getElementsByTagName('MovieImdbID'):
                    sub['MovieImdbID'] = entry.getElementsByTagName('MovieImdbID')[0].firstChild.data
                if entry.getElementsByTagName('TotalSubs'):
                    sub['TotalSubs'] = entry.getElementsByTagName('TotalSubs')[0].firstChild.data
                if entry.getElementsByTagName('Newest'):
                    sub['Newest'] = entry.getElementsByTagName('Newest')[0].firstChild.data
                if sub:
                    result_entries.append(sub)
            except IndexError, e:
                pass
        return result_entries
