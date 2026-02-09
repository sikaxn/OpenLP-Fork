# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008 OpenLP Developers                                   #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################
"""
The :mod:`~openlp.plugins.songs.songsplugin` module contains the Plugin class
for the Songs plugin.
"""

import logging
import sqlite3
from pathlib import Path
from tempfile import gettempdir

from PySide6 import QtCore, QtWidgets

from openlp.core.state import State
from openlp.core.common.actions import ActionList
from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.registry import Registry
from openlp.core.lib import build_icon
from openlp.core.db.manager import DBManager
from openlp.core.lib.plugin import Plugin, StringContent
from openlp.core.lib.ui import create_action
from openlp.core.ui.icons import UiIcons
from openlp.plugins.songs import reporting
from openlp.plugins.songs.forms.duplicatesongremovalform import DuplicateSongRemovalForm
from openlp.plugins.songs.forms.songselectform import SongSelectForm
from openlp.plugins.songs.lib import clean_song, upgrade
from openlp.plugins.songs.lib.db import Song, init_schema
from openlp.plugins.songs.lib.importer import SongFormat
from openlp.plugins.songs.lib.importers.openlp import OpenLPSongImport
from openlp.plugins.songs.lib.mediaitem import SongMediaItem
from openlp.plugins.songs.lib.songstab import SongsTab


log = logging.getLogger(__name__)
song_footer = {
    'songs/footer template': """\
${title}<br/>

%if authors_none:
  <%
    authors = ", ".join(authors_none)
  %>
  ${authors_none_label}:&nbsp;${authors}<br/>
%endif

%if authors_words_music:
  <%
    authors = ", ".join(authors_words_music)
  %>
  ${authors_words_music_label}:&nbsp;${authors}<br/>
%endif

%if authors_words:
  <%
    authors = ", ".join(authors_words)
  %>
  ${authors_words_label}:&nbsp;${authors}<br/>
%endif

%if authors_music:
  <%
    authors = ", ".join(authors_music)
  %>
  ${authors_music_label}:&nbsp;${authors}<br/>
%endif

%if authors_translation:
  <%
    authors = ", ".join(authors_translation)
  %>
  ${authors_translation_label}:&nbsp;${authors}<br/>
%endif

%if copyright:
  &copy;&nbsp;${copyright}<br/>
%endif

%if songbook_entries:
  <%
    entries = ", ".join(songbook_entries)
  %>
  ${entries}<br/>
%endif

%if ccli_license:
  ${ccli_license_label}&nbsp;${ccli_license}<br/>
%endif
""",
}


