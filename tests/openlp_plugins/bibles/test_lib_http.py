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
    Package to test the openlp.plugin.bible.lib.https package.
"""
import os
from unittest.mock import MagicMock

import pytest

from openlp.plugins.bibles.lib.importers.http import BGExtract, BSExtract, CWExtract


if not os.environ.get('OPENLP_RUN_HTTP_BIBLE_TESTS'):
    pytest.skip('Skip Bible HTTP tests to prevent GitLab CI from being blacklisted', allow_module_level=True)


@pytest.fixture
def bg_extract(settings, registry):
    """A fixture to return a BibleGateway extractor"""
    registry.register('service_list', MagicMock())
    registry.register('main_window', MagicMock())
    bg = BGExtract()
    yield bg


@pytest.fixture
def cw_extract(settings, registry):
    """A fixture to return a Crosswalk extractor"""
    registry.register('service_list', MagicMock())
    registry.register('main_window', MagicMock())
    cw = CWExtract()
    yield cw


@pytest.fixture
def bs_extract(settings, registry):
    """A fixture to return a BibleServer extractor"""
    registry.register('service_list', MagicMock())
    registry.register('main_window', MagicMock())
    bs = BSExtract()
    yield bs


def test_biblegateway_get_bibles(bg_extract):
    """
    Test getting list of bibles from BibleGateway.com
    """
    # GIVEN: A new Bible Gateway extraction class
    # WHEN: downloading bible list from Crosswalk
    bibles = bg_extract.get_bibles_from_http()

    # THEN: The list should not be None, and some known bibles should be there
    assert bibles is not None
    assert ('Holman Christian Standard Bible (HCSB)', 'HCSB', 'en') in bibles


def test_bible_gateway_extract_books(bg_extract):
    """
    Test the Bible Gateway retrieval of book list for NIV bible
    """
    # GIVEN: A new Bible Gateway extraction class
    # WHEN: The Books list is called
    books = bg_extract.get_books_from_http('NIV')

    # THEN: We should get back a valid service item
    assert len(books) == 66, 'The bible should not have had any books added or removed'
    assert books[0] == 'Genesis', 'The first bible book should be Genesis'


def test_bible_gateway_extract_books_support_redirect(bg_extract):
    """
    Test the Bible Gateway retrieval of book list for DN1933 bible with redirect (bug 1251437)
    """
    # GIVEN: A new Bible Gateway extraction class
    # WHEN: The Books list is called
    books = bg_extract.get_books_from_http('DN1933')

    # THEN: We should get back a valid service item
    assert len(books) == 66, 'This bible should have 66 books'


def test_bible_gateway_extract_verse(bg_extract):
    """
    Test the Bible Gateway retrieval of verse list for NIV bible John 3
    """
    # GIVEN: A new Bible Gateway extraction class
    # WHEN: The Books list is called
    results = bg_extract.get_bible_chapter('NIV', 'John', 3)

    # THEN: We should get back a valid service item
    assert len(results.verse_list) == 36, 'The book of John should not have had any verses added or removed'


def test_bible_gateway_extract_verse_nkjv(bg_extract):
    """
    Test the Bible Gateway retrieval of verse list for NKJV bible John 3
    """
    # GIVEN: A new Bible Gateway extraction class
    # WHEN: The Books list is called
    results = bg_extract.get_bible_chapter('NKJV', 'John', 3)

    # THEN: We should get back a valid service item
    assert len(results.verse_list) == 36, 'The book of John should not have had any verses added or removed'


def test_crosswalk_extract_books(cw_extract):
    """
    Test Crosswalk retrieval of book list for NIV bible
    """
    # GIVEN: A new Bible Gateway extraction class
    # WHEN: The Books list is called
    books = cw_extract.get_books_from_http('niv')

    # THEN: We should get back a valid service item
    assert len(books) == 66, 'The bible should not have had any books added or removed'


def test_crosswalk_extract_verse(cw_extract):
    """
    Test Crosswalk retrieval of verse list for NIV bible John 3
    """
    # GIVEN: A new Bible Gateway extraction class
    # WHEN: The Books list is called
    results = cw_extract.get_bible_chapter('niv', 'john', 3)

    # THEN: We should get back a valid service item
    assert len(results.verse_list) == 36, 'The book of John should not have had any verses added or removed'


def test_crosswalk_get_bibles(cw_extract):
    """
    Test getting list of bibles from Crosswalk.com
    """
    # GIVEN: A new Crosswalk extraction class
    # WHEN: downloading bible list from Crosswalk
    bibles = cw_extract.get_bibles_from_http()

    # THEN: The list should not be None, and some known bibles should be there
    assert bibles is not None
    assert ('Giovanni Diodati 1649 (Italian)', 'gdb', 'it') in bibles


def test_crosswalk_get_verse_text(cw_extract):
    """
    Test verse text from Crosswalk.com
    """
    # GIVEN: A new Crosswalk extraction class
    # WHEN: downloading NIV Genesis from Crosswalk
    niv_genesis_chapter_one = cw_extract.get_bible_chapter('niv', 'Genesis', 1)

    # THEN: The verse list should contain the verses
    assert niv_genesis_chapter_one.has_verse_list() is True
    assert 'In the beginning God created the heavens and the earth.' == niv_genesis_chapter_one.verse_list[1], \
        'The first chapter of genesis should have been fetched.'


def test_bibleserver_get_bibles(bs_extract):
    """
    Test getting list of bibles from BibleServer.com
    """
    # GIVEN: A new Bible Server extraction class
    # WHEN: downloading bible list from bibleserver
    bibles = bs_extract.get_bibles_from_http()

    # THEN: The list should not be None, and some known bibles should be there
    assert bibles is not None
    assert ('New Int. Readers Version', 'NIRV', 'en') in bibles
    assert ('Священное Писание, Восточный перевод', 'CARS', 'ru') in bibles


def test_bibleserver_get_verse_text(bs_extract):
    """
    Test verse text from bibleserver.com
    """
    # GIVEN: A new Crosswalk extraction class
    # WHEN: downloading NIV Genesis from Crosswalk
    niv_genesis_chapter_one = bs_extract.get_bible_chapter('NIV', 'Genesis', 1)

    # THEN: The verse list should contain the verses
    assert niv_genesis_chapter_one.has_verse_list() is True
    assert 'In the beginning God created the heavens and the earth.' == niv_genesis_chapter_one.verse_list[1], \
        'The first chapter of genesis should have been fetched.'


def test_bibleserver_get_chapter_with_bridged_verses(bs_extract):
    """
    Test verse text from bibleserver.com
    """
    # GIVEN: A new Crosswalk extraction class
    # WHEN: downloading PCB Genesis from BibleServer
    pcb_genesis_chapter_one = bs_extract.get_bible_chapter('PCB', 'Genesis', 1)

    # THEN: The verse list should contain the verses
    assert pcb_genesis_chapter_one.has_verse_list() is True
    assert 7 in pcb_genesis_chapter_one.verse_list
    assert 8 not in pcb_genesis_chapter_one.verse_list
