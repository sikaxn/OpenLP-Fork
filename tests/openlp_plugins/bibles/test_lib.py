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
from openlp.plugins.bibles import lib
from openlp.plugins.bibles.lib import SearchResults, get_reference_match, update_reference_separators


@pytest.fixture
def mocked_bible_test(registry):
    """Local test setup"""
    ret_value = MagicMock(**{'value.return_value': ''})
    Registry().register('settings', ret_value)


@patch('openlp.plugins.bibles.lib.update_reference_separators')
def test_get_reference_separator(mocked_update_reference_separators):
    """
    Test the get_reference_separator method
    """
    # GIVEN: A list of expected separators and the lib module's constant is empty
    lib.REFERENCE_SEPARATORS = None
    separators = {'sep_r': '\\s*(?:e)\\s*', 'sep_e_default': 'end', 'sep_v_display': 'w', 'sep_l_display': 'r',
                  'sep_v_default': ':|v|V|verse|verses', 'sep_l': '\\s*(?:r)\\s*', 'sep_l_default': ',|and',
                  'sep_e': '\\s*(?:t)\\s*', 'sep_v': '\\s*(?:w)\\s*', 'sep_r_display': 'e', 'sep_r_default': '-|to'}

    def _update_side_effect():
        """
        Update the references after mocking out the method
        """
        lib.REFERENCE_SEPARATORS = separators

    mocked_update_reference_separators.side_effect = _update_side_effect

    # WHEN: Calling get_reference_separator
    for key, value in separators.items():
        lib.get_reference_separator(key)

        # THEN: get_reference_separator should return the correct separator
        assert separators[key] == value
    mocked_update_reference_separators.assert_called_once_with()


def test_search_results_creation():
    """
    Test the creation and construction of the SearchResults class
    """
    # GIVEN: A book, chapter and a verse list
    book = 'Genesis'
    chapter = 1
    verse_list = {
        1: 'In the beginning God created the heavens and the earth.',
        2: 'The earth was without form and void, and darkness was over the face of the deep. And the Spirit of '
           'God was hovering over the face of the waters.'
    }

    # WHEN: We create the search results object
    search_results = SearchResults(book, chapter, verse_list)

    # THEN: It should have a book, a chapter and a verse list
    assert search_results is not None, 'The search_results object should not be None'
    assert search_results.book == book, 'The book should be "Genesis"'
    assert search_results.chapter == chapter, 'The chapter should be 1'
    assert search_results.verse_list == verse_list, 'The verse lists should be identical'


def test_search_results_has_verse_list():
    """
    Test that a SearchResults object with a valid verse list returns True when checking ``has_verse_list()``
    """
    # GIVEN: A valid SearchResults object with a proper verse list
    search_results = SearchResults('Genesis', 1, {1: 'In the beginning God created the heavens and the earth.'})

    # WHEN: We check that the SearchResults object has a verse list
    has_verse_list = search_results.has_verse_list()

    # THEN: It should be True
    assert has_verse_list is True, 'The SearchResults object should have a verse list'


def test_search_results_has_no_verse_list():
    """
    Test that a SearchResults object with an empty verse list returns False when checking ``has_verse_list()``
    """
    # GIVEN: A valid SearchResults object with an empty verse list
    search_results = SearchResults('Genesis', 1, {})

    # WHEN: We check that the SearchResults object has a verse list
    has_verse_list = search_results.has_verse_list()

    # THEN: It should be False
    assert has_verse_list is False, 'The SearchResults object should have a verse list'


