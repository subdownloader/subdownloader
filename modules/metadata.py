#!/usr/bin/env python
# Copyright (c) 2015 SubDownloader Developers - See COPYING - GPLv3

import logging

log = logging.getLogger('subdownloader.modules.metadata')


class MetadataVideo(object):

    def __init__(self, duration_ms, framerate):
        self.duration_ms = duration_ms
        self.framerate = framerate


class Metadata(object):

    def __init__(self):
        self.videos = []

    def _addVideo(self, video):
        self.videos.append(video)

    @classmethod
    def parse_dummy(filepath):
        log.warning('Using dummy metadata parser.')
        return None

    @classmethod
    def parse_kaa_metadata(cls, filepath):
        metaRes = cls()
        parseRes = kaa.metadata.parse(filepath)
        if parseRes is None:
            return metaRes
        for video in parseRes.video:
            metaRes._addVideo(
                MetadataVideo(
                    duration_ms=1000 * parseRes.length,
                    framerate=video.fps
                )
            )
        return metaRes

    @classmethod
    def parse_pymediainfo(cls, filepath):
        metaRes = cls()
        parseRes = pymediainfo.MediaInfo.parse(filepath)
        for track in parseRes.tracks:
            if track.track_type == 'Video':
                metaRes._addVideo(
                    MetadataVideo(
                        duration_ms=track.duration,
                        framerate=float(track.frame_rate)
                    )
                )
        return metaRes

try:
    import kaa.metadata
    log.debug('Using kaa.metadata')
    parseFunc = Metadata.parse_kaa_metadata
except ImportError:
    try:
        import pymediainfo
        log.debug('Using pymediainfo')
        parseFunc = Metadata.parse_pymediainfo
    except:
        parseFunc = Metadata.parse_dummy
        log.error('Failed to import metadata module.')
        log.error('This means you will be unable to automatically')
        log.error('download your subtitles or upload your videos')
        log.error('with all details.')

# expose metadata parsing method for global usage


def parse(filepath):
    return parseFunc(filepath)
