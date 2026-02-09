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
The :mod:`db` module provides the ability to provide a csv file of all songs
"""
import csv
import logging
from pathlib import Path

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.widgets.dialogs import FileDialog
from openlp.plugins.songs.lib.db import Song


log = logging.getLogger(__name__)


def report_song_list():
    """
    Export the song list as a CSV file.
    :return: Nothing
    """
    main_window = Registry().get('main_window')
    plugin = Registry().get('songs').plugin
    report_file_path, filter_used = FileDialog.getSaveFileName(
        main_window,
        translate('SongPlugin.ReportSongList', 'Save File'),
        Path(translate('SongPlugin.ReportSongList', 'song_extract.csv')),
        translate('SongPlugin.ReportSongList', 'CSV format (*.csv)'))
    if report_file_path is None:
        return
    report_file_path.with_suffix('.csv')
    Registry().get('application').set_busy_cursor()
    try:
        with report_file_path.open('wt', encoding='utf8') as export_file:
            fieldnames = ('Title', 'Alternative Title', 'Copyright', 'Author(s)', 'Song Book', 'Topic')
            writer = csv.DictWriter(export_file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            headers = dict((n, n) for n in fieldnames)
            writer.writerow(headers)
            song_list = plugin.manager.get_all_objects(Song)
            for song in song_list:
                author_list = []
                for author_song in song.authors_songs:
                    author_list.append(author_song.author.display_name)
                author_string = ' | '.join(author_list)
                book_list = []
                for book_song in song.songbook_entries:
                    if hasattr(book_song, 'entry') and book_song.entry:
                        book_list.append('{name} #{entry}'.format(name=book_song.songbook.name, entry=book_song.entry))
                book_string = ' | '.join(book_list)
                topic_list = []
                for topic_song in song.topics:
                    if hasattr(topic_song, 'name'):
                        topic_list.append(topic_song.name)
                topic_string = ' | '.join(topic_list)
                writer.writerow({'Title': song.title,
                                 'Alternative Title': song.alternate_title,
                                 'Copyright': song.copyright,
                                 'Author(s)': author_string,
                                 'Song Book': book_string,
                                 'Topic': topic_string})
            Registry().get('application').set_normal_cursor()
            main_window.information_message(
                translate('SongPlugin.ReportSongList', 'Report Creation'),
                translate('SongPlugin.ReportSongList',
                          'Report \n{name} \nhas been successfully created. ').format(name=report_file_path)
            )
    except OSError as ose:
        Registry().get('application').set_normal_cursor()
        log.exception('Failed to write out song usage records')
        critical_error_message_box(translate('SongPlugin.ReportSongList', 'Song Extraction Failed'),
                                   translate('SongPlugin.ReportSongList',
                                             'An error occurred while extracting: {error}'
                                             ).format(error=ose.strerror))
