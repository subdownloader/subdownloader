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
import shutil
from subprocess import check_call

log = logging.getLogger("translation_generator")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


class TranslationGenerator(object):
    """Translation file generator"""

    def __init__(self, name, source_path, po_path, mo_path):
        self._source_path = source_path
        self._po_path = po_path
        self._mo_path = mo_path
        self._basename = name

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
        pot_path = (self._po_path / self._basename).with_suffix(".pot")
        command = ["xgettext", "--keyword=_", "--keyword=_translate",
                   "--output={output}".format(output=str(pot_path))]
        command.extend(files_to_translate)
        check_call(command)
        log.debug("pot file \"{pot}\" created!".format(pot=str(pot_path)))

        pot_copy_path = self._mo_path / pot_path.name
        log.debug("Copying pot file to mo path: {pot_copy_path}".format(pot_copy_path=str(pot_copy_path)))
        shutil.copy(str(pot_path), str(pot_copy_path))

    def _iter_po_dir(self):
        for locale_dir_path in self._po_path.iterdir():
            if not locale_dir_path.is_dir():
                continue
            yield locale_dir_path

    def do_po(self):
        """
        Update all po files with the data in the pot reference file.
        """
        log.debug("Start updating po files ...")
        pot_path = (self._po_path / self._basename).with_suffix(".pot")
        for po_dir_path in self._iter_po_dir():
            po_path = (po_dir_path / self._basename).with_suffix(".po")
            if po_path.exists():
                log.debug("update {po}:".format(po=str(po_path)))
                check_call(["msgmerge", "-U", str(po_path), str(pot_path)])
            else:
                log.debug("create {po}:".format(po=str(po_path)))
                check_call(["msginit", "-i", str(pot_path), "-o", str(po_path), "--no-translator"])
            po_copy_path = self._mo_path / po_path.parent.name / po_path.name
            po_copy_path.parent.mkdir(exist_ok=True)
            log.debug("Copying po file to mo path: {po_copy_path}".format(po_copy_path=str(po_copy_path)))

            shutil.copy(str(po_path), str(po_copy_path))
        log.debug("All po files updated")

    def do_mo(self):
        """
        Generate mo files for all po files.
        """
        log.debug("Start updating mo files ...")
        for po_dir_path in self._iter_po_dir():
            po_path = (po_dir_path / self._basename).with_suffix(".po")
            lc_path = self._mo_path / po_dir_path.name / "LC_MESSAGES"
            lc_path.mkdir(parents=True, exist_ok=True)
            mo_path = (lc_path / self._basename).with_suffix(".mo")
            log.debug("Creating from {po}: {mo}".format(po=str(po_path), mo=str(mo_path)))
            check_call(["msgfmt", str(po_path), "-o", str(mo_path)])
        log.debug("All mo files updated")

def parse_args():
    parser = argparse.ArgumentParser(description="Update the internationalization files: pot, po's and mo's.")

    parser.add_argument("-n", "--name", dest="name", default=None, help="Name of the project")

    parser.add_argument("-s", "--source", required=True, dest="source_path", help="Directory of input python SOURCE files")
    parser.add_argument("-p", "--po_path", required=True, dest="po_path", help="Directory of PO(T) file(s)")
    parser.add_argument("-m", "--mo_path", required=True, dest="mo_path", help="Directory of MO files")

    what_group = parser.add_argument_group(title="What to create/update. If no option is given, "
                                                 "action is performed on all")
    what_group.add_argument("--pot", dest="what_pot", action="store_true",
                            help="Create POT file (Portable Object Template)")
    what_group.add_argument("--po", dest="what_po", action="store_true",
                            help="Create PO files (Portable Object)")
    what_group.add_argument("--mo", dest="what_mo", action="store_true",
                            help="Create MO files (Machine Object)")

    args = parser.parse_args()

    arguments = {}

    source_path = pathlib.Path(args.source_path)
    if not source_path.is_dir():
        parser.error("Source path is not a directory")
    arguments["source_path"] = source_path

    po_path = pathlib.Path(args.po_path)
    if not po_path.is_dir():
        parser.error("PO path is not a directory")
    arguments["po_path"] = po_path

    mo_path = pathlib.Path(args.mo_path)
    if not mo_path.is_dir():
        parser.error("MO path is not a directory")
    arguments["mo_path"] = mo_path

    do_what = {"pot": args.what_pot, "po": args.what_po, "mo": args.what_mo}
    if not any(do_what.values()):
        for key in do_what:
            do_what[key] = True

    arguments["name"] = args.name if args.name else "subdownloader"

    return arguments, do_what

if __name__ == '__main__':
    translation_args, what = parse_args()
    translation_generator = TranslationGenerator(**translation_args)
    if what["pot"]:
        translation_generator.do_pot()
    if what["po"]:
        translation_generator.do_po()
    if what["mo"]:
        translation_generator.do_mo()
