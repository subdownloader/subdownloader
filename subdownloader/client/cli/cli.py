# -*- coding: utf-8 -*-
# Copyright (c) 2018 SubDownloader Developers - See COPYING - GPLv3

from cmd import Cmd
from os import linesep
from pathlib import Path
import shlex

from subdownloader.client.cli.callback import ProgressBarCallback
from subdownloader.client.state import SubtitleRenameStrategy
from subdownloader.util import IllegalPathException
from subdownloader.filescan import scan_videopaths
from subdownloader.provider.provider import ProviderConnectionError
from subdownloader.languages.language import Language, NotALanguageException
from subdownloader.subtitle2 import RemoteSubtitleFile


class CliCmd(Cmd):
    def __init__(self, state):
        Cmd.__init__(self)
        self._state = state
        self._return_code = 1
        self.prompt = '>>> '

        # Download state
        self._videos = []
        self._video_rsubs = set()

        # Text query state
        self._text_query = None
        self._query_rsubs = set()

    def _invalidate_videos(self):
        self.set_videos([])

    def set_videos(self, videos):
        self._videos = videos
        self._video_rsubs = set()

    def get_videos_subtitle(self, i):
        if i < 0:
            raise IndexError()
        nb_subs_met = 0
        for video in self._videos:
            for subtitle_network in video.get_subtitles():
                if not self.download_filter_language_object(subtitle_network):
                    continue
                nb_subs_met_tmp = nb_subs_met + len(subtitle_network)
                if i < nb_subs_met_tmp:
                    return subtitle_network[i - nb_subs_met]
                nb_subs_met = nb_subs_met_tmp
        else:
            raise IndexError()

    def _invalidate_text_queries(self):
        self.set_text_query(None)

    def set_text_query(self, query):
        self._text_query = query
        self._query_rsubs = set()

    def download_filter_language_object(self, subtitle):
        subtitle_languages = subtitle.get_language()
        if subtitle_languages.is_generic():
            return subtitle
        filter_languages = self.state.get_download_languages()
        if not filter_languages:
            return subtitle
        if subtitle_languages in filter_languages:
            return subtitle

    def print(self, *what):
        self.stdout.write(' '.join(what))
        self.stdout.write(linesep)

    def read_line(self, prefix):
        self.stdout.write(prefix)
        return self.stdin.readline().strip()

    @property
    def return_code(self):
        return self._return_code

    @property
    def state(self):
        return self._state

    def default(self, line):
        Cmd.default(self, line)

    def postloop(self):
        self.state.logout()

    @staticmethod
    def get_callback():
        return ProgressBarCallback()

    LEN_ARG_COL = 15

    def help_EOF(self):
        self.print(_('Exit program') + ' (CTRL+D).')
        self.print()
        self.print('EOF')
        self.print()

    def do_EOF(self, arg):
        self._return_code = 1
        return True

    def help_quit(self):
        self.print(_('Exit program') + '.')
        self.print()
        self.print('quit')
        self.print()

    def do_quit(self, arg):
        self._return_code = 0
        return True

    def help_languages(self):
        lang = _('LANGUAGE')
        self.print(_('Get/replace the filter languages. (default is to get the filter languages)'))
        self.print()
        self.print('languages [0 | {lang} [{lang} [...]]]'.format(lang=lang))
        self.print()
        self.print('  {lang} '.format(lang=lang).ljust(self.LEN_ARG_COL) +
                   _('Add {lang} as filter language (current filter will be lost).').format(lang=lang))
        self.print('  0 '.ljust(self.LEN_ARG_COL) + _('Clear all filter languages.'))
        self.print()

    def do_languages(self, arg):
        if arg:
            langs = None
            if langs is None:
                try:
                    if int(arg) == 0:
                        langs = []
                except ValueError:
                    pass
            if langs is None:
                try:
                    langs = [Language.from_unknown(l_str, xx=True, xxx=True, name=True, locale=True)
                             for l_str in shlex.split(arg)]
                except NotALanguageException as e:
                    self.print(_('"{}" is not a valid language').format(e.value))
                    return
            self.state.set_download_languages(langs)
        if arg:
            self.print(ngettext('New filter language:', 'New filter languages:',
                                len(self.state.get_download_languages())))
        else:
            self.print(ngettext('Current filter language:', 'Current filter languages:',
                       len(self.state.get_download_languages())))
        if self.state.get_download_languages():
            for language in self.state.get_download_languages():
                self.print('- {}'.format(language.name()))
        else:
            self.print(_('(None)'))

    # def complete_languages(self, text, line, begidx, endidx):
    #     # FIXME: implement completer for languages

    def help_filepath(self):
        self.print(_('Get/set the file path(s).'))
        self.print()
        self.print('filepath [PATH [PATH [...]]]')
        self.print()
        self.print('  PATH'.ljust(self.LEN_ARG_COL) + _('File path to add.'))
        self.print()

    def do_filepath(self, arg):
        if arg:
            self.state.set_video_paths([Path(p) for p in shlex.split(arg)])
        if arg:
            self.print(ngettext('New file path:', 'New file paths:', len(self.state.get_video_paths())))
        else:
            self.print(ngettext('Current file path:', 'Current file paths:', len(self.state.get_video_paths())))
        for path in self.state.get_video_paths():
            self.print('- {}'.format(path))

    # def complete_videopath(self, text, line, begidx, endidx):
    #     # FIXME: implement completer for paths

    def help_filescan(self):
        self.print(_('Scan the file path(s) for videos.'))
        self.print()
        self.print('filescan')
        self.print()

    def do_filescan(self, arg):
        callback = self.get_callback()

        callback.set_title_text(_("Scanning..."))
        callback.set_label_text(_("Scanning files"))
        callback.set_finished_text(_("Scanning finished"))
        callback.set_block(True)
        callback.show()

        try:
            local_videos, local_subs = scan_videopaths(self.state.get_video_paths(), callback,
                                                       recursive=self.state.is_recursive())
        except IllegalPathException as e:
            callback.finish()
            self.print(_('The video path "{}" does not exist').format(e.path()))
            return

        callback.finish()

        self.set_videos(local_videos)
        self.print(_('{}/{} videos/subtitles have been found').format(len(local_videos), len(local_subs)))

    def help_vidsearch(self):
        self.print(_('Search for corresponding subtitles for the videos on the current providers.'))
        self.print()
        self.print('vidsearch')
        self.print()

    def do_vidsearch(self, arg):
        callback = self.get_callback()
        callback.set_title_text(_("Asking Server..."))
        callback.set_label_text(_("Searching subtitles..."))
        callback.set_updated_text(_("Searching subtitles ( %d / %d )"))
        callback.set_finished_text(_("Search finished"))
        callback.set_block(True)
        callback.show()

        try:
            self.state.search_videos_all(self._videos, callback)
        except ProviderConnectionError:
            callback.finish()
            self.print(_('Failed to search for videos.'))
            return

        callback.finish()
        self.print(_('Search finished.'))

    @staticmethod
    def classify_rsubtitles_language(video):
        lang_network = {}
        for network in video.get_subtitles().get_subtitle_networks():
            lang_network.setdefault(network.get_language(), []).append(network)
        return lang_network

    def help_videos(self):
        self.print(_('Get/clear the videos (default is get all videos).'))
        self.print()
        self.print('videos [clear]')
        self.print()
        self.print('  clear'.ljust(self.LEN_ARG_COL) + _('Clear the videos'))
        self.print()

    def do_videos(self, arg):
        if arg:
            if arg == 'clear':
                self.set_videos([])
            else:
                self.print(_('Unknown command'))
                return
        self.print(_('Current videos:'))

        counter = 0
        counter_len = len(str(sum(video.get_subtitles().get_nb_subtitles() for video in self._videos)))
        nb_selected = 0

        for video in self._videos:
            self.print('- {}'.format(video.get_filename()))
            for network in video.get_subtitles():
                if not self.download_filter_language_object(network):
                    continue
                network_language = network.get_language()

                xx = ('??' if network_language.is_generic() else network_language.xx()).upper()
                self.print('  [{xx}] {fn} ({bs} {bs_str})'.format(fn=network.get_filename(), bs=network.get_file_size(),
                                                                  bs_str=_('bytes'), xx=xx))
                for subtitle in network:
                    if subtitle.is_local():
                        x = 'X'
                    else:  # if subtitle.is_remote():
                        if subtitle in self._video_rsubs:
                            x = 'x'
                            nb_selected += 1
                        else:
                            x = ' '
                    self.print('       <{x}> [{i}] {s}'.format(i=str(counter).rjust(counter_len), x=x,
                                                               s=self.subtitle_to_short_string(subtitle)))
                    counter += 1

        if nb_selected:
            self.print()
            self.print(ngettext('{} subtitle selected', '{} subtitles selected', nb_selected).format(nb_selected))

    @staticmethod
    def subtitle_to_long_string(subtitle):
        if subtitle.is_local():
            provider_str = _('LOCAL')
        else:
            provider_str = subtitle.get_provider().get_name()
        subtitle_language = subtitle.get_language()
        xx = ('??' if subtitle_language.is_generic() else subtitle_language.xx()).upper()
        return '[{xx}] {fn} ({bs} {bs_str}) [{prov}]'.format(fn=subtitle.get_filename(), xx=xx,
                                                             bs=subtitle.get_file_size(), bs_str=_('bytes'),
                                                             prov=provider_str)

    @staticmethod
    def subtitle_to_short_string(subtitle):
        if subtitle.is_local():
            provider_str = _('LOCAL')
        else:
            provider_str = subtitle.get_provider().get_name()
        return '{fn} [{prov}]'.format(fn=subtitle.get_filename(), prov=provider_str)

    def help_vidselect(self):
        self.print('Select a subtitle of the videos.')
        self.print()
        self.print('vidselect INDEX [INDEX [INDEX [...]]]')
        self.print()
        self.print('  INDEX'.ljust(self.LEN_ARG_COL) + _('Index of the subtitle to select.'))
        self.print()

    def do_vidselect(self, arg):
        if not arg:
            self.print(_('Need an argument.'))
            return
        try:
            subs_i = tuple(int(a) for a in shlex.split(arg))
        except ValueError:
            self.print(_('Invalid value'))
            return
        try:
            subtitles = tuple(self.get_videos_subtitle(sub_i) for sub_i in subs_i)
        except IndexError:
            self.print(_('Value out of range.'))
            return
        self.print(ngettext('Selected subtitle:', 'Selected subtitles:', len(subtitles)))
        for subtitle in subtitles:
            self.print(' - {sub}'.format(sub=self.subtitle_to_long_string(subtitle)))
            if subtitle.is_local():
                self.print(_('Cannot select local subtitles.'))
                return
            if subtitle in self._video_rsubs:
                self.print(_('Subtitle was already added. Ignoring.'))
        self._video_rsubs.update(subtitles)

    def help_viddeselect(self):
        self.print('Deselect a subtitle of the videos.')
        self.print()
        self.print('viddeselect INDEX [INDEX [INDEX [...]]]')
        self.print()
        self.print('  INDEX'.ljust(self.LEN_ARG_COL) + _('Index of the subtitle to deselect.'))
        self.print()

    def do_viddeselect(self, arg):
        if not arg:
            self.print(_('Need an argument.'))
            return
        try:
            subs_i = tuple(int(a) for a in shlex.split(arg))
        except ValueError:
            self.print(_('Invalid value'))
            return
        try:
            subtitles = tuple(self.get_videos_subtitle(sub_i) for sub_i in subs_i)
        except IndexError:
            self.print(_('Value out of range.'))
            return
        self.print(ngettext('Deselected subtitle:', 'Deselected subtitles:', len(subtitles)))
        for subtitle in subtitles:
            self.print(' - {sub}'.format(sub=self.subtitle_to_long_string(subtitle)))
            if subtitle.is_local():
                self.print(_('Cannot deselect local subtitle'))
                return
            if subtitle not in self._video_rsubs:
                self.print(_('Subtitle was not selected'))
                return
        for subtitle in subtitles:
            self._video_rsubs.remove(subtitle)

    def help_login(self):
        self.print(_('Log in to a provider (default is all providers).'))
        self.print()
        self.print('login [PROVIDER]')
        self.print()
        self.print('  PROVIDER '.ljust(self.LEN_ARG_COL) + _('Provider name to log in.'))
        self.print()

    def do_login(self, arg):
        item = arg if arg else None
        try:
            self.state.connect(item)
            self.state.login(item)
            self.print(_('Log in successful.'))
        except ProviderConnectionError:
            self.print(_('Failed to log in.'))
        except IndexError:
            self.print(_('Unknown provider.'))

    def help_logout(self):
        self.print(_('Log out of a provider (default is all providers).'))
        self.print()
        self.print('logout [PROVIDER]')
        self.print()
        self.print('  PROVIDER '.ljust(self.LEN_ARG_COL) + _('Provider name to log out.'))
        self.print()

    def do_logout(self, arg):
        item = arg if arg else None
        try:
            self.state.logout(item)
            self.state.disconnect(item)
            self.print(_('Log out successful.'))
        except ProviderConnectionError:
            self.print(_('Failed to log out.'))
        except IndexError:
            self.print(_('Unknown provider.'))

    def help_ping(self):
        self.print(_('Ping a provider (default is all providers).'))
        self.print()
        self.print('ping [PROVIDER]')
        self.print()
        self.print('  PROVIDER '.ljust(self.LEN_ARG_COL) + _('Provider name to ping.'))
        self.print()

    def do_ping(self, arg):
        item = arg if arg else None
        try:
            self.state.ping(item)
            self.print(_('Sending ping succesful.'))
        except ProviderConnectionError:
            self.print(_('Failed to ping.'))
        except IndexError:
            self.print(_('Unknown provider.'))

    def help_providers(self):
        self.print(_('Add, remove and print info about providers (default is print info about all providers).'))
        self.print()
        self.print('providers [add | remove | list PROVIDER]')
        self.print()
        self.print('  add PROVIDER '.ljust(self.LEN_ARG_COL) + _('Add PROVIDER.'))
        self.print('  remove PROVIDER '.ljust(self.LEN_ARG_COL) + _('Remove PROVIDER.'))
        self.print('  list PROVIDER '.ljust(self.LEN_ARG_COL) + _('Print info about PROVIDER.'))
        self.print()

    def do_providers(self, arg):
        args = shlex.split(arg)
        if args:
            if len(args) != 2:
                self.print(_('Wrong number of arguments.'))
                return
            cmd = args[0]
            name = args[1]
            if cmd == 'add':
                res = self.state.provider_add(name)
                if res:
                    self.print(_('Provider added.'))
                else:
                    self.print(_('Add failed.'))
            elif cmd == 'remove':
                res = self.state.provider_remove(name)
                if res:
                    self.print(_('Provider removed.'))
                    self._invalidate_videos()
                    self._invalidate_text_queries()
                else:
                    self.print(_('Removal failed.'))
            elif cmd == 'list':
                try:
                    provider = self.state.provider_get(name)
                    self.print(_('- Name: {} ({})').format(provider.get_name(), provider.get_short_name()))
                    self.print(_('- Connected: {}').format(provider.connected()))
                    self.print(_('- Logged in: {}').format(provider.logged_in()))
                except IndexError:
                    self.print(_('Provider "{}" not found').format(name))
            else:
                self.print(_('Unknown command "{}".').format(cmd))
        else:
            providers = self.state.get_providers()
            if providers:
                self.print(
                    ngettext('{} active provider:', '{} active providers:', len(providers)).format(len(providers)))
                for provider in providers:
                    logged_in_str = _('logged in') if provider.logged_in() else _('logged out')
                    self.print(' - {}: {}'.format(provider.get_name(), logged_in_str))
            else:
                self.print(_('No active provider.'))

    def help_recursive(self):
        self.print(_('Get/set recursive flag (default is to get the current flag).'))
        self.print()
        self.print('recursive [0 | 1]')
        self.print()
        self.print('  0'.ljust(self.LEN_ARG_COL) + _('Disable recursive flag'))
        self.print('  1'.ljust(self.LEN_ARG_COL) + _('Enable recursive flag'))
        self.print()

    def do_recursive(self, arg):
        if arg:
            try:
                self.state.set_recursive(int(arg))
                return
            except ValueError:
                self.print(_('Invalid argument.'))
                return
        self.print(_('Recursive: {}').format(self.state.is_recursive()))

    RENAME_INDEX_STRATEGY = {
        'vid': SubtitleRenameStrategy.VIDEO,
        'vid_lang': SubtitleRenameStrategy.VIDEO_LANG,
        'vid_lang_upl': SubtitleRenameStrategy.VIDEO_LANG_UPLOADER,
        'online': SubtitleRenameStrategy.ONLINE
    }

    @staticmethod
    def get_strategy_rename_doc(strategy):
        if strategy == SubtitleRenameStrategy.VIDEO:
            return _('Use the local video filename as name for the downloaded subtitle.')
        elif strategy == SubtitleRenameStrategy.VIDEO_LANG:
            return _('Use the local video filename + language as name for the downloaded subtitle.')
        elif strategy == SubtitleRenameStrategy.VIDEO_LANG_UPLOADER:
            return _('Use the local video filename + uploader + language as name for the downloaded subtitle.')
        else:  # if strategy == SubtitleRenameStrategy.ONLINE:
            return _('Use the on-line subtitle filename as name for the downloaded subtitles.')

    def help_rename(self):
        self.print(_('Get/set the subtitle rename strategy. (default is to get the rename strategy)'))
        self.print()
        self.print('rename [{}]'.format(' | '.join(str(k) for k in self.RENAME_INDEX_STRATEGY.keys())))
        self.print()

        for index, strategy in self.RENAME_INDEX_STRATEGY.items():
            self.print('  {}'.format(index).ljust(self.LEN_ARG_COL) + self.get_strategy_rename_doc(strategy))
        self.print()

    def do_rename(self, arg):
        if not arg:
            self.print(_('Current subtitle rename strategy:'))
        else:
            try:
                strategy = self.RENAME_INDEX_STRATEGY[arg]
            except KeyError:
                self.print(_('Invalid subtitle rename strategy'))
                return
            self.state.set_subtitle_rename_strategy(strategy)
            self.print(_('New subtitle rename strategy:'))
        self.print(self.get_strategy_rename_doc(self.state.get_subtitle_rename_strategy()))

    def get_file_save_as_cb(self):
        def file_save_as_cb(path, filename):
            self.print('{}: {}'.format(_('Current download path'), path / filename))
            new_path_str = self.read_line('New')
            if not new_path_str:
                return path / filename
            return Path(new_path_str)
        return file_save_as_cb

    def help_viddownload(self):
        self.print(_('Download the selected subtitles for the video files.'))
        self.print()
        self.print('viddownload')
        self.print()

    def do_viddownload(self, arg):
        if arg:
            self.print(_('Unknown arguments: {}').format(arg))
            return
        subs_to_download = {rsub for rsub in self._video_rsubs if self.download_filter_language_object(rsub)}
        self.print(_('Number of subs to download: {}'.format(len(subs_to_download))))
        for rsub in subs_to_download:
            self.print('- {}'.format(self.subtitle_to_long_string(rsub)))
            provider_type = rsub.get_provider()
            try:
                provider = self.state.provider_get(provider_type)
            except IndexError:
                self.print(_('Provider not available.'))
                return
            target_path = self.state.calculate_download_path(rsub, self.get_file_save_as_cb())
            callback = self.get_callback()
            try:
                rsub.download(target_path=target_path, provider_instance=provider, callback=callback)
            except ProviderConnectionError:
                self.print(_('An error happened during download'))
                return
            self._video_rsubs.remove(rsub)

    # FIXME: merge these..

    def query_active(self):
        return self._text_query is not None

    def do_query(self, arg):
        if not arg:
            if not self.query_active():
                self.print(_('No query active'))
            else:
                self.print('{}: "{}"'.format(_('Current query'), self._text_query.text))
                self.print('{}: {}'.format(_('More movies available'), self._text_query.more_movies_available()))
            return
        self.set_text_query(self.state.query_text_all(text=arg))

    def do_querymore(self, arg):
        if not self.query_active():
            self.print(_('No query active'))
            return

        try:
            self._text_query.search_more_movies()
        except ProviderConnectionError:
            self.print(_('An error occured'))

    def do_queryhasmore(self, arg):
        if arg:
            self.print(_('Unknown arguments: {}').format(arg))
            return
        if not self.query_active():
            self.print(_('No query active'))
            return
        self.print(_('Yes') if self._text_query.more_movies_available() else _('No'))

    def do_querysubsearch(self, arg):
        if not self.query_active():
            self.print(_('No query active'))
            return
        try:
            rmovie_network_i = int(arg)
            rmovie_network = self._text_query.movies[rmovie_network_i]
        except ValueError:
            self.print(_('Need an argument'))
            return
        except IndexError:
            self.print(_('Movie not available'))
            return
        if not rmovie_network.more_subtitles_available():
            self.print(_('List of all remote subtitles fetched'))
            return
        rmovie_network.search_more_subtitles()

    def do_queryshow(self, arg):
        if arg:
            self.print(_('Unknown arguments: {}').format(arg))
            return
        if not self.query_active():
            self.print(_('No query active'))
            return
        sub_i = 0
        for rmovie_network_i, rmovie_network in enumerate(self._text_query.movies):
            rmovie_identity = rmovie_network.get_identities()
            video_identity = rmovie_identity.video_identity
            name = video_identity.get_name()
            year = video_identity.get_year()
            subs_total = rmovie_network.get_nb_subs_total()
            subs_avail = rmovie_network.get_nb_subs_available()
            print('[{rmov_i}] {name} ({year}) [{nb_avail}/{nb_total}]'.format(
                rmov_i=rmovie_network_i, name=name, year=year, nb_avail=subs_avail, nb_total=subs_total))
            for rsub_network in rmovie_network.get_subtitles():
                if not self.download_filter_language_object(rsub_network):
                    continue
                print('  [{xx}] {nb} {subtitles_str} ({full_lang_str})'.format(
                    xx=rsub_network.get_language().xx(),
                    nb=len(rsub_network),
                    subtitles_str=ngettext('subtitle', 'subtitles', len(rsub_network)),
                    full_lang_str=_(rsub_network.get_language().name())))
                for rsub in rsub_network:
                    if not isinstance(rsub, RemoteSubtitleFile):
                        continue
                    x = rsub in self._query_rsubs
                    uploader = _('unknown') if rsub.get_uploader() is None else rsub.get_uploader()
                    print('    <{x}> [{sub_i}] {rating_str}: {rat}, {uploader_str}: {upl}'.format(
                        x='x' if x else ' ',
                        sub_i=sub_i,
                        rating_str=_('Rating'), rat=rsub.get_rating(),
                        uploader_str=_('Uploader'), upl=uploader))
                    sub_i += 1

    def query_get_subtitle(self, index):
        sub_i = 0
        for rmovie_network in self._text_query.movies:
            for rsub_network in rmovie_network.get_subtitles():
                if not self.download_filter_language_object(rsub_network):
                    continue
                for rsub in rsub_network:
                    if not isinstance(rsub, RemoteSubtitleFile):
                        continue
                    if sub_i == index:
                        return rsub
                    sub_i += 1

        return None

    def do_queryselect(self, arg):
        if not self.query_active():
            self.print(_('No query active'))
            return
        try:
            sel_i = int(arg)
        except ValueError:
            self.print(_('Invalid index'))
            return
        rsub = self.query_get_subtitle(sel_i)
        if rsub is None:
            self.print(_('Index out of range'))
            return
        self._query_rsubs.add(rsub)

    def do_querydeselect(self, arg):
        if not self.query_active():
            self.print(_('No query active'))
            return
        try:
            sel_i = int(arg)
        except ValueError:
            self.print(_('Invalid index'))
            return
        rsub = self.query_get_subtitle(sel_i)
        if rsub is None:
            self.print(_('Index out of range'))
            return
        self._query_rsubs.remove(rsub)

    def do_querydownload(self, arg):
        if arg:
            self.print(_('Unknown arguments: {}').format(arg))
            return
        subs_to_download = {rsub for rsub in self._query_rsubs if self.download_filter_language_object(rsub)}
        self.print(_('Number of subs to download: {}'.format(len(subs_to_download))))
        for rsub in subs_to_download:
            self.print('- {}'.format(self.subtitle_to_long_string(rsub)))
            provider_type = rsub.get_provider()
            try:
                provider = self.state.provider_get(provider_type)
            except IndexError:
                self.print(_('Provider not available.'))
                return
            target_path = self.state.calculate_download_query_path(rsub, self.get_file_save_as_cb())
            callback = self.get_callback()
            try:
                rsub.download(target_path=target_path, provider_instance=provider, callback=callback)
            except ProviderConnectionError:
                self.print(_('An error happened during download'))
                return
            self._query_rsubs.remove(rsub)