def test_reference_matched_full(mocked_bible_test):
    """
    Test that the 'full' regex parses bible verse references correctly.
    """
    # GIVEN: Some test data which contains different references to parse, with the expected results.
    # The following test data tests with about 240 variants when using the default 'separators'
    # The amount is exactly 222 without '1. John 23' and'1. John. 23'
    test_data = [
        # Input reference, book name, chapter + verse reference
        ('Psalm 23', 'Psalm', '23'),
        ('Psalm. 23', 'Psalm', '23'),
        ('Psalm 23{to}24', 'Psalm', '23-24'),
        ('Psalm 23{verse}1{to}2', 'Psalm', '23:1-2'),
        ('Psalm 23{verse}1{to}{end}', 'Psalm', '23:1-end'),
        ('Psalm 23{verse}1{to}2{_and}5{to}6', 'Psalm', '23:1-2,5-6'),
        ('Psalm 23{verse}1{to}2{_and}5{to}{end}', 'Psalm', '23:1-2,5-end'),
        ('Psalm 23{verse}1{to}2{_and}24{verse}1{to}3', 'Psalm', '23:1-2,24:1-3'),
        ('Psalm 23{verse}1{to}{end}{_and}24{verse}1{to}{end}', 'Psalm', '23:1-end,24:1-end'),
        ('Psalm 23{verse}1{to}24{verse}1', 'Psalm', '23:1-24:1'),
        ('Psalm 23{_and}24', 'Psalm', '23,24'),
        ('1 John 23', '1 John', '23'),
        ('1 John. 23', '1 John', '23'),
        ('1. John 23', '1. John', '23'),
        ('1. John. 23', '1. John', '23'),
        ('1 John 23{to}24', '1 John', '23-24'),
        ('1 John 23{verse}1{to}2', '1 John', '23:1-2'),
        ('1 John 23{verse}1{to}{end}', '1 John', '23:1-end'),
        ('1 John 23{verse}1{to}2{_and}5{to}6', '1 John', '23:1-2,5-6'),
        ('1 John 23{verse}1{to}2{_and}5{to}{end}', '1 John', '23:1-2,5-end'),
        ('1 John 23{verse}1{to}2{_and}24{verse}1{to}3', '1 John', '23:1-2,24:1-3'),
        ('1 John 23{verse}1{to}{end}{_and}24{verse}1{to}{end}', '1 John', '23:1-end,24:1-end'),
        ('1 John 23{verse}1{to}24{verse}1', '1 John', '23:1-24:1'),
        ('1 John 23{_and}24', '1 John', '23,24')]

    full_reference_match = get_reference_match('full')
    for reference_text, book_result, ranges_result in test_data:
        to_separators = ['-', ' - ', 'to', ' to '] if '{to}' in reference_text else ['']
        verse_separators = [':', ' : ', 'v', ' v ', 'V', ' V ', 'verse', ' verse ', 'verses', ' verses '] \
            if '{verse}' in reference_text else ['']
        and_separators = [',', ' , ', 'and', ' and '] if '{_and}' in reference_text else ['']
        end_separators = ['end', ' end '] if '{end}' in reference_text else ['']

        for to in to_separators:
            for verse in verse_separators:
                for _and in and_separators:
                    for end in end_separators:
                        reference_text = reference_text.format(to=to, verse=verse, _and=_and, end=end)

                        # WHEN: Attempting to parse the input string
                        match = full_reference_match.match(reference_text)

                        # THEN: A match should be returned, and the book and reference should match the
                        #       expected result
                        assert match is not None, '{text} should provide a match'.format(text=reference_text)
                        assert book_result == match.group('book'), \
                            '{text} does not provide the expected result for the book group.'\
                            .format(text=reference_text)
                        assert ranges_result == match.group('ranges'), \
                            '{text} does not provide the expected result for the ranges group.' \
                            .format(text=reference_text)


def test_reference_matched_range(mocked_bible_test):
    """
    Test that the 'range' regex parses bible verse references correctly.
    Note: This test takes in to account that the regex does not work quite as expected!
    see https://gitlab.com/openlp/openlp/issues/240
    """
    # GIVEN: Some test data which contains different references to parse, with the expected results.
    # The following test data tests with 45 variants when using the default 'separators'
    test_data = [
        ('23', None, '23', None, None, None),
        ('23{to}24', None, '23', '-24', None, '24'),
        ('23{verse}1{to}2', '23', '1', '-2', None, '2'),
        ('23{verse}1{to}{end}', '23', '1', '-end', None, None),
        ('23{verse}1{to}24{verse}1', '23', '1', '-24:1', '24', '1')]
    full_reference_match = get_reference_match('range')
    for reference_text, from_chapter, from_verse, range_to, to_chapter, to_verse in test_data:
        to_separators = ['-', ' - ', 'to', ' to '] if '{to}' in reference_text else ['']
        verse_separators = [':', ' : ', 'v', ' v ', 'V', ' V ', 'verse', ' verse ', 'verses', ' verses '] \
            if '{verse}' in reference_text else ['']
        and_separators = [',', ' , ', 'and', ' and '] if '{_and}' in reference_text else ['']
        end_separators = ['end', ' end '] if '{end}' in reference_text else ['']

        for to in to_separators:
            for verse in verse_separators:
                for _and in and_separators:
                    for end in end_separators:
                        reference_text = reference_text.format(to=to, verse=verse, _and=_and, end=end)

                        # WHEN: Attempting to parse the input string
                        match = full_reference_match.match(reference_text)

                        # THEN: A match should be returned, and the to/from chapter/verses should match as
                        #       expected
                        assert match is not None, '{text} should provide a match'.format(text=reference_text)
                        assert match.group('from_chapter') == from_chapter
                        assert match.group('from_verse') == from_verse
                        assert match.group('range_to') == range_to
                        assert match.group('to_chapter') == to_chapter
                        assert match.group('to_verse') == to_verse


