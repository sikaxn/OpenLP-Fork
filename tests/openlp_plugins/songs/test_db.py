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
This module contains tests for the db submodule of the Songs plugin.
"""
import os
import shutil
from unittest.mock import patch, PropertyMock

from openlp.core.db.upgrades import upgrade_db
from openlp.plugins.songs.lib import upgrade
from openlp.plugins.songs.lib.db import Author, AuthorType, SongBook, Song
from tests.utils.constants import TEST_RESOURCES_PATH


@patch('openlp.plugins.songs.lib.db.get_natural_key')
@patch('openlp.plugins.songs.lib.db.create_separated_list')
@patch('openlp.plugins.songs.lib.db.sort_key_cache', new_callable=dict)
@patch('openlp.plugins.songs.lib.db.song_detail_cache', new_callable=dict)
def test_init_on_load(mock_detail_cache, mock_sort_cache, mock_create_list, mock_get_key):
    """
    Test if init_on_load creates sort_key and show_text
    """
    # GIVEN: A song with title, authors, and mocked external dependencies
    mock_get_key.return_value = 'mocked-key'
    mock_create_list.return_value = 'Test Author'
    song = Song()
    song.title = 'This is a Test'
    song.id = 123
    song.last_modified = '2025-04-23'
    song.authors_songs = []
    song.media_files = []
    author = Author()
    author.display_name = 'Test Author'
    song.add_author(author)

    # WHEN: We call init_on_load
    song.init_on_load()

    # THEN: sort_key and show_text use mocked values
    assert song.sort_key == 'mocked-key'
    assert song.song_detail == 'This is a Test (Test Author)'
    assert mock_sort_cache['This is a Test'] == 'mocked-key'
    assert mock_detail_cache['123-2025-04-23'] == 'This is a Test (Test Author)'
    mock_get_key.assert_called_once_with('This is a Test')
    mock_create_list.assert_called_once_with(['Test Author'])


@patch('openlp.plugins.songs.lib.db.get_natural_key')
@patch('openlp.plugins.songs.lib.db.sort_key_cache', new_callable=dict)
@patch('openlp.plugins.songs.lib.db.song_detail_cache', new_callable=dict)
def test_init_on_load_fallback_to_title(mock_detail_cache, mock_sort_cache, mock_get_key):
    """
    Test init_on_load uses title as show_text when no authors are present
    """
    # GIVEN: A song with title but no authors
    mock_get_key.return_value = 'mocked-key'
    song = Song()
    song.title = 'This is a Test'
    song.id = 456
    song.last_modified = '2025-04-23'
    song.authors_songs = []
    song.media_files = []

    # WHEN: init_on_load is called without any authors
    song.init_on_load()

    # THEN: show_text falls back to title, and sort_key is still calculated
    assert song.sort_key == 'mocked-key'
    assert song.song_detail == 'This is a Test (This is a Test)'
    assert mock_sort_cache['This is a Test'] == 'mocked-key'
    assert mock_detail_cache['456-2025-04-23'] == 'This is a Test (This is a Test)'
    mock_get_key.assert_called_once_with('This is a Test')


@patch('openlp.plugins.songs.lib.db.get_natural_key')
@patch('openlp.plugins.songs.lib.db.create_separated_list')
@patch('openlp.plugins.songs.lib.db.sort_key_cache', new_callable=dict)
@patch('openlp.plugins.songs.lib.db.song_detail_cache', new_callable=dict)
def test_init_on_load_uses_cached_values(mock_detail_cache, mock_sort_cache, mock_create_list, mock_get_key):
    """
    Test init_on_load uses cached sort_key and show_text if available
    """
    # GIVEN: Caches already populated
    mock_sort_cache['This is a Test'] = 'cached-mocked-key'
    mock_detail_cache['789-2025-04-23'] = 'Cached Song Detail'
    song = Song()
    song.title = 'This is a Test'
    song.id = 789
    song.last_modified = '2025-04-23'
    song.authors_songs = []
    song.media_files = []

    # WHEN: init_on_load is called
    song.init_on_load()

    # THEN: Cached values are used; external functions are not called
    assert song.sort_key == 'cached-mocked-key'
    assert song.song_detail == 'Cached Song Detail'
    mock_get_key.assert_not_called()
    mock_create_list.assert_not_called()


@patch('openlp.plugins.songs.lib.db.get_natural_key')
@patch('openlp.plugins.songs.lib.db.create_separated_list')
@patch('openlp.plugins.songs.lib.db.sort_key_cache', new_callable=dict)
@patch('openlp.plugins.songs.lib.db.song_detail_cache', new_callable=dict)
def test_init_on_load_force_recalculation(mock_detail_cache, mock_sort_cache, mock_create_list, mock_get_key):
    """
    Test init_on_load recalculates song_detail when force flag is True
    """
    # GIVEN: A song with cached song_detail
    mock_get_key.return_value = 'mocked-key'
    mock_create_list.return_value = 'Recalc Author'
    mock_detail_cache['999-2025-04-23'] = 'Old Cached Value'
    song = Song()
    song.title = 'Recalculation Test'
    song.id = 999
    song.last_modified = '2025-04-23'
    song.authors_songs = []
    song.media_files = []
    author = Author()
    author.display_name = 'Recalc Author'
    song.add_author(author)

    # WHEN: init_on_load is called with force_song_detail_recalculation=True
    song.init_on_load(force_song_detail_recalculation=True)

    # THEN: song_detail should be recalculated and cache updated
    assert song.song_detail == 'Recalculation Test (Recalc Author)'
    assert mock_detail_cache['999-2025-04-23'] == 'Recalculation Test (Recalc Author)'
    mock_create_list.assert_called_once_with(['Recalc Author'])


@patch('openlp.plugins.songs.lib.db.get_natural_key')
@patch('openlp.plugins.songs.lib.db.create_separated_list')
@patch('openlp.plugins.songs.lib.db.sort_key_cache', new_callable=dict)
@patch('openlp.plugins.songs.lib.db.song_detail_cache', new_callable=dict)
def test_init_on_load_with_media_files(mock_detail_cache, mock_sort_cache, mock_create_list, mock_get_key):
    """
    Test init_on_load includes (A) in song_detail when media_files exist
    """
    # GIVEN: A song with one or more media files
    mock_get_key.return_value = 'mocked-key'
    mock_create_list.return_value = 'Media Author'
    song = Song()
    song.title = 'Media Song'
    song.id = 101
    song.last_modified = '2025-04-23'
    song.authors_songs = []
    author = Author()
    author.display_name = 'Media Author'
    song.add_author(author)

    # WHEN: init_on_load is called and len() returns 1
    with patch.object(Song, 'media_files', new_callable=PropertyMock) as mock_media:
        mock_media.return_value = [1]
        song.init_on_load()

    # THEN: song_detail should include '(A)' to indicate media presence
    assert song.song_detail == 'Media Song (A) (Media Author)'
    assert mock_detail_cache['101-2025-04-23'] == 'Media Song (A) (Media Author)'


def test_add_author():
    """
    Test adding an author to a song
    """
    # GIVEN: A song and an author
    song = Song()
    song.authors_songs = []
    author = Author()
    author.first_name = "Max"
    author.last_name = "Mustermann"

    # WHEN: We add an author to the song
    song.add_author(author)

    # THEN: The author should have been added with author_type=None
    assert 1 == len(song.authors_songs)
    assert "Max" == song.authors_songs[0].author.first_name
    assert "Mustermann" == song.authors_songs[0].author.last_name
    assert song.authors_songs[0].author_type is None


def test_add_author_with_type():
    """
    Test adding an author with a type specified to a song
    """
    # GIVEN: A song and an author
    song = Song()
    song.authors_songs = []
    author = Author()
    author.first_name = "Max"
    author.last_name = "Mustermann"

    # WHEN: We add an author to the song
    song.add_author(author, AuthorType.Words)

    # THEN: The author should have been added with author_type=None
    assert 1 == len(song.authors_songs)
    assert "Max" == song.authors_songs[0].author.first_name
    assert "Mustermann" == song.authors_songs[0].author.last_name
    assert AuthorType.Words == song.authors_songs[0].author_type


def test_remove_author():
    """
    Test removing an author from a song
    """
    # GIVEN: A song with an author
    song = Song()
    song.authors_songs = []
    author = Author()
    song.add_author(author)

    # WHEN: We remove the author
    song.remove_author(author)

    # THEN: It should have been removed
    assert 0 == len(song.authors_songs)


def test_remove_author_with_type():
    """
    Test removing an author with a type specified from a song
    """
    # GIVEN: A song with two authors
    song = Song()
    song.authors_songs = []
    author = Author()
    song.add_author(author)
    song.add_author(author, AuthorType.Translation)

    # WHEN: We remove the author with a certain type
    song.remove_author(author, AuthorType.Translation)

    # THEN: It should have been removed and the other author should still be there
    assert 1 == len(song.authors_songs)
    assert song.authors_songs[0].author_type is None


def test_get_author_type_from_translated_text():
    """
    Test getting an author type from translated text
    """
    # GIVEN: A string with an author type
    author_type_name = AuthorType.get_translated_type(AuthorType.Words)

    # WHEN: We call the method
    author_type = AuthorType.from_translated_text(author_type_name)

    # THEN: The type should be correct
    assert author_type == AuthorType.Words


def test_author_get_display_name():
    """
    Test that the display name of an author is correct
    """
    # GIVEN: An author
    author = Author()
    author.display_name = "John Doe"

    # WHEN: We call the get_display_name() function
    display_name = author.get_display_name()

    # THEN: It should return only the name
    assert "John Doe" == display_name


def test_author_get_display_name_with_type_words():
    """
    Test that the display name of an author with a type is correct (Words)
    """
    # GIVEN: An author
    author = Author()
    author.display_name = "John Doe"

    # WHEN: We call the get_display_name() function
    display_name = author.get_display_name(AuthorType.Words)

    # THEN: It should return the name with the type in brackets
    assert "John Doe (Words)" == display_name


def test_author_get_display_name_with_type_translation():
    """
    Test that the display name of an author with a type is correct (Translation)
    """
    # GIVEN: An author
    author = Author()
    author.display_name = "John Doe"

    # WHEN: We call the get_display_name() function
    display_name = author.get_display_name(AuthorType.Translation)

    # THEN: It should return the name with the type in brackets
    assert "John Doe (Translation)" == display_name


def test_add_songbooks():
    """
    Test that adding songbooks to a song works correctly
    """
    # GIVEN: A mocked song and songbook
    song = Song()
    song.songbook_entries = []
    songbook = SongBook()
    songbook.name = "Thy Word"

    # WHEN: We add two songbooks to a Song
    song.add_songbook_entry(songbook, "120")
    song.add_songbook_entry(songbook, "550A")

    # THEN: The song should have two songbook entries
    assert len(song.songbook_entries) == 2, 'There should be two Songbook entries.'


def test_upgrade_old_song_db(settings, temp_folder):
    """
    Test that we can upgrade an old song db to the current schema
    """
    # GIVEN: An old song db
    old_db_path = os.path.join(TEST_RESOURCES_PATH, "songs", 'songs-1.9.7.sqlite')
    old_db_tmp_path = os.path.join(temp_folder, 'songs-1.9.7.sqlite')
    shutil.copyfile(old_db_path, old_db_tmp_path)
    db_url = 'sqlite:///' + old_db_tmp_path

    # WHEN: upgrading the db
    updated_to_version, latest_version = upgrade_db(db_url, upgrade)

    # THEN: the song db should have been upgraded to the latest version
    assert updated_to_version == latest_version, 'The song DB should have been upgrade to the latest version'


def test_upgrade_invalid_song_db(settings, temp_folder):
    """
    Test that we can upgrade an invalid song db to the current schema
    """
    # GIVEN: A song db with invalid version
    invalid_db_path = os.path.join(TEST_RESOURCES_PATH, "songs", 'songs-2.2-invalid.sqlite')
    invalid_db_tmp_path = os.path.join(temp_folder, 'songs-2.2-invalid.sqlite')
    shutil.copyfile(invalid_db_path, invalid_db_tmp_path)
    db_url = 'sqlite:///' + invalid_db_tmp_path

    # WHEN: upgrading the db
    updated_to_version, latest_version = upgrade_db(db_url, upgrade)

    # THEN: the song db should have been upgraded to the latest version without errors
    assert updated_to_version == latest_version, 'The song DB should have been upgrade to the latest version'