class SongsPlugin(Plugin):
    """
    This plugin enables the user to create, edit and display songs. Songs are divided into verses, and the verse order
    can be specified. Authors, topics and song books can be assigned to songs as well.
    """
    log.info('Song Plugin loaded')

    def __init__(self):
        """
        Create and set up the Songs plugin.
        """
        super(SongsPlugin, self).__init__('songs', SongMediaItem, SongsTab)
        self.manager = DBManager('songs', init_schema, upgrade_mod=upgrade)
        Registry().register('songs_manager', self.manager)
        self.weight = -10
        self.icon_path = UiIcons().music
        self.icon = build_icon(self.icon_path)
        self.songselect_form = None
        self.settings.extend_default_settings(song_footer)
        State().add_service(self.name, self.weight, is_plugin=True)
        State().update_pre_conditions(self.name, self.check_pre_conditions())
        if not self.settings.value('songs/last import type'):
            self.settings.setValue('songs/last import type', SongFormat.OpenLyrics)

    def check_pre_conditions(self):
        """
        Check the plugin can run.
        """
        return self.manager.session is not None

    def initialise(self):
        """
        Initialise the plugin
        """
        log.info('Songs Initialising')
        super(SongsPlugin, self).initialise()
        self.songselect_form = SongSelectForm(Registry().get('main_window'), self, self.manager)
        self.songselect_form.initialise()
        self.song_import_item.setVisible(True)
        self.song_export_item.setVisible(True)
        self.song_tools_menu.menuAction().setVisible(True)
        action_list = ActionList.get_instance()
        action_list.add_action(self.song_import_item, UiStrings().Import)
        action_list.add_action(self.song_export_item, UiStrings().Export)
        action_list.add_action(self.tools_reindex_item, UiStrings().Tools)
        action_list.add_action(self.tools_find_duplicates, UiStrings().Tools)
        action_list.add_action(self.tools_report_song_list, UiStrings().Tools)

    def add_import_menu_item(self, import_menu):
        """
        Give the Songs plugin the opportunity to add items to the **Import** menu.

        :param import_menu: The actual **Import** menu item, so that your actions can use it as their parent.
        """
        # Main song import menu item - will eventually be the only one
        self.song_import_item = create_action(
            import_menu, 'songImportItem',
            text=translate('SongsPlugin', '&Song'),
            tooltip=translate('SongsPlugin', 'Import songs using the import wizard.'),
            triggers=self.on_song_import_item_clicked)
        import_menu.addAction(self.song_import_item)
        self.import_songselect_item = create_action(
            import_menu, 'import_songselect_item', text=translate('SongsPlugin', 'CCLI SongSelect'),
            statustip=translate('SongsPlugin', 'Import songs from CCLI\'s SongSelect service.'),
            triggers=self.on_import_songselect_item_triggered
        )
        import_menu.addAction(self.import_songselect_item)

    def add_export_menu_item(self, export_menu):
        """
        Give the Songs plugin the opportunity to add items to the **Export** menu.

        :param export_menu: The actual **Export** menu item, so that your actions can use it as their parent.
        """
        # Main song import menu item - will eventually be the only one
        self.song_export_item = create_action(
            export_menu, 'songExportItem',
            text=translate('SongsPlugin', '&Song'),
            tooltip=translate('SongsPlugin', 'Exports songs using the export wizard.'),
            triggers=self.on_song_export_item_clicked)
        export_menu.addAction(self.song_export_item)

    def add_tools_menu_item(self, tools_menu):
        """
        Give the Songs plugin the opportunity to add items to the **Tools** menu.

        :param tools_menu: The actual **Tools** menu item, so that your actions can use it as their parent.
        """
        log.info('add tools menu')
        self.tools_menu = tools_menu
        self.song_tools_menu = QtWidgets.QMenu(tools_menu)
        self.song_tools_menu.setObjectName('song_tools_menu')
        self.song_tools_menu.setTitle(translate('SongsPlugin', 'Songs'))
        self.tools_reindex_item = create_action(
            tools_menu, 'toolsReindexItem',
            text=translate('SongsPlugin', '&Re-index Songs'),
            icon=UiIcons().music,
            statustip=translate('SongsPlugin', 'Re-index the songs database to improve searching and ordering.'),
            triggers=self.on_tools_reindex_item_triggered)
        self.tools_find_duplicates = create_action(
            tools_menu, 'toolsFindDuplicates',
            text=translate('SongsPlugin', 'Find &Duplicate Songs'),
            statustip=translate('SongsPlugin', 'Find and remove duplicate songs in the song database.'),
            triggers=self.on_tools_find_duplicates_triggered, can_shortcuts=True)
        self.tools_report_song_list = create_action(
            tools_menu, 'toolsSongListReport',
            text=translate('SongsPlugin', 'Song List Report'),
            statustip=translate('SongsPlugin', 'Produce a CSV file of all the songs in the database.'),
            triggers=self.on_tools_report_song_list_triggered)

        self.tools_menu.addAction(self.song_tools_menu.menuAction())
        self.song_tools_menu.addAction(self.tools_reindex_item)
        self.song_tools_menu.addAction(self.tools_find_duplicates)
        self.song_tools_menu.addAction(self.tools_report_song_list)

        self.song_tools_menu.menuAction().setVisible(False)

    @staticmethod
    def on_tools_report_song_list_triggered():
        reporting.report_song_list()

    def on_tools_reindex_item_triggered(self):
        """
        Rebuild each song.
        """
        max_songs = self.manager.get_object_count(Song)
        if max_songs == 0:
            return
        progress_dialog = QtWidgets.QProgressDialog(
            translate('SongsPlugin', 'Reindexing songs...'), UiStrings().Cancel, 0, max_songs, self.main_window)
        progress_dialog.setWindowTitle(translate('SongsPlugin', 'Reindexing songs'))
        progress_dialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        songs = self.manager.get_all_objects(Song)
        for number, song in enumerate(songs):
            clean_song(self.manager, song)
            progress_dialog.setValue(number + 1)
        self.manager.save_objects(songs)
        self.media_item.on_search_text_button_clicked()

    def on_tools_find_duplicates_triggered(self):
        """
        Search for duplicates in the song database.
        """
        DuplicateSongRemovalForm(self).exec()

    def on_import_songselect_item_triggered(self):
        """
        Run the SongSelect importer.
        """
        self.songselect_form.exec()
        self.media_item.on_search_text_button_clicked()

    def on_song_import_item_clicked(self):
        """
        Run the song import wizard.
        """
        if self.media_item:
            self.media_item.on_import_click()

    def on_song_export_item_clicked(self):
        """
        Run the song export wizard.
        """
        if self.media_item:
            self.media_item.on_export_click()

    @staticmethod
    def about():
        """
        Provides information for the plugin manager to display.

        :return: A translatable string with some basic information about the Songs plugin
        """
        return translate('SongsPlugin', '<strong>Songs Plugin</strong>'
                                        '<br />The songs plugin provides the ability to display and manage songs.')

    def uses_theme(self, theme):
        """
        Called to find out if the song plugin is currently using a theme.

        :param theme: The theme to check for usage
        :return: count of the number of times the theme is used.
        """
        return len(self.manager.get_all_objects(Song, Song.theme_name == theme))

    def rename_theme(self, old_theme, new_theme):
        """
        Renames a theme the song plugin is using making the plugin use the new name.

        :param old_theme: The name of the theme the plugin should stop using.
        :param new_theme: The new name the plugin should now use.
        """
        songs_using_theme = self.manager.get_all_objects(Song, Song.theme_name == old_theme)
        for song in songs_using_theme:
            song.theme_name = new_theme
            self.manager.save_object(song)

    def import_songs(self, import_format, **kwargs):
        """
        Add the correct importer class

        :param import_format: The import_format to be used
        :param kwargs: The arguments
        :return: the correct importer
        """
        class_ = SongFormat.get(import_format, 'class')
        importer = class_(self.manager, **kwargs)
        importer.register(self.media_item.import_wizard)
        return importer

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('SongsPlugin', 'Song', 'name singular'),
            'plural': translate('SongsPlugin', 'Songs', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('SongsPlugin', 'Songs', 'container title')
        }
        # Middle Header Bar
        tooltips = {
            'load': '',
            'import': '',
            'new': translate('SongsPlugin', 'Add a new song.'),
            'edit': translate('SongsPlugin', 'Edit the selected song.'),
            'delete': translate('SongsPlugin', 'Delete the selected song.'),
            'preview': translate('SongsPlugin', 'Preview the selected song.'),
            'live': translate('SongsPlugin', 'Send the selected song live.'),
            'service': translate('SongsPlugin', 'Add the selected song to the service.')
        }
        self.set_plugin_ui_text_strings(tooltips)

    def first_time(self):
        """
        If the first time wizard has run, this function is run to import all the new songs into the database.
        """
        self.application.process_events()
        db_dir_path = Path(gettempdir(), 'openlp')
        if not db_dir_path.exists():
            return
        song_db_paths = []
        song_count = 0
        for db_file_path in db_dir_path.glob('songs_*.sqlite'):
            self.application.process_events()
            song_db_paths.append(db_file_path)
            song_count += SongsPlugin._count_songs(db_file_path)
        if not song_db_paths:
            return
        self.application.process_events()
        progress = QtWidgets.QProgressDialog(self.main_window)
        progress.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        progress.setWindowTitle(translate('SongsPlugin', 'Importing Songs'))
        progress.setLabelText(UiStrings().StartingImport)
        progress.setCancelButton(None)
        progress.setRange(0, song_count)
        progress.setMinimumDuration(0)
        progress.forceShow()
        self.application.process_events()
        for db_path in song_db_paths:
            importer = OpenLPSongImport(self.manager, file_path=db_path)
            importer.do_import(progress)
            self.application.process_events()
        progress.setValue(song_count)
        self.application.process_events()
        self.on_tools_reindex_item_triggered()
        self.application.process_events()
        self.media_item.on_search_text_button_clicked()

    def finalise(self):
        """
        Time to tidy up on exit
        """
        log.info('Songs Finalising')
        self.new_service_created()
        # Clean up files and connections
        self.manager.finalise()
        self.song_import_item.setVisible(False)
        self.song_export_item.setVisible(False)
        action_list = ActionList.get_instance()
        action_list.remove_action(self.song_import_item, UiStrings().Import)
        action_list.remove_action(self.song_export_item, UiStrings().Export)
        action_list.remove_action(self.tools_reindex_item, UiStrings().Tools)
        action_list.remove_action(self.tools_find_duplicates, UiStrings().Tools)
        action_list.add_action(self.tools_report_song_list, UiStrings().Tools)
        self.song_tools_menu.menuAction().setVisible(False)
        super(SongsPlugin, self).finalise()

    def new_service_created(self):
        """
        Remove temporary songs from the database
        """
        songs = self.manager.get_all_objects(Song, Song.temporary == True)  # noqa: E712
        for song in songs:
            self.manager.delete_object(Song, song.id)

    @staticmethod
    def _count_songs(db_path):
        """
        Provide a count of the songs in the database

        :param Path db_path: The database to use
        :return: The number of songs in the db.
        :rtype: int
        """
        connection = sqlite3.connect(str(db_path))
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(id) AS song_count FROM songs')
        song_count = cursor.fetchone()[0]
        connection.close()
        try:
            song_count = int(song_count)
        except (TypeError, ValueError):
            song_count = 0
        return song_count
