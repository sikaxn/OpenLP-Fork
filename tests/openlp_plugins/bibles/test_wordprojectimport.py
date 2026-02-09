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
This module contains tests for the WordProject Bible importer.
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from openlp.plugins.bibles.lib.importers.wordproject import WordProjectBible
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'bibles'
INDEX_PAGE = (TEST_PATH / 'wordproject_index.htm').read_bytes().decode()
CHAPTER_PAGE = (TEST_PATH / 'wordproject_chapter.htm').read_bytes().decode()
CORRUPTED_CHAPTER_PAGE = (TEST_PATH / 'wordproject_chapter_corrupted.htm').read_bytes().decode()


@patch.object(Path, 'read_text')
@patch.object(Path, 'exists')
def test_process_books(mocked_exists, mocked_read_text, settings):
    """
    Test the process_books() method
    """
    # GIVEN: A WordProject importer and a bunch of mocked things
    importer = WordProjectBible(MagicMock(), path='.', name='.', file_path=Path('kj.zip'))
    importer.base_path = Path()
    importer.stop_import_flag = False
    importer.language_id = 'en'
    mocked_read_text.return_value = INDEX_PAGE
    mocked_exists.return_value = True

    # WHEN: process_books() is called
    with patch.object(importer, '_unzip_file') as mocked_unzip_file, \
            patch.object(importer, 'find_and_create_book') as mocked_find_and_create_book, \
            patch.object(importer, 'process_chapters') as mocked_process_chapters, \
            patch.object(importer, 'session') as mocked_session:
        mocked_unzip_file.return_value = True
        importer.process_books()

    # THEN: The right methods should have been called
    mocked_read_text.assert_called_once_with(encoding='utf-8', errors='ignore')
    assert mocked_find_and_create_book.call_count == 66, 'There should be 66 books'
    assert mocked_process_chapters.call_count == 66, 'There should be 66 books'
    assert mocked_session.commit.call_count == 66, 'There should be 66 books'


@patch.object(Path, 'read_text')
def test_process_chapters(mocked_read_text, settings):
    """
    Test the process_chapters() method
    """
    # GIVEN: A WordProject importer and a bunch of mocked things
    importer = WordProjectBible(MagicMock(), path='.', name='.', file_path=Path('kj.zip'))
    importer.base_path = Path()
    importer.stop_import_flag = False
    importer.language_id = 'en'
    mocked_read_text.return_value = CHAPTER_PAGE
    mocked_db_book = MagicMock()
    mocked_db_book.name = 'Genesis'
    book_id = 1
    book_link = '01/1.htm'

    # WHEN: process_chapters() is called
    with patch.object(importer, 'set_current_chapter') as mocked_set_current_chapter, \
            patch.object(importer, 'process_verses') as mocked_process_verses:
        importer.process_chapters(mocked_db_book, book_id, book_link)

    # THEN: The right methods should have been called
    expected_set_current_chapter_calls = [call('Genesis', ch) for ch in range(1, 51)]
    expected_process_verses_calls = [call(mocked_db_book, 1, ch) for ch in range(1, 51)]
    mocked_read_text.assert_called_once_with(encoding='utf-8', errors='ignore')
    assert mocked_set_current_chapter.call_args_list == expected_set_current_chapter_calls
    assert mocked_process_verses.call_args_list == expected_process_verses_calls


@patch.object(Path, 'read_text')
def test_process_chapters_corrupted_header(mocked_read_text, settings):
    """
    Test the process_chapters() method when there's a "corrupted" header with a span instead of a p
    """
    # GIVEN: A WordProject importer and a bunch of mocked things
    importer = WordProjectBible(MagicMock(), path='.', name='.', file_path=Path('kj.zip'))
    importer.base_path = Path()
    importer.stop_import_flag = False
    importer.language_id = 'en'
    mocked_read_text.return_value = CORRUPTED_CHAPTER_PAGE
    mocked_db_book = MagicMock()
    mocked_db_book.name = 'Genesis'
    book_id = 1
    book_link = '01/1.htm'

    # WHEN: process_chapters() is called
    with patch.object(importer, 'set_current_chapter') as mocked_set_current_chapter, \
            patch.object(importer, 'process_verses') as mocked_process_verses:
        importer.process_chapters(mocked_db_book, book_id, book_link)

    # THEN: The right methods should have been called
    expected_set_current_chapter_calls = [call('Genesis', ch) for ch in range(1, 51)]
    expected_process_verses_calls = [call(mocked_db_book, 1, ch) for ch in range(1, 51)]
    mocked_read_text.assert_called_once_with(encoding='utf-8', errors='ignore')
    assert mocked_set_current_chapter.call_args_list == expected_set_current_chapter_calls
    assert mocked_process_verses.call_args_list == expected_process_verses_calls


