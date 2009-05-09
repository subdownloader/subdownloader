#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) 2007-2009 Ivan Garcia capiscuas@gmail.com
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    see <http://www.gnu.org/licenses/>.

def compVer(ver1,ver2):
    #Checks to see if ver1 >= ver2
    vl1 = ver1.split('.')
    vl2 = ver2.split('.')
    while 1:
        if int(vl1[0]) > int(vl2[0]):
            return 1
        elif int(vl1[0]) == int(vl2[0]):
            del vl1[0]
            del vl2[0]
            if len(vl1) >= 1 and len(vl2) == 0:
                true = 1
                for each in vl1:
                    if int(each) <> 0:
                        true = 0
                return true
            elif len(vl1) == 0 and len(vl2) >= 1:
                true = 1
                for each in vl2:
                    if int(each) <> 0:
                        true = 0
                return true
            elif len(vl1) == 0 and len(vl2) == 0:
                return 1
            else:
                continue
        elif int(vl1[0]) < int(vl2[0]):
            return 0

def randomSerialKey():
    import string 
    from random import Random
    d = ''.join( Random().sample(string.letters+string.digits, 16) )
    serialkey =  "-".join([d[0:4], d[4:8], d[8:12], d[12:]]).upper()
    print serialkey
