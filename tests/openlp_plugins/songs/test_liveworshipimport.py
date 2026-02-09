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
This module contains tests for the LiveWorship song importer.
"""
from unittest.mock import MagicMock, patch

from tests.utils import load_external_result_data
from tests.utils.constants import RESOURCE_PATH

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.songs.lib.importers.liveworship import LiveWorshipImport


TEST_PATH = RESOURCE_PATH / 'songs' / 'liveworship'


def _get_item(data, key):
    """
    Get an item or return a blank string
    """
    if key in data:
        return data[key]
    return ''


@patch('openlp.plugins.songs.lib.importers.liveworship.SongImport')
def test_create_importer(mocked_songimport: MagicMock, registry: Registry, settings: Settings):
    """
    Test creating an instance of the LiveWorship file importer
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    mocked_manager = MagicMock()

    # WHEN: An importer object is created
    importer = LiveWorshipImport(mocked_manager, file_paths=[])

    # THEN: The importer object should not be None
    assert importer is not None, 'Import should not be none'


@patch('openlp.plugins.songs.lib.importers.liveworship.SongImport')
def test_parse_xml_dump(mocked_songimport: MagicMock, registry: Registry, settings: Settings):
    """
    Test importing a simple XML dump in LiveWorshipImport
    """
    # GIVEN: A mocked out SongImport class, a mocked out "manager" and a simple XML dump
    mocked_manager = MagicMock()
    importer = LiveWorshipImport(mocked_manager, file_paths=[])
    importer.finish = MagicMock()
    importer.import_wizard = MagicMock()
    importer.import_source = TEST_PATH / 'valentina-db-simplified-dump.xml'

    # WHEN: The XML is loaded and processed
    importer.load_xml_dump()
    importer.extract_songs()

    # THEN: The imported data should look like expected
    result_data = load_external_result_data(TEST_PATH / 'A Child Of The King.json')
    assert importer.title == _get_item(result_data, 'title')
    assert importer.verses == _get_item(result_data, 'verses')
    assert importer.topics[0] == _get_item(result_data, 'topics')[0]
    assert importer.authors[0][0] == _get_item(result_data, 'authors')[0]
    assert importer.authors[1][0] == _get_item(result_data, 'authors')[1]
