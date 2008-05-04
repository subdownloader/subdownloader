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

import urllib
from xml.dom import minidom
#from subdownloader.modules import configuration

class SearchByName(object):
    
    def __init__(self):
        pass
        
    def search(self, moviename, sublanguageid="eng"):
        #xml_url = configuration.General.search_url % (sublanguageid, moviename)
        xml_url = "http://www.opensubtitles.com/en/search2/sublanguageid-%s/moviename-%s/xml"% (sublanguageid, moviename)
        raw_xml = urllib.urlopen(xml_url).read()
        search = self.parse_results(raw_xml)
        return search
    
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
        if not data:
            return []
        # catch all subtitles information
        for entry in data:
            try:
                sub = {}
                sub['IDSubtitle'] = entry.getElementsByTagName('IDSubtitle')[0].firstChild.data
                sub['MovieID'] = { 'Link': entry.getElementsByTagName('MovieID')[0].getAttribute('Link'), 
                                            'LinkImdb': entry.getElementsByTagName('MovieID')[0].getAttribute('LinkImdb')
                                            }
                sub['MovieThumb'] = entry.getElementsByTagName('MovieThumb')[0].firstChild.data
                sub['LinkUseNext'] = entry.getElementsByTagName('LinkUseNext')[0].firstChild.data
                sub['LinkZoozle'] = entry.getElementsByTagName('LinkZoozle')[0].firstChild.data
                sub['LinkTorrentbar'] = entry.getElementsByTagName('LinkTorrentbar')[0].firstChild.data
                sub['LinkBoardreader'] = entry.getElementsByTagName('LinkBoardreader')[0].firstChild.data
                sub['MovieName'] = entry.getElementsByTagName('MovieName')[0].firstChild.data
                sub['MovieYear'] = entry.getElementsByTagName('MovieYear')[0].firstChild.data
                sub['MovieImdbRating'] = entry.getElementsByTagName('MovieImdbRating')[0].firstChild.data
                sub['MovieImdbID'] = entry.getElementsByTagName('MovieImdbID')[0].firstChild.data
                sub['TotalSubs'] = entry.getElementsByTagName('TotalSubs')[0].firstChild.data
                sub['Newest'] = entry.getElementsByTagName('Newest')[0].firstChild.data
                result_entries.append(sub)
            except IndexError, e:
                pass
        return result_entries
