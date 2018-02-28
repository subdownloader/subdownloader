# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging

log = logging.getLogger('subdownloader.modules.metadata')


class MetadataVideoTrack(object):
    """
    Instances of this class collect some metadata of a video track.
    Only metadata is stored. It is meant to be attached to an actual video.
    """
    def __init__(self, duration_ms, framerate, framecount):
        """
        Create a new MetadataVideoTrack instance.
        :param duration_ms: Duration of the video track (in milliseconds)
        :param framerate: Frame rate of the video track (in frames per second)
        """
        self._duration_ms = duration_ms
        self._framerate = framerate
        self._framecount = framecount

    def get_framecount(self):
        return self._framecount

    def get_framerate(self):
        return self._framerate

    def get_duration_ms(self):
        return self._duration_ms

# FIXME: add ffprobe? ffprobe -v quiet -print_format json -show_format -show_streams ${VIDEO}


class Metadata(object):
    """
    Instances of this class collect metadata of all the video tracks.
    """
    def __init__(self):
        """
        Create a mew Metadata instance.
        """
        self._video_tracks = []

    def add_metadata(self, metadata):
        """
        Add a new MetadataVideoTrack instance
        :param metadata: metadata of a video track
        """
        self._video_tracks.append(metadata)

    def get_videotracks(self):
        """
        Get metadata of all tracks
        :return: metadata of all tracks as a list
        """
        return self._video_tracks


class PyMediaInfoParser(object):
    def __init__(self):
        if not self.is_available():
            raise RuntimeError('Cannot create PyMediaInfoParser')

    @staticmethod
    def is_available():
        try:
            log.debug('Trying PyMediaInfoParser ...')
            import pymediainfo
            if pymediainfo.MediaInfo.can_parse():
                log.debug('... Succeeded')
                return True
            else:
                log.debug('... Failed! (can_parse failed)')
                return False
        except ImportError:
            log.debug('... Failed! (ImportError)')
            return False

    @staticmethod
    def parse_path(path):
        """
        Parse a video at filepath, using pymediainfo framework.
        :param path: path of video to parse as string
        """
        import pymediainfo

        metadata = Metadata()
        log.debug('pymediainfo: parsing "{path}" ...'.format(path=path))
        parseRes = pymediainfo.MediaInfo.parse(str(path))
        log.debug('... parsing FINISHED')
        for track in parseRes.tracks:
            log.debug('... found track type: "{track_type}"'.format(track_type=track.track_type))
            if track.track_type == 'Video':
                duration_ms = track.duration
                framerate = track.frame_rate
                framecount = track.frame_count
                log.debug('mode={mode}'.format(mode=track.frame_rate_mode))
                if duration_ms is None or framerate is None:
                    log.debug('... Video track does not have duration and/or framerate.')
                    continue
                log.debug('... duration = {duration_ms} ms, framerate = {framerate} fps'.format(duration_ms=duration_ms,
                                                                                               framerate=framerate))
                metadata.add_metadata(
                    MetadataVideoTrack(
                        duration_ms=duration_ms,
                        framerate=float(framerate),
                        framecount=framecount
                    )
                )
        return metadata

parser = None

log.debug('Importing metadata parsing module ...')

if PyMediaInfoParser.is_available():
    parser = PyMediaInfoParser()

if not parser:
    log.debug('No parsing module found')

log.debug('... Importing metadata parsing module finished')


def available():
    return parser is not None


def parse(path):
    """
    Parse video at filepath
    :param path: path of video to parse as string
    :return: Metadata Instance of the video
    """
    return parser.parse_path(path)
