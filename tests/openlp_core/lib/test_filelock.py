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
Package to test the openlp.core.lib.filelock package.
"""
import time
from pathlib import Path
from unittest.mock import patch

from openlp.core.lib.filelock import FileLock, LOCK_EXPIRE_SECS


@patch('openlp.core.lib.filelock.QtWidgets.QMessageBox.critical')
def test_file_lock_simple(mocked_critical, temp_folder):
    """
    Test the creation of a FileLock
    """
    # GIVEN: A FileLock
    file_lock = FileLock(Path(temp_folder), 'openlp-version')

    # WHEN: Creating a lock without any other lock active
    lock_acquired = file_lock.lock()

    # cleanup before end
    if lock_acquired:
        file_lock.release()

    # THEN: Lock should be acquired
    assert lock_acquired


@patch('openlp.core.lib.filelock.QtWidgets.QMessageBox.critical')
def test_file_lock_relock(mocked_critical, temp_folder):
    """
    Test the relocking of a FileLock
    """
    # GIVEN: A FileLock
    file_lock = FileLock(Path(temp_folder), 'openlp-version')

    # WHEN: Locking and then updating the lock without any other lock active
    lock_acquired = file_lock.lock()
    assert lock_acquired
    file_lock.update_lock_file()
    relocking_succeded = file_lock.has_lock

    # cleanup before end
    if lock_acquired:
        file_lock.release()

    # THEN: The relocking should succeed
    assert relocking_succeded


@patch('openlp.core.lib.filelock.QtWidgets.QMessageBox.critical')
@patch('openlp.core.lib.filelock.getpass.getuser')
def test_file_lock_already_locked(mocked_getuser, mocked_critical, temp_folder):
    """
    Test the creation of a FileLock when a lock already exists
    """
    # GIVEN: 2 FileLocks
    file_lock1 = FileLock(Path(temp_folder), 'openlp-version')
    file_lock2 = FileLock(Path(temp_folder), 'openlp-version')

    # WHEN: Creating 2 locks with 2 different users
    mocked_getuser.side_effect = ['user1', 'user2']
    lock1_acquired = file_lock1.lock()
    lock2_acquired = file_lock2.lock()

    # cleanup before end
    if lock1_acquired:
        file_lock1.release()
    if lock2_acquired:
        file_lock2.release()

    # THEN: Only the first should succeed
    assert lock1_acquired
    assert not lock2_acquired


@patch('openlp.core.lib.filelock.QtWidgets.QMessageBox.critical')
@patch('openlp.core.lib.filelock.getpass.getuser')
@patch('openlp.core.lib.filelock.time.time')
def test_file_lock_claim_expired_lock(mocked_time, mocked_getuser, mocked_critical, temp_folder):
    """
    Test the claiming of an expired lock
    """
    # GIVEN: 2 FileLocks
    file_lock1 = FileLock(Path(temp_folder), 'openlp-version')
    file_lock2 = FileLock(Path(temp_folder), 'openlp-version')

    # WHEN: Creating 2 locks with 2 different users, at 2 different times, 7 minutes apart
    mocked_getuser.side_effect = ['user1', 'user2']
    lock_time = time.time_ns() / 1000000000 + LOCK_EXPIRE_SECS + 1
    mocked_time.return_value = lock_time
    lock1_acquired = file_lock1.lock()
    lock2_acquired = file_lock2.lock()

    # cleanup before end
    if lock1_acquired:
        file_lock1.release()
    if lock2_acquired:
        file_lock2.release()

    # THEN: Both locks should succeed
    assert lock1_acquired
    assert lock2_acquired
