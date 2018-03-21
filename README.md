# SubDownloader

[![PyPI version](https://badge.fury.io/py/SubDownloader.svg)](https://pypi.python.org/pypi/SubDownloader/) [![Travis status](https://travis-ci.org/subdownloader/subdownloader.svg?branch=master)](https://travis-ci.org/subdownloader/subdownloader) [![Appveyor status](https://ci.appveyor.com/api/projects/status/63u81ypw4wdlt3bk?svg=true)](https://ci.appveyor.com/project/subdownloader/subdownloader)

SubDownloader is a Free Open-Source tool written in Python for automatic download/upload of subtitles for video files. It uses some smart hashing algorithms to work fast.

## Dependencies

Required:

- [Python]: version 3.5+.
- [pyQt5]: Python Qt5 bindings (graphical interface)
  * This package requires [Qt]
- Python packages:
  * [argparse]: parsing command line options (standard since Python 3.2)
  * [python-progressbar]: command line interface

Optional:

- [pymediainfo]: replaces python-kaa-metadata in Python 3, needs [mediaInfo](https://mediaarea.net) version 2.1.6 or higher
- [langdetect]: language detection of subtitles by their contents 
- [argcomplete]: Bash tab completion for argparse

### Build dependencies

- [python3-qt][pyQt5]: `pyuic5` and `pyrcc5` are needed to generate the gui from the interface description, these tools may be in devel package

## Running the program

### Graphical Interface

```sh
$ ./subdownloader.py -g
```

### Command Line

```sh
$ ./subdownloader.py -c
```

### Help

```sh
$ ./subdownloader.py -h
```

### Install Nautilus extension

```sh
ln -s $PATHTOSUBDOWNLOADER/subdownloader-nautilus/subdownloader_nautilus.py ~/.local/share/nautilus-python/extensions/
```

`subdownloader` needs to be in the `$PATH` environment variable.

## Credits

The [original developers][subdownloader-launchpad] of the subdownloader program.

## License

SubDownloader is licensed under [GPL v3]

   [Python]: <https://www.python.org/>
   [argparse]: <https://python.readthedocs.org/en/latest/library/argparse.html>
   [python-progressbar]: <https://github.com/niltonvolpato/python-progressbar>
   [Qt]: <https://www.qt.io/>
   [pyQt5]: <https://riverbankcomputing.com/software/pyqt/intro>
   [pymediainfo]: <https://pymediainfo.readthedocs.org/>
   [argcomplete]: <https://argcomplete.readthedocs.org/>
   [langdetect]: <https://github.com/Mimino666/langdetect>
   [GPL v3]: <https://www.gnu.org/licenses/gpl-3.0.html>
   [subdownloader-launchpad]: https://launchpad.net/subdownloader
