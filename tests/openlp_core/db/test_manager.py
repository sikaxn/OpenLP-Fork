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
Package to test the openlp.core.lib package.
"""
from sqlite3 import OperationalError as SQLiteOperationalError
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import InvalidRequestError, OperationalError as SQLAlchemyOperationalError

from openlp.core.common.settings import Settings
from openlp.core.db.manager import DBManager
from openlp.plugins.songs.lib.db import Song


@patch('openlp.core.db.manager.init_url')
@patch('openlp.core.db.manager.upgrade_db')
def test_manager_init(mocked_upgrade_db: MagicMock, mocked_init_url: MagicMock, temp_folder: str,
                      settings: Settings):
    """Test the initialisation of the DB manager"""
    # GIVEN: A bunch of mocked out functions and objects
    mocked_db_url = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_init_url.return_value = mocked_db_url
    mocked_session = MagicMock()
    mocked_upgrade_mod = MagicMock()
    mocked_upgrade_db.return_value = (0, 1)
    mocked_init_schema = MagicMock()
    mocked_init_schema.return_value = mocked_session

    # WHEN: DBManager() is called
    manager = DBManager('test', mocked_init_schema, 'test_db.sqlite', mocked_upgrade_mod)

    # THEN: The database manager should have been correctly initialised
    assert manager.is_dirty is False
    assert manager.db_url == mocked_db_url
    assert manager.session is mocked_session
    mocked_init_url.assert_called_once_with('test', 'test_db.sqlite')
    mocked_init_schema.assert_called_once_with(mocked_db_url)
    mocked_upgrade_db.assert_called_once_with(mocked_db_url, mocked_upgrade_mod)


@patch('openlp.core.db.manager.init_url')
def test_manager_init_with_session(mocked_init_url: MagicMock, temp_folder: str, settings: Settings):
    """Test the initialisation of the DB manager with a provided session"""
    # GIVEN: A bunch of mocked out functions and objects
    mocked_db_url = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_init_url.return_value = mocked_db_url
    mocked_session = MagicMock()
    mocked_init_schema = MagicMock()

    # WHEN: DBManager() is called
    manager = DBManager('test', mocked_init_schema, 'test_db.sqlite', None, mocked_session)

    # THEN: The database manager should have been correctly initialised
    assert manager.is_dirty is False
    assert manager.db_url == mocked_db_url
    assert manager.session is mocked_session
    mocked_init_url.assert_called_once_with('test', 'test_db.sqlite')
    mocked_init_schema.assert_not_called()


@patch('openlp.core.db.manager.init_url')
@patch('openlp.core.db.manager.handle_db_error')
def test_manager_init_session_error(mocked_handle_db_error: MagicMock, mocked_init_url: MagicMock,
                                    temp_folder: str, settings: Settings):
    """Test the initialisation of the DB manager when there's an error creating the session"""
    # GIVEN: A bunch of mocked out functions and objects
    mocked_db_url = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_init_url.return_value = mocked_db_url
    mocked_init_schema = MagicMock()
    mocked_init_schema.side_effect = SQLAlchemyOperationalError(
        statement='create database',
        params=[],
        orig=SQLiteOperationalError('database is locked')
    )

    # WHEN: DBManager() is called
    DBManager('test', mocked_init_schema, 'test_db.sqlite')

    # THEN: The handle_db_error() method should have been called
    mocked_init_schema.assert_called_once_with(mocked_db_url)
    mocked_handle_db_error.assert_called_once_with('test', 'test_db.sqlite')


@patch('openlp.core.db.manager.init_url')
@patch('openlp.core.db.manager.upgrade_db')
@patch('openlp.core.db.manager.handle_db_error')
def test_manager_init_upgrade_error(mocked_handle_db_error: MagicMock, mocked_upgrade_db: MagicMock,
                                    mocked_init_url: MagicMock, temp_folder: str, settings: Settings):
    """Test the initialisation of the DB manager when there's an error upgrading"""
    # GIVEN: A bunch of mocked out functions and objects
    mocked_db_url = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_init_url.return_value = mocked_db_url
    mocked_session = MagicMock()
    mocked_upgrade_mod = MagicMock()
    mocked_upgrade_db.side_effect = SQLAlchemyOperationalError(
        statement='alter table',
        params=[],
        orig=SQLiteOperationalError('database is locked')
    )

    # WHEN: DBManager() is called
    DBManager('test', MagicMock(), 'test_db.sqlite', mocked_upgrade_mod, mocked_session)

    # THEN: The handle_db_error() method should have been called
    mocked_upgrade_db.assert_called_once_with(mocked_db_url, mocked_upgrade_mod)
    mocked_handle_db_error.assert_called_once_with('test', 'test_db.sqlite')


