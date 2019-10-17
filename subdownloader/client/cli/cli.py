# -*- coding: utf-8 -*-
# Copyright (c) 2019 SubDownloader Developers - See COPYING - GPLv3

from cmd import Cmd
import logging
from os import linesep
from pathlib import Path
import re
import shlex

from subdownloader.client.cli.callback import ProgressBarCallback
from subdownloader.client.cli.state import CliState
from subdownloader.client.state import SubtitleNamingStrategy
from subdownloader.util import IllegalPathException
from subdownloader.filescan import scan_videopaths
import subdownloader.project
from subdownloader.provider.provider import ProviderConnectionError
from subdownloader.languages.language import Language, NotALanguageException, UnknownLanguage
from subdownloader.languages.language import LANGUAGES as ALL_LANGUAGES
from subdownloader.subtitle2 import RemoteSubtitleFile
from subdownloader.movie import LocalMovie, VideoSubtitle

log = logging.getLogger(__name__)


class BadCliArguments(Exception):
    pass


class CliCmd(Cmd):
    def __init__(self, settings, options):
        Cmd.__init__(self)
        self._state = CliState()
        self._settings = settings
        self._state.load_options(options)
        self._state.load_settings(settings)

        self._return_code = 1
        self.prompt = '>>> '

        # Download state
        # FIXME: abstract to FileQueryState object
        self._videos = []
        self._video_rsubs = set()

        # Text query state
        # FIXME: abstract to TextQueryState object
        self._text_query = None
        self._query_rsubs = set()

        # Upload state
        self._upload_movie = LocalMovie()

        self.intro = '{name} {version}\n{intro}'.format(
            name=subdownloader.project.PROJECT_TITLE,
            version=subdownloader.project.PROJECT_VERSION_FULL_STR,
            intro=_('Type "{}" for more information.').format('help'),
        )

    def run(self):
        if self._state.get_console():
            return self.cmdloop()
        else:
            if self._state.get_list_languages():
                self.onecmd('listlanguages')
            else:
                # FIXME: check CliAction
                return self.run_headless()

    _RE_SHLEX_UNQUOTE = re.compile(r'''(["'])(.*)\1|(.*)''')

    def shlex_parse_argstr(self, argline):
        try:
            raw_args = shlex.split(argline, posix=True)
        except ValueError as e:
            raise BadCliArguments(*e.args)
        result = []
        for arg in raw_args:
            m = self._RE_SHLEX_UNQUOTE.match(arg)
            result.append(m.group(2) or m.group(3))
        return result

    def run_headless(self):
        self.onecmd('login')
        self.onecmd('filescan')
        self.onecmd('vidsearch')
        for video in self._videos:
            self._print_videos([video])
            nb, nb_total = self.get_number_remote_subtitles(video)
            if not nb:
                if nb_total:
                    print(_('Video has no subtitles that match your filter. Skipping.'))
                else:
                    print(_('Video has no subtitles. Skipping.'))
                continue

            if self._state.get_interactive():
                try:
                    sub_i = int(input('{} [0-{}) '.format(_('What subtitle would you like to download?'), nb)).strip())
                except (IndexError, ValueError):
                    self.echo(_('Invalid index.'))
                    return 1
            else:
                self.echo('{} ({})'.format(_('Auto-selecting first subtitle.'),
                                            _('Use interactive mode to select another subtitle.')))
                sub_i = 0
            try:
                subtitle = self.get_videos_subtitle(sub_i, [video])
            except IndexError:
                self.echo(_('Video has no subtitles that match the filter.'))
                continue
            self.echo(_('Selected subtitle:'),  self.subtitle_to_long_string(subtitle))
            if subtitle.is_local():
                self.echo(_('Cannot select local subtitles.'))
                continue
            self._video_rsubs.update({subtitle})
        self.onecmd('viddownload')

    def cleanup(self):
        self._state.providers.logout()

    def _invalidate_videos(self):
        self.set_videos([])

    def set_videos(self, videos):
        self._videos = videos
        self._video_rsubs = set()

    def get_videos_subtitle(self, sub_index_req, videos=None):
        if sub_index_req < 0:
            raise IndexError()
        if videos is None:
            videos = self._videos
        subtitle_index = 0
        for video in videos:
            for subtitle_network in video.get_subtitles():
                if not self.download_filter_language_object(subtitle_network):
                    continue
                # if sub_index_req > subtitle_index + len(subtitle_network):
                #     continue
                for subtitle in subtitle_network.get_subtitles():
                    if subtitle.is_local():
                        continue
                    if subtitle_index == sub_index_req:
                        return subtitle
                    subtitle_index += 1
        else:
            raise IndexError()

    def get_number_remote_subtitles(self, video):
        count_filter = 0
        count_total = 0
        for subtitle_network in video.get_subtitles():
            for subtitle in subtitle_network:
                if subtitle.is_remote():
                    if self.download_filter_language_object(subtitle_network):
                        count_filter += 1
                    count_total += 1
        return count_filter, count_total

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

    def echo(self, *what):
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

    def onecmd(self, line):
        log.debug('onecmd("{}")'.format(line))
        try:
            return Cmd.onecmd(self, line)
        except BadCliArguments:
            self.echo(_('Bad arguments'))
            return False

    def postloop(self):
        self.cleanup()

    def get_callback(self):
        return ProgressBarCallback(fd=self.stdout)

    LEN_ARG_COL = 15

    def help_EOF(self):
        self.echo(_('Exit program') + ' (CTRL+D).')
        self.echo()
        self.echo('EOF')
        self.echo()

    def do_EOF(self, arg):
        self._return_code = 0
        return True

    def help_exit(self):
        self.echo(_('Alias for {}').format('quit'))
        self.echo()
        return self.help_quit()

    def do_exit(self, arg):
        return self.do_quit(arg)

    def help_quit(self):
        self.echo(_('Exit program') + '.')
        self.echo()
        self.echo('quit')
        self.echo()

    def do_quit(self, arg):
        self._return_code = 0
        return True

    def help_language(self):
        self.echo(_('Alias for {}').format('languages'))
        self.echo()
        return self.help_languages()

    def do_language(self, arg):
        return self.do_languages(arg)

    def help_languages(self):
        lang = _('LANGUAGE')
        self.echo(_('Get/replace the filter languages. (default is to get the filter languages)'))
        self.echo()
        self.echo('languages [0 | {lang} [{lang} [...]]]'.format(lang=lang))
        self.echo()
        self.echo('  {lang} '.format(lang=lang).ljust(self.LEN_ARG_COL) +
                   _('Add {lang} as filter language (current filter will be lost).').format(lang=lang))
        self.echo('  0 '.ljust(self.LEN_ARG_COL) + _('Clear all filter languages.'))
        self.echo()

    def do_languages(self, arg):
        if arg:
            try:
                if int(arg) == 0:
                    self.state.set_download_languages([])
                self.echo(_('Filter languages cleared'))
                return
            except ValueError:
                pass

            try:
                langs = [Language.from_unknown(l_str, xx=True, xxx=True, name=True, locale=True)
                         for l_str in self.shlex_parse_argstr(arg)]
            except NotALanguageException as e:
                self.echo(_('"{}" is not a valid language').format(e.value))
                return
            self.state.set_download_languages(langs)
            self.echo(ngettext('New filter language:', 'New filter languages:',
                                len(self.state.get_download_languages())))
            for language in self.state.get_download_languages():
                self.echo('- {}'.format(language.name()))
            return
        else:
            self.echo(ngettext('Current filter language:', 'Current filter languages:',
                       len(self.state.get_download_languages())))
            if self.state.get_download_languages():
                for language in self.state.get_download_languages():
                    self.echo('- {}'.format(language.name()))
            else:
                self.echo(_('(None)'))

    # def complete_languages(self, text, line, begidx, endidx):
    #     # FIXME: implement completer for languages

    def help_listlanguages(self):
        self.echo(_('List all available languages.'))
        self.echo()
        self.echo('listlanguages')
        self.echo()

    def do_listlanguages(self, arg):
        if arg:
            self.echo(_('Unknown arguments: {}').format(arg))
            return
        fmt = '{name:<25} | {locale:<10} | {lid:<10} | {iso639:<10}'
        header = fmt.format(name=_('name'), locale=_('locale'), lid=_('ISO639-3'), iso639=_('ISO639-2'))
        self.echo(header)
        self.echo('-'*len(header))
        for lang in ALL_LANGUAGES[1:]:
            self.echo(fmt.format(name=lang['LanguageName'][0],
                                  locale=', '.join(lang['locale']),
                                  lid=', '.join(lang['LanguageID']),
                                  iso639=', '.join(lang['ISO639'])))

    def help_filepath(self):
        self.echo(_('Get/set the file path(s).'))
        self.echo()
        self.echo('filepath [PATH [PATH [...]]]')
        self.echo()
        self.echo('  PATH'.ljust(self.LEN_ARG_COL) + _('File path to add.'))
        self.echo()

    def do_filepath(self, arg):
        if arg:
            self.state.set_video_paths([Path(p).expanduser() for p in self.shlex_parse_argstr(arg)])
        if arg:
            self.echo(ngettext('New file path:', 'New file paths:', len(self.state.get_video_paths())))
        else:
            self.echo(ngettext('Current file path:', 'Current file paths:', len(self.state.get_video_paths())))
        for path in self.state.get_video_paths():
            self.echo('- {}'.format(path))

    # def complete_videopath(self, text, line, begidx, endidx):
    #     # FIXME: implement completer for paths

    def help_filescan(self):
        self.echo(_('Scan the file path(s) for videos.'))
        self.echo()
        self.echo('filescan')
        self.echo()

    def do_filescan(self, arg):
        callback = self.get_callback()

        callback.set_title_text(_('Scanning...'))
        callback.set_label_text(_('Scanning files'))
        callback.set_finished_text(_('Scanning finished'))
        callback.set_block(True)
        callback.show()

        try:
            local_videos, local_subs = scan_videopaths(self.state.get_video_paths(), callback,
                                                       recursive=self.state.get_recursive())
        except IllegalPathException as e:
            callback.finish()
            self.echo(_('The video path "{}" does not exist').format(e.path()))
            return

        callback.finish()

        self.set_videos(local_videos)
        self.echo(_('{}/{} videos/subtitles have been found').format(len(local_videos), len(local_subs)))

    def help_vidsearch(self):
        self.echo(_('Search for corresponding subtitles for the videos on the current providers.'))
        self.echo()
        self.echo('vidsearch')
        self.echo()

    def do_vidsearch(self, arg):
        callback = self.get_callback()
        callback.set_title_text(_('Asking Server...'))
        callback.set_label_text(_('Searching subtitles...'))
        callback.set_updated_text(_('Searching subtitles ( %d / %d )'))
        callback.set_finished_text(_('Search finished'))
        callback.set_block(True)
        callback.show()

        try:
            self.state.search_videos(self._videos, callback)
        except ProviderConnectionError:
            callback.finish()
            self.echo(_('Failed to search for videos.'))
            return

        callback.finish()
        self.echo(_('Search finished.'))

    @staticmethod
    def classify_rsubtitles_language(video):
        lang_network = {}
        for network in video.get_subtitles().get_subtitle_networks():
            lang_network.setdefault(network.get_language(), []).append(network)
        return lang_network

    def help_videos(self):
        self.echo(_('Get/clear the videos (default is get all videos).'))
        self.echo()
        self.echo('videos [clear]')
        self.echo()
        self.echo('  clear'.ljust(self.LEN_ARG_COL) + _('Clear the videos'))
        self.echo()

    def do_videos(self, arg):
        if arg:
            if arg == 'clear':
                self.set_videos([])
            else:
                self.echo(_('Unknown command'))
                return
        self.echo(_('Current videos:'))

        nb_selected = self._print_videos(self._videos)

        if nb_selected:
            self.echo()
            self.echo(ngettext('{} subtitle selected', '{} subtitles selected', nb_selected).format(nb_selected))

    def _print_videos(self, videos):
        counter = 0
        counter_len = len(str(sum(video.get_subtitles().get_nb_subtitles() for video in self._videos)))
        nb_selected = 0

        for video in videos:
            self.echo('- {}'.format(video.get_filename()))
            for network in video.get_subtitles():
                if not self.download_filter_language_object(network):
                    continue
                network_language = network.get_language()

                xx = ('??' if network_language.is_generic() else network_language.xx()).upper()
                self.echo('  [{xx}] {fn} ({bs} {bs_str})'.format(fn=network.get_filename(), bs=network.get_file_size(),
                                                                  bs_str=_('bytes'), xx=xx))
                for subtitle in network:
                    if subtitle.is_local():
                        x = 'X'
                        str_counter = '   '
                    else:  # if subtitle.is_remote():
                        if subtitle in self._video_rsubs:
                            x = 'x'
                            nb_selected += 1
                        else:
                            x = ' '
                        str_counter = '{:>3}'.format(counter)
                        counter += 1
                    self.echo('       <{x}> [{i}] {s}'.format(i=str_counter, x=x,
                                                               s=self.subtitle_to_short_string(subtitle)))
        return nb_selected

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
        self.echo('Select a subtitle of the videos.')
        self.echo()
        self.echo('vidselect INDEX [INDEX [INDEX [...]]]')
        self.echo()
        self.echo('  INDEX'.ljust(self.LEN_ARG_COL) + _('Index of the subtitle to select.'))
        self.echo()

    def do_vidselect(self, arg):
        if not arg:
            self.echo(_('Need an argument.'))
            return
        try:
            subs_i = tuple(int(a) for a in self.shlex_parse_argstr(arg))
        except ValueError:
            self.echo(_('Invalid value'))
            return
        try:
            subtitles = tuple(self.get_videos_subtitle(sub_i) for sub_i in subs_i)
        except IndexError:
            self.echo(_('Value out of range.'))
            return
        self.echo(ngettext('Selected subtitle:', 'Selected subtitles:', len(subtitles)))
        for subtitle in subtitles:
            self.echo(' - {sub}'.format(sub=self.subtitle_to_long_string(subtitle)))
            if subtitle.is_local():
                self.echo(_('Cannot select local subtitles.'))
                return
            if subtitle in self._video_rsubs:
                self.echo(_('Subtitle was already added. Ignoring.'))
        self._video_rsubs.update(subtitles)

    def help_viddeselect(self):
        self.echo('Deselect a subtitle of the videos.')
        self.echo()
        self.echo('viddeselect INDEX [INDEX [INDEX [...]]]')
        self.echo()
        self.echo('  INDEX'.ljust(self.LEN_ARG_COL) + _('Index of the subtitle to deselect.'))
        self.echo()

    def do_viddeselect(self, arg):
        if not arg:
            self.echo(_('Need an argument.'))
            return
        try:
            subs_i = tuple(int(a) for a in self.shlex_parse_argstr(arg))
        except ValueError:
            self.echo(_('Invalid value'))
            return
        try:
            subtitles = tuple(self.get_videos_subtitle(sub_i) for sub_i in subs_i)
        except IndexError:
            self.echo(_('Value out of range.'))
            return
        self.echo(ngettext('Deselected subtitle:', 'Deselected subtitles:', len(subtitles)))
        for subtitle in subtitles:
            self.echo(' - {sub}'.format(sub=self.subtitle_to_long_string(subtitle)))
            if subtitle.is_local():
                self.echo(_('Cannot deselect local subtitle'))
                return
            if subtitle not in self._video_rsubs:
                self.echo(_('Subtitle was not selected'))
                return
        for subtitle in subtitles:
            self._video_rsubs.remove(subtitle)

    def help_login(self):
        self.echo(_('Log in to a provider (default is all providers).'))
        self.echo()
        self.echo('login [PROVIDER]')
        self.echo()
        self.echo('  PROVIDER '.ljust(self.LEN_ARG_COL) + _('Provider name to log in.'))
        self.echo()

    def do_login(self, arg):
        item = arg if arg else None
        try:
            self.state.providers.connect(item)
            self.state.providers.login(item)
            self.echo(_('Log in successful.'))
        except ProviderConnectionError:
            self.echo(_('Failed to log in.'))
        except IndexError:
            self.echo(_('Unknown provider.'))

    def help_logout(self):
        self.echo(_('Log out of a provider (default is all providers).'))
        self.echo()
        self.echo('logout [PROVIDER]')
        self.echo()
        self.echo('  PROVIDER '.ljust(self.LEN_ARG_COL) + _('Provider name to log out.'))
        self.echo()

    def do_logout(self, arg):
        item = arg if arg else None
        try:
            self.state.providers.logout(item)
            self.state.providers.disconnect(item)
            self.echo(_('Log out successful.'))
        except ProviderConnectionError:
            self.echo(_('Failed to log out.'))
        except IndexError:
            self.echo(_('Unknown provider.'))

    def help_ping(self):
        self.echo(_('Ping a provider (default is all providers).'))
        self.echo()
        self.echo('ping [PROVIDER]')
        self.echo()
        self.echo('  PROVIDER '.ljust(self.LEN_ARG_COL) + _('Provider name to ping.'))
        self.echo()

    def do_ping(self, arg):
        item = arg if arg else None
        try:
            self.state.providers.ping(item)
            self.echo(_('Sending ping succesful.'))
        except ProviderConnectionError:
            self.echo(_('Failed to ping.'))
        except IndexError:
            self.echo(_('Unknown provider.'))

    def help_providers(self):
        self.echo(_('Enable, disable and print info about providers (default is print info about all providers).'))
        self.echo()
        self.echo('providers [add | remove | list] PROVIDER')
        self.echo()
        self.echo('  enable PROVIDER '.ljust(self.LEN_ARG_COL) + _('Enable PROVIDER.'))
        self.echo('  disable PROVIDER '.ljust(self.LEN_ARG_COL) + _('Disable PROVIDER.'))
        self.echo('  list PROVIDER '.ljust(self.LEN_ARG_COL) + _('Print info about PROVIDER.'))
        self.echo()

    def do_providers(self, arg):
        args = self.shlex_parse_argstr(arg)
        if args:
            if len(args) != 2:
                self.echo(_('Wrong number of arguments.'))
                return
            cmd = args[0]
            name = args[1]
            try:
                providerState = self.state.providers.get(name)
            except IndexError:
                self.echo(_('Provider not available.'))
                return
            provider = providerState.provider
            if cmd == 'enable':
                providerState.setEnabled(True)
            elif cmd == 'disable':
                providerState.setEnabled(False)
            elif cmd == 'list':
                try:
                    self.echo(_('- Name: {} ({})').format(provider.get_name(), provider.get_short_name()))
                    self.echo(_('- Enabled: {}').format(providerState.getEnabled()))
                    self.echo(_('- Connected: {}').format(provider.connected()))
                    self.echo(_('- Logged in: {}').format(provider.logged_in()))
                except IndexError:
                    self.echo(_('Provider "{}" not found').format(name))
            else:
                self.echo(_('Unknown command "{}".').format(cmd))
        else:
            providerStates = list(self._state.providers.all_states)
            nbEnabled = len(list(ps for ps in providerStates if ps.getEnabled()))
            if providerStates:
                self.echo(_('#providers: {}').format(len(providerStates)))
                self.echo(_('#enabled providers: {}').format(nbEnabled))
                for providerState in iter(self.state.providers.all_states):
                    provider = providerState.provider
                    if providerState.getEnabled():
                        logged_in_str = _('logged in') if provider.logged_in() else _('logged out')
                        self.echo(' - {}: {} ({})'.format(provider.get_name(), _('Enabled'), logged_in_str))
                    else:
                        self.echo('- {}: {}'.format(provider.get_name(), _('Disabled')))
            else:
                self.echo(_('No providers.'))

    def help_recursive(self):
        self.echo(_('Get/set recursive flag (default is to get the current flag).'))
        self.echo()
        self.echo('recursive [0 | 1]')
        self.echo()
        self.echo('  0'.ljust(self.LEN_ARG_COL) + _('Disable recursive flag'))
        self.echo('  1'.ljust(self.LEN_ARG_COL) + _('Enable recursive flag'))
        self.echo()

    def do_recursive(self, arg):
        if arg:
            try:
                self.state.set_recursive(True if int(arg) else False)
                return
            except ValueError:
                self.echo(_('Invalid argument.'))
                return
        self.echo(_('Recursive: {}').format(self.state.get_recursive()))

    NAMING_STRATEGY_LUT = {
        'vid': SubtitleNamingStrategy.VIDEO,
        'vid_lang': SubtitleNamingStrategy.VIDEO_LANG,
        'vid_lang_upl': SubtitleNamingStrategy.VIDEO_LANG_UPLOADER,
        'online': SubtitleNamingStrategy.ONLINE
    }

    @staticmethod
    def get_strategy_naming_doc(strategy):
        if strategy == SubtitleNamingStrategy.VIDEO:
            return _('Use the local video filename as name for the downloaded subtitle.')
        elif strategy == SubtitleNamingStrategy.VIDEO_LANG:
            return _('Use the local video filename + language as name for the downloaded subtitle.')
        elif strategy == SubtitleNamingStrategy.VIDEO_LANG_UPLOADER:
            return _('Use the local video filename + uploader + language as name for the downloaded subtitle.')
        else:  # if strategy == SubtitleNamingStrategy.ONLINE:
            return _('Use the on-line subtitle filename as name for the downloaded subtitles.')

    def help_rename(self):
        self.echo(_('Get/set the subtitle naming strategy. (default is to get the current naming strategy)'))
        self.echo()
        self.echo('rename [{}]'.format(' | '.join(str(k) for k in self.NAMING_STRATEGY_LUT.keys())))
        self.echo()

        for index, strategy in self.NAMING_STRATEGY_LUT.items():
            self.echo('  {}'.format(index).ljust(self.LEN_ARG_COL) + self.get_strategy_naming_doc(strategy))
        self.echo()

    def do_rename(self, arg):
        if not arg:
            self.echo(_('Current subtitle naming strategy:'))
        else:
            try:
                strategy = self.NAMING_STRATEGY_LUT[arg]
            except KeyError:
                self.echo(_('Invalid subtitle naming strategy'))
                return
            self.state.set_subtitle_naming_strategy(strategy)
            self.echo(_('New subtitle naming strategy:'))
        self.echo(self.get_strategy_naming_doc(self.state.get_subtitle_naming_strategy()))

    def get_file_save_as_cb(self):
        def file_save_as_cb(path, filename):
            self.echo('{}: {}'.format(_('Current download path'), path / filename))
            new_path_str = self.read_line('New')
            if not new_path_str:
                return path / filename
            return Path(new_path_str)
        return file_save_as_cb

    def help_viddownload(self):
        self.echo(_('Download the selected subtitles for the video files.'))
        self.echo()
        self.echo('viddownload')
        self.echo()

    def do_viddownload(self, arg):
        if arg:
            self.echo(_('Unknown arguments: {}').format(arg))
            return
        subs_to_download = {rsub for rsub in self._video_rsubs if self.download_filter_language_object(rsub)}
        self.echo(_('Number of subs to download: {}'.format(len(subs_to_download))))
        for rsub in subs_to_download:
            self.echo('- {}'.format(self.subtitle_to_long_string(rsub)))
            provider_type = rsub.get_provider()
            try:
                providerState = self.state.providers.get(provider_type)
            except IndexError:
                self.echo(_('Provider "{}" not available.').format(provider_type.get_name()))
                return
            target_path = self.state.calculate_download_path(rsub, self.get_file_save_as_cb())
            callback = self.get_callback()
            try:
                rsub.download(target_path=target_path, provider_instance=providerState.provider, callback=callback)
            except ProviderConnectionError:
                self.echo(_('An error happened during download'))
                return
            self._video_rsubs.remove(rsub)

    # FIXME: merge these..

    def query_active(self):
        return self._text_query is not None

    def help_query(self):
        self.echo(_('Set the text query for searching for subtitles by video name.'))
        self.echo()
        self.echo('query TEXT')
        self.echo()

    def do_query(self, arg):
        if not arg:
            if not self.query_active():
                self.echo(_('No query active'))
            else:
                self.echo('{}: "{}"'.format(_('Current query'), self._text_query.text))
                self.echo('{}: {}'.format(_('More movies available'), self._text_query.more_movies_available()))
            return
        self.set_text_query(self.state.providers.query_text(text=arg))

    def help_querymore(self):
        self.echo(_('Look for more video matches for the current text query.'))
        self.echo(_('The optional argument \'all\' will fetch all videos.'))
        self.echo()
        self.echo('querymore [all]')
        self.echo()

    def do_querymore(self, arg):
        if not self.query_active():
            self.echo(_('No query active'))
            return

        args = self.shlex_parse_argstr(arg)

        fetch_all = False
        if len(args) > 0:
            if args[0] != 'all':
                self.echo(_('Invalid argument'))
                return
            fetch_all = True

        if not self._text_query.more_movies_available():
            self.echo(_('No more videos are available'))
            return

        nb_before = len(self._text_query.movies)

        try:
            if fetch_all:
                while self._text_query.more_movies_available():
                    self._text_query.search_more_movies()
            else:
                self._text_query.search_more_movies()
        except ProviderConnectionError:
            self.echo(_('An error occured'))

        nb_after = len(self._text_query.movies)

        self.echo(_('Found {} extra videos.').format(nb_after - nb_before))

    def help_queryhasmore(self):
        self.echo(_('Check whether more videos can be found using querymore.'))
        self.echo()
        self.echo('queryhasmore')
        self.echo()

    def do_queryhasmore(self, arg):
        if arg:
            self.echo(_('Unknown arguments: {}').format(arg))
            return
        if not self.query_active():
            self.echo(_('No query active'))
            return
        self.echo(_('Yes') if self._text_query.more_movies_available() else _('No'))

    def help_querysubsearch(self):
        self.echo(_('Look for more subtitles for a particular video.'))
        self.echo(_('The optional argument \'all\' will fetch all subtitles.'))
        self.echo()
        self.echo('querysubsearch INDEX [all]')
        self.echo()

    def do_querysubsearch(self, arg):
        if not self.query_active():
            self.echo(_('No query active'))
            return
        args = self.shlex_parse_argstr(arg)

        if len(args) == 0:
            self.echo(_('Need an argument'))
            return

        fetch_all = False
        if len(args) > 1:
            if args[1] != 'all':
                self.echo(_('Invalid argument'))
                return
            fetch_all = True

        if len(args) > 2:
            self.echo(_('Too many arguments'))
            return

        try:
            rmovie_network_i = int(args[0])
            rmovie_network = self._text_query.movies[rmovie_network_i]
        except ValueError:
            self.echo(_('Invalid argument'))
            return
        except IndexError:
            self.echo(_('Movie not available'))
            return

        nb_subtitles_before = len(rmovie_network.get_subtitles())

        if not rmovie_network.more_subtitles_available():
            self.echo(_('No more subtitles are available'))
            return

        if fetch_all:
            while rmovie_network.more_subtitles_available():
                rmovie_network.search_more_subtitles()
        else:
            rmovie_network.search_more_subtitles()

        nb_subtitles_after = len(rmovie_network.get_subtitles())

        self.echo(_('Found {} extra subtitles').format(nb_subtitles_after-nb_subtitles_before))

    def help_queryshow(self):
        self.echo(_('Display the current videos and subtitles, found by query'))
        self.echo()
        self.echo('queryshow')
        self.echo()

    def do_queryshow(self, arg):
        if arg:
            self.echo(_('Unknown arguments: {}').format(arg))
            return
        if not self.query_active():
            self.echo(_('No query active'))
            return
        sub_i = 0
        for rmovie_network_i, rmovie_network in enumerate(self._text_query.movies):
            rmovie_identity = rmovie_network.get_identities()
            video_identity = rmovie_identity.video_identity
            name = video_identity.get_name()
            year = video_identity.get_year()
            subs_avail = rmovie_network.get_nb_subs_available()
            subs_total = rmovie_network.get_nb_subs_total()
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
                    print('    <{x}> [{sub_i}] {fn} {rating_str}: {rat}, {uploader_str}: {upl}'.format(
                        x='x' if x else ' ',
                        sub_i=sub_i,
                        fn=rsub.get_filename(),
                        rating_str=_('Rating'), rat=rsub.get_rating(),
                        uploader_str=_('Uploader'), upl=uploader))
                    sub_i += 1

    def _query_get_subtitle(self, index):
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

    def help_queryselect(self):
        self.echo('Select a subtitle of the current query.')
        self.echo()
        self.echo('queryselect INDEX [INDEX [INDEX [...]]]')
        self.echo()
        self.echo('  INDEX'.ljust(self.LEN_ARG_COL) + _('Index of the subtitle to select.'))
        self.echo()

    def do_queryselect(self, arg):
        if not self.query_active():
            self.echo(_('No query active'))
            return
        try:
            sel_i = int(arg)
        except ValueError:
            self.echo(_('Invalid index'))
            return
        rsub = self._query_get_subtitle(sel_i)
        if rsub is None:
            self.echo(_('Index out of range'))
            return
        self._query_rsubs.add(rsub)

    def help_querydeselect(self):
        self.echo('Deselect a subtitle of the current query.')
        self.echo()
        self.echo('querydeselect INDEX [INDEX [INDEX [...]]]')
        self.echo()
        self.echo('  INDEX'.ljust(self.LEN_ARG_COL) + _('Index of the subtitle to deselect.'))
        self.echo()

    def do_querydeselect(self, arg):
        if not self.query_active():
            self.echo(_('No query active'))
            return
        try:
            sel_i = int(arg)
        except ValueError:
            self.echo(_('Invalid index'))
            return
        rsub = self._query_get_subtitle(sel_i)
        if rsub is None:
            self.echo(_('Index out of range'))
            return
        self._query_rsubs.remove(rsub)

    def help_querydownload(self):
        self.echo(_('Download the selected subtitles of the text query.'))
        self.echo()
        self.echo('querydownload')
        self.echo()

    def do_querydownload(self, arg):
        if arg:
            self.echo(_('Unknown arguments: {}').format(arg))
            return
        subs_to_download = {rsub for rsub in self._query_rsubs if self.download_filter_language_object(rsub)}
        self.echo(_('Number of subs to download: {}'.format(len(subs_to_download))))
        for rsub in subs_to_download:
            self.echo('- {}'.format(self.subtitle_to_long_string(rsub)))
            provider_type = rsub.get_provider()
            try:
                providerState = self.state.providers.get(provider_type)
            except IndexError:
                self.echo(_('Provider not available.'))
                return
            target_path = self.state.calculate_download_query_path(rsub, self.get_file_save_as_cb())
            callback = self.get_callback()
            try:
                rsub.download(target_path=target_path, provider_instance=providerState.provider, callback=callback)
            except ProviderConnectionError:
                self.echo(_('An error happened during download'))
                return
            self._query_rsubs.remove(rsub)

    def do_upload_reset(self, arg):
        if arg:
            self.echo(_('Unknown arguments: {}').format(arg))
            return

        self._upload_movie = LocalMovie()

    def do_upload_filescan(self, arg):
        if arg:
            self.echo(_('Unknown arguments: {}').format(arg))
            return

        self._upload_movie = LocalMovie()

        callback = self.get_callback()

        callback.set_title_text(_('Scanning...'))
        callback.set_label_text(_('Scanning files'))
        callback.set_finished_text(_('Scanning finished'))
        callback.set_block(True)
        callback.show()

        try:
            local_videos, local_subs = scan_videopaths(self.state.get_video_paths(), callback,
                                                       recursive=self.state.get_recursive())
        except IllegalPathException as e:
            callback.finish()
            self.echo(_('The video path "{}" does not exist').format(e.path()))
            return

        callback.finish()

        local_videos.sort(key=lambda v : v.get_filename())

        data = []
        nb_subs = 0
        langs = dict()
        for video in local_videos:
            try:
                subtitle = next(video.get_subtitles().iter_local_subtitles())
                lang = subtitle.detect_language_contents()
                subtitle.set_language_if_unknown(lang)
                langs.setdefault(subtitle.get_language(), 0)
                langs[subtitle.get_language()] += 1
                nb_subs += 1
            except StopIteration:
                subtitle = None
            vid_sub = VideoSubtitle(video, subtitle)
            data.append(vid_sub)

        self._upload_movie.set_data(data)

        unk = UnknownLanguage.create_generic()
        if unk in langs:
            del langs[unk]
        if len(langs) == 1:
            lang = tuple(langs.keys())[0]
        else:
            lang = unk
        if self._upload_movie.get_language().is_generic():
            self._upload_movie.set_language(lang)

        self.set_videos(local_videos)
        self.echo(_('{}/{} videos/subtitles have been found').format(len(data), nb_subs))

    def do_upload_insertrow(self, arg):
        args = self.shlex_parse_argstr(arg)
        if len(args) != 1:
            self.echo(_('Need one argument'))
            return

        data = self._upload_movie.get_data()
        try:
            index = int(args[0])
            if index < 0 or index > len(data):
                raise ValueError
        except ValueError:
            index_err = ' ' + _('Index must be in range {}.').format('[0, {}]'.format(len(data)))
            self.echo('{}{}'.format(_('Invalid index.'), index_err))
            return

        data.insert(index, VideoSubtitle())
        self._upload_movie.set_data(data)

    def do_upload_deleterow(self, arg):
        args = self.shlex_parse_argstr(arg)
        if len(args) != 1:
            self.echo(_('Need one argument'))
            return

        data = self._upload_movie.get_data()
        try:
            index = int(args[0])
            if index < 0 or index > len(data):
                raise ValueError
        except ValueError:
            if len(data) == 0:
                index_err = ''
            else:
                index_err = ' ' + _('Index must be in range {}.').format('[0, {})'.format(len(data)))
            self.echo('{}{}'.format(_('Invalid index.'), index_err))
            return

        del data[index]
        self._upload_movie.set_data(data)

    def do_upload_moverow(self, arg):
        args = self.shlex_parse_argstr(arg)
        if len(args) != 2:
            self.echo(_('Need two arguments'))
            return

        data = self._upload_movie.get_data()
        try:
            index_from = int(args[0])
            index_to = int(args[1])
            if index_from < 0 or index_from > len(data):
                raise ValueError
            if index_to < 0 or index_to > len(data):
                raise ValueError
        except ValueError:
            if len(data) == 0:
                index_err = ''
            else:
                index_err = ' ' + _('Index must be in range {}.').format('[0, {})'.format(len(data)))
            self.echo('{}{}'.format(_('Invalid index.'), index_err))
            return

        moved = data[index_from]
        data[index_from] = None
        data.insert(index_to, moved)
        data.remove(None)
        self._upload_movie.set_data(data)

    @classmethod
    def _arg_string_opt(cls, arg):
        arg = arg.strip()
        return arg if arg else None

    @classmethod
    def _arg_bool(cls, arg):
        arg = arg.strip().lower()
        if arg in ('true', 'yes', '1'):
            return True
        elif arg in ('false', 'no', '0'):
            return False
        raise ValueError

    def do_upload_set_name(self, arg):
        args = self.shlex_parse_argstr(arg)

        if len(args) != 1:
            self.echo('Need 1 argument')
            return

        self._upload_movie.set_movie_name(self._arg_string_opt(args[0]))

    def do_upload_set_imdb(self, arg):
        args = self.shlex_parse_argstr(arg)

        if len(args) != 1:
            self.echo('Need 1 argument')
            return

        self._upload_movie.set_imdb_id(self._arg_string_opt(args[0]))

    def do_upload_set_language(self, arg):
        args = self.shlex_parse_argstr(arg)

        if len(args) == 0:
            self._upload_movie.set_language(UnknownLanguage.create_generic())
            return

        if len(args) != 1:
            self.echo('Need 1 argument')
            return
        try:
            lang = Language.from_unknown(args[0], xx=True, xxx=True, name=True, locale=True)
            self.echo(_('Upload language set to {}.').format(lang.name()))
            self._upload_movie.set_language(lang)
        except NotALanguageException:
            self.echo(_('Unknown language'))
            return

    def do_upload_set_release_name(self, arg):
        args = self.shlex_parse_argstr(arg)

        if len(args) != 1:
            self.echo('Need 1 argument')
            return

        self._upload_movie.set_release_name(self._arg_string_opt(args[0]))

    def do_upload_set_comments(self, arg):
        args = self.shlex_parse_argstr(arg)

        if len(args) != 1:
            self.echo('Need 1 argument')
            return

        self._upload_movie.set_comments(self._arg_string_opt(args[0]))

    def do_upload_set_author(self, arg):
        args = self.shlex_parse_argstr(arg)

        if len(args) != 1:
            self.echo('Need 1 argument')
            return

        self._upload_movie.set_author(self._arg_string_opt(args[0]))

    def do_upload_set_hearing_impaired(self, arg):
        args = self.shlex_parse_argstr(arg)

        if len(args) != 1:
            self.echo('Need 1 argument')
            return

        try:
            self._upload_movie.set_hearing_impaired(self._arg_bool(args[0]))
        except ValueError:
            self.echo(_('Invalid argument value'))

    def do_upload_set_high_definition(self, arg):
        args = self.shlex_parse_argstr(arg)

        if len(args) != 1:
            self.echo('Need 1 argument')
            return

        try:
            self._upload_movie.set_high_definition(self._arg_bool(args[0]))
        except ValueError:
            self.echo(_('Invalid argument value'))

    def do_upload_set_automatic_translation(self, arg):
        args = self.shlex_parse_argstr(arg)

        if len(args) != 1:
            self.echo('Need 1 argument')
            return

        try:
            self._upload_movie.set_automatic_translation(self._arg_bool(args[0]))
        except ValueError:
            self.echo(_('Invalid argument value'))

    def do_upload_list(self, arg):
        if arg:
            self.echo(_('Unknown arguments: {}').format(arg))
            return

        def elide_empty(v=None):
            empty = False
            if v is None:
                empty = True
            elif isinstance(v, str):
                if not v.strip():
                    empty = True
            if empty:
                return '({})'.format(_('not set'))
            else:
                return v

        def yes_no(b):
            if b is None:
                return '({})'.format(_('not set'))
            return _('yes') if b else _('no')

        self.echo('{}:{}'.format(_('files').capitalize(), '' if self._upload_movie.get_data() else ' {}'.format(elide_empty())))
        if self._upload_movie.get_data():
            for i, d in enumerate(self._upload_movie.get_data()):
                if d.video is None:
                    v_str = elide_empty()
                else:
                    v_str = d.video.get_filename()

                if d.subtitle is None:
                    s_str = elide_empty()
                else:
                    s_str = d.subtitle.get_filename()
                self.echo('{: >3} {}: {}'.format(i, _('video').capitalize(), v_str))
                self.echo('{} {}: {}'.format(''.rjust(3), _('subtitle').capitalize(), s_str))
        lang = self._upload_movie.get_language()
        if lang.is_generic():
            lang_name = None
        else:
            lang_name = lang.name()
        self.echo('{}: {}'.format(_('movie name').capitalize(), elide_empty(self._upload_movie.get_movie_name())))
        self.echo('{}: {}'.format(_('IMDb id'), elide_empty(self._upload_movie.get_imdb_id())))
        self.echo('{}: {}'.format(_('language').capitalize(), elide_empty(lang_name)))
        self.echo('{}: {}'.format(_('release name').capitalize(), elide_empty(self._upload_movie.get_release_name())))
        self.echo('{}: {}'.format(_('comments').capitalize(), elide_empty(self._upload_movie.get_comments())))
        self.echo('{}: {}'.format(_('author').capitalize(), elide_empty(self._upload_movie.get_author())))
        self.echo('{}: {}'.format(_('hearing impaired').capitalize(), yes_no(self._upload_movie.is_hearing_impaired())))
        self.echo('{}: {}'.format(_('high definition').capitalize(), yes_no(self._upload_movie.is_high_definition())))
        self.echo('{}: {}'.format(_('automatic translation').capitalize(), yes_no(self._upload_movie.is_automatic_translation())))

    def do_upload(self, arg):
        args = self.shlex_parse_argstr(arg)
        if len(args) != 1:
            self.echo(_('Need one argument'))
            return

        provider_name = args[0]
        self.echo(_('Upload subtitle(s) to provider "{}".').format(provider_name))

        providerState = self._state.providers.get(provider_name)
        if not providerState:
            self.echo(_('Provider "{}" not available.').format(provider_name))
            return

        try:
            upload_result = providerState.provider.upload_subtitles(self._upload_movie)
            if upload_result.ok:
                self.echo(_('Upload succeeded'))
            else:
                self.echo('{}: {}'.format(_('Upload failed'), upload_result.reason))
        except ProviderConnectionError as e:
            self.echo('{}: {}'.format(_('Upload failed'), e.get_msg()))
