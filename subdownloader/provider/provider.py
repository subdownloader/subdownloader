# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

import logging

log = logging.getLogger('subdownloader.provider.provider')


class ProviderConnectionError(Exception):
    def __init__(self, msg, code=None):
        Exception.__init__(self)
        self._msg = msg
        self._code = code

    def get_msg(self):
        return self._msg

    def get_code(self):
        return self._code

    def __str__(self):
        return 'code={code}; msg={msg}'.format(msg=self._msg, code=self._code)


class ProviderNotConnectedError(ProviderConnectionError):
    def __init__(self):
        ProviderConnectionError.__init__(self, None)


class SubtitleProvider(object):
    """
    Represents an abstract SubtitleProvider..
    """
    # FIXME: add documentation

    def __init__(self):
        pass

    def __del__(self):
        try:
            self.disconnect()
        except ProviderConnectionError:
            log.warning('Disconnect failed during destructor', exc_info=True)

    def get_settings(self):
        raise NotImplementedError()

    def set_settings(self, settings):
        raise NotImplementedError()

    def connect(self):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()

    def connected(self):
        raise NotImplementedError()

    def login(self):
        raise NotImplementedError()

    def logout(self):
        raise NotImplementedError()

    def logged_in(self):
        raise NotImplementedError()

    def search_videos(self, videos, callback, language=None):
        raise NotImplementedError()

    def query_text(self, query):
        raise NotImplementedError()

    # def download_subtitles(self, remotesubs):
    #     raise NotImplementedError()
    #
    # def upload_subtitles(self, l_dict_subs):
    #     raise NotImplementedError()

    def ping(self):
        raise NotImplementedError()

    # @classmethod
    # def supports_mode(cls, method):
    #     raise NotImplementedError()

    @classmethod
    def get_name(cls):
        raise NotImplementedError()

    @classmethod
    def get_short_name(cls):
        raise NotImplementedError()


class ProviderSettings(object):
    def __init__(self):
        pass

    def as_dict(self):
        raise NotImplementedError()

    def load(self, **kwargs):
        raise NotImplementedError()


class SubtitleTextQuery(object):
    def __init__(self, query):
        self._query = query

    def get_movies(self):
        raise NotImplementedError()

    def get_nb_movies_online(self):
        raise NotImplementedError()

    @property
    def query(self):
        return self._query

    def more_movies_available(self):
        raise NotImplementedError()

    def search_more_movies(self):
        raise NotImplementedError()

    def search_more_subtitles(self, movie):
        raise NotImplementedError()