@patch('openlp.core.db.manager.init_url')
@patch('openlp.core.db.manager.upgrade_db')
@patch('openlp.core.db.manager.critical_error_message_box')
def test_manager_init_upgrade_version_mismatch(mocked_critical_error_message_box: MagicMock,
                                               mocked_upgrade_db: MagicMock, mocked_init_url: MagicMock,
                                               temp_folder: str, settings: Settings):
    """Test the initialisation of the DB manager when there's a mismatching version during upgrading"""
    # GIVEN: A bunch of mocked out functions and objects
    mocked_db_url = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_init_url.return_value = mocked_db_url
    mocked_session = MagicMock()
    mocked_upgrade_mod = MagicMock()
    mocked_upgrade_db.return_value = (2, 1)

    # WHEN: DBManager() is called
    DBManager('test', MagicMock(), 'test_db.sqlite', mocked_upgrade_mod, mocked_session)

    # THEN: An error message should be shown to the user
    mocked_upgrade_db.assert_called_once_with(mocked_db_url, mocked_upgrade_mod)
    mocked_critical_error_message_box.assert_called_once_with(
        'Database Error',
        'The database being loaded was created in a more recent version of '
        'OpenLP. The database is version 2, while OpenLP expects version 1. '
        f'The database will not be loaded.\n\nDatabase: {mocked_db_url}'
    )


@patch('openlp.core.db.manager.init_url')
def test_manager_save_object(mocked_init_url: MagicMock, temp_folder: str, settings: Settings):
    """Test the save_object method of the DB manager"""
    # GIVEN: A db Manager object
    mocked_init_url.return_value = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_session = MagicMock()
    mocked_init_schema = MagicMock()
    manager = DBManager('test', mocked_init_schema, 'test_db.sqlite', None, mocked_session)
    test_song = Song()

    # WHEN: save_object() is called
    result = manager.save_object(test_song, commit=True)

    # THEN: song should have been saved to the database
    mocked_session.add.assert_called_once_with(test_song)
    mocked_session.commit.assert_called_once_with()
    assert manager.is_dirty is True
    assert result is True


@patch('openlp.core.db.manager.init_url')
def test_manager_save_object_with_retry(mocked_init_url: MagicMock, temp_folder: str, settings: Settings):
    """Test the save_object method of the DB manager with a retry on OperationalError"""
    # GIVEN: A db Manager object
    mocked_init_url.return_value = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_session = MagicMock()
    mocked_session.commit.side_effect = SQLAlchemyOperationalError(
        statement='update song',
        params=[],
        orig=SQLiteOperationalError('database is locked')
    )
    mocked_init_schema = MagicMock()
    manager = DBManager('test', mocked_init_schema, 'test_db.sqlite', None, mocked_session)
    test_song = Song()

    # WHEN: save_object() is called
    with pytest.raises(SQLAlchemyOperationalError):
        manager.save_object(test_song, commit=True)

    # THEN: song should have been saved to the database
    assert mocked_session.add.call_count == 3
    assert mocked_session.commit.call_count == 3
    assert mocked_session.rollback.call_count == 3


@patch('openlp.core.db.manager.init_url')
def test_manager_save_object_with_invalid_request_error(mocked_init_url: MagicMock, temp_folder: str,
                                                        settings: Settings):
    """Test the save_object method of the DB manager with an InvalidRequestError"""
    # GIVEN: A db Manager object
    mocked_init_url.return_value = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_session = MagicMock()
    mocked_session.commit.side_effect = InvalidRequestError()
    mocked_init_schema = MagicMock()
    manager = DBManager('test', mocked_init_schema, 'test_db.sqlite', None, mocked_session)
    test_song = Song()

    # WHEN: save_object() is called
    result = manager.save_object(test_song, commit=True)

    # THEN: song should have been saved to the database
    assert result is False
    assert mocked_session.add.call_count == 1
    assert mocked_session.commit.call_count == 1
    assert mocked_session.rollback.call_count == 1


@patch('openlp.core.db.manager.init_url')
def test_manager_save_object_with_other_exception(mocked_init_url: MagicMock, temp_folder: str,
                                                  settings: Settings):
    """Test the save_object method of the DB manager with any other exception"""
    # GIVEN: A db Manager object
    class FakeException(Exception):
        pass

    mocked_init_url.return_value = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_session = MagicMock()
    mocked_session.commit.side_effect = FakeException()
    mocked_init_schema = MagicMock()
    manager = DBManager('test', mocked_init_schema, 'test_db.sqlite', None, mocked_session)
    test_song = Song()

    # WHEN: save_object() is called
    with pytest.raises(FakeException):
        manager.save_object(test_song, commit=True)

    # THEN: song should have been saved to the database
    assert mocked_session.add.call_count == 1
    assert mocked_session.commit.call_count == 1
    assert mocked_session.rollback.call_count == 1


@patch('openlp.core.db.manager.init_url')
def test_manager_save_objects(mocked_init_url: MagicMock, temp_folder: str, settings: Settings):
    """Test the save_objects method of the DB manager"""
    # GIVEN: A db Manager object
    mocked_init_url.return_value = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_session = MagicMock()
    mocked_init_schema = MagicMock()
    manager = DBManager('test', mocked_init_schema, 'test_db.sqlite', None, mocked_session)
    test_songs = [Song(), Song()]

    # WHEN: save_objects() is called
    result = manager.save_objects(test_songs, commit=True)

    # THEN: song should have been saved to the database
    mocked_session.add_all.assert_called_once_with(test_songs)
    mocked_session.commit.assert_called_once_with()
    assert manager.is_dirty is True
    assert result is True


