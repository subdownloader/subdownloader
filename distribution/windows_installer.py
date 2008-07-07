#!/usr/bin/env python
# -*- coding: utf8 -*-

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

import os, sys
(parent, current) = os.path.split(os.path.dirname(os.getcwd()))
sys.path.insert(0, os.path.dirname(parent))

from distutils.core import setup
import py2exe
import glob
import traceback, subprocess

if len(sys.argv) == 1:
    sys.argv.append("py2exe")

from subdownloader import APP_TITLE, APP_VERSION
print sys.path



def py2exe():
    sys.argv[1:2] = ['py2exe']
    sys.argv.append ( "--verbose" ) 
    print sys.argv
    
    setup(name=APP_TITLE,
        version=APP_VERSION,
        description='Find Subtitles for your Videos',
        author='Ivan Garcia',
        author_email='contact@ivangarcia.org',
        url='http://www.subdownloader.net',
        #includes=['FileManagement', 'cli', 'gui', 'languages', 'modules'],
        package_dir={'subdownloader':'.'},
        zipfile = None, 
        #icon='psctrl/data/pyslovar/icon.ico',
        data_files=[
                    ('gui/images', ['gui/images/splash.png']),#glob.glob('gui/images/*.png')+glob.glob('gui/images/*.ico')+glob.glob('gui/images/*.jpg')+['gui/images/subd_splash.gif']),
                    #('gui/images/flags', glob.glob('gui/images/flags/*.gif')),
                    ('languages/lm', glob.glob('languages/lm/*.lm')),
                    ('', ['README'])
        ],
        windows=[{
                        'script':'run.py', 
                        'icon_resources':[(1, 'gui/images/icon32.ico')]}], 
        console=[{'script':'build_tarball.py'}], 
        options = { 'py2exe' : {'compressed': 1,
                                      'optimize'  : 2, 
                                      'includes'  : [
                                                 'sip', 
                                                 'subdownloader.modules.configuration.*'
                                                 ],
                                      'excludes'  : ["Tkconstants", "Tkinter", "tcl",
                                                     "_imagingtk", "ImageTk", "FixTk"
                                                    ],
                                       #'bundle_files': 1, 
                                       }
                        }
        )

class NSISInstaller(object):
    TEMPLATE = r'''
; The name of the installer

!define PRODUCT_NAME "%(name)s"
!define PRODUCT_VERSION "%(version)s"
Name "${PRODUCT_NAME}"
; The file to write
OutFile "%(outpath)s\${PRODUCT_NAME}-${PRODUCT_VERSION}.exe"

; The default installation directory
InstallDir $PROGRAMFILES\${PRODUCT_NAME}

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\${PRODUCT_NAME}" "Install_Dir"

;--------------------------------
; Pages
Page components
Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles
;--------------------------------
; The stuff to install
Section "${PRODUCT_NAME} (required)"
  SectionIn RO

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  ; Put file there
  File /r dist\*.*
  
  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\${PRODUCT_NAME} "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "NoRepair" 1
  WriteUninstaller "uninstall.exe"
  
SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\run.exe" "" "$INSTDIR\run.exe" 0
SectionEnd

; Uninstaller
Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
  DeleteRegKey HKLM SOFTWARE\${PRODUCT_NAME}

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\*.*"

  ; Remove directories used
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
  RMDir /r "$INSTDIR"

SectionEnd
    '''
    def __init__(self, name, py2exe_dir, output_dir):
        self.installer = self.__class__.TEMPLATE % dict(name=name, py2exe_dir=py2exe_dir,
                                                   version=APP_VERSION, 
                                                   outpath=os.path.abspath(output_dir))
        
    def build(self):
        f = open('installer.nsi', 'w')
        path = f.name
        f.write(self.installer)
        f.close()
        try:
            subprocess.call('"C:\Program Files\NSIS\makensis.exe" /V2 ' + path, shell=True)
        except Exception, e:
            print path
            traceback.print_exc(e)
        else:
            os.remove(path)

if __name__ == '__main__':
    
        print 'Create EXE'
        PY2EXE_BUILD = os.path.join('build','py2exe')
        PY2EXE_DIST = os.path.join('dist','py2exe')
        #if os.path.exists(PY2EXE_BUILD):
           # shutil.rmtree(PY2EXE_BUILD)
        #if os.path.exists(PY2EXE_DIST):
           # shutil.rmtree(PY2EXE_DIST)
        #py2exe()
        print 'Building Installer'
        installer = NSISInstaller(APP_TITLE,'dist', 'packages')
        installer.build()
