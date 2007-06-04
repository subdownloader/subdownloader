# Requires wxPython.  This sample demonstrates:
#
# - single file exe using wxPython as GUI.

from distutils.core import setup
import py2exe
import sys
import os
import globals

# If run without args, build executables, in quiet mode.
if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")
    

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = globals.version
        self.company_name = "MyCompany"
        self.copyright = "capiscuas@gmail.com"
        self.name = "Subdownloader"

################################################################
# A program using wxPython

# The manifest will be inserted as resource into test_wx.exe.  This
# gives the controls the Windows XP appearance (if run on XP ;-)
#
# Another option would be to store it in a file named
# test_wx.exe.manifest, and copy it with the data_files option into
# the dist-dir.
#
manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24


test_wx = Target(
    # used for the versioninfo resource
    description = "Subdownloader",

    # what to build
    script = "SubDownloader.py",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="test_wx"))],
    icon_resources = [(1, "icon48.ico")],
    dest_base = "SubDownloader")

################################################################
#I changed compressed = 0 to try to avoid the reported problems ImportError: MemoryLoadLibrary failed loading wx\_core_.pyd 
setup(
    #packages=['wx'],
    options = {"py2exe": {"compressed": 0,
                          "optimize": 2,
                          "ascii": 1,
                          "bundle_files": 1,
                          "packages": ["wx","encodings"]}},
    zipfile = None,
    windows = [test_wx],
    )

print "EXE GENERATED"