@patch('openlp.core.db.manager.init_url')
def test_manager_save_objects_with_retry(mocked_init_url: MagicMock, temp_folder: str, settings: Settings):
    """Test the save_objects method of the DB manager with a retry on OperationalError"""
    # GIVEN: A db Manager object
    mocked_init_url.return_value = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_session = MagicMock()
    mocked_session.commit.side_effect = SQLAlchemyOperationalError(
        statement='update song',
        params=[],
        orig=SQLiteOperationalError('database is locked')
    )
    mocked_init_schema = MagicMock()
    manager = DBManager('test', mocked_init_schema, 'test_db.sqlite', None, mocked_session)
    test_songs = [Song(), Song()]

    # WHEN: save_objects() is called
    with pytest.raises(SQLAlchemyOperationalError):
        manager.save_objects(test_songs, commit=True)

    # THEN: song should have been saved to the database
    assert mocked_session.add_all.call_count == 3
    assert mocked_session.commit.call_count == 3
    assert mocked_session.rollback.call_count == 3


@patch('openlp.core.db.manager.init_url')
def test_manager_save_objects_with_invalid_request_error(mocked_init_url: MagicMock, temp_folder: str,
                                                         settings: Settings):
    """Test the save_objects method of the DB manager with an InvalidRequestError"""
    # GIVEN: A db Manager object
    mocked_init_url.return_value = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_session = MagicMock()
    mocked_session.commit.side_effect = InvalidRequestError()
    mocked_init_schema = MagicMock()
    manager = DBManager('test', mocked_init_schema, 'test_db.sqlite', None, mocked_session)
    test_songs = [Song(), Song()]

    # WHEN: save_objects() is called
    result = manager.save_objects(test_songs, commit=True)

    # THEN: song should have been saved to the database
    assert result is False
    assert mocked_session.add_all.call_count == 1
    assert mocked_session.commit.call_count == 1
    assert mocked_session.rollback.call_count == 1


@patch('openlp.core.db.manager.init_url')
def test_manager_save_objects_with_other_exception(mocked_init_url: MagicMock, temp_folder: str,
                                                   settings: Settings):
    """Test the save_objects method of the DB manager with any other exception"""
    # GIVEN: A db Manager object
    class FakeException(Exception):
        pass

    mocked_init_url.return_value = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_session = MagicMock()
    mocked_session.commit.side_effect = FakeException()
    mocked_init_schema = MagicMock()
    manager = DBManager('test', mocked_init_schema, 'test_db.sqlite', None, mocked_session)
    test_songs = [Song(), Song()]

    # WHEN: save_objects() is called
    with pytest.raises(FakeException):
        manager.save_objects(test_songs, commit=True)

    # THEN: song should have been saved to the database
    assert mocked_session.add_all.call_count == 1
    assert mocked_session.commit.call_count == 1
    assert mocked_session.rollback.call_count == 1


@patch('openlp.core.db.manager.text')
@patch('openlp.core.db.manager.init_url')
@patch('openlp.core.db.manager.create_engine')
def test_manager_finalise_exception(mocked_create_engine: MagicMock, mocked_init_url: MagicMock,
                                    mocked_text: MagicMock, temp_folder: str, settings: Settings):
    """Test that the finalise method silently fails on an exception"""
    # GIVEN: A db Manager object
    mocked_init_url.return_value = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_session = MagicMock()
    mocked_text.side_effect = lambda t: t

    def init_schema(url):
        return mocked_session

    mocked_create_engine.return_value.connect.return_value.execute.side_effect = SQLAlchemyOperationalError(
        statement='vacuum',
        params=[],
        orig=SQLiteOperationalError('database is locked')
    )
    manager = DBManager('test', init_schema)
    manager.is_dirty = True

    # WHEN: finalise() is called
    manager.finalise()

    # THEN: vacuum should have been called on the database
    mocked_create_engine.return_value.connect.return_value.execute.assert_called_once_with('vacuum')


@patch('openlp.core.db.manager.text')
@patch('openlp.core.db.manager.init_url')
@patch('openlp.core.db.manager.create_engine')
def test_manager_finalise(mocked_create_engine: MagicMock, mocked_init_url: MagicMock, mocked_text: MagicMock,
                          temp_folder: str, settings: Settings):
    """Test that the finalise method works correctly"""
    # GIVEN: A db Manager object
    mocked_init_url.return_value = f'sqlite:///{temp_folder}/test_db.sqlite'
    mocked_session = MagicMock()
    mocked_text.side_effect = lambda t: t

    def init_schema(url):
        return mocked_session

    manager = DBManager('test', init_schema)
    manager.is_dirty = True

    # WHEN: finalise() is called
    manager.finalise()

    # THEN: vacuum should have been called on the database
    mocked_create_engine.return_value.connect.return_value.execute.assert_called_once_with('vacuum')
