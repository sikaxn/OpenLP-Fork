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
This module contains tests for the Songbeamer song importer.
"""
from unittest.mock import MagicMock

import pytest

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.songs.lib.importers.songbeamer import SongBeamerImport, SongBeamerTypes
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'songs' / 'songbeamer'


@pytest.fixture
def importer(registry: Registry, settings: Settings):
    # with patch('openlp.plugins.songs.lib.importers.songbeamer.SongImport'):
    #     yield SongBeamerImport(MagicMock(), file_paths=[])
    return SongBeamerImport(MagicMock(), file_paths=[])


def test_songbeamer_file_import(settings: Settings):
    """
    Test that loading an SongBeamer file works correctly on various files
    """
    with SongImportTestHelper('SongBeamerImport', 'songbeamer') as helper:
        # Mock out the settings - always return False
        Settings().setValue('songs/enable chords', True)
        helper.file_import([TEST_PATH / 'Amazing Grace.sng'],
                           helper.load_external_result_data(TEST_PATH / 'Amazing Grace.json'))
        helper.file_import([TEST_PATH / 'Lobsinget dem Herrn.sng'],
                           helper.load_external_result_data(TEST_PATH / 'Lobsinget dem Herrn.json'))
        helper.file_import([TEST_PATH / 'When I Call On You.sng'],
                           helper.load_external_result_data(TEST_PATH / 'When I Call On You.json'))
        helper.file_import([TEST_PATH / 'Großer Gott.sng'],
                           helper.load_external_result_data(TEST_PATH / 'Großer Gott.json'))


def test_songbeamer_cp1252_encoded_file(settings: Settings):
    """
    Test that a CP1252 encoded file get's decoded properly.
    """
    with SongImportTestHelper('SongBeamerImport', 'songbeamer') as helper:
        helper.file_import([TEST_PATH / 'cp1252song.sng'],
                           helper.load_external_result_data(TEST_PATH / 'cp1252song.json'))


def test_create_importer(importer: SongBeamerImport):
    """
    Test creating an instance of the SongBeamer file importer
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    # WHEN: An importer object is created
    # THEN: The importer object should not be None
    assert importer is not None, 'Import should not be none'


def test_invalid_import_source(importer: SongBeamerImport):
    """
    Test SongBeamerImport.do_import handles different invalid import_source values
    """
    # GIVEN: A mocked out import wizard
    mocked_import_wizard = MagicMock()
    importer.import_wizard = mocked_import_wizard
    importer.stop_import_flag = True

    # WHEN: Import source is not a list
    for source in ['not a list', 0]:
        importer.import_source = source

        # THEN: do_import should return none and the progress bar maximum should not be set.
        assert importer.do_import() is None, \
            'do_import should return None when import_source is not a list'
        assert mocked_import_wizard.progress_bar.setMaximum.called is False, \
            'setMaxium on import_wizard.progress_bar should not have been called'


def test_valid_import_source(importer: SongBeamerImport):
    """
    Test SongBeamerImport.do_import handles different invalid import_source values
    """
    # GIVEN: A mocked out import wizard
    mocked_import_wizard = MagicMock()
    importer.import_wizard = mocked_import_wizard
    importer.stop_import_flag = True

    # WHEN: Import source is a list
    importer.import_source = ['List', 'of', 'files']

    # THEN: do_import should return none and the progress bar setMaximum should be called with the length of
    #       import_source.
    assert importer.do_import() is None, \
        'do_import should return None when import_source is a list and stop_import_flag is True'
    mocked_import_wizard.progress_bar.setMaximum.assert_called_with(len(importer.import_source))


@pytest.mark.parametrize('line,is_found,verse_type', [('Refrain', True, 'c'),
                                                      ('ReFrain ', True, 'c'),
                                                      ('VersE 1', True, 'v1'),
                                                      ('$$M=special', True, 'o'),
                                                      ('Jesus my saviour', False, None),
                                                      ('Praise him', False, None),
                                                      (' ', False, None),
                                                      ('', False, None)])
def test_check_verse_marks(importer: SongBeamerImport, line: str, is_found: bool, verse_type: str | None):
    """
    Tests different lines to see if a verse mark is detected or not
    """
    # GIVEN: line with unnumbered verse-type
    importer.current_verse_type = None
    # WHEN: line is being checked for verse marks
    result = importer.check_verse_marks(line)
    # THEN: we should get back true and c as self.importer.current_verse_type
    assertion_message = f'Versemark for <{line}> should be found, value {is_found}' if is_found \
                        else f'No versemark for <{line}> should be found, value {is_found}'
    assert result is is_found, assertion_message
    assert importer.current_verse_type == verse_type, f'<{line}> should be interpreted as <{verse_type}>'


def test_verse_marks_defined_in_lowercase(settings: Settings):
    """
    Test that the verse marks are all defined in lowercase
    """
    # GIVEN: SongBeamber MarkTypes
    for tag in SongBeamerTypes.MarkTypes.keys():
        # THEN: tag should be defined in lowercase
        assert tag == tag.lower(), 'Tags should be defined in lowercase'