def test_reference_matched_range_separator(mocked_bible_test):
    # GIVEN: Some test data which contains different references to parse, with the expected results.
    # The following test data tests with 111 variants when using the default 'separators'
    # The regex for handling ranges is a bit screwy, see https://gitlab.com/openlp/openlp/issues/240
    test_data = [
        ('23', ['23']),
        ('23{to}24', ['23-24']),
        ('23{verse}1{to}2', ['23:1-2']),
        ('23{verse}1{to}{end}', ['23:1-end']),
        ('23{verse}1{to}2{_and}5{to}6', ['23:1-2', '5-6']),
        ('23{verse}1{to}2{_and}5{to}{end}', ['23:1-2', '5-end']),
        ('23{verse}1{to}2{_and}24{verse}1{to}3', ['23:1-2', '24:1-3']),
        ('23{verse}1{to}{end}{_and}24{verse}1{to}{end}', ['23:1-end', '24:1-end']),
        ('23{verse}1{to}24{verse}1', ['23:1-24:1']),
        ('23,24', ['23', '24'])]
    full_reference_match = get_reference_match('range_separator')
    for reference_text, ranges in test_data:
        to_separators = ['-', ' - ', 'to', ' to '] if '{to}' in reference_text else ['']
        verse_separators = [':', ' : ', 'v', ' v ', 'V', ' V ', 'verse', ' verse ', 'verses', ' verses '] \
            if '{verse}' in reference_text else ['']
        and_separators = [',', ' , ', 'and', ' and '] if '{_and}' in reference_text else ['']
        end_separators = ['end', ' end '] if '{end}' in reference_text else ['']

        for to in to_separators:
            for verse in verse_separators:
                for _and in and_separators:
                    for end in end_separators:
                        reference_text = reference_text.format(to=to, verse=verse, _and=_and, end=end)

                        # WHEN: Attempting to parse the input string
                        references = full_reference_match.split(reference_text)

                        # THEN: The list of references should be as the expected results
                        assert references == ranges


def test_update_reference_separators_custom_seps(request, settings):
    """
    Test the update_reference_separators() function with custom separators
    """
    # Clean up after the test
    def cleanup_references():
        lib.REFERENCE_SEPARATORS = {}
        settings.remove('bibles/verse separator')
        settings.remove('bibles/range separator')
        settings.remove('bibles/list separator')
        settings.remove('bibles/end separator')
        update_reference_separators()

    request.addfinalizer(cleanup_references)

    # GIVEN: A custom set of separators
    settings.setValue('bibles/verse separator', ':||v')
    settings.setValue('bibles/range separator', '-')
    settings.setValue('bibles/list separator', ',')
    settings.setValue('bibles/end separator', '.')

    # WHEN: update_reference_separators() is called
    update_reference_separators()

    # THEN: The reference separators should be updated and correct
    expected_separators = {
        'sep_e': '\\s*(?:\\.)\\s*',
        'sep_e_default': 'end',
        'sep_l': '\\s*(?:(?:[,‚]))\\s*',
        'sep_l_default': ',|and',
        'sep_l_display': ',',
        'sep_r': '\\s*(?:(?:[-\xad‐‑‒——−﹣－]))\\s*',
        'sep_r_default': '-|to',
        'sep_r_display': '-',
        'sep_v': '\\s*(?::|v)\\s*',
        'sep_v_default': ':|v|V|verse|verses',
        'sep_v_display': ':'
    }
    assert lib.REFERENCE_SEPARATORS == expected_separators
