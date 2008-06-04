#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import shutil

exclude_dirs = [".svn", "gui"]
exclude_files = ["pyc", "~"]

def copy_cli_files():
    #os.mkdir("subdownloader_cli")
    shutil.copytree(".", "./subdownloader_cli")
    for root, dirs, fileNames in os.walk("./subdownloader_cli"):
        # check for unwanted directories
        if os.path.split(root)[-1] in exclude_dirs:
            shutil.rmtree(root)
            continue
        for fileName in fileNames:
            for ext in exclude_files:
                if re.search("%s$"% ext, fileName):
                    os.remove(os.path.join(root, fileName))
                    
if __name__ == "__main__":
    copy_cli_files()
