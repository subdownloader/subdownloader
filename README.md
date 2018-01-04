# SubDownloader

SubDownloader is a Free Open-Source tool written in Python for automatic download/upload of subtitles for video files. It uses some smart hashing algorithms to work fast.

## Dependencies

Required:
- [Python]: version 2.7+ or 3
- Python packages:
  * [argparse]: parsing command line options (standard since Python 3.2)
  * [python-progressbar]: command line interface
- Graphical interface:
  * [Qt]: graphical interface
  * [pyQt]: Python bindings (version 5)

Optional:
- [kaa-metadata]: currently only available for Python 2
- [pymediainfo]: used as fallback for python-kaa-metadata. This package needs [MediaInfo](https://mediaarea.net). Version 2.1.6 or higher.
- [langdetect]: language detection of subtitles by their contents 
- [argcomplete]: Bash tab completion for argparse

### Build dependencies

- [python3-qt5-devel][pyQt]: generate the gui from the interface description


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

```
ln -s $PATHTOSUBDOWNLOADER/subdownloader-nautilus/subdownloader_nautilus.py ~/.local/share/nautilus-python/extensions/
```

## Credits

The [original developers][subdownloader-launchpad] of the subdownloader program.

## License

SubDownloader is licensed under [GPL v3].

   [Python]: <https://www.python.org/>
   [argparse]: <https://python.readthedocs.org/en/latest/library/argparse.html>
   [python-progressbar]: <https://github.com/niltonvolpato/python-progressbar>
   [Qt]: <https://www.qt.io/>
   [pyQt]: <https://riverbankcomputing.com/software/pyqt/intro>
   [kaa-metadata]: <https://github.com/freevo/kaa-metadata>
   [pymediainfo]: <https://pymediainfo.readthedocs.org/>
   [argcomplete]: <https://argcomplete.readthedocs.org/>
   [langdetect]: <https://github.com/Mimino666/langdetect>
   [GPL v3]: <https://www.gnu.org/licenses/gpl-3.0.html>
   [subdownloader-launchpad]: https://launchpad.net/subdownloader
