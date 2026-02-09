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
This module contains tests for the report_song_list function.
"""
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.songs.reporting import report_song_list


@patch('openlp.plugins.songs.reporting.csv')
@patch('openlp.plugins.songs.reporting.FileDialog')
def test_report_song_list(mock_file_dialog: MagicMock, mocked_csv: MagicMock, registry: Registry,
                          settings: Settings):
    """
    Test that report_song_list works
    """
    # GIVEN: A mocked save file and mocked song list
    mock_file = MagicMock()
    mock_file.open.side_effect = MagicMock()
    mock_file_dialog.getSaveFileName = MagicMock(return_value=(mock_file, None))
    topic1 = MagicMock()
    topic2 = MagicMock()
    book1 = MagicMock()
    book2 = MagicMock()
    topic1.name = 'Topic 1'
    topic2.name = 'Topic 2'
    book1.name = 'Song Book 1'
    book2.name = 'Song Book 2'
    song_list = [MagicMock(**{
        'title': 'The Song Title',
        'alternate_title': 'The alternate title',
        'copyright': 'The copyright',
        'authors_songs': [
            MagicMock(author=MagicMock(display_name='Bob')),
            MagicMock(author=MagicMock(display_name='Bill')),
        ],
        'songbook_entries': [
            MagicMock(entry='Book 1 entry', songbook=book1),
            MagicMock(entry='Book 2 entry', songbook=book2),
        ],
        'topics': [
            topic1,
            topic2,
        ]
    })]
    mocked_songs = MagicMock(plugin=MagicMock(manager=MagicMock(get_all_objects=MagicMock(return_value=song_list))))
    mocked_main_window = MagicMock()
    mocked_application = MagicMock()
    registry.register('songs', mocked_songs)
    registry.register('main_window', mocked_main_window)
    registry.remove('application')
    registry.register('application', mocked_application)
    mock_writer = MagicMock()
    mocked_csv.DictWriter.return_value = mock_writer

    # WHEN: report_song_list is called
    report_song_list()

    # THEN: getSaveFileName called, Busy cursor set and unset, writer called with correct values
    mock_file_dialog.getSaveFileName.assert_called_once()
    mocked_application.set_busy_cursor.assert_called_once()
    mocked_application.set_normal_cursor.assert_called_once()
    mock_writer.writerow.assert_called_with({
        'Title': 'The Song Title',
        'Alternative Title': 'The alternate title',
        'Copyright': 'The copyright',
        'Author(s)': 'Bob | Bill',
        'Song Book': 'Song Book 1 #Book 1 entry | Song Book 2 #Book 2 entry',
        'Topic': 'Topic 1 | Topic 2'
    })


@patch('openlp.plugins.songs.reporting.log')
@patch('openlp.plugins.songs.reporting.FileDialog')
def test_report_song_list_error_reading(mock_file_dialog: MagicMock, mock_log: MagicMock, registry: Registry,
                                        settings: Settings):
    """
    Test that report song list sends an exception if the selected file location is not writable
    """
    # GIVEN: A mocked file that returns a os error on open
    def raise_os_error(mode, encoding):
        assert mode == 'wt'
        assert encoding == 'utf8'
        raise OSError
    mock_file = MagicMock()
    mock_file.open.side_effect = raise_os_error
    mock_file_dialog.getSaveFileName = MagicMock(return_value=(mock_file, None))
    mocked_songs = MagicMock()
    registry.register('songs', mocked_songs)
    registry.register('main_window', MagicMock())

    # WHEN: report_song_list is called
    report_song_list()

    # THEN: getSaveFileName called, made exception log
    mock_file_dialog.getSaveFileName.assert_called_once()
    mock_log.exception.assert_called_once()


@patch('openlp.plugins.songs.reporting.FileDialog')
def test_report_song_list_cancel(mock_file_dialog: MagicMock, registry: Registry, settings: Settings):
    """
    Test that report song list does not crash if no file location was specified
    """
    # GIVEN: getSaveFileName returns None
    mock_file_dialog.getSaveFileName = MagicMock(return_value=(None, None))
    mocked_songs = MagicMock()
    registry.register('songs', mocked_songs)
    registry.register('main_window', MagicMock())

    # WHEN: report_song_list is called
    report_song_list()

    # THEN: Did not crash, and getSaveFileName was called
    mock_file_dialog.getSaveFileName.assert_called_once()
