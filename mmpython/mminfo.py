
#if 0
# -----------------------------------------------------------------------
# $Id: mminfo,v 1.4 2004/05/28 12:26:24 dischi Exp $
# -----------------------------------------------------------------------
# $Log: mminfo,v $
# Revision 1.4  2004/05/28 12:26:24  dischi
# Replace __str__ with unicode to avoid bad transformations. Everything
# inside mmpython should be handled as unicode object.
#
# Revision 1.3  2004/05/24 12:54:35  dischi
# debug update
#
# Revision 1.2  2004/05/17 19:10:57  dischi
# better DEBUG handling
#
# Revision 1.1  2004/05/17 19:00:58  dischi
# rename mediatest.py to mminfo and install it as script to bin
#
#
# -----------------------------------------------------------------------
# MMPython - Media Metadata for Python
# Copyright (C) 2003 Thomas Schueppel, Dirk Meyer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
# 
# -----------------------------------------------------------------------
#endif


import sys
import os

# add .. for source usage
sys.path = ['..'] + sys.path


print 'mmpython media info'

#if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
    #print
    #print 'usage: mminfo [options] files'
    #print
    #print 'options:'
    #print '  -d   turn on debug information. For complete debug set -d 2'
    #print
    #print 'A file can be a normal file, a device for VCD/VCD/AudioCD'
    #print
    #print 'Examples:'
    #print '  mminfo foo.avi bar.mpg'
    #print '  mminfo /dev/dvd'
    #print
    #sys.exit(0)

## turn on debug
#if sys.argv[1] == '-d':
    #try:
        #int(sys.argv[2])
        #os.environ['MMPYTHON_DEBUG'] = sys.argv[2]
        #sys.argv = sys.argv[2:]
    #except:
        #os.environ['MMPYTHON_DEBUG'] = '1'
        #sys.argv = sys.argv[1:]
    
from mmpython import *
#sys.argv[1] = "D:\divx\Al.Sur.De.Granada.avi"

for file in sys.argv[1:]:
    medium = parse(file)
    print
    if len(file) > 70:
        print "filename : %s[...]%s" % (file[:30], file[len(file)-30:])
    else:
        print "filename : %s" % file
    if medium:
        print unicode(medium).encode('latin-1', 'replace')
        print
        print
    else:
        print "No Match found"
