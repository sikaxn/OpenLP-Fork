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
This module contains tests for the WorshipCenter Pro song importer.
"""
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings

from tests.utils import load_external_result_data
from tests.utils.constants import RESOURCE_PATH

try:
    from openlp.plugins.songs.lib.importers.opspro import OPSProImport
    CAN_RUN_TESTS = True
except ImportError:
    CAN_RUN_TESTS = False


pytestmark = pytest.mark.skipif(not CAN_RUN_TESTS, reason='Not Windows, skipping test')
TEST_PATH = RESOURCE_PATH / 'songs' / 'opspro'


def _get_item(data, key):
    """
    Get an item or return a blank string
    """
    if key in data:
        return data[key]
    return ''


def _build_data(test_file, dual_language):
    """
    Build the test data
    """
    song = MagicMock()
    song.ID = 100
    song.SongNumber = 123
    song.SongBookName = 'The Song Book'
    song.Title = 'Song Title'
    song.CopyrightText = 'Music and text by me'
    song.Version = '1'
    song.Origin = '...'
    lyrics = MagicMock()
    lyrics.Lyrics = (TEST_PATH / test_file).read_bytes().decode()
    lyrics.Type = 1
    lyrics.IsDualLanguage = dual_language
    return song, lyrics


@patch('openlp.plugins.songs.lib.importers.opspro.SongImport')
def test_create_importer(mocked_songimport: MagicMock, registry: Registry, settings: Settings):
    """
    Test creating an instance of the OPS Pro file importer
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    mocked_manager = MagicMock()

    # WHEN: An importer object is created
    importer = OPSProImport(mocked_manager, file_paths=[])

    # THEN: The importer object should not be None
    assert importer is not None, 'Import should not be none'


@patch('openlp.plugins.songs.lib.importers.opspro.SongImport')
def test_detect_chorus(mocked_songimport: MagicMock, registry: Registry, settings: Settings):
    """
    Test importing lyrics with a chorus in OPS Pro
    """
    # GIVEN: A mocked out SongImport class, a mocked out "manager" and a mocked song and lyrics entry
    mocked_manager = MagicMock()
    importer = OPSProImport(mocked_manager, file_paths=[])
    importer.finish = MagicMock()
    song, lyrics = _build_data('you are so faithfull.txt', False)

    # WHEN: An importer object is created
    importer.process_song(song, lyrics, [])

    # THEN: The imported data should look like expected
    result_data = load_external_result_data(TEST_PATH / 'You are so faithful.json')
    assert importer.verses == _get_item(result_data, 'verses')
    assert importer.verse_order_list_generated == _get_item(result_data, 'verse_order_list')


@patch('openlp.plugins.songs.lib.importers.opspro.SongImport')
def test_join_and_split(mocked_songimport: MagicMock, registry: Registry, settings: Settings):
    """
    Test importing lyrics with a split and join tags works in OPS Pro
    """
    # GIVEN: A mocked out SongImport class, a mocked out "manager" and a mocked song and lyrics entry
    mocked_manager = MagicMock()
    importer = OPSProImport(mocked_manager, file_paths=[])
    importer.finish = MagicMock()
    song, lyrics = _build_data('amazing grace.txt', False)

    # WHEN: An importer object is created
    importer.process_song(song, lyrics, [])

    # THEN: The imported data should look like expected
    result_data = load_external_result_data(TEST_PATH / 'Amazing Grace.json')
    assert importer.verses == _get_item(result_data, 'verses')
    assert importer.verse_order_list_generated == _get_item(result_data, 'verse_order_list')


@patch('openlp.plugins.songs.lib.importers.opspro.SongImport')
def test_trans_off_tag(mocked_songimport: MagicMock, registry: Registry, settings: Settings):
    """
    Test importing lyrics with a split and join and translations tags works in OPS Pro
    """
    # GIVEN: A mocked out SongImport class, a mocked out "manager" and a mocked song and lyrics entry
    mocked_manager = MagicMock()
    importer = OPSProImport(mocked_manager, file_paths=[])
    importer.finish = MagicMock()
    song, lyrics = _build_data('amazing grace2.txt', True)

    # WHEN: An importer object is created
    importer.process_song(song, lyrics, [])

    # THEN: The imported data should look like expected
    result_data = load_external_result_data(TEST_PATH / 'Amazing Grace.json')
    assert importer.verses == _get_item(result_data, 'verses')
    assert importer.verse_order_list_generated == _get_item(result_data, 'verse_order_list')


@patch('openlp.plugins.songs.lib.importers.opspro.SongImport')
def test_trans_tag(mocked_songimport: MagicMock, registry: Registry, settings: Settings):
    """
    Test importing lyrics with various translations tags works in OPS Pro
    """
    # GIVEN: A mocked out SongImport class, a mocked out "manager" and a mocked song and lyrics entry
    mocked_manager = MagicMock()
    importer = OPSProImport(mocked_manager, file_paths=[])
    importer.finish = MagicMock()
    song, lyrics = _build_data('amazing grace3.txt', True)

    # WHEN: An importer object is created
    importer.process_song(song, lyrics, [])

    # THEN: The imported data should look like expected
    result_data = load_external_result_data(TEST_PATH / 'Amazing Grace3.json')
    assert importer.verses == _get_item(result_data, 'verses')
    assert importer.verse_order_list_generated == _get_item(result_data, 'verse_order_list')
