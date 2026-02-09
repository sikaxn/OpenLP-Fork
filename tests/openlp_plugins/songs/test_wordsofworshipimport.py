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
This module contains tests for the Words of Worship song importer.
"""
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'songs' / 'wordsofworship'


def test_amazing_grace_song_import(registry: Registry, settings: Settings):
    """
    Test that loading a Words of Worship file works correctly
    """
    with SongImportTestHelper('WordsOfWorshipImport', 'wordsofworship') as helper:
        helper.file_import([TEST_PATH / 'Amazing Grace (6 Verses)_v2_1_2.wow-song'],
                           helper.load_external_result_data(TEST_PATH / 'Amazing Grace (6 Verses)_v2_1_2.json'))


def test_when_morning_gilds_song_import(registry: Registry, settings: Settings):
    """
    Test that loading a Words of Worship file v2.0.0 works correctly
    """
    with SongImportTestHelper('WordsOfWorshipImport', 'wordsofworship') as helper:
        helper.file_import([TEST_PATH / 'When morning gilds the skies_v2_0_0.wsg'],
                           helper.load_external_result_data(TEST_PATH / 'When morning gilds the skies_v2_0_0.json'))


def test_holy_holy_holy_song_import(registry: Registry, settings: Settings):
    """
    Test that loading a Words of Worship file works correctly
    """
    with SongImportTestHelper('WordsOfWorshipImport', 'wordsofworship') as helper:
        helper.file_import([TEST_PATH / 'Holy Holy Holy Lord God Almighty_v2_1_2.wow-song'],
                           helper.load_external_result_data(TEST_PATH / 'Holy Holy Holy Lord God Almighty_v2_1_2.json'))


def test_test_song_v2_0_0_song_import(registry: Registry, settings: Settings):
    """
    Test that loading a Words of Worship file v2.0.0 works correctly
    """
    with SongImportTestHelper('WordsOfWorshipImport', 'wordsofworship') as helper:
        helper.file_import([TEST_PATH / 'Test_Song_v2_0_0.wsg'],
                           helper.load_external_result_data(TEST_PATH / 'Test_Song_v2_0_0.json'))


def test_test_song_song_import(registry: Registry, settings: Settings):
    """
    Test that loading a Words of Worship file v2.1.2 works correctly
    """
    with SongImportTestHelper('WordsOfWorshipImport', 'wordsofworship') as helper:
        helper.file_import([TEST_PATH / 'Test_Song_v2_1_2.wow-song'],
                           helper.load_external_result_data(TEST_PATH / 'Test_Song_v2_1_2.json'))
