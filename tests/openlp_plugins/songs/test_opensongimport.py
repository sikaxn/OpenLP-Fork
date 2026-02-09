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
This module contains tests for the OpenSong song importer.
"""
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.songs.lib.importers.opensong import OpenSongImport
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'songs' / 'opensong'


def test_opensong_file_import(registry: Registry, settings: Settings):
    """
    Test that loading an OpenSong file works correctly on various files
    """
    with SongImportTestHelper('OpenSongImport', 'opensong') as helper:
        helper.file_import([TEST_PATH / 'Amazing Grace'],
                           helper.load_external_result_data(TEST_PATH / 'Amazing Grace.json'))
        helper.file_import([TEST_PATH / 'Beautiful Garden Of Prayer'],
                           helper.load_external_result_data(TEST_PATH / 'Beautiful Garden Of Prayer.json'))
        helper.file_import([TEST_PATH / 'One, Two, Three, Four, Five'],
                           helper.load_external_result_data(TEST_PATH / 'One, Two, Three, Four, Five.json'))
        helper.file_import([TEST_PATH / 'Amazing Grace2'],
                           helper.load_external_result_data(TEST_PATH / 'Amazing Grace.json'))
        helper.file_import([TEST_PATH / 'Amazing Grace with bad CCLI'],
                           helper.load_external_result_data(TEST_PATH / 'Amazing Grace without CCLI.json'))


def test_create_importer(registry: Registry, settings: Settings):
    """
    Test creating an instance of the OpenSong file importer
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    with patch('openlp.plugins.songs.lib.importers.opensong.SongImport'):
        mocked_manager = MagicMock()

        # WHEN: An importer object is created
        importer = OpenSongImport(mocked_manager, file_paths=[])

        # THEN: The importer object should not be None
        assert importer is not None, 'Import should not be none'


def test_invalid_import_source(registry: Registry, settings: Settings):
    """
    Test OpenSongImport.do_import handles different invalid import_source values
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    with patch('openlp.plugins.songs.lib.importers.opensong.SongImport'):
        mocked_manager = MagicMock()
        mocked_import_wizard = MagicMock()
        importer = OpenSongImport(mocked_manager, file_paths=[])
        importer.import_wizard = mocked_import_wizard
        importer.stop_import_flag = True

        # WHEN: Import source is not a list
        for source in ['not a list', 0]:
            importer.import_source = source

            # THEN: do_import should return none and the progress bar maximum should not be set.
            assert importer.do_import() is None, 'do_import should return None when import_source is not a list'
            assert mocked_import_wizard.progress_bar.setMaximum.called is False, \
                'setMaximum on import_wizard.progress_bar should not have been called'


def test_valid_import_source(registry: Registry, settings: Settings):
    """
    Test OpenSongImport.do_import handles different invalid import_source values
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    with patch('openlp.plugins.songs.lib.importers.opensong.SongImport'):
        mocked_manager = MagicMock()
        mocked_import_wizard = MagicMock()
        importer = OpenSongImport(mocked_manager, file_paths=[])
        importer.import_wizard = mocked_import_wizard
        importer.stop_import_flag = True

        # WHEN: Import source is a list
        importer.import_source = ['List', 'of', 'files']

        # THEN: do_import should return none and the progress bar setMaximum should be called with the length of
        #       import_source.
        assert importer.do_import() is None, \
            'do_import should return None when import_source is a list and stop_import_flag is True'
        mocked_import_wizard.progress_bar.setMaximum.assert_called_with(len(importer.import_source))
