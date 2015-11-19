#!/usr/bin/env python
# Copyright (c) 2010 SubDownloader Developers - See COPYING - GPLv3

import sys
import os
import re
import shutil
import zipfile
import commands
import tempfile

projectdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, projectdir)

from modules import APP_TITLE, APP_VERSION

exclude_dirs = ["flags", ".git", ".svn", ".bzr", "firesubtitles",
    "build", "distribution",  "debian", "mmpython"]
exclude_files = [".gitignore", ".bzrignore", "pyc", "~", "tmp",
    "xml", "e4p", "e4q", "e4s", "e4t", "zip", "cfg", "lockfile",
    "log", "build_tarball.py", "notes.py", "srt", "windows_installer.py",
    "expiration.py", "paypal.png"]

def checkPoFiles(localedir = os.path.join(projectdir, "locale")):
    error = False
    for root, dirs, files in os.walk(localedir):
                if re.search(".*locale$", os.path.split(root)[0]):
                        _lang = os.path.split(root)[-1]
                
                if not 'subdownloader.po' in files and not dirs:
                        print ".po not found in %s" % _lang
                        error = True
    
    if error:
        return False
    return True
                        
def copy_to_temp(project_directory, temp_path):
    sys.stdout.write("Copying project directory to '%s'..."% temp_path)
    sys.stdout.flush()
    shutil.copytree(project_directory, temp_path)
    sys.stdout.write(" done\n")
    sys.stdout.flush()
    
def clean_temp_directory(temp_path, exclude_dirs=exclude_dirs):
    sys.stdout.write("Cleaning '%s'..."% temp_path)
    sys.stdout.flush()
    for root, dirs, fileNames in os.walk(temp_path):
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
    
def distribution_clean(temp_path, exclude_dirs, gui):
    if not gui:
        sys.stdout.write("Excluding 'gui' folder.\n")
        exclude_dirs.append("gui") # append another unwanted directory

        # just a thing to replace some lines on the code
        sys.stdout.write("Rewriting 'run.py'.")
        fileName = 'run.py'
        f = open(os.path.join(temp_path, fileName), "r")
        text = f.read()
        f.close()
        final = open(os.path.join(temp_path, fileName), "w")
        text = text.replace("import gui.main", "pass")
        text = text.replace("gui.main.main(options)", "log.warning('GUI mode unavailable')")
        final.write(text)
        final.close()

    clean_temp_directory(temp_path, exclude_dirs=exclude_dirs)

def remove_temp(temp_path):
    sys.stdout.write("Removing temporary directory '%s'..."% temp_path)
    sys.stdout.flush()
    shutil.rmtree(temp_path)
    sys.stdout.write(" done\n")
    sys.stdout.flush()
    
def toZip( zipFile, directory, compress_lib=zipfile):
    sys.stdout.write("Compressing '%s' to '%s'..."% (directory, zipFile))
    sys.stdout.flush()
    z = compress_lib.ZipFile("%s.zip" % zipFile, 'w', compression=zipfile.ZIP_DEFLATED)
    for root, dirs, fileNames in os.walk(directory):
        for fileName in fileNames:
            if fileName is not zipFile: #avoid self compress
                filePath = os.path.join(root, fileName)
                z.write( filePath, os.path.join(filePath.lstrip("/tmp/")) )
    z.close()
    sys.stdout.write(" done\n")
    sys.stdout.flush()
    return zipFile
    
def toTarGz(filename_noext, directory):
    compressedFileName = "%s.tar.gz" % filename_noext
    sys.stdout.write("Compressing '%s' to '%s'..."% (directory, compressedFileName))
    sys.stdout.flush()
   
    import tarfile

    def fileFilter(tarinfo):
        if tarinfo.name == compressedFileName:
            return None
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = "root"
        return tarinfo

    tar = tarfile.open(compressedFileName, "w:gz")
    for root, dirs, fileNames in os.walk(directory):
        for fileName in fileNames:
            filePath = os.path.join(root, fileName)
            arcname = filePath[len(directory):]
            tar.add(filePath, arcname=arcname, filter=fileFilter)
    tar.close()

    sys.stdout.write(" done\n")
    sys.stdout.flush()
    return compressedFileName
    
def get_git_revision():
    version = commands.getoutput('git rev-parse HEAD')
    return version

import argparse
import tarfile

def create_distribution(projectdirectory):
    outdir = tempfile.mkdtemp()
    compressedFileName = "fff.tar.gz"
    outfilename = os.path.join(outdir, compressedFileName)
    tar = tarfile.open(outfilename, "w:gz")

    def fileFilter(tarinfo):
        if tarinfo.name == compressedFileName:
            #avoid self compress
            return None
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = "root"
        return tarinfo

    for root, dirs, fileNames in os.walk(projectdirectory, topdown=False):
        for fileName in fileNames:
            filePath = os.path.join(root, fileName)
            _, _, relativePath = filePath.partition(projectdirectory)
            tar.add(filePath, arcname=relativePath, filter=fileFilter)
    sys.stdout.write("output=%s\n" % (outfilename))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create distributable tarball')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-cli', dest='gui', action='store_false',
        help='Create CLI only distribution')
    group.add_argument('-gui', dest='gui', action='store_true',
        help='Create GUI+CLI distribution')
    args = parser.parse_args()

    git_revision = get_git_revision()
    sys.stdout.write("Git revision %s\n" % (git_revision))

    if args.gui:
        fileNameBase = "subdownloader-"
    else:
        fileNameBase = "subdownloader_cli-"
    fileName = fileNameBase + APP_VERSION

    #Create temporary directory
    temp_parent = tempfile.mkdtemp()
    temp_path = os.path.join(temp_parent, fileName)

    # create the tarball directory tree
    if not checkPoFiles():
        sys.exit(1)

    copy_to_temp(projectdir, temp_path)

    distribution_clean(temp_path, exclude_dirs, args.gui)

    # create the tarball and delete the source directory
    #toZip(compressedFileName)
    toTarGz(fileName, temp_path)

    # delete temporary directory
    remove_temp(temp_parent)
