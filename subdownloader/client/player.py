# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from enum import Enum
import logging
from pathlib import Path
import platform
import shlex
import shutil
import subprocess

log = logging.getLogger('subdownloader.client.player')


class VideoPlayerConfigKey(Enum):
    VIDEOPLAYER_PATH = ('options', 'VideoPlayerPath', )
    VIDEOPLAYER_PARAMS = ('options', 'VideoPlayerParameters', )


class VideoPlayer(object):
    def __init__(self, path, args_format):
        self._path = path
        self._command = args_format

    def get_path(self):
        return self._path

    def get_command(self):
        return self._command

    def play_video(self, video, subtitleFile):
        args = [self._path]

        try:
            parameters_args = shlex.split(self._command)
        except ValueError:
            raise RuntimeError(_('Unable to launch videoplayer'))  # FIXME: catch + show messagebox

        for param in parameters_args:
            args.append(param.format(video.get_filepath(), subtitleFile.get_filepath()))

        log.debug('VideoPlayer.play_video: args={}'.format(args))
        try:
            log.debug('Trying to create subprocess...')
            p = subprocess.Popen(args)
            log.debug("... SUCCESS: pid = {}".format(p.pid))
        except IOError:
            log.debug('... FAIL', exc_info=True)
            raise RuntimeError(_('Unable to launch videoplayer'))  # FIXME: catch + show messagebox

    @classmethod
    def find(cls, player_name_requested=None):
        log.debug('initializeVideoPlayer(...)')
        log.debug('platform.system={}'.format(platform.system()))
        predefined_video_player = None
        if platform.system() == 'Linux':
            linux_players = {
                'vlc': {'parameters': '{0} --sub-file {1}'},
                'mplayer': {'parameters': '{0} -sub {1}'},
                'xine': {'parameters': '{0}#subtitle:{1}'},
            }
            for player_name, player_data in linux_players.items():
                if player_name_requested is not None and player_name_requested != player_name:
                    continue
                log.debug('Trying "{}"...'.format(player_name))
                path = shutil.which(player_name)
                if path:
                    log.debug('... found "{}"'.format(path))
                    predefined_video_player = cls(path, player_data['parameters'])
                    break
        elif platform.system() == 'Windows':
            import winreg
            windows_players = {
                'vlc': {'regRoot': winreg.HKEY_LOCAL_MACHINE, 'regFolder': 'SOFTWARE\\VideoLan\\VLC', 'regKey': '', 'parameters': '{0} --sub-file={1}'},
                'mpc': {'regRoot': winreg.HKEY_LOCAL_MACHINE, 'regFolder': 'SOFTWARE\\Gabest\\Media Player Classic', 'regKey': 'ExePath', 'parameters': '{0} /sub {1}'},
            }
            for player_name, player_data in windows_players.items():
                if player_name_requested is not None and player_name_requested != player_name:
                    continue
                try:
                    log.debug('Trying register key "{}"...'.format(player_data['regFolder']))
                    registry = winreg.OpenKey(player_data['regRoot'],  player_data['regFolder'])
                    path, type = winreg.QueryValueEx(registry, player_data['regKey'])
                    log.debug('... found "{}"'.format(path))
                    predefined_video_player = cls(path, player_data['parameters'])
                    break
                except (WindowsError, OSError):
                    log.debug('... Cannot find registry for {regRoot}'.format(regRoot=player_data['regRoot']))
        elif platform.system() == 'Darwin':
            macos_players = {
                'vlc': {'path': Path('/usr/bin/open'), 'parameters': '-a /Applications/VLC.app {0} --sub-file {1}'},
                'MPlayer OSX': {'path': Path('/Applications/MPlayer OSX.app/Contents/MacOS/MPlayer OSX'), 'parameters': '{0} -sub {1}'},
                'MPlayer OS X 2': {'path': Path('/Applications/MPlayer OS X 2.app/Contents/MacOS/MPlayer OS X 2'), 'parameters': '{0} -sub {1}'},
            }
            for player_name, player_data in macos_players.items():
                if player_name_requested is not None and player_name_requested != player_name:
                    continue
                log.debug('Trying "{}"...'.format(player_data['path']))
                if player_data['path'].exists():
                    log.debug('... found "{}"'.format(player_data['path']))
                    predefined_video_player = cls(player_data['path'], player_data['parameters'])
        else:
            log.warning('Unknown platform: {}'.format(platform.system()))

        return predefined_video_player

    def save_settings(self, settings):
        settings.set_path(VideoPlayerConfigKey.VIDEOPLAYER_PATH.value, self.get_path())
        settings.set_str(VideoPlayerConfigKey.VIDEOPLAYER_PARAMS.value, self.get_command())

    @classmethod
    def from_settings(cls, settings):
        path = settings.get_str(VideoPlayerConfigKey.VIDEOPLAYER_PATH, None)
        command = settings.get_str(VideoPlayerConfigKey.VIDEOPLAYER_PARAMS, None)
        if path is None or command is None:
            return None
        return cls(None, path, command)

    def __repr__(self):
        return '<VideoPlayer:{}:{}>'.format(self._path, self._command)
