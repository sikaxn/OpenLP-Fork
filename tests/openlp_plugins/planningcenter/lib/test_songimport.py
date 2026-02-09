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
Package to test the openlp.plugins.planningcenter.lib.songimport package.
"""
import datetime
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.planningcenter.lib.songimport import PlanningCenterSongImport


@pytest.fixture
def song_import(registry: Registry, settings: Settings) -> PlanningCenterSongImport:
    registry.register('songs', MagicMock())
    yield PlanningCenterSongImport()


@patch('openlp.plugins.songs.lib.importers.songimport.Song')
@patch('openlp.plugins.songs.lib.importers.songimport.Author')
def test_add_song_without_lyrics(MockAuthor: MagicMock, MockSong: MagicMock, song_import: PlanningCenterSongImport):
    """
    Test that a song can be added with None lyrics
    """
    # GIVEN: A PlanningCenterSongImport Class and some values
    item_title = 'Title'
    author = 'Author'
    lyrics = None
    theme_name = 'Theme Name'
    last_modified = datetime.datetime.now()
    # WHEN:  A song is added without lyrics
    song_import.add_song(item_title, author, lyrics, theme_name, last_modified)
    # THEN:  A mock song has valid title, lyrics, and theme_name values
    assert MockSong.return_value.title == item_title, 'Mock Song Title matches input title'
    assert item_title in MockSong.return_value.lyrics, 'Mock Song Lyrics contain input title'
    assert MockSong.return_value.theme_name == theme_name, 'Mock Song Theme matches input theme'


@patch('openlp.plugins.songs.lib.importers.songimport.Song')
@patch('openlp.plugins.songs.lib.importers.songimport.Author')
def test_add_song_with_lyrics(MockAuthor: MagicMock, MockSong: MagicMock, song_import: PlanningCenterSongImport):
    """
    Test that a song can be added with lyrics
    """
    # GIVEN: A PlanningCenterSongImport Class and some values
    item_title = 'Title'
    author = 'Author'
    copyright = "Copyright"
    ccli_number = 1111
    lyrics = 'This is my song!'
    theme_name = 'Theme Name'
    last_modified = datetime.datetime.now()
    # WHEN:  A song is added with lyrics
    song_import.add_song(item_title, author, lyrics, theme_name, last_modified, copyright, ccli_number)
    # THEN:  A mock song has valid title, lyrics, and theme_name values
    assert MockSong.return_value.title == item_title, 'Mock Song Title matches input title'
    assert MockSong.return_value.copyright == copyright
    assert MockSong.return_value.ccli_number == ccli_number
    assert lyrics in MockSong.return_value.lyrics, 'Mock Song Lyrics contain input lyrics'
    assert MockSong.return_value.theme_name == theme_name, 'Mock Song Theme matches input theme'


@patch('openlp.plugins.songs.lib.importers.songimport.Song')
@patch('openlp.plugins.songs.lib.importers.songimport.Author')
def test_add_song_with_verse(MockAuthor: MagicMock, MockSong: MagicMock, song_import: PlanningCenterSongImport):
    """
    Test that a song can be added with lyrics that contain a verse header
    """
    # GIVEN: A PlanningCenterSongImport Class
    item_title = 'Title'
    author = 'Author'
    copyright = "Copyright"
    ccli_number = 1111
    lyrics = 'V1\nThis is my song!'
    theme_name = 'Theme Name'
    last_modified = datetime.datetime.now()
    # WHEN:  A song is added with lyrics that contain a verse tag
    song_import.add_song(item_title, author, lyrics, theme_name, last_modified, copyright, ccli_number)
    # THEN:  A mock song has valid title, lyrics, and theme_name values
    assert MockSong.return_value.title == item_title, 'Mock Song Title matches input title'
    assert MockSong.return_value.copyright == copyright
    assert MockSong.return_value.ccli_number == ccli_number
    assert 'This is my song!' in MockSong.return_value.lyrics, 'Mock Song Lyrics contain input lyrics'
    assert 'type="v"' in MockSong.return_value.lyrics, 'Mock Song Lyrics contain input verse'
    assert MockSong.return_value.theme_name == theme_name, 'Mock Song Theme matches input theme'


@patch('openlp.plugins.songs.lib.importers.songimport.Song')
@patch('openlp.plugins.songs.lib.importers.songimport.Author')
def test_add_song_with_verse_order(MockAuthor: MagicMock, MockSong: MagicMock, song_import: PlanningCenterSongImport):
    """
    Test that a song can be added with verse order properly set
    """
    # GIVEN: A PlanningCenterSongImport Class and values including verse_order
    item_title = 'Title'
    author = 'Author'
    copyright = "Copyright"
    ccli_number = 1111
    lyrics = 'V1\nVerse one\n\nChorus\nThis is the chorus'
    theme_name = 'Theme Name'
    last_modified = datetime.datetime.now()
    verse_order = "v1 c v1"
    mock_song_instance = MagicMock()
    MockSong.return_value = mock_song_instance
    # Mock the manager.get_object to return our mock song
    song_import.manager.get_object = MagicMock(return_value=mock_song_instance)
    # WHEN: A song is added with verse order
    song_import.add_song(item_title, author, lyrics, theme_name, last_modified, copyright, ccli_number, verse_order)
    # THEN: The mock song has the verse_order properly set
    assert mock_song_instance.title == item_title, 'Mock Song Title matches input title'
    assert mock_song_instance.copyright == copyright
    assert mock_song_instance.ccli_number == ccli_number
    assert mock_song_instance.verse_order == verse_order, 'Mock Song verse_order matches input verse_order'
    assert 'Verse one' in mock_song_instance.lyrics, 'Mock Song Lyrics contain verse text'
    assert 'This is the chorus' in mock_song_instance.lyrics, 'Mock Song Lyrics contain chorus text'
    assert mock_song_instance.theme_name == theme_name, 'Mock Song Theme matches input theme'


def test_parse_lyrics_with_end_marker(song_import: PlanningCenterSongImport):
    """
    Test that a lyrics after an END marker are skipped
    """
    # GIVEN: A PlanningCenterSongImport Class
    # WHEN:  _split_lyrics_into_verses is called with lyrics that contain an END marker
    lyrics = 'This is my song!\n\n{<b>END</b>}\n\nSkip this part of the song'
    output_verses = song_import._split_lyrics_into_verses(lyrics)
    # THEN:  A mock song has valid title, lyrics, and theme_name values
    assert len(output_verses) == 1, 'A single verse is returned'
    assert 'This is my song!' in output_verses[0]['verse_text'], 'Output lyrics contain input lyrics'
    assert 'END' not in output_verses[0]['verse_text'], 'Output Lyrics do not contain END'
    assert 'Skip this part of the song' not in output_verses[0]['verse_text'], 'Output Lyrics stop at end'


def test_parse_lyrics_with_multiple_verses(song_import: PlanningCenterSongImport):
    """
    Test lyrics with verse marker inside
    """
    # GIVEN: A PlanningCenterSongImport Class
    # WHEN:  _split_lyrics_into_verses is called with lyrics that contain a verse marker inside (chorus)
    lyrics = 'First Verse\n\nChorus\nThis is my Chorus\n'
    output_verses = song_import._split_lyrics_into_verses(lyrics)
    # THEN:  A mock song has valid title, lyrics, and theme_name values
    assert len(output_verses) == 2, 'Two output verses are returned'
    assert output_verses[1]['verse_type'] == 'c', 'Second verse is a chorus'


def test_parse_lyrics_with_single_spaced_verse_tags(song_import: PlanningCenterSongImport):
    """
    Test lyrics with verse marker inside
    """
    # GIVEN: A PlanningCenterSongImport Class
    # WHEN:  _split_lyrics_into_verses is called with lyrics that contain a verse marker inside (chorus)
    lyrics = 'V1\nFirst Verse\nV2\nSecondVerse\n'
    output_verses = song_import._split_lyrics_into_verses(lyrics)
    # THEN:  A mock song has valid title, lyrics, and theme_name values
    assert len(output_verses) == 2, 'Two output verses are returned'


@patch('openlp.plugins.songs.lib.importers.songimport.Song')
@patch('openlp.plugins.songs.lib.importers.songimport.Author')
def test_add_song_with_empty_verse_order(MockAuthor: MagicMock, MockSong: MagicMock,
                                         song_import: PlanningCenterSongImport):
    """
    Test that a song can be added with empty verse order (KeyError case)
    """
    # GIVEN: A PlanningCenterSongImport Class and values with empty verse_order
    item_title = 'Title'
    author = 'Author'
    copyright = "Copyright"
    ccli_number = 1111
    lyrics = 'V1\nVerse one\n\nChorus\nThis is the chorus'
    theme_name = 'Theme Name'
    last_modified = datetime.datetime.now()
    verse_order = ""  # Empty verse order to test edge case
    mock_song_instance = MagicMock()
    MockSong.return_value = mock_song_instance
    song_import.manager.get_object = MagicMock(return_value=mock_song_instance)
    # WHEN: A song is added with empty verse order
    song_import.add_song(item_title, author, lyrics, theme_name, last_modified, copyright, ccli_number, verse_order)
    # THEN: The mock song has empty verse_order set
    assert mock_song_instance.verse_order == "", 'Mock Song verse_order is empty string'
