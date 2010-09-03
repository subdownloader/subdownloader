# Copyright (c) 2010 Entertainer Developers - See COPYING - GPLv2
# Modified to use with SubDownloader.
'''Generate translations related files, pot/po/mo'''

import glob
import os
import re
from subprocess import call
import sys

class TranslationsGenerator(object):
    '''Translation file generator'''

    def __init__(self, main_dir = '../', pot_dir = '../locale',
        po_dir = '../locale', exclude_dir_pattern = 'images'):

        # Directorys of python files to search for translations
        self.main_dir = main_dir

        # A directory pattern to exclude when searching
        self.exclude = exclude_dir_pattern

        # Directory where pot file is stored
        self.pot_dir = pot_dir

        # Directory where po files are stored
        self.po_dir = po_dir

    def update_pot(self, pot_file = 'subdownloader.pot'):
        '''Update the pot file

        If the pot file does not exist, create one.
        '''

        # List of file names to feed to xgettext
        files_to_translate = []

        # Cycle through all the files and collect the necessary data
        # pylint: disable-msg=W0612
        for root, dirs, files in os.walk(self.main_dir):
            if self.exclude in root:
                continue
            for filename in files:
                full_path = os.path.join(root, filename)

                ext = os.path.splitext(full_path)[1]
                if ext == '.py':
                    files_to_translate.append(full_path)

        # Generate pot file
        command = ['xgettext', '--language=Python', '--keyword=_',
            '--output=%s/%s' % (self.pot_dir, pot_file)]
        command.extend(files_to_translate)
        call(command)

    def update_pos(self, pot_file = 'subdownloader.pot'):
        '''Update all po files with the data in the pot reference file.'''

        pot_path = os.path.join(self.pot_dir, pot_file)

        pos = glob.glob(os.path.join(self.po_dir, '*.po'))
        for po in pos:
            call(['msgmerge', '-U', po, pot_path])

    def update_mos(self, search_pattern = 'subdownloader.po',
        mo_name = 'subdownloader.mo'):
        '''Generate mo files for all po files

        Search pattern is the pattern that all the po files are in. The saved
        value is the locale that is pulled out of the po filename.
        '''

        pos = glob.glob(os.path.join(self.po_dir, '*.po'))
        for po in pos:
            match = re.search(search_pattern, po)
            lang = match.group(1)
            lang_dir = '../locale/%s/LC_MESSAGES' % lang

            # Create the directory and all its intermediates if needed
            if not os.path.exists(lang_dir):
                os.makedirs(lang_dir)

            # Create the mo file from the po file
            mo_out = os.path.join(lang_dir, '%s' % mo_name)
            call(['msgfmt', po, '-o', mo_out])

if __name__ == '__main__':
    translation_generator = TranslationsGenerator()

    if 'pot' in sys.argv:
        translation_generator.update_pot()
        print 'Done.'
    if 'po' in sys.argv:
        translation_generator.update_pos()
        print 'Done.'
    if 'mo' in sys.argv:
        translation_generator.update_mos()
        print 'Done.'

    if len(sys.argv) == 1:
        print '= Generate translations related files =\nUsage: translations_generator.py [pot, po, mo]'
