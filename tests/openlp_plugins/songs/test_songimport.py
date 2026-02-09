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
This module contains tests for the SongImport submodule of the Songs plugin.
"""
from unittest.mock import MagicMock

from openlp.plugins.songs.lib.db import AuthorType
from openlp.plugins.songs.lib.importers.songimport import SongImport


def test_parse_author_simple_with_type(settings):
    # GIVEN: A SongImport object with a mocked DB manager and a dummy file path
    db_manager_mock = MagicMock()
    song_import = SongImport(db_manager_mock, file_path='/dummy/')
    # WHEN: Parsing simple author name with type
    song_import.parse_author('Random Author', AuthorType.Words)
    # THEN: The result should be an registered author of that type
    assert song_import.authors == [('Random Author', AuthorType.Words)]


def test_parse_author_list_with_type(settings):
    # GIVEN: A SongImport object with a mocked DB manager and a dummy file path
    db_manager_mock = MagicMock()
    song_import = SongImport(db_manager_mock, file_path='/dummy/')
    # WHEN: Parsing simple list of author names with type
    song_import.parse_author('Random Author, Important Name; Very Important Person', AuthorType.Words)
    # THEN: The result should be registered authors of that type
    assert song_import.authors == [('Random Author', AuthorType.Words),
                                   ('Important Name', AuthorType.Words),
                                   ('Very Important Person', AuthorType.Words)]


def test_parse_author_with_prefix(settings):
    # GIVEN: A SongImport object with a mocked DB manager and a dummy file path
    db_manager_mock = MagicMock()
    song_import = SongImport(db_manager_mock, file_path='/dummy/')
    # WHEN: Parsing author name with type prefixes
    song_import.parse_author('Lyrics: Random Author')
    # THEN: The result should be an registered author of that type
    assert song_import.authors == [('Random Author', AuthorType.Words)]


def test_parse_author_with_multiple_prefixes(settings):
    # GIVEN: A SongImport object with a mocked DB manager and a dummy file path
    db_manager_mock = MagicMock()
    song_import = SongImport(db_manager_mock, file_path='/dummy/')
    # WHEN: Parsing author names with multiple inline prefixes
    song_import.parse_author('Music by Random Author, Important Name; Lyrics: Very Important Person. '
                             'Translation: Very Clever Person')
    # THEN: The result should be registered authors of that type
    assert song_import.authors == [('Random Author', AuthorType.Music),
                                   ('Important Name', AuthorType.Music),
                                   ('Very Important Person', AuthorType.Words),
                                   ('Very Clever Person', AuthorType.Translation)]
