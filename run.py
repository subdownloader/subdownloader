##    Copyright (C) 2007 Ivan Garcia contact@ivangarcia.org
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

# this will allow logic imports
import sys, os,  logging
sys.path.append(os.path.dirname(os.getcwd()))

# simple aplication starter
import gui.main

#d = {'hoy': '123', 'clientip': '192.168.0.1', 'user': 'ivan'}
#FORMAT = "%(asctime)-30s %(clientip)s %(levelname)s:%(name)s %(message)s"
#FORMAT = "hoy-15s %(clientip)s %(user)-8s %(message)s"
"""
CRITICAL 	50
ERROR 	40
WARNING 	30
INFO 	20
DEBUG 	10
NOTSET 	0
"""
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "[%(asctime)s] %(levelname)s::%(name)s # %(message)s"

logging.basicConfig(level=LOG_LEVEL,
                    format=LOG_FORMAT,
                     datefmt='%y-%m-%d %H:%M',
                    #uncomment next two lines if we want logging into a file
                    #filename='/tmp/subdownloader.log',
                    #filemode='w',
                    )

# create the root logger named 'subdownloader' 
# consequent ones should follow its parent as. 'subdownloader.package.foo'
log = logging.getLogger("subdownloader")

if __name__ == "__main__": 
    log.info('Subdownloader starting...')
    #sys.stdout.write("Subdownloader running... "); sys.stdout.flush()
    gui.main.main()
    log.info('Subdownloader closed for construction.')
    #sys.stdout.write("stopped!\n"); sys.stdout.flush()
