#!/usr/bin/env python3
#  Copyright (c) 2017 Entertainer Developers - See COPYING - GPLv2
"""Generate translations related files, pot/po/mo"""

import argparse
import logging
import os
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
from subprocess import check_call
import sys

log = logging.getLogger("translation_generator")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

def error(message):
    print(message, file=sys.stderr)
    sys.exit(1)


class TranslationGenerator(object):
    """Translation file generator"""

    def __init__(self, source_path, output_path):
        self._source_path = source_path
        self._output_path = output_path
        self._basename = "subdownloader"
        self._pot_path = (self._output_path / self._basename).with_suffix(".pot")

    def _iter_suffix(self, suffix):
        for root, dirs, files in os.walk(str(self._source_path)):
            for filename in files:
                file_path = pathlib.Path(root, filename)
                if file_path.suffix == suffix:
                    yield file_path

    def do_pot(self):
        """
        Sync the template with the python code.
        """
        files_to_translate = []
        log.debug("Collecting python sources for pot ...")
        for source_path in self._iter_suffix(suffix=".py"):
            log.debug("... add to pot: {source}".format(source=str(source_path)))
            files_to_translate.append(str(source_path))
        log.debug("Finished collection sources.")
        command = ["xgettext", "--language=Python", "--keyword=_", "--keyword=_translate",
                   "--output={output}".format(output=str(self._pot_path))]
        log.debug("pot file \"{pot}\" created!".format(pot=str(self._pot_path)))
        command.extend(files_to_translate)
        check_call(command)

    def _iter_po_dir_path(self):
        for locale_dir_path in self._output_path.iterdir():
            if not locale_dir_path.is_dir():
                continue
            yield locale_dir_path

    def do_po(self):
        """
        Update all po files with the data in the pot reference file.
        """
        log.debug("Start updating po files ...")
        for po_dir_path in self._iter_po_dir_path():
            if not po_dir_path.is_dir():
                continue
            po_path = (po_dir_path / self._basename).with_suffix(".po")
            log.debug("update {po}:".format(po=str(po_path)))
            check_call(["msgmerge", "-U", str(po_path), str(self._pot_path)])
        log.debug("All po files updated")

    def do_mo(self):
        """
        Generate mo files for all po files.
        """
        log.debug("Start updating mo files ...")
        for po_dir_path in self._iter_po_dir_path():
            po_path = (po_dir_path / self._basename).with_suffix(".po")
            mo_path = (po_dir_path / "LC_MESSAGES" / self._basename).with_suffix(".mo")
            log.debug("Creating from {po}: {mo}".format(po=str(po_path), mo=str(mo_path)))
            check_call(["msgfmt", str(po_path), "-o", str(mo_path)])
        log.debug("All mo files updated")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Update the internationalization files: pot, po's and mo's.")
    parser.add_argument("-s", "--source", dest="sourcedir", required=True, help="Directory of input python files")
    parser.add_argument("-o", "--output", dest="outputdir", required=True, help="Directory of mo and po files")

    what_group = parser.add_argument_group(title="What to create/update. If no option is given, "
                                                 "action is performed on all")
    what_group.add_argument("--pot", dest="what_pot", action="store_true",
                                help="Work on POT files (Portable Object Template)")
    what_group.add_argument("--po", dest="what_po", action="store_true",
                                help="Work on PO files (Portable Object)")
    what_group.add_argument("--mo", dest="what_mo", action="store_true",
                                help="Work on PM files (Machine Object)")

    args = parser.parse_args()
    source_path = pathlib.Path(args.sourcedir)
    if not source_path.is_dir():
        parser.error("Input is not a directory")
    output_path = pathlib.Path(args.outputdir)
    if not output_path.is_dir():
        parser.error("Output is not a directory")
    what = {"pot": args.what_pot, "po": args.what_po, "mo": args.what_mo}
    if not any(what.values()):
        for key in what:
            what[key] = True

    translation_generator = TranslationGenerator(source_path=source_path, output_path=output_path)
    if what["pot"]:
        translation_generator.do_pot()
    if what["po"]:
        translation_generator.do_po()
    if what["mo"]:
        translation_generator.do_mo()
