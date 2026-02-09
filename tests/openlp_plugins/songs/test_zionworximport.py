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
This module contains tests for the ZionWorx song importer.
"""
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.lib.importers.zionworx import ZionWorxImport
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'songs' / 'zionworx'


@patch('openlp.plugins.songs.lib.importers.zionworx.SongImport')
def test_create_importer(MockSongImport: MagicMock, registry: Registry, settings: Settings):
    """
    Test creating an instance of the ZionWorx file importer
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    # WHEN: An importer object is created
    importer = ZionWorxImport(MagicMock(), file_paths=[])

    # THEN: The importer should be an instance of SongImport
    assert isinstance(importer, SongImport)


@pytest.mark.parametrize('filebase', ['zionworx', 'amazing-grace-arabic'])
def test_zion_wrox(filebase, mock_settings):
    """Test that the ZionWorx importer correctly imports songs"""
    test_file_import = SongImportTestHelper('ZionWorxImport', 'zionworx')
    test_file_import.setUp()
    test_file_import.file_import(TEST_PATH / f'{filebase}.csv',
                                 test_file_import.load_external_result_data(TEST_PATH / f'{filebase}.json'))
    test_file_import.tearDown()
