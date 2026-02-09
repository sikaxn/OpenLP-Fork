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
This module contains tests for the CSV Bible importer.
"""
import csv
import pytest
from collections import namedtuple
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, call, patch

from openlp.core.lib.exceptions import ValidationError
from openlp.plugins.bibles.lib.bibleimport import BibleImport
from openlp.plugins.bibles.lib.importers.csvbible import Book, CSVBible, CSVBibleFileType, Verse, _has_header
from tests.utils import load_external_result_data
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'bibles'


def test_create_importer(settings):
    """
    Test creating an instance of the CSV file importer
    """
    # GIVEN: A mocked out "manager"
    mocked_manager = MagicMock()

    # WHEN: An importer object is created
    importer = \
        CSVBible(mocked_manager, path='.', name='.', books_path=Path('books.csv'), verse_path=Path('verse.csv'))

    # THEN: The importer should be an instance of BibleImport
    assert isinstance(importer, BibleImport)
    assert importer.books_path == Path('books.csv')
    assert importer.verses_path == Path('verse.csv')


def test_book_namedtuple():
    """
    Test that the Book namedtuple is created as expected
    """
    # GIVEN: The Book namedtuple
    # WHEN: Creating an instance of Book
    result = Book('id', 'testament_id', 'name', 'abbreviation')

    # THEN: The attributes should match up with the data we used
    assert result.id == 'id'
    assert result.testament_id == 'testament_id'
    assert result.name == 'name'
    assert result.abbreviation == 'abbreviation'


def test_verse_namedtuple():
    """
    Test that the Verse namedtuple is created as expected
    """
    # GIVEN: The Verse namedtuple
    # WHEN: Creating an instance of Verse
    result = Verse('book_id_name', 'chapter_number', 'number', 'text')

    # THEN: The attributes should match up with the data we used
    assert result.book_id_name == 'book_id_name'
    assert result.chapter_number == 'chapter_number'
    assert result.number == 'number'
    assert result.text == 'text'


def test_get_book_name_id():
    """
    Test that get_book_name() returns the correct book when called with an id
    """
    # GIVEN: A dictionary of books with their id as the keys
    books = {1: 'Book 1', 2: 'Book 2', 3: 'Book 3'}

    # WHEN: Calling get_book_name() and the name is an integer represented as a string
    test_data = [['1', 'Book 1'], ['2', 'Book 2'], ['3', 'Book 3']]
    for name, expected_result in test_data:
        actual_result = CSVBible.get_book_name(name, books)

        # THEN: get_book_name() should return the book name associated with that id from the books dictionary
        assert actual_result == expected_result


def test_get_book_name():
    """
    Test that get_book_name() returns the name when called with a non integer value
    """
    # GIVEN: A dictionary of books with their id as the keys
    books = {1: 'Book 1', 2: 'Book 2', 3: 'Book 3'}

    # WHEN: Calling get_book_name() and the name is not an integer represented as a string
    test_data = [['Book 4', 'Book 4'], ['Book 5', 'Book 5'], ['Book 6', 'Book 6']]
    for name, expected_result in test_data:
        actual_result = CSVBible.get_book_name(name, books)

        # THEN: get_book_name() should return the input
        assert actual_result == expected_result


def test_parse_csv_file():
    """
    Test the parse_csv_file() with sample data
    """
    # GIVEN: A mocked csv.reader which returns an iterator with test data
    test_data = [['1', '1', 'name 1', 'abbrev 1'], ['2', '2', 'name 2', 'abbrev 2'], ['3', '3', 'name 3', 'abbrev 3']]
    TestTuple = namedtuple('TestTuple', 'line_no line_id name abbrev')
    mocked_csv_file = MagicMock()
    mocked_enter_file = MagicMock()
    mocked_csv_file.open.return_value.__enter__.return_value = mocked_enter_file

    with patch('openlp.plugins.bibles.lib.importers.csvbible.get_file_encoding', return_value='utf-8'), \
            patch('openlp.plugins.bibles.lib.importers.csvbible.reader',
                  return_value=iter(test_data)) as mocked_reader, \
            patch('openlp.plugins.bibles.lib.importers.csvbible._has_header') as mocked_has_header:
        mocked_has_header.return_value = False

        # WHEN: Calling the CSVBible parse_csv_file method with a file name and TestTuple
        result = CSVBible.parse_csv_file(mocked_csv_file, TestTuple, CSVBibleFileType.Book)

        # THEN: A list of TestTuple instances with the parsed data should be returned
        assert result == [TestTuple('1', '1', 'name 1', 'abbrev 1'), TestTuple('2', '2', 'name 2', 'abbrev 2'),
                          TestTuple('3', '3', 'name 3', 'abbrev 3')]
        mocked_csv_file.open.assert_called_once_with('r', encoding='utf-8', newline='')
        mocked_reader.assert_called_once_with(mocked_enter_file, delimiter=',', quotechar='"')


def test_has_header():
    """
    Test the _has_header() with sample data
    """
    # GIVEN: A mocked csv.reader which returns an iterator with test data
    test_data = """<book_id>,<testament_id>,<book_name>,<abbreviation>
