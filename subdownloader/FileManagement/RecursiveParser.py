# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

import logging
import os


log = logging.getLogger('subdownloader.FileManagement.RecursiveParser')

class RecursiveParser:

    '''
    The RecursiveParser class contains methods to recursively find directories, files, or specific files in a
    directory structure
    '''

    def __init__(self):
        pass

    # The getRecursiveFileList() method accepts a directory path as an argument and
    # then recursively searches through that path looking for files to return
    # to you in the form of a list.
    def getRecursiveFileList(self, basedir, extensions=[]):
        '''
        getRecursiveFileList takes a directory in the form of a string and returns a list of all
        of the files contained therein.  If you would like to search only for specific file
        extensions, pass a list of extensions as the second argument
        (e.g. getRecursiveFileList('/home/user/files', ['htm', 'html', 'css'])
        '''

        subdirlist = []
        filelist = []

        try:
            # First, we check to see if the "extensions" variable has any items in it.  If
            # it does, then we first check to see if the current item is a file or not, and
            # if it is a file, we check to see if its extension is one of the ones specified
            # in the "extensions" variable.  If all these tests pass, then we add the file
            # to the file list.  If not, we don't.
            if len(extensions) > 0:
                for item in os.listdir(basedir):
                    if os.path.isfile(os.path.join(basedir, item)):
                        if extensions.count(item[item.rfind('.') + 1:].lower()) > 0:
                            filelist.append(os.path.join(basedir, item))
                    else:
                        subdirlist.append(os.path.join(basedir, item))
            # If the "extensions" variable is empty, then we add anything that is a file to
            # "filelist".
            else:
                for item in os.listdir(basedir):
                    if os.path.isfile(os.path.join(basedir, item)):
                        filelist.append(os.path.join(basedir, item))
                    else:
                        print('islink: {}'.format(os.path.islink(basedir)))
                        subdirlist.append(os.path.join(basedir, item))

        except OSError as e:
            log.exception("Please select a specific folder.")

        except TypeError as e:
            log.exception("The calling code has passed an invalid parameter to getRecursiveFileList.")
            log.error(e)

        except Exception as e:
            log.error(e)

        # Recursively call getRecursiveDirList until you reach the end of the
        # directory structure
        for subdir in subdirlist:
            filelist += self.getRecursiveFileList(subdir, extensions)

        filelist.sort()

        return filelist
