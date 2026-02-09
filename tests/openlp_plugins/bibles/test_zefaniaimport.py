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
This module contains tests for the Zefania Bible importer.
"""
from unittest.mock import MagicMock, patch

from openlp.plugins.bibles.lib.db import BibleDB
from openlp.plugins.bibles.lib.importers.zefania import ZefaniaBible
from tests.utils import load_external_result_data
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'bibles'


def test_create_importer(settings):
    """
    Test creating an instance of the Zefania file importer
    """
    # GIVEN: A mocked out "manager"
    mocked_manager = MagicMock()

    # WHEN: An importer object is created
    importer = ZefaniaBible(mocked_manager, path='.', name='.', file_path=None)

    # THEN: The importer should be an instance of BibleDB
    assert isinstance(importer, BibleDB)


def test_file_import(settings):
    """
    Test the actual import of Zefania Bible file
    """
    # GIVEN: Test files with a mocked out "manager", "import_wizard", and mocked functions
    #        get_book_ref_id_by_name, create_verse, create_book, session and get_language.
    test_data = load_external_result_data(TEST_PATH / 'dk1933.json')
    bible_file = 'zefania-dk1933.xml'
    with patch('openlp.plugins.bibles.lib.importers.zefania.ZefaniaBible.application'):
        mocked_manager = MagicMock()
        mocked_import_wizard = MagicMock()
        importer = ZefaniaBible(mocked_manager, path='.', name='.', file_path=None)
        importer.wizard = mocked_import_wizard
        importer.create_verse = MagicMock()
        importer.create_book = MagicMock()
        importer.session = MagicMock()
        importer.get_language = MagicMock()
        importer.get_language.return_value = 'Danish'

        # WHEN: Importing bible file
        importer.file_path = TEST_PATH / bible_file
        importer.do_import()

        # THEN: The create_verse() method should have been called with each verse in the file.
        assert importer.create_verse.called is True
        for verse_tag, verse_text in test_data['verses']:
            importer.create_verse.assert_any_call(importer.create_book().id, 1, verse_tag, verse_text)
        importer.create_book.assert_any_call('Genesis', 1, 1)


def test_file_import_no_book_name(settings):
    """
    Test the import of Zefania Bible file without book names
    """
    # GIVEN: Test files with a mocked out "manager", "import_wizard", and mocked functions
    #        get_book_ref_id_by_name, create_verse, create_book, session and get_language.
    test_data = load_external_result_data(TEST_PATH / 'rst.json')
    bible_file = 'zefania-rst.xml'
    with patch('openlp.plugins.bibles.lib.importers.zefania.ZefaniaBible.application'):
        mocked_manager = MagicMock()
        mocked_import_wizard = MagicMock()
        importer = ZefaniaBible(mocked_manager, path='.', name='.', file_path=None)
        importer.wizard = mocked_import_wizard
        importer.create_verse = MagicMock()
        importer.create_book = MagicMock()
        importer.session = MagicMock()
        importer.get_language = MagicMock()
        importer.get_language.return_value = 'Russian'

        # WHEN: Importing bible file
        importer.file_path = TEST_PATH / bible_file
        importer.do_import()

        # THEN: The create_verse() method should have been called with each verse in the file.
        assert importer.create_verse.called is True
        for verse_tag, verse_text in test_data['verses']:
            importer.create_verse.assert_any_call(importer.create_book().id, 1, verse_tag, verse_text)
        importer.create_book.assert_any_call('Exodus', 2, 1)
