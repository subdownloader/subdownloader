#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import shutil
import zipfile

exclude_dirs = [".svn", "gui", "firesubtitles", "Subdownloader"]
exclude_files = ["pyc", "~", "tmp", "xml", "e4p", "e4q", "e4s", "e4t", "zip", "cfg"]

def copy_to_temp(copy_to="subdownloader_cli"):
    sys.stdout.write("Copying current path contents to '%s'..."% copy_to)
    sys.stdout.flush()
    #os.mkdir("subdownloader_cli")
    shutil.copytree(".", os.path.join(".", copy_to))
    sys.stdout.write(" done\n")
    sys.stdout.flush()
    sys.stdout.write("Cleaning '%s'..."% copy_to)
    sys.stdout.flush()
    for root, dirs, fileNames in os.walk("./subdownloader_cli"):
        # check for unwanted directories
        if os.path.split(root)[-1] in exclude_dirs:
            shutil.rmtree(root)
            continue
        # check for unwanted files
        for fileName in fileNames:
            for ext in exclude_files:
                if re.search("%s$"% ext, fileName):
                    os.remove(os.path.join(root, fileName))
    sys.stdout.write(" done\n")
    sys.stdout.flush()
    
def convert_to_cli(dir="subdownloader_cli"):
    # just a thing to replace some lines on the code
    fileName = 'run.py'
    f = open(os.path.join(dir, fileName))
    text = f.read()
    f.close()
    final = open(os.path.join(dir, fileName), 'w')
    text = text.replace("import gui.main", "pass")
    text = text.replace("gui.main.main(options)", "log.warning('GUI mode unavailable')")
    final.write(text)
    final.close()

def remove_temp(temp_path="subdownloader_cli"):
    sys.stdout.write("Removing temporary directory '%s'..."% temp_path)
    sys.stdout.flush()
    shutil.rmtree(temp_path)
    sys.stdout.write(" done\n")
    sys.stdout.flush()
    
def toZip( directory, zipFile, compress_lib=zipfile):
    sys.stdout.write("Compressing '%s' to '%s'..."% (directory, zipFile))
    sys.stdout.flush()
    z = compress_lib.ZipFile(zipFile, 'w', compression=zipfile.ZIP_DEFLATED)
    for root, dirs, fileNames in os.walk("subdownloader_cli"):
        for fileName in fileNames:
            if fileName is not zipFile: #avoid self compress
                filePath = os.path.join(root, fileName)
                z.write( filePath )
    z.close()
    sys.stdout.write(" done\n")
    sys.stdout.flush()
    return zipFile


if __name__ == "__main__":
    # create the tarball directory tree
    copy_to_temp()
    convert_to_cli()
    # create the tarball and delete the source directory
    toZip("subdownloader_cli", "subdownloader_cli.zip")
    # delete temporary directory
    remove_temp()
