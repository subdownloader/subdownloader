#!/usr/bin/env python

"""Setup script for the mmpython distribution."""

__revision__ = "$Id: setup.py,v 1.12 2004/05/25 14:10:19 the_krow Exp $"

from distutils.core import setup, Extension
import popen2
import version

extensions = [ Extension('mmpython/disc/cdrom', ['disc/cdrommodule.c']) ]
# check for libdvdread (bad hack!)
# Windows does not have Popen4, so catch exception here
try:
    child = popen2.Popen4('gcc -ldvdread')
    if child.fromchild.readline().find('cannot find') == -1:
        # gcc failed, but not with 'cannot find', so libdvd must be
        # somewhere (I hope)
        extensions.append(Extension('mmpython/disc/ifoparser', ['disc/ifomodule.c'],
                                    libraries=[ 'dvdread' ], 
                                    library_dirs=['/usr/local/lib'],
                                    include_dirs=['/usr/local/include']))
    child.wait()
except AttributeError, e:
    print "No Popen4 found. This seems to be Windows."
    print "Installing without libdvdread support."
    # Hack: disable extensions for Windows. 
    # This would better be done by a clean detect of windows. But how?
    extensions = []
    
    

setup (# Distribution meta-data
       name = "mmpython",
       version = version.VERSION,
       description = "Module for retrieving information about media files",
       author = "Thomas Schueppel, Dirk Meyer",
       author_email = "freevo-devel@lists.sourceforge.net",
       url = "http://mmpython.sf.net",

       scripts     = [ 'mminfo' ],
       package_dir = {'mmpython.video': 'video',
                      'mmpython.audio': 'audio',
                      'mmpython.audio.eyeD3': 'audio/eyeD3',
                      'mmpython.image': 'image',
                      'mmpython.disc' : 'disc',
                      'mmpython.misc' : 'misc',
                      'mmpython': ''},

       packages = [ 'mmpython', 'mmpython.video', 'mmpython.audio', 'mmpython.audio.eyeD3',
                    'mmpython.image', 'mmpython.disc', 'mmpython.misc' ],
       
       # Description of the modules and packages in the distribution
       ext_modules = extensions
                       
      )

