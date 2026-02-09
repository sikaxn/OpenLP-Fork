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
This module contains tests for the OpenLP song importer.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.songs.lib.importers.openlp import OpenLPSongImport

from tests.utils.constants import RESOURCE_PATH

TEST_PATH = RESOURCE_PATH / 'songs' / 'openlp'


def test_create_importer(registry: Registry, settings: Settings):
    """
    Test creating an instance of the OpenLP database importer
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    with patch('openlp.plugins.songs.lib.importers.openlp.SongImport'):
        mocked_manager = MagicMock()

        # WHEN: An importer object is created
        importer = OpenLPSongImport(mocked_manager, file_paths=[])

        # THEN: The importer object should not be None
        assert importer is not None, 'Import should not be none'


def test_invalid_import_source(registry: Registry, settings: Settings):
    """
    Test OpenLPSongImport.do_import handles different invalid import_source values
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    with patch('openlp.plugins.songs.lib.importers.openlp.SongImport'):
        mocked_manager = MagicMock()
        mocked_import_wizard = MagicMock()
        importer = OpenLPSongImport(mocked_manager, file_paths=[])
        importer.import_wizard = mocked_import_wizard
        importer.stop_import_flag = True

        # WHEN: Import source is not a list
        importer.import_source = Path()

        # THEN: do_import should return none and the progress bar maximum should not be set.
        assert importer.do_import() is None, 'do_import should return None when import_source is not a list'
        assert mocked_import_wizard.progress_bar.setMaximum.called is False, \
            'setMaximum on import_wizard.progress_bar should not have been called'


@pytest.mark.parametrize('base_name', ['songs-1.9.7', 'songs-2.4.6'])
@patch('openlp.plugins.songs.lib.importers.openlp.Song')
@patch('openlp.plugins.songs.lib.importers.openlp.Author')
@patch('openlp.plugins.songs.lib.importers.openlp.Topic')
@patch('openlp.plugins.songs.lib.importers.openlp.SongBook')
@patch('openlp.plugins.songs.lib.importers.openlp.MediaFile')
def test_openlp_db_import(MockMediaFile: MagicMock, MockSongBook: MagicMock, MockTopic: MagicMock,
                          MockAuthor: MagicMock, MockSong: MagicMock, mock_settings: MagicMock, base_name: str):
    """Test that OpenLP is able to import an older OpenLP database"""
    # GIVEN: An OpenLP importer and a bunch of mocks
    mocked_progress_dialog = MagicMock()
    mocked_author = MagicMock()
    MockAuthor.return_value = mocked_author
    mocked_song = MagicMock()
    MockSong.return_value = mocked_song
    mocked_topic_salvation = MagicMock()
    mocked_topic_grace = MagicMock()
    MockTopic.side_effect = [mocked_topic_grace, mocked_topic_salvation]
    mocked_songbook = MagicMock()
    MockSongBook.return_value = mocked_songbook
    mocked_media_file = MagicMock()
    MockMediaFile.return_value = mocked_media_file
    mocked_manager = MagicMock()
    mocked_manager.get_object_filtered.return_value = None
    importer = OpenLPSongImport(mocked_manager, file_path=TEST_PATH / f'{base_name}.sqlite')
    importer.import_wizard = MagicMock()

    # WHEN: The database is imported
    importer.do_import(mocked_progress_dialog)

    # THEN: The correct songs should ahve been imported
    expected_song = json.load((TEST_PATH / f'{base_name}.json').open())
    importer.import_wizard.progress_bar.setMaximum.assert_called_once_with(1)
    assert mocked_song.title == expected_song['title']
    for author in expected_song['authors']:
        MockAuthor.assert_called_with(first_name=author['first_name'], last_name=author['last_name'],
                                      display_name=author['display_name'])
        mocked_song.add_author.assert_called_with(mocked_author, author.get('type', ''))
    if 'verse_order' in expected_song:
        assert mocked_song.verse_order == expected_song['verse_order']
    if 'copyright' in expected_song:
        assert mocked_song.copyright == expected_song['copyright']
    if 'theme_name' in expected_song:
        assert mocked_song.theme_name == expected_song['theme_name']
    for topic in expected_song.get('topics', []):
        assert call(name=topic) in MockTopic.call_args_list
        if topic == 'Grace':
            assert call(mocked_topic_grace) in mocked_song.topics.append.call_args_list
        elif topic == 'Salvation':
            assert call(mocked_topic_salvation) in mocked_song.topics.append.call_args_list
    for songbook_entry in expected_song.get('songbooks', []):
        MockSongBook.assert_called_with(name=songbook_entry['songbook'], publisher=None)
        assert call(mocked_songbook, songbook_entry.get('entry', '')) in mocked_song.add_songbook_entry.call_args_list
    for media_file in expected_song.get('media_files', []):
        MockMediaFile.assert_called_once_with(file_path=Path(media_file["file_name"]), file_hash=None)
        assert call(mocked_media_file) in mocked_song.media_files.append.call_args_list
