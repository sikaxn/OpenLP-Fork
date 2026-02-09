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
This module contains tests for the SongShow Plus song importer.
"""
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.songs.lib import VerseType
from openlp.plugins.songs.lib.importers.songshowplus import SongShowPlusImport
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH

TEST_PATH = RESOURCE_PATH / 'songs' / 'songshowplus'


@pytest.fixture
def importer(registry: Registry, settings: Settings):
    with patch('openlp.plugins.songs.lib.importers.songshowplus.SongImport'):
        yield SongShowPlusImport(MagicMock(), file_paths=[])


def test_song_show_plus(mock_settings: MagicMock):
    test_file_import = SongImportTestHelper('SongShowPlusImport', 'songshowplus')
    test_file_import.setUp()
    test_file_import.file_import([TEST_PATH / 'Amazing Grace.sbsong'],
                                 test_file_import.load_external_result_data(TEST_PATH / 'Amazing Grace.json'))
    test_file_import.file_import([TEST_PATH / 'Beautiful Garden Of Prayer.sbsong'],
                                 test_file_import.load_external_result_data(TEST_PATH /
                                                                            'Beautiful Garden Of Prayer.json'))
    test_file_import.file_import([TEST_PATH / 'a mighty fortress is our god.sbsong'],
                                 test_file_import.load_external_result_data(TEST_PATH /
                                                                            'a mighty fortress is our god.json'))
    test_file_import.file_import([TEST_PATH / 'cleanse-me.sbsong'],
                                 test_file_import.load_external_result_data(TEST_PATH / 'cleanse-me.json'))
    test_file_import.tearDown()


def test_create_importer(importer: SongShowPlusImport):
    """
    Test creating an instance of the SongShow Plus file importer
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    # THEN: The importer object should not be None
    assert importer is not None, 'Import should not be none'


@pytest.mark.parametrize('source', [('not a list',), (0,)])
def test_invalid_import_source(importer: SongShowPlusImport, source: Any):
    """
    Test SongShowPlusImport.do_import handles different invalid import_source values
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    mocked_import_wizard = MagicMock()
    importer.import_wizard = mocked_import_wizard
    importer.stop_import_flag = True

    # WHEN: Import source is not a list, and the importer is run
    importer.import_source = source
    result = importer.do_import()

    # THEN: do_import should return none and the progress bar maximum should not be set.
    assert result is None, 'do_import should return None when import_source is not a list'
    assert mocked_import_wizard.progress_bar.setMaximum.called is False, \
        'setMaximum on import_wizard.progress_bar should not have been called'


def test_valid_import_source(importer: SongShowPlusImport):
    """
    Test SongShowPlusImport.do_import handles different invalid import_source values
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    mocked_import_wizard = MagicMock()
    importer.import_wizard = mocked_import_wizard
    importer.stop_import_flag = True

    # WHEN: Import source is a list
    importer.import_source = ['List', 'of', 'files']
    result = importer.do_import()

    # THEN: do_import should return none and the progress bar setMaximum should be called with the length of
    #       import_source.
    assert result is None, \
        'do_import() should return None when import_source is a list and stop_import_flag is True'
    mocked_import_wizard.progress_bar.setMaximum.assert_called_with(len(importer.import_source))


@pytest.mark.parametrize('original_tag,openlp_tag', [('Verse 1', VerseType.tags[VerseType.Verse] + '1'),
                                                     ('Verse 2', VerseType.tags[VerseType.Verse] + '2'),
                                                     ('verse1', VerseType.tags[VerseType.Verse] + '1'),
                                                     ('Verse', VerseType.tags[VerseType.Verse] + '1'),
                                                     ('Verse1', VerseType.tags[VerseType.Verse] + '1'),
                                                     ('chorus 1', VerseType.tags[VerseType.Chorus] + '1'),
                                                     ('bridge 1', VerseType.tags[VerseType.Bridge] + '1'),
                                                     ('pre-chorus 1', VerseType.tags[VerseType.PreChorus] + '1'),
                                                     ('different 1', VerseType.tags[VerseType.Other] + '1'),
                                                     ('random 1', VerseType.tags[VerseType.Other] + '1')])
def test_to_openlp_verse_tag_unique(importer: SongShowPlusImport, original_tag: str, openlp_tag: str):
    """
    Test to_openlp_verse_tag method by simulating adding a verse
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    # WHEN: Supplied with the following arguments replicating verses being added
    # THEN: The returned value should should correlate with the input arguments
    assert importer.to_openlp_verse_tag(original_tag) == openlp_tag, \
        f'SongShowPlusImport.to_openlp_verse_tag should return "{openlp_tag}" when called with "{original_tag}"'


@pytest.mark.skip('Broken never worked')
def test_to_openlp_verse_tag_verse_order(importer: SongShowPlusImport):
    """
    Test to_openlp_verse_tag method by simulating adding a verse to the verse order
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    # WHEN: Supplied with the following arguments replicating a verse order being added
    test_values = [
        ('Verse 1', VerseType.tags[VerseType.Verse] + '1'),
        ('Verse 2', VerseType.tags[VerseType.Verse] + '2'),
        ('verse1', VerseType.tags[VerseType.Verse] + '1'),
        ('Verse', VerseType.tags[VerseType.Verse] + '1'),
        ('Verse1', VerseType.tags[VerseType.Verse] + '1'),
        ('chorus 1', VerseType.tags[VerseType.Chorus] + '1'),
        ('bridge 1', VerseType.tags[VerseType.Bridge] + '1'),
        ('pre-chorus 1', VerseType.tags[VerseType.PreChorus] + '1'),
        ('different 1', VerseType.tags[VerseType.Other] + '1'),
        ('random 1', VerseType.tags[VerseType.Other] + '2'),
        ('unused 2', None)]

    # THEN: The returned value should should correlate with the input arguments
    for original_tag, openlp_tag in test_values:
        assert importer.to_openlp_verse_tag(original_tag, ignore_unique=True) == openlp_tag, \
            'SongShowPlusImport.to_openlp_verse_tag should return "%s" when called with "%s"' % \
            (openlp_tag, original_tag)