@patch.object(Path, 'read_text')
def test_process_verses(mocked_read_text, settings):
    """
    Test the process_verses() method
    """
    # GIVEN: A WordProject importer and a bunch of mocked things
    importer = WordProjectBible(MagicMock(), path='.', name='.', file_path=Path('kj.zip'))
    importer.base_path = Path()
    importer.stop_import_flag = False
    importer.language_id = 'en'
    mocked_read_text.return_value = CHAPTER_PAGE
    mocked_db_book = MagicMock()
    mocked_db_book.name = 'Genesis'
    book_number = 1
    chapter_number = 1

    # WHEN: process_verses() is called
    with patch.object(importer, 'process_verse') as mocked_process_verse:
        importer.process_verses(mocked_db_book, book_number, chapter_number)

    # THEN: All the right methods should have been called
    mocked_read_text.assert_called_once_with(encoding='utf-8', errors='ignore')
    assert mocked_process_verse.call_count == 31


def test_process_verse(settings):
    """
    Test the process_verse() method
    """
    # GIVEN: An importer and a mocked method
    importer = WordProjectBible(MagicMock(), path='.', name='.', file_path=Path('kj.zip'))
    mocked_db_book = MagicMock()
    mocked_db_book.id = 1
    chapter_number = 1
    verse_number = 1
    verse_text = '  In the beginning, God created the heavens and the earth   '

    # WHEN: process_verse() is called
    with patch.object(importer, 'create_verse') as mocked_create_verse:
        importer.process_verse(mocked_db_book, chapter_number, verse_number, verse_text)

    # THEN: The create_verse() method should have been called
    mocked_create_verse.assert_called_once_with(1, 1, 1, 'In the beginning, God created the heavens and the earth')


def test_process_verse_no_text(settings):
    """
    Test the process_verse() method when there's no text
    """
    # GIVEN: An importer and a mocked method
    importer = WordProjectBible(MagicMock(), path='.', name='.', file_path=Path('kj.zip'))
    mocked_db_book = MagicMock()
    mocked_db_book.id = 1
    chapter_number = 1
    verse_number = 1
    verse_text = ''

    # WHEN: process_verse() is called
    with patch.object(importer, 'create_verse') as mocked_create_verse:
        importer.process_verse(mocked_db_book, chapter_number, verse_number, verse_text)

    # THEN: The create_verse() method should NOT have been called
    assert mocked_create_verse.call_count == 0


def test_do_import(settings):
    """
    Test the do_import() method
    """
    # GIVEN: An importer and mocked methods
    importer = WordProjectBible(MagicMock(), path='.', name='.', file_path='kj.zip')

    # WHEN: do_import() is called
    with patch.object(importer, '_unzip_file') as mocked_unzip_file, \
            patch.object(importer, 'get_language_id') as mocked_get_language_id, \
            patch.object(importer, 'process_books') as mocked_process_books, \
            patch.object(importer, '_cleanup') as mocked_cleanup:
        mocked_unzip_file.return_value = True
        mocked_process_books.return_value = True
        mocked_get_language_id.return_value = 1
        result = importer.do_import()

    # THEN: The correct methods should have been called
    mocked_unzip_file.assert_called_once_with()
    mocked_get_language_id.assert_called_once_with(None, bible_name='kj.zip')
    mocked_process_books.assert_called_once_with()
    mocked_cleanup.assert_called_once_with()
    assert result is True


def test_do_import_no_language(settings):
    """
    Test the do_import() method when the language is not available
    """
    # GIVEN: An importer and mocked methods
    importer = WordProjectBible(MagicMock(), path='.', name='.', file_path='kj.zip')

    # WHEN: do_import() is called
    with patch.object(importer, '_unzip_file') as mocked_unzip_file, \
            patch.object(importer, 'get_language_id') as mocked_get_language_id, \
            patch.object(importer, 'process_books') as mocked_process_books, \
            patch.object(importer, '_cleanup') as mocked_cleanup:
        mocked_get_language_id.return_value = None
        result = importer.do_import()

    # THEN: The correct methods should have been called
    mocked_unzip_file.assert_called_once_with()
    mocked_get_language_id.assert_called_once_with(None, bible_name='kj.zip')
    assert mocked_process_books.call_count == 0
    mocked_cleanup.assert_called_once_with()
    assert result is False


@pytest.mark.parametrize('input_, output', [
    ('1', 1),
    ('02.', 2),
    ('3-4', 3),
    ('exodus', None)
])
def test_get_number(input_: str, output: int, settings):
    importer = WordProjectBible(MagicMock(), path='.', name='.', file_path='dummy.zip')
    assert importer.get_number(input_) == output
