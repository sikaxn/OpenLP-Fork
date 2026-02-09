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
This module contains tests for the lib submodule of the Bibles plugin.
"""
import pytest
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.plugins.bibles.lib import parse_reference, update_reference_separators
from openlp.plugins.bibles.lib.manager import BibleManager
from tests.utils.constants import TEST_RESOURCES_PATH


__default_settings__ = {
    'bibles/verse separator': '',
    'bibles/range separator': '',
    'bibles/list separator': '',
    'bibles/end separator': ''
}


@pytest.fixture()
def manager(settings):
    Registry().register('service_list', MagicMock())
    # set default separators to the empty default values
    Registry().get('settings').extend_default_settings(__default_settings__)
    with patch('openlp.core.common.applocation.AppLocation.get_section_data_path') as mocked_get_data_path, \
            patch('openlp.core.common.applocation.AppLocation.get_files') as mocked_get_files:
        # GIVEN: A mocked out AppLocation.get_files()
        update_reference_separators()
        mocked_get_files.return_value = ["tests.sqlite"]
        mocked_get_data_path.return_value = TEST_RESOURCES_PATH + "/bibles"
        return BibleManager(MagicMock())


def test_parse_reference_numbered_book_single_chapter_no_verse_reference(manager):
    """
    Test the parse_reference method with 1 Timothy 1
    """
    # GIVEN given a bible in the bible manager
    # WHEN asking to parse the bible reference
    results = parse_reference('1 Timothy 1', manager.db_cache['tests'], MagicMock(), 54)
    # THEN a one tuple verse array should be returned
    assert [(54, 1, 1, -1)] == results, "The bible verses should match the expected results"


def test_parse_reference_numbered_book_single_range_single_chapter_multiple_verses(manager):
    """
    Test the parse_reference method with 1 Timothy 1:1-2
    """
    # GIVEN given a bible in the bible manager
    # WHEN asking to parse the bible reference
    results = parse_reference('1 Timothy 1:1-2', manager.db_cache['tests'], MagicMock(), 54)
    # THEN a one tuple verse array should be returned
    assert [(54, 1, 1, 2)] == results, "The bible verses should match the expected results"


def test_parse_reference_numbered_book_single_range_multiple_chapters_specific_verses(manager):
    """
    Test the parse_reference method with 1 Timothy 1:1-2
    """
    # GIVEN given a bible in the bible manager
    # WHEN asking to parse the bible reference
    results = parse_reference('1 Timothy 1:1-2:1', manager.db_cache['tests'], MagicMock(), 54)
    # THEN a two tuple verse array should be returned
    assert [(54, 1, 1, -1), (54, 2, 1, 1)] == results, \
        "The bible verses should match the expected results"


def test_parse_reference_invalid_book(manager):
    """
    Test the parse_reference method with non existent book
    """
    # GIVEN given a bible in the bible manager
    # WHEN asking to parse the bible reference
    results = parse_reference('Raoul 1', manager.db_cache['tests'], MagicMock())
    # THEN an empty verse array should be returned
    assert [] == results, "The bible search should return an empty list"


def test_parse_reference_numbered_book_single_range_single_chapter_with_end_reference(manager):
    """
    Test the parse_reference method with 1 Timothy 1:3-end
    """
    # GIVEN given a bible in the bible manager
    # WHEN asking to parse the bible reference
    results = parse_reference('1 Timothy 1:3-end', manager.db_cache['tests'], MagicMock(), 54)
    # THEN a one tuple verse array should be returned
    assert [(54, 1, 3, -1)] == results, "The bible verses should match the expected results"


def test_parse_reference_numbered_book_single_range_single_chapter_with_end_reference_no_bible_ref_id(manager):
    """
    Test the parse_reference method with 1 Timothy 1:3-end without a bible ref id to match
    how the GUI does the search.  This is logged in issue #282
    """
    # GIVEN given a bible in the bible manager
    # WHEN asking to parse the bible reference in Language 0 (english)
    results = parse_reference('1 Timothy 1:3-end', manager.db_cache['tests'], 0)
    # THEN a one tuple verse array should be returned
    assert [(54, 1, 3, -1)] == results, "The bible verses should match the expected results"


def test_parse_reference_book_ref_id_invalid(manager):
    """
    Test the parse_reference method with 1 Timothy 1:1 with an invalid bible ref id
    """
    # GIVEN given a bible in the bible manager
    # WHEN asking to parse the bible reference with an invalid bible reference id
    results = parse_reference('1 Timothy 1:1', manager.db_cache['tests'], MagicMock(), -666)
    # THEN an empty verse array should be returned
    assert [] == results, "The bible verse list should be empty"


def test_parse_reference_no_from_chapter_in_second_range(manager):
    """
    Test the parse_reference method with 1 Timothy 1:1,3
    """
    # GIVEN given a bible in the bible manager
    # WHEN asking to parse the bible reference that has no from_chapter in the second range
    results = parse_reference('1 Timothy 1:1,3', manager.db_cache['tests'], MagicMock(), 54)
    # THEN a two tuple verse array should be returned
    assert [(54, 1, 1, 1), (54, 1, 3, 3)] == results, "The bible verses should match the expected results"


def test_parse_reference_to_chapter_less_than_from_chapter(manager):
    """
    Test the parse_reference method with 1 Timothy 2:1-1:1
    """
    # GIVEN given a bible in the bible manager
    # WHEN asking to parse the bible reference with a to_chapter less than the from_chapter
    results = parse_reference('1 Timothy 2:1-1:1', manager.db_cache['tests'], MagicMock(), 54)
    # THEN an empty verse array should be returned
    assert [] == results, "The bible verse list should be empty"


def test_parse_reference_no_from_chapter_specified(manager):
    """
    Test the parse_reference method with 1 Timothy :1-2
    """
    # GIVEN given a bible in the bible manager
    # WHEN asking to parse the bible reference with no from_chapter specified
    results = parse_reference('1 Timothy :1-2', manager.db_cache['tests'], MagicMock(), 54)
    # THEN a two tuple verse array should be returned with the bible verse references treated as chapter references
    assert [(54, 1, 1, -1), (54, 2, 1, -1)] == results, "The bible verses should match the expected results"


def test_parse_reference_three_chapters(manager):
    """
    Test the parse_reference method with 1 Timothy 1-3
    """
    # GIVEN given a bible in the bible manager
    # WHEN asking to parse the bible reference with three chapters
    results = parse_reference('1 Timothy 1-3', manager.db_cache['tests'], MagicMock(), 54)
    # THEN a three tuple verse array should be returned
    assert [(54, 1, 1, -1), (54, 2, 1, -1), (54, 3, 1, -1)] == results, \
        "The bible verses should match the expected results"


def test_parse_reference_non_regexp_matching_reference(manager):
    """
    Test the parse_reference method with 1 Timothy
    """
    # GIVEN given a bible in the bible manager
    # WHEN asking to parse the bible reference that fails the regexp matching
    results = parse_reference('1 Timothy', manager.db_cache['tests'], MagicMock(), 54)
    # THEN an empty verse array should be returned
    assert [] == results, "The bible verse list should be empty"
