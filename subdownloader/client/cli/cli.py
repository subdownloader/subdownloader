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
from subdownloader.languages.language import Language, NotALanguageException
from subdownloader.languages.language import LANGUAGES as ALL_LANGUAGES
from subdownloader.subtitle2 import RemoteSubtitleFile

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
        self._videos = []
        self._video_rsubs = set()

        # Text query state
        self._text_query = None
        self._query_rsubs = set()

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
                    self.print(_('Invalid index.'))
                    return 1
            else:
                self.print('{} ({})'.format(_('Auto-selecting first subtitle.'),
                                            _('Use interactive mode to select another subtitle.')))
                sub_i = 0
            try:
                subtitle = self.get_videos_subtitle(sub_i, [video])
            except IndexError:
                self.print(_('Video has no subtitles that match the filter.'))
                continue
            self.print(_('Selected subtitle:'),  self.subtitle_to_long_string(subtitle))
            if subtitle.is_local():
                self.print(_('Cannot select local subtitles.'))
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

    def onecmd(self, line):
        log.debug('onecmd("{}")'.format(line))
        try:
            return Cmd.onecmd(self, line)
        except BadCliArguments:
            self.print(_('Bad arguments'))
            return False

    def postloop(self):
        self.cleanup()

    def get_callback(self):
        return ProgressBarCallback(fd=self.stdout)

    LEN_ARG_COL = 15

    def help_EOF(self):
        self.print(_('Exit program') + ' (CTRL+D).')
        self.print()
        self.print('EOF')
        self.print()

    def do_EOF(self, arg):
        self._return_code = 0
        return True

    def help_exit(self):
        self.print(_('Alias for {}').format('quit'))
        self.print()
        return self.help_quit()

    def do_exit(self, arg):
        return self.do_quit(arg)

    def help_quit(self):
        self.print(_('Exit program') + '.')
        self.print()
        self.print('quit')
        self.print()

    def do_quit(self, arg):
        self._return_code = 0
        return True

    def help_language(self):
        self.print(_('Alias for {}').format('languages'))
        self.print()
        return self.help_languages()

    def do_language(self, arg):
        return self.do_languages(arg)

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
            try:
                if int(arg) == 0:
                    self.state.set_download_languages([])
                self.print(_('Filter languages cleared'))
                return
            except ValueError:
                pass

            try:
                langs = [Language.from_unknown(l_str, xx=True, xxx=True, name=True, locale=True)
                         for l_str in self.shlex_parse_argstr(arg)]
            except NotALanguageException as e:
                self.print(_('"{}" is not a valid language').format(e.value))
                return
            self.state.set_download_languages(langs)
            self.print(ngettext('New filter language:', 'New filter languages:',
                                len(self.state.get_download_languages())))
            for language in self.state.get_download_languages():
                self.print('- {}'.format(language.name()))
            return
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

    def help_listlanguages(self):
        self.print(_('List all available languages.'))
        self.print()
        self.print('listlanguages')
        self.print()

    def do_listlanguages(self, arg):
        if arg:
            self.print(_('Unknown arguments: {}').format(arg))
            return
        fmt = '{name:<25} | {locale:<10} | {lid:<10} | {iso639:<10}'
        header = fmt.format(name=_('name'), locale=_('locale'), lid=_('ISO639-3'), iso639=_('ISO639-2'))
        self.print(header)
        self.print('-'*len(header))
        for lang in ALL_LANGUAGES[1:]:
            self.print(fmt.format(name=lang['LanguageName'][0],
                                  locale=', '.join(lang['locale']),
                                  lid=', '.join(lang['LanguageID']),
                                  iso639=', '.join(lang['ISO639'])))

    def help_filepath(self):
        self.print(_('Get/set the file path(s).'))
        self.print()
        self.print('filepath [PATH [PATH [...]]]')
        self.print()
        self.print('  PATH'.ljust(self.LEN_ARG_COL) + _('File path to add.'))
        self.print()

    def do_filepath(self, arg):
        if arg:
            self.state.set_video_paths([Path(p) for p in self.shlex_parse_argstr(arg)])
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
                                                       recursive=self.state.get_recursive())
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

        nb_selected = self._print_videos(self._videos)

        if nb_selected:
            self.print()
            self.print(ngettext('{} subtitle selected', '{} subtitles selected', nb_selected).format(nb_selected))

    def _print_videos(self, videos):
        counter = 0
        counter_len = len(str(sum(video.get_subtitles().get_nb_subtitles() for video in self._videos)))
        nb_selected = 0

        for video in videos:
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
                        str_counter = '   '
                    else:  # if subtitle.is_remote():
                        if subtitle in self._video_rsubs:
                            x = 'x'
                            nb_selected += 1
                        else:
                            x = ' '
                        str_counter = '{:>3}'.format(counter)
                        counter += 1
                    self.print('       <{x}> [{i}] {s}'.format(i=str_counter, x=x,
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
            subs_i = tuple(int(a) for a in self.shlex_parse_argstr(arg))
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
            subs_i = tuple(int(a) for a in self.shlex_parse_argstr(arg))
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
            self.state.providers.connect(item)
            self.state.providers.login(item)
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
            self.state.providers.logout(item)
            self.state.providers.disconnect(item)
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
            self.state.providers.ping(item)
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
        args = self.shlex_parse_argstr(arg)
        if args:
            if len(args) != 2:
                self.print(_('Wrong number of arguments.'))
                return
            cmd = args[0]
            name = args[1]
            if cmd == 'add':
                res = self.state.providers.add_name(name, self._settings)
                if res:
                    self.print(_('Provider added.'))
                else:
                    self.print(_('Add failed.'))
            elif cmd == 'remove':
                res = self.state.providers.remove(name)
                if res:
                    self.print(_('Provider removed.'))
                    self._invalidate_videos()
                    self._invalidate_text_queries()
                else:
                    self.print(_('Removal failed.'))
            elif cmd == 'list':
                try:
                    provider = self.state.providers.get(name)
                    self.print(_('- Name: {} ({})').format(provider.get_name(), provider.get_short_name()))
                    self.print(_('- Connected: {}').format(provider.connected()))
                    self.print(_('- Logged in: {}').format(provider.logged_in()))
                except IndexError:
                    self.print(_('Provider "{}" not found').format(name))
            else:
                self.print(_('Unknown command "{}".').format(cmd))
        else:
            providers = list(self.state.providers.iter())
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
                self.state.set_recursive(True if int(arg) else False)
                return
            except ValueError:
                self.print(_('Invalid argument.'))
                return
        self.print(_('Recursive: {}').format(self.state.get_recursive()))

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
        self.print(_('Get/set the subtitle naming strategy. (default is to get the current naming strategy)'))
        self.print()
        self.print('rename [{}]'.format(' | '.join(str(k) for k in self.NAMING_STRATEGY_LUT.keys())))
        self.print()

        for index, strategy in self.NAMING_STRATEGY_LUT.items():
            self.print('  {}'.format(index).ljust(self.LEN_ARG_COL) + self.get_strategy_naming_doc(strategy))
        self.print()

    def do_rename(self, arg):
        if not arg:
            self.print(_('Current subtitle naming strategy:'))
        else:
            try:
                strategy = self.NAMING_STRATEGY_LUT[arg]
            except KeyError:
                self.print(_('Invalid subtitle naming strategy'))
                return
            self.state.set_subtitle_naming_strategy(strategy)
            self.print(_('New subtitle naming strategy:'))
        self.print(self.get_strategy_naming_doc(self.state.get_subtitle_naming_strategy()))

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
                provider = self.state.providers.find(provider_type)
            except IndexError:
                self.print(_('Provider "{}" not available.').format(provider_type.get_name()))
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

    def help_query(self):
        self.print(_('Set the text query for searching for subtitles by video name.'))
        self.print()
        self.print('query TEXT')
        self.print()

    def do_query(self, arg):
        if not arg:
            if not self.query_active():
                self.print(_('No query active'))
            else:
                self.print('{}: "{}"'.format(_('Current query'), self._text_query.text))
                self.print('{}: {}'.format(_('More movies available'), self._text_query.more_movies_available()))
            return
        self.set_text_query(self.state.providers.query_text_all(text=arg))

    def help_querymore(self):
        self.print(_('Look for more video matches for the current text query.'))
        self.print(_('The optional argument \'all\' will fetch all videos.'))
        self.print()
        self.print('querymore [all]')
        self.print()

    def do_querymore(self, arg):
        if not self.query_active():
            self.print(_('No query active'))
            return

        args = self.shlex_parse_argstr(arg)

        fetch_all = False
        if len(args) > 0:
            if args[0] != 'all':
                self.print(_('Invalid argument'))
                return
            fetch_all = True

        if not self._text_query.more_movies_available():
            self.print(_('No more videos are available'))
            return

        nb_before = len(self._text_query.movies)

        try:
            if fetch_all:
                while self._text_query.more_movies_available():
                    self._text_query.search_more_movies()
            else:
                self._text_query.search_more_movies()
        except ProviderConnectionError:
            self.print(_('An error occured'))

        nb_after = len(self._text_query.movies)

        self.print(_('Found {} extra videos.').format(nb_after - nb_before))

    def help_queryhasmore(self):
        self.print(_('Check whether more videos can be found using querymore.'))
        self.print()
        self.print('queryhasmore')
        self.print()

    def do_queryhasmore(self, arg):
        if arg:
            self.print(_('Unknown arguments: {}').format(arg))
            return
        if not self.query_active():
            self.print(_('No query active'))
            return
        self.print(_('Yes') if self._text_query.more_movies_available() else _('No'))

    def help_querysubsearch(self):
        self.print(_('Look for more subtitles for a particular video.'))
        self.print(_('The optional argument \'all\' will fetch all subtitles.'))
        self.print()
        self.print('querysubsearch INDEX [all]')
        self.print()

    def do_querysubsearch(self, arg):
        if not self.query_active():
            self.print(_('No query active'))
            return
        args = self.shlex_parse_argstr(arg)

        if len(args) == 0:
            self.print(_('Need an argument'))
            return

        fetch_all = False
        if len(args) > 1:
            if args[1] != 'all':
                self.print(_('Invalid argument'))
                return
            fetch_all = True

        if len(args) > 2:
            self.print(_('Too many arguments'))
            return

        try:
            rmovie_network_i = int(args[0])
            rmovie_network = self._text_query.movies[rmovie_network_i]
        except ValueError:
            self.print(_('Invalid argument'))
            return
        except IndexError:
            self.print(_('Movie not available'))
            return

        nb_subtitles_before = len(rmovie_network.get_subtitles())

        if not rmovie_network.more_subtitles_available():
            self.print(_('No more subtitles are available'))
            return

        if fetch_all:
            while rmovie_network.more_subtitles_available():
                rmovie_network.search_more_subtitles()
        else:
            rmovie_network.search_more_subtitles()

        nb_subtitles_after = len(rmovie_network.get_subtitles())

        self.print(_('Found {} extra subtitles').format(nb_subtitles_after-nb_subtitles_before))

    def help_queryshow(self):
        self.print(_('Display the current videos and subtitles, found by query'))
        self.print()
        self.print('queryshow')
        self.print()

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
        self.print('Select a subtitle of the current query.')
        self.print()
        self.print('queryselect INDEX [INDEX [INDEX [...]]]')
        self.print()
        self.print('  INDEX'.ljust(self.LEN_ARG_COL) + _('Index of the subtitle to select.'))
        self.print()

    def do_queryselect(self, arg):
        if not self.query_active():
            self.print(_('No query active'))
            return
        try:
            sel_i = int(arg)
        except ValueError:
            self.print(_('Invalid index'))
            return
        rsub = self._query_get_subtitle(sel_i)
        if rsub is None:
            self.print(_('Index out of range'))
            return
        self._query_rsubs.add(rsub)

    def help_querydeselect(self):
        self.print('Deselect a subtitle of the current query.')
        self.print()
        self.print('querydeselect INDEX [INDEX [INDEX [...]]]')
        self.print()
        self.print('  INDEX'.ljust(self.LEN_ARG_COL) + _('Index of the subtitle to deselect.'))
        self.print()

    def do_querydeselect(self, arg):
        if not self.query_active():
            self.print(_('No query active'))
            return
        try:
            sel_i = int(arg)
        except ValueError:
            self.print(_('Invalid index'))
            return
        rsub = self._query_get_subtitle(sel_i)
        if rsub is None:
            self.print(_('Index out of range'))
            return
        self._query_rsubs.remove(rsub)

    def help_querydownload(self):
        self.print(_('Download the selected subtitles of the text query.'))
        self.print()
        self.print('querydownload')
        self.print()

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
                provider = self.state.providers.find(provider_type)
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
