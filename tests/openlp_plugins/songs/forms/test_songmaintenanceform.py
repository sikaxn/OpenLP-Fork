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
Package to test the openlp.plugins.songs.forms.songmaintenanceform package.
"""
import pytest
import os

from unittest.mock import MagicMock, call, create_autospec, patch, ANY

from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import UiStrings
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.db.manager import DBManager
from openlp.plugins.songs.lib.db import init_schema, Author, AuthorSong, SongBook, Song, SongBookEntry
from openlp.plugins.songs.forms.songmaintenanceform import SongMaintenanceForm

from sqlalchemy.sql import and_


@pytest.fixture()
def db_manager() -> MagicMock():
    return MagicMock()


@pytest.fixture()
def maintenance_form(registry: Registry, settings: Settings, db_manager: MagicMock) -> SongMaintenanceForm:
    main_window = QtWidgets.QMainWindow()
    registry.register('main_window', main_window)
    frm = SongMaintenanceForm(db_manager)
    yield frm
    del frm
    del main_window


def test_constructor(db_manager: MagicMock, maintenance_form: SongMaintenanceForm):
    """
    Test that a SongMaintenanceForm is created successfully
    """
    # GIVEN: A SongMaintenanceForm
    # WHEN: The form is created
    # THEN: It should have some of the right components
    assert maintenance_form is not None
    assert maintenance_form.manager is db_manager


@patch('openlp.plugins.songs.forms.songmaintenanceform.QtWidgets.QDialog.exec')
def test_exec(mocked_exec: MagicMock, maintenance_form: SongMaintenanceForm):
    """
    Test the song maintenance form being executed
    """
    # GIVEN: A song maintenance form
    mocked_exec.return_value = True

    # WHEN: The song mainetnance form is executed
    with patch.object(maintenance_form, 'type_list_widget') as mocked_type_list_widget, \
            patch.object(maintenance_form, 'reset_authors') as mocked_reset_authors, \
            patch.object(maintenance_form, 'reset_topics') as mocked_reset_topics, \
            patch.object(maintenance_form, 'reset_song_books') as mocked_reset_song_books:
        result = maintenance_form.exec(from_song_edit=True)

    # THEN: The correct methods should have been called
    assert maintenance_form.from_song_edit is True
    mocked_type_list_widget.setCurrentRow.assert_called_once_with(0)
    mocked_reset_authors.assert_called_once_with()
    mocked_reset_topics.assert_called_once_with()
    mocked_reset_song_books.assert_called_once_with()
    mocked_type_list_widget.setFocus.assert_called_once_with()
    mocked_exec.assert_called_once_with(maintenance_form)
    assert result is True


def test_get_current_item_id_no_item(maintenance_form: SongMaintenanceForm):
    """
    Test _get_current_item_id() when there's no item
    """
    # GIVEN: A song maintenance form without a selected item
    mocked_list_widget = MagicMock()
    mocked_list_widget.currentItem.return_value = None

    # WHEN: _get_current_item_id() is called
    result = maintenance_form._get_current_item_id(mocked_list_widget)

    # THEN: The result should be -1
    mocked_list_widget.currentItem.assert_called_once_with()
    assert result == -1


def test_get_current_item_id(maintenance_form: SongMaintenanceForm):
    """
    Test _get_current_item_id() when there's a valid item
    """
    # GIVEN: A song maintenance form with a selected item
    mocked_item = MagicMock()
    mocked_item.data.return_value = 7
    mocked_list_widget = MagicMock()
    mocked_list_widget.currentItem.return_value = mocked_item

    # WHEN: _get_current_item_id() is called
    result = maintenance_form._get_current_item_id(mocked_list_widget)

    # THEN: The result should be -1
    mocked_list_widget.currentItem.assert_called_once_with()
    mocked_item.data.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole)
    assert result == 7


@patch('openlp.plugins.songs.forms.songmaintenanceform.critical_error_message_box')
def test_delete_item_no_item_id(mocked_critical_error_message_box: MagicMock, maintenance_form: SongMaintenanceForm):
    """
    Test the _delete_item() method when there is no item selected
    """
    # GIVEN: Some mocked items
    maintenance_form.manager.get_object.return_value = None
    mocked_list_widget = MagicMock()
    mocked_reset_func = MagicMock()
    dialog_title = 'Delete Item'
    delete_text = 'Are you sure you want to delete this item?'
    error_text = 'There was a problem deleting this item'

    # WHEN: _delete_item() is called
    with patch.object(maintenance_form, '_get_current_item_id') as mocked_get_current_item_id:
        mocked_get_current_item_id.return_value = -1
        maintenance_form._delete_item(SongBook, mocked_list_widget, mocked_reset_func, dialog_title, delete_text,
                                      error_text)

    # THEN: The right things should have been called
    mocked_get_current_item_id.assert_called_once_with(mocked_list_widget)
    mocked_critical_error_message_box.assert_called_once_with(dialog_title, UiStrings().NISs)


@patch('openlp.plugins.songs.forms.songmaintenanceform.critical_error_message_box')
def test_delete_item_invalid_item(mocked_critical_error_message_box: MagicMock, maintenance_form: SongMaintenanceForm):
    """
    Test the _delete_item() method when the item doesn't exist in the database
    """
    # GIVEN: Some mocked items
    maintenance_form.manager.get_object.return_value = None
    mocked_list_widget = MagicMock()
    mocked_reset_func = MagicMock()
    dialog_title = 'Delete Item'
    delete_text = 'Are you sure you want to delete this item?'
    error_text = 'There was a problem deleting this item'

    # WHEN: _delete_item() is called
    with patch.object(maintenance_form, '_get_current_item_id') as mocked_get_current_item_id:
        mocked_get_current_item_id.return_value = 1
        maintenance_form._delete_item(SongBook, mocked_list_widget, mocked_reset_func, dialog_title, delete_text,
                                      error_text)

    # THEN: The right things should have been called
    mocked_get_current_item_id.assert_called_once_with(mocked_list_widget)
    maintenance_form.manager.get_object.assert_called_once_with(SongBook, 1)
    mocked_critical_error_message_box.assert_called_once_with(dialog_title, error_text)


@patch('openlp.plugins.songs.forms.songmaintenanceform.critical_error_message_box')
def test_delete_item(mocked_critical_error_message_box: MagicMock, maintenance_form: SongMaintenanceForm):
    """
    Test the _delete_item() method
    """
    # GIVEN: Some mocked items
    mocked_item = MagicMock()
    mocked_item.songs = []
    mocked_item.id = 1
    maintenance_form.manager.get_object.return_value = mocked_item
    mocked_critical_error_message_box.return_value = QtWidgets.QMessageBox.StandardButton.Yes
    mocked_list_widget = MagicMock()
    mocked_reset_func = MagicMock()
    dialog_title = 'Delete Item'
    delete_text = 'Are you sure you want to delete this item?'
    error_text = 'There was a problem deleting this item'

    # WHEN: _delete_item() is called
    with patch.object(maintenance_form, '_get_current_item_id') as mocked_get_current_item_id:
        mocked_get_current_item_id.return_value = 1
        maintenance_form._delete_item(SongBook, mocked_list_widget, mocked_reset_func, dialog_title, delete_text,
                                      error_text)

    # THEN: The right things should have been called
    mocked_get_current_item_id.assert_called_once_with(mocked_list_widget)
    maintenance_form.manager.get_object.assert_called_once_with(SongBook, 1)
    mocked_critical_error_message_box.assert_called_once_with(dialog_title, delete_text, maintenance_form, True)
    maintenance_form.manager.delete_object.assert_called_once_with(SongBook, 1)
    mocked_reset_func.assert_called_once_with()


@patch('openlp.plugins.songs.forms.songmaintenanceform.critical_error_message_box')
def test_delete_book_assigned(mocked_critical_error_message_box: MagicMock, maintenance_form: SongMaintenanceForm):
    """
    Test the _delete_item() method
    """
    # GIVEN: Some mocked items
    mocked_item = create_autospec(SongBook, spec_set=True)
    mocked_item.id = 1
    mocked_item.songs = [MagicMock(title='Amazing Grace')]
    maintenance_form.manager.get_object.return_value = mocked_item
    mocked_critical_error_message_box.return_value = QtWidgets.QMessageBox.StandardButton.Yes
    mocked_list_widget = MagicMock()
    mocked_reset_func = MagicMock()
    dialog_title = 'Delete Book'
    delete_text = 'Are you sure you want to delete the selected book?'
    error_text = 'This book cannot be deleted, it is currenty assigned to at least one song.'

    # WHEN: _delete_item() is called
    with patch.object(maintenance_form, '_get_current_item_id') as mocked_get_current_item_id:
        mocked_get_current_item_id.return_value = 1
        maintenance_form._delete_item(SongBook, mocked_list_widget, mocked_reset_func, dialog_title, delete_text,
                                      error_text)

    # THEN: The right things should have been called
    mocked_get_current_item_id.assert_called_once_with(mocked_list_widget)
    maintenance_form.manager.get_object.assert_called_once_with(SongBook, 1)
    mocked_critical_error_message_box.assert_called_once_with(dialog_title, error_text + '\n\nAmazing Grace')
    maintenance_form.manager.delete_object.assert_not_called()
    mocked_reset_func.assert_not_called()


@patch('openlp.plugins.songs.forms.songmaintenanceform.QtWidgets.QListWidgetItem')
@patch('openlp.plugins.songs.forms.songmaintenanceform.Author')
def test_reset_authors(MockedAuthor: MagicMock, MockedQListWidgetItem: MagicMock,
                       maintenance_form: SongMaintenanceForm):
    """
    Test the reset_authors() method
    """
    # GIVEN: A mocked authors_list_widget and a few other mocks
    mocked_author1 = MagicMock()
    mocked_author1.display_name = 'John Newton'
    mocked_author1.id = 1
    mocked_author2 = MagicMock()
    mocked_author2.display_name = ''
    mocked_author2.first_name = 'John'
    mocked_author2.last_name = 'Wesley'
    mocked_author2.id = 2
    mocked_authors = [mocked_author1, mocked_author2]
    mocked_author_item1 = MagicMock()
    mocked_author_item2 = MagicMock()
    MockedQListWidgetItem.side_effect = [mocked_author_item1, mocked_author_item2]
    MockedAuthor.display_name = None
    maintenance_form.manager.get_all_objects.return_value = mocked_authors

    # WHEN: reset_authors() is called
    with patch.object(maintenance_form, 'authors_list_widget') as mocked_authors_list_widget:
        maintenance_form.reset_authors()

    # THEN: The authors list should be reset
    expected_widget_item_calls = [call('John Wesley'), call('John Newton')]
    mocked_authors_list_widget.clear.assert_called_once_with()
    maintenance_form.manager.get_all_objects.assert_called_once_with(MockedAuthor)
    # Do not care which order items are called since the order is different on macos vs others
    MockedQListWidgetItem.assert_has_calls(expected_widget_item_calls, any_order=True)
    mocked_author_item1.setData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole, ANY)
    mocked_author_item2.setData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole, ANY)
    mocked_authors_list_widget.addItem.assert_has_calls([
        call(mocked_author_item1), call(mocked_author_item2)])


@patch('openlp.plugins.songs.forms.songmaintenanceform.QtWidgets.QListWidgetItem')
@patch('openlp.plugins.songs.forms.songmaintenanceform.Topic')
def test_reset_topics(MockedTopic: MagicMock, MockedQListWidgetItem: MagicMock, maintenance_form: SongMaintenanceForm):
    """
    Test the reset_topics() method
    """
    # GIVEN: Some mocked out objects and methods
    MockedTopic.name = 'Grace'
    mocked_topic = MagicMock()
    mocked_topic.id = 1
    mocked_topic.name = 'Grace'
    maintenance_form.manager.get_all_objects.return_value = [mocked_topic]
    mocked_topic_item = MagicMock()
    MockedQListWidgetItem.return_value = mocked_topic_item

    # WHEN: reset_topics() is called
    with patch.object(maintenance_form, 'topics_list_widget') as mocked_topic_list_widget:
        maintenance_form.reset_topics()

    # THEN: The topics list should be reset correctly
    mocked_topic_list_widget.clear.assert_called_once_with()
    maintenance_form.manager.get_all_objects.assert_called_once_with(MockedTopic)
    MockedQListWidgetItem.assert_called_once_with('Grace')
    mocked_topic_item.setData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole, 1)
    mocked_topic_list_widget.addItem.assert_called_once_with(mocked_topic_item)


@patch('openlp.plugins.songs.forms.songmaintenanceform.QtWidgets.QListWidgetItem')
@patch('openlp.plugins.songs.forms.songmaintenanceform.SongBook')
def test_reset_song_books(MockedBook: MagicMock, MockedQListWidgetItem: MagicMock,
                          maintenance_form: SongMaintenanceForm):
    """
    Test the reset_song_books() method
    """
    # GIVEN: Some mocked out objects and methods
    MockedBook.name = 'Hymnal'
    mocked_song_book = MagicMock()
    mocked_song_book.id = 1
    mocked_song_book.name = 'Hymnal'
    mocked_song_book.publisher = 'Hymns and Psalms, Inc.'
    maintenance_form.manager.get_all_objects.return_value = [mocked_song_book]
    mocked_song_book_item = MagicMock()
    MockedQListWidgetItem.return_value = mocked_song_book_item

    # WHEN: reset_song_books() is called
    with patch.object(maintenance_form, 'song_books_list_widget') as mocked_song_book_list_widget:
        maintenance_form.reset_song_books()

    # THEN: The song_books list should be reset correctly
    mocked_song_book_list_widget.clear.assert_called_once_with()
    maintenance_form.manager.get_all_objects.assert_called_once_with(MockedBook)
    MockedQListWidgetItem.assert_called_once_with('Hymnal (Hymns and Psalms, Inc.)')
    mocked_song_book_item.setData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole, 1)
    mocked_song_book_list_widget.addItem.assert_called_once_with(mocked_song_book_item)


@patch('openlp.plugins.songs.forms.songmaintenanceform.and_')
@patch('openlp.plugins.songs.forms.songmaintenanceform.Author')
def test_check_author_exists(MockedAuthor: MagicMock, mocked_and: MagicMock, maintenance_form: SongMaintenanceForm):
    """
    Test the check_author_exists() method
    """
    # GIVEN: A bunch of mocked out stuff
    MockedAuthor.first_name = 'John'
    MockedAuthor.last_name = 'Newton'
    MockedAuthor.display_name = 'John Newton'
    mocked_new_author = MagicMock()
    mocked_new_author.first_name = 'John'
    mocked_new_author.last_name = 'Newton'
    mocked_new_author.display_name = 'John Newton'
    mocked_and.return_value = True
    mocked_authors = [MagicMock(), MagicMock()]
    maintenance_form.manager.get_all_objects.return_value = mocked_authors

    # WHEN: check_author_exists() is called
    with patch.object(maintenance_form, '_check_object_exists') as mocked_check_object_exists:
        mocked_check_object_exists.return_value = True
        result = maintenance_form.check_author_exists(mocked_new_author, edit=True)

    # THEN: The correct result is returned
    mocked_and.assert_called_once_with(True, True, True)
    maintenance_form.manager.get_all_objects.assert_called_once_with(MockedAuthor, True)
    mocked_check_object_exists.assert_called_once_with(mocked_authors, mocked_new_author, True)
    assert result is True


@patch('openlp.plugins.songs.forms.songmaintenanceform.Topic')
def test_check_topic_exists(MockedTopic: MagicMock, maintenance_form: SongMaintenanceForm):
    """
    Test the check_topic_exists() method
    """
    # GIVEN: Some mocked stuff
    MockedTopic.name = 'Grace'
    mocked_new_topic = MagicMock()
    mocked_new_topic.name = 'Grace'
    mocked_topics = [MagicMock(), MagicMock()]
    maintenance_form.manager.get_all_objects.return_value = mocked_topics

    # WHEN: check_topic_exists() is run
    with patch.object(maintenance_form, '_check_object_exists') as mocked_check_object_exists:
        mocked_check_object_exists.return_value = True
        result = maintenance_form.check_topic_exists(mocked_new_topic, True)

    # THEN: The correct things should have been called
    maintenance_form.manager.get_all_objects.assert_called_once_with(MockedTopic, True)
    mocked_check_object_exists.assert_called_once_with(mocked_topics, mocked_new_topic, True)
    assert result is True


@patch('openlp.plugins.songs.forms.songmaintenanceform.and_')
@patch('openlp.plugins.songs.forms.songmaintenanceform.SongBook')
def test_check_song_book_exists(MockedBook: MagicMock, mocked_and: MagicMock, maintenance_form):
    """
    Test the check_song_book_exists() method
    """
    # GIVEN: Some mocked stuff
    MockedBook.name = 'Hymns'
    MockedBook.publisher = 'Christian Songs'
    mocked_new_book = MagicMock()
    mocked_new_book.name = 'Hymns'
    mocked_new_book.publisher = 'Christian Songs'
    mocked_and.return_value = True
    mocked_books = [MagicMock(), MagicMock()]
    maintenance_form.manager.get_all_objects.return_value = mocked_books

    # WHEN: check_book_exists() is run
    with patch.object(maintenance_form, '_check_object_exists') as mocked_check_object_exists:
        mocked_check_object_exists.return_value = True
        result = maintenance_form.check_song_book_exists(mocked_new_book, True)

    # THEN: The correct things should have been called
    mocked_and.assert_called_once_with(True, True)
    maintenance_form.manager.get_all_objects.assert_called_once_with(MockedBook, True)
    mocked_check_object_exists.assert_called_once_with(mocked_books, mocked_new_book, True)
    assert result is True


def test_check_object_exists_no_existing_objects(maintenance_form: SongMaintenanceForm):
    """
    Test the _check_object_exists() method when there are no existing objects
    """
    # GIVEN: A SongMaintenanceForm instance
    # WHEN: _check_object_exists() is called without existing objects
    # THEN: The result should be True
    assert maintenance_form._check_object_exists([], None, False) is True


def test_check_object_exists_without_edit(maintenance_form: SongMaintenanceForm):
    """
    Test the _check_object_exists() method when edit is false
    """
    # GIVEN: A SongMaintenanceForm instance
    # WHEN: _check_object_exists() is called with edit set to false
    # THEN: The result should be False
    assert maintenance_form._check_object_exists([MagicMock()], None, False) is False


def test_check_object_exists_not_found(maintenance_form: SongMaintenanceForm):
    """
    Test the _check_object_exists() method when the object is not found
    """
    # GIVEN: A SongMaintenanceForm instance and some mocked objects
    mocked_existing_objects = [MagicMock(id=1)]
    mocked_new_object = MagicMock(id=2)

    # WHEN: _check_object_exists() is called with edit set to false
    # THEN: The result should be False
    assert maintenance_form._check_object_exists(mocked_existing_objects, mocked_new_object, True) is False


def test_check_object_exists(maintenance_form: SongMaintenanceForm):
    """
    Test the _check_object_exists() method
    """
    # GIVEN: A SongMaintenanceForm instance and some mocked objects
    mocked_existing_objects = [MagicMock(id=1)]
    mocked_new_object = MagicMock(id=1)

    # WHEN: _check_object_exists() is called with edit set to false
    # THEN: The result should be False
    assert maintenance_form._check_object_exists(mocked_existing_objects, mocked_new_object, True) is True


def test_merge_song_books(request, registry: Registry, settings: Settings, temp_folder: str):
    """
    Test the functionality of merging 2 song books.
    """
    # GIVEN a test database populated with test data, and a song maintenance form
    db_tmp_path = os.path.join(temp_folder, 'test-song-maint-merge-songbooks.sqlite')

    def cleanup_db():
        try:
            os.unlink(db_tmp_path)
        except Exception:
            # Ignore exceptions
            pass

    request.addfinalizer(cleanup_db)

    # Create a db manager
    manager = DBManager('songs', init_schema, db_file_path=db_tmp_path)

    # create 2 song books, both with the same name
    book1 = SongBook()
    book1.name = 'test book1'
    book1.publisher = ''
    manager.save_object(book1)
    book2 = SongBook()
    book2.name = 'test book1'
    book2.publisher = ''
    manager.save_object(book2)

    # create 3 songs, all with same search_title
    song1 = Song()
    song1.title = 'test song1'
    song1.lyrics = 'lyrics1'
    song1.search_title = 'test song'
    song1.search_lyrics = 'lyrics1'
    manager.save_object(song1)
    song2 = Song()
    song2.title = 'test song2'
    song2.lyrics = 'lyrics2'
    song2.search_title = 'test song'
    song2.search_lyrics = 'lyrics2'
    manager.save_object(song2)
    song3 = Song()
    song3.title = 'test song3'
    song3.lyrics = 'lyrics3'
    song3.search_title = 'test song'
    song3.search_lyrics = 'lyrics3'
    manager.save_object(song3)

    # associate songs with song books
    song1.add_songbook_entry(book1, '10')
    song2.add_songbook_entry(book1, '20')
    song2.add_songbook_entry(book2, '30')
    song3.add_songbook_entry(book1, '40')
    song3.add_songbook_entry(book2, '')

    song_maintenance_form = SongMaintenanceForm(manager)

    # WHEN the song books are merged, getting rid of book1
    song_maintenance_form.merge_song_books(book1)

    # THEN the database should reflect correctly the merge

    songs = manager.get_all_objects(Song, Song.search_title == 'test song')
    songbook1_entries = manager.get_all_objects(SongBookEntry, SongBookEntry.songbook_id == book1.id)
    songbook2_entries = manager.get_all_objects(SongBookEntry, SongBookEntry.songbook_id == book2.id)
    song1_book2_entry = manager.get_all_objects(SongBookEntry, and_(SongBookEntry.songbook_id == book2.id,
                                                                    SongBookEntry.song_id == song1.id))
    song2_book2_entry = manager.get_all_objects(SongBookEntry, and_(SongBookEntry.songbook_id == book2.id,
                                                                    SongBookEntry.song_id == song2.id))
    song3_book2_entry = manager.get_all_objects(SongBookEntry, and_(SongBookEntry.songbook_id == book2.id,
                                                                    SongBookEntry.song_id == song3.id))
    books = manager.get_all_objects(SongBook, SongBook.name == 'test book1')

    # song records should not be deleted
    assert len(songs) == 3
    # the old book should have been deleted, with its songs_songbooks records
    assert len(books) == 1
    assert len(songbook1_entries) == 0

    # each of the 3 songs should be associated with book2
    assert len(songbook2_entries) == 3

    # the individual SongBookEntry records should be correct
    assert len(song1_book2_entry) == 1
    assert song1_book2_entry[0].entry == '10'

    assert len(song2_book2_entry) == 1
    # entry field should not be overridden, as it was set previously for book2
    assert song2_book2_entry[0].entry == '30'

    assert len(song3_book2_entry) == 1
    # entry field should be overridden, as it was not set previously
    assert song3_book2_entry[0].entry == '40'


def test_merge_authors(request, registry: Registry, settings: Settings, temp_folder: str):
    """
    Test merging two authors
    """
    # GIVEN a test database populated with test data, and a song maintenance form
    db_tmp_path = os.path.join(temp_folder, 'test-song-maint-merge-authors.sqlite')
    # Create a db manager
    manager = DBManager('songs', init_schema, db_file_path=db_tmp_path)
    # create 2 song books, both with the same name
    author1 = Author(first_name='John', last_name='Newton', display_name='John Newton')
    manager.save_object(author1)
    author2 = Author(first_name='John', last_name='Newton', display_name='John Newton')
    manager.save_object(author2)
    # create 3 songs, all with same search_title
    song1 = Song()
    song1.title = 'test song1'
    song1.lyrics = 'lyrics1'
    song1.search_title = 'test song'
    song1.search_lyrics = 'lyrics1'
    manager.save_object(song1)
    song2 = Song()
    song2.title = 'test song2'
    song2.lyrics = 'lyrics2'
    song2.search_title = 'test song'
    song2.search_lyrics = 'lyrics2'
    manager.save_object(song2)
    song3 = Song()
    song3.title = 'test song3'
    song3.lyrics = 'lyrics3'
    song3.search_title = 'test song'
    song3.search_lyrics = 'lyrics3'
    manager.save_object(song3)
    # associate songs with authors
    song1.add_author(author1)
    song2.add_author(author1)
    song3.add_author(author2)
    manager.save_objects([song1, song2, song3])
    song_maintenance_form = SongMaintenanceForm(manager)

    # WHEN the song books are merged, getting rid of book1
    with patch.object(Song, 'init_on_load') as mock_init_on_load:
        song_maintenance_form.merge_authors(author1)

    # THEN the database should reflect correctly the merge
    songs = manager.get_all_objects(Song, Song.search_title == 'test song')
    author_song1 = manager.get_all_objects(AuthorSong, AuthorSong.author_id == author1.id)
    author_song2 = manager.get_all_objects(AuthorSong, AuthorSong.author_id == author2.id)
    song1_author2 = manager.get_all_objects(AuthorSong, and_(AuthorSong.author_id == author2.id,
                                                             AuthorSong.song_id == song1.id))
    song2_author2 = manager.get_all_objects(AuthorSong, and_(AuthorSong.author_id == author2.id,
                                                             AuthorSong.song_id == song2.id))
    song3_author2 = manager.get_all_objects(AuthorSong, and_(AuthorSong.author_id == author2.id,
                                                             AuthorSong.song_id == song3.id))
    authors = manager.get_all_objects(Author, Author.display_name == 'John Newton')
    # song records should not be deleted
    assert len(songs) == 3
    # the old author should have been deleted
    assert len(authors) == 1
    # there should not be any songs associated with this author
    assert len(author_song1) == 0
    # each of the 3 songs should be associated with author2
    assert len(author_song2) == 3
    # the individual AuthorSong records should be correct
    assert len(song1_author2) == 1
    assert len(song2_author2) == 1
    assert len(song3_author2) == 1
    assert mock_init_on_load.call_count == 2
    mock_init_on_load.assert_any_call(force_song_detail_recalculation=True)


@patch('openlp.plugins.songs.forms.songmaintenanceform.critical_error_message_box')
@patch('openlp.plugins.songs.forms.songmaintenanceform.translate')
def test_on_edit_author_button_clicked_new_author(mock_translate, mock_critical_error, maintenance_form):
    """
    Test the on_edit_author_button_clicked method without any conflict
    """
    # Given: A mock author and setup for editing
    mock_translate.return_value = 'Translated message'
    author = MagicMock()
    author.id = 1
    author.first_name = 'John'
    author.last_name = 'Doe'
    author.display_name = 'John Doe'
    author.songs = [MagicMock(init_on_load=MagicMock())]
    maintenance_form.authors_list_widget = MagicMock()
    maintenance_form._get_current_item_id = MagicMock(return_value=1)
    maintenance_form.manager.get_object = MagicMock(return_value=author)
    maintenance_form.author_form.auto_display_name = True
    maintenance_form.author_form.first_name_edit = MagicMock()
    maintenance_form.author_form.last_name_edit = MagicMock()
    maintenance_form.author_form.display_edit = MagicMock()
    maintenance_form.author_form.first_name_edit.text.return_value = 'Johnny'
    maintenance_form.author_form.last_name_edit.text.return_value = 'Doestar'
    maintenance_form.author_form.display_edit.text.return_value = 'Johnny Doestar'
    maintenance_form.author_form.exec = MagicMock(return_value=QtWidgets.QDialog.Accepted)
    maintenance_form.check_author_exists = MagicMock(return_value=True)
    maintenance_form.manager.save_object = MagicMock(return_value=True)
    maintenance_form.reset_authors = MagicMock()
    maintenance_form.from_song_edit = False

    with patch('openlp.plugins.songs.forms.songmaintenanceform.Registry') as mock_registry:
        registry_instance = mock_registry.return_value
        registry_instance.execute = MagicMock()

        # When: on_edit_author_button_clicked is called
        maintenance_form.on_edit_author_button_clicked()

    # Then: The author is updated and saved, and related functions are called
    assert author.first_name == 'Johnny'
    assert author.last_name == 'Doestar'
    assert author.display_name == 'Johnny Doestar'
    maintenance_form.manager.save_object.assert_called_once_with(author)
    maintenance_form.reset_authors.assert_called_once()
    registry_instance.execute.assert_called_once_with('songs_load_list')
    author.songs[0].init_on_load.assert_called_once_with(force_song_detail_recalculation=True)


@patch('openlp.plugins.songs.forms.songmaintenanceform.critical_error_message_box')
@patch('openlp.plugins.songs.forms.songmaintenanceform.translate')
def test_on_edit_author_button_clicked_author_exists_and_merge(mock_translate, mock_critical_error, maintenance_form):
    """
    Test the on_edit_author_button_clicked method when the author exists and the user chooses to merge
    """
    # Given: A mock author setup where the author already exists
    mock_translate.side_effect = lambda *args, **kwargs: args[-1]
    author = MagicMock()
    author.id = 1
    author.first_name = 'John'
    author.last_name = 'Doe'
    author.display_name = 'John Doe'
    maintenance_form.authors_list_widget = MagicMock()
    maintenance_form._get_current_item_id = MagicMock(return_value=1)
    maintenance_form.manager.get_object = MagicMock(return_value=author)
    maintenance_form.author_form.first_name_edit = MagicMock(text=MagicMock(return_value='Johnny'))
    maintenance_form.author_form.last_name_edit = MagicMock(text=MagicMock(return_value='Doestar'))
    maintenance_form.author_form.display_edit = MagicMock(text=MagicMock(return_value='Johnny Doestar'))
    maintenance_form.author_form.exec = MagicMock(return_value=QtWidgets.QDialog.Accepted)
    maintenance_form.check_author_exists = MagicMock(return_value=False)
    maintenance_form._merge_objects = MagicMock()
    maintenance_form.merge_authors = MagicMock()
    maintenance_form.reset_authors = MagicMock()
    mock_critical_error.return_value = QtWidgets.QMessageBox.StandardButton.Yes

    # When: on_edit_author_button_clicked is called
    maintenance_form.on_edit_author_button_clicked()

    # Then: The merge flow is triggered
    maintenance_form._merge_objects.assert_called_once_with(author, maintenance_form.merge_authors,
                                                            maintenance_form.reset_authors)


@patch('openlp.plugins.songs.forms.songmaintenanceform.critical_error_message_box')
@patch('openlp.plugins.songs.forms.songmaintenanceform.translate')
def test_on_edit_author_button_clicked_author_exists_and_user_declines_merge(mock_translate, mock_critical_error,
                                                                             maintenance_form):
    """
    Test the on_edit_author_button_clicked method when the author exists and the user declines to merge
    """
    # Given: A mock author setup with conflict and the user chooses not to merge
    mock_translate.side_effect = lambda *args, **kwargs: args[-1]
    author = MagicMock()
    author.id = 1
    author.first_name = 'John'
    author.last_name = 'Doe'
    author.display_name = 'John Doe'
    maintenance_form.authors_list_widget = MagicMock()
    maintenance_form._get_current_item_id = MagicMock(return_value=1)
    maintenance_form.manager.get_object = MagicMock(return_value=author)
    maintenance_form.author_form.first_name_edit = MagicMock(text=MagicMock(return_value='Johnny'))
    maintenance_form.author_form.last_name_edit = MagicMock(text=MagicMock(return_value='Doestar'))
    maintenance_form.author_form.display_edit = MagicMock(text=MagicMock(return_value='Johnny Doestar'))
    maintenance_form.author_form.exec = MagicMock(return_value=QtWidgets.QDialog.Accepted)
    maintenance_form.check_author_exists = MagicMock(return_value=False)
    mock_critical_error.return_value = QtWidgets.QMessageBox.StandardButton.No

    # When: on_edit_author_button_clicked is called
    maintenance_form.on_edit_author_button_clicked()

    # Then: The original author names are restored, and error is shown
    assert author.first_name == 'John'
    assert author.last_name == 'Doe'
    assert author.display_name == 'John Doe'
    mock_critical_error.assert_called()