1,1,Genesis,Gen
"""

    # WHEN: Sample data is given to _has_header()
    result = _has_header(test_data, CSVBibleFileType.Book)

    # THEN: The result should be true
    assert result is True


def test_has_no_header():
    """
    Test the _has_header() with sample data that does not have a header
    """
    # GIVEN: A mocked csv.reader which returns an iterator with test data
    test_data = """1,1,Genesis,Gen
2,1,Exodus,Exo
"""

    # WHEN: Sample data is given to _has_header()
    result = _has_header(test_data, CSVBibleFileType.Book)

    # THEN: The result should be true
    assert result is False


def test_parse_csv_file_oserror():
    """
    Test the parse_csv_file() handles an OSError correctly
    """
    # GIVEN: Mocked a mocked open object which raises an OSError
    mocked_csv_file = MagicMock()
    mocked_csv_file.__str__.return_value = 'file.csv'
    mocked_csv_file.open.side_effect = OSError()

    with patch('openlp.plugins.bibles.lib.importers.csvbible.get_file_encoding',
               return_value={'encoding': 'utf-8', 'confidence': 0.99}):

        # WHEN: Calling CSVBible.parse_csv_file
        # THEN: A ValidationError should be raised
        with pytest.raises(ValidationError) as context:
            CSVBible.parse_csv_file(mocked_csv_file, None, CSVBibleFileType.Book)
        assert context.value != ValidationError('Parsing "file.csv" failed')


def test_parse_csv_file_csverror():
    """
    Test the parse_csv_file() handles an csv.Error correctly
    """
    # GIVEN: Mocked a csv.reader which raises an csv.Error
    mocked_csv_file = MagicMock()
    mocked_csv_file.__str__.return_value = 'file.csv'

    with patch('openlp.plugins.bibles.lib.importers.csvbible.get_file_encoding',
               return_value={'encoding': 'utf-8', 'confidence': 0.99}), \
            patch('openlp.plugins.bibles.lib.importers.csvbible.reader', side_effect=csv.Error):

        # WHEN: Calling CSVBible.parse_csv_file
        # THEN: A ValidationError should be raised
        with pytest.raises(ValidationError) as context:
            CSVBible.parse_csv_file(mocked_csv_file, None, CSVBibleFileType.Book)
        assert context.value != ValidationError('Parsing "file.csv" failed')


def test_process_books_stopped_import(registry):
    """
    Test process books when the import is stopped
    """
    # GIVEN: An instance of CSVBible with the stop_import_flag set to True
    mocked_manager = MagicMock()
    with patch('openlp.plugins.bibles.lib.bibleimport.BibleDB._setup'):
        importer = CSVBible(mocked_manager, path='.', name='.', books_path=Path('books.csv'),
                            verse_path=Path('verse.csv'))
        type(importer).application = PropertyMock()
        importer.stop_import_flag = True
        importer.wizard = MagicMock()

        # WHEN: Calling process_books
        result = importer.process_books(['Book 1'])

        # THEN: increment_progress_bar should not be called and the return value should be an empty dictionary
        assert importer.wizard.increment_progress_bar.called is False
        assert result == {}


def test_process_books(registry):
    """
    Test process books when it completes successfully
    """
    # GIVEN: An instance of CSVBible with the stop_import_flag set to False, and some sample data
    mocked_manager = MagicMock()
    with patch('openlp.plugins.bibles.lib.bibleimport.BibleDB._setup'), \
            patch('openlp.plugins.bibles.lib.importers.csvbible.translate'):
        importer = CSVBible(mocked_manager, path='.', name='.', books_path=Path('books.csv'),
                            verse_path=Path('verse.csv'))
        importer.find_and_create_book = MagicMock()
        importer.language_id = 10
        importer.stop_import_flag = False
        importer.wizard = MagicMock()

        books = [Book('1', '1', '1. Mosebog', '1Mos'), Book('2', '1', '2. Mosebog', '2Mos')]

        # WHEN: Calling process_books
        result = importer.process_books(books)

        # THEN: translate and find_and_create_book should have been called with both book names.
        # 		The returned data should be a dictionary with both song's id and names.
        assert importer.find_and_create_book.mock_calls == \
            [call('1. Mosebog', 2, 10), call('2. Mosebog', 2, 10)]
        assert result == {1: '1. Mosebog', 2: '2. Mosebog'}


def test_process_verses_stopped_import(registry):
    """
    Test process_verses when the import is stopped
    """
    # GIVEN: An instance of CSVBible with the stop_import_flag set to True
    mocked_manager = MagicMock()
    with patch('openlp.plugins.bibles.lib.bibleimport.BibleDB._setup'):
        importer = CSVBible(mocked_manager, path='.', name='.', books_path=Path('books.csv'),
                            verse_path=Path('verse.csv'))
        importer.get_book_name = MagicMock()
        importer.session = MagicMock()
        importer.stop_import_flag = True
        importer.wizard = MagicMock()

        # WHEN: Calling process_verses
        result = importer.process_verses(['Dummy Verse'], [])

        # THEN: get_book_name should not be called and the return value should be None
        assert importer.get_book_name.called is False
        assert result is None


def test_process_verses_successful(registry):
    """
    Test process_verses when the import is successful
    """
    # GIVEN: An instance of CSVBible with the application and wizard attributes mocked out, and some test data.
    mocked_manager = MagicMock()
    with patch('openlp.plugins.bibles.lib.bibleimport.BibleDB._setup'), \
            patch('openlp.plugins.bibles.lib.importers.csvbible.translate'):
        importer = CSVBible(mocked_manager, path='.', name='.', books_path=Path('books.csv'),
                            verse_path=Path('verse.csv'))
        importer.create_verse = MagicMock()
        importer.get_book = MagicMock(return_value=Book('1', '1', '1. Mosebog', '1Mos'))
        importer.get_book_name = MagicMock(return_value='1. Mosebog')
        importer.session = MagicMock()
        importer.stop_import_flag = False
        importer.wizard = MagicMock()
        verses = [Verse(1, 1, 1, 'I Begyndelsen skabte Gud Himmelen og Jorden.'),
                  Verse(1, 1, 2, 'Og Jorden var øde og tom, og der var Mørke over Verdensdybet. '
                                 'Men Guds Ånd svævede over Vandene.')]
        books = {1: '1. Mosebog'}

        # WHEN: Calling process_verses
        importer.process_verses(verses, books)

        # THEN: create_verse is called with the test data
        assert importer.get_book_name.mock_calls == [call(1, books), call(1, books)]
        importer.get_book.assert_called_once_with('1. Mosebog')
        assert importer.session.commit.call_count == 2
        assert importer.create_verse.mock_calls == \
            [call('1', 1, 1, 'I Begyndelsen skabte Gud Himmelen og Jorden.'),
             call('1', 1, 2, 'Og Jorden var øde og tom, og der var Mørke over Verdensdybet. '
                             'Men Guds Ånd svævede over Vandene.')]


def test_do_import_invalid_language_id(registry):
    """
    Test do_import when the user cancels the language selection dialog box
    """
    # GIVEN: An instance of CSVBible and a mocked get_language which simulates the user cancelling the language box
    mocked_manager = MagicMock()
    with patch('openlp.plugins.bibles.lib.bibleimport.BibleDB._setup'):
        importer = CSVBible(mocked_manager, path='.', name='.', books_path=Path('books.csv'),
                            verse_path=Path('verse.csv'))
        importer.get_language = MagicMock(return_value=None)

        # WHEN: Calling do_import
        result = importer.do_import('Bible Name')

        # THEN: The False should be returned.
        importer.get_language.assert_called_once_with('Bible Name')
        assert result is False


def test_do_import_success(registry):
    """
    Test do_import when the import succeeds
    """
    # GIVEN: An instance of CSVBible
    mocked_manager = MagicMock()
    with patch('openlp.plugins.bibles.lib.bibleimport.BibleDB._setup'):
        importer = CSVBible(mocked_manager, path='.', name='.', books_path=Path('books.csv'),
                            verse_path=Path('verses.csv'))
        importer.get_language = MagicMock(return_value=10)
        importer.parse_csv_file = MagicMock(side_effect=[['Book 1'], ['Verse 1']])
        importer.process_books = MagicMock(return_value=['Book 1'])
        importer.process_verses = MagicMock(return_value=['Verse 1'])
        importer.session = MagicMock()
        importer.stop_import_flag = False
        importer.wizard = MagicMock()

        # WHEN: Calling do_import
        result = importer.do_import('Bible Name')

        # THEN: parse_csv_file should be called twice,
        # and True should be returned.
        assert importer.parse_csv_file.mock_calls == \
            [call(Path('books.csv'), Book, CSVBibleFileType.Book),
             call(Path('verses.csv'), Verse, CSVBibleFileType.Verse)]
        importer.process_books.assert_called_once_with(['Book 1'])
        importer.process_verses.assert_called_once_with(['Verse 1'], ['Book 1'])
        assert result is True


def test_file_import(settings):
    """
    Test the actual import of CSV Bible file
    """
    # GIVEN: Test files with a mocked out "manager", "import_wizard", and mocked functions
    #        get_book_ref_id_by_name, create_verse, create_book, session and get_language.
    test_data = load_external_result_data(TEST_PATH / 'dk1933.json')
    books_file = TEST_PATH / 'dk1933-books.csv'
    verses_file = TEST_PATH / 'dk1933-verses.csv'
    with patch('openlp.plugins.bibles.lib.importers.csvbible.CSVBible.application'):
        mocked_manager = MagicMock()
        mocked_import_wizard = MagicMock()
        importer = CSVBible(mocked_manager, path='.', name='.', books_path=books_file, verse_path=verses_file)
        importer.wizard = mocked_import_wizard
        importer.get_book_ref_id_by_name = MagicMock()
        importer.create_verse = MagicMock()
        importer.create_book = MagicMock()
        importer.session = MagicMock()
        importer.get_language = MagicMock()
        importer.get_language.return_value = 'Danish'
        importer.get_book = MagicMock()

        # WHEN: Importing bible file
        importer.do_import()

        # THEN: The create_verse() method should have been called with each verse in the file.
        assert importer.create_verse.called is True
        for verse_tag, verse_text in test_data['verses']:
            importer.create_verse.assert_any_call(importer.get_book().id, 1, verse_tag, verse_text)
        importer.create_book.assert_any_call('1. Mosebog', importer.get_book_ref_id_by_name(), 1)
        importer.create_book.assert_any_call('1. Krønikebog', importer.get_book_ref_id_by_name(), 1)
