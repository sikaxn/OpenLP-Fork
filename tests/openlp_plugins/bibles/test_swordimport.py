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
This module contains tests for the SWORD Bible importer.
"""
from unittest import skipUnless
from unittest.mock import MagicMock, patch

from openlp.plugins.bibles.lib.db import BibleDB
from tests.utils import load_external_result_data
from tests.utils.constants import RESOURCE_PATH


try:
    from openlp.plugins.bibles.lib.importers.sword import SwordBible
    HAS_PYSWORD = True
except ImportError:
    HAS_PYSWORD = False


TEST_PATH = RESOURCE_PATH / 'bibles'


@skipUnless(HAS_PYSWORD, 'pysword not installed')
def test_create_importer(settings):
    """
    Test creating an instance of the Sword file importer
    """
    # GIVEN: A mocked out "manager"
    mocked_manager = MagicMock()

    # WHEN: An importer object is created
    importer = SwordBible(mocked_manager, path='.', name='.', file_path=None, sword_key='', sword_path='')

    # THEN: The importer should be an instance of BibleDB
    assert isinstance(importer, BibleDB)


@skipUnless(HAS_PYSWORD, 'pysword not installed')
@patch('openlp.plugins.bibles.lib.importers.sword.modules')
def test_simple_import(mocked_pysword_modules, settings):
    """
    Test that a simple SWORD import works
    """
    # GIVEN: Test files with a mocked out "manager", "import_wizard", and mocked functions
    #       get_book_ref_id_by_name, create_verse, create_book, session and get_language.
    #       Also mocked pysword structures
    mocked_manager = MagicMock()
    mocked_import_wizard = MagicMock()
    importer = SwordBible(mocked_manager, path='.', name='.', file_path=None, sword_key='', sword_path='')
    test_data = load_external_result_data(TEST_PATH / 'dk1933.json')
    importer.wizard = mocked_import_wizard
    importer.get_book_ref_id_by_name = MagicMock()
    importer.create_verse = MagicMock()
    importer.create_book = MagicMock()
    importer.session = MagicMock()
    importer.get_language = MagicMock(return_value='Danish')
    mocked_bible = MagicMock()
    mocked_genesis = MagicMock()
    mocked_genesis.name = 'Genesis'
    mocked_genesis.num_chapters = 1
    books = {'ot': [mocked_genesis]}
    mocked_structure = MagicMock()
    mocked_structure.get_books.return_value = books
    mocked_bible.get_structure.return_value = mocked_structure
    mocked_bible.get_iter.return_value = [verse[1] for verse in test_data['verses']]
    mocked_module = MagicMock()
    mocked_module.get_bible_from_module.return_value = mocked_bible
    mocked_pysword_modules.SwordModules.return_value = mocked_module

    # WHEN: Importing bible file
    importer.do_import()

    # THEN: The create_verse() method should have been called with each verse in the file.
    assert importer.create_verse.called is True
    for verse_tag, verse_text in test_data['verses']:
        importer.create_verse.assert_any_call(importer.create_book().id, 1, int(verse_tag), verse_text)
