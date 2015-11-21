#!/usr/bin/env python
# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

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
                    if int(each) != 0:
                        true = 0
                return true
            elif len(vl1) == 0 and len(vl2) >= 1:
                true = 1
                for each in vl2:
                    if int(each) != 0:
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
    print(serialkey)
