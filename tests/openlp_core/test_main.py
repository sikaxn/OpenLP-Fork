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
Test OpenLP's ``__main__`` module
"""
from unittest.mock import MagicMock, patch

from openlp.__main__ import start, set_up_fault_handling, tear_down_fault_handling


@patch('openlp.__main__.error_log_file')
def test_tear_down_fault_handling(mocked_error_log_file: MagicMock):
    """Test that the teardown function closes the file"""
    # GIVEN: A mocked error log file
    # WHEN: tear_down_fault_handling() is called
    tear_down_fault_handling()

    # THEN: The log file should have been closed
    mocked_error_log_file.close.assert_called_once()


@patch('openlp.__main__.AppLocation.get_directory')
@patch('openlp.__main__.create_paths')
@patch('openlp.__main__.atexit.register')
@patch('openlp.__main__.faulthandler.enable')
def test_set_up_fault_handling(mocked_enable: MagicMock, mocked_register: MagicMock, mocked_create_paths: MagicMock,
                               mocked_get_directory: MagicMock):
    """Test that the set_up_fault_handling() function does the correct things"""
    # GIVEN: A whole bunch o' mocks
    # WHEN: set_up_fault_handling() is called
    set_up_fault_handling()

    # THEN: The correct calls should have been made
    mocked_create_paths.assert_called_once()
    mocked_register.assert_called_once_with(tear_down_fault_handling)
    mocked_enable.assert_called_once()


@patch('openlp.__main__.create_paths')
@patch('openlp.__main__.atexit.register')
@patch('openlp.__main__.atexit.unregister')
def test_set_up_fault_handling_exception(mocked_unregister: MagicMock, mocked_register: MagicMock,
                                         mocked_create_paths: MagicMock):
    """Test that the set_up_fault_handling() function tears itself down correctly if there is an issue"""
    # GIVEN: A whole bunch o' mocks
    mocked_register.side_effect = OSError('Test')
    # WHEN: set_up_fault_handling() is called
    set_up_fault_handling()

    # THEN: The correct calls should have been made
    mocked_create_paths.assert_called_once()
    mocked_unregister.assert_called_once_with(tear_down_fault_handling)


@patch('openlp.__main__.multiprocessing.freeze_support')
@patch('openlp.__main__.set_up_fault_handling')
@patch('openlp.__main__.is_win')
@patch('openlp.__main__.main')
def test_start(mocked_main: MagicMock, mocked_is_win: MagicMock, mocked_fault_handling: MagicMock,
               mocked_freeze_support: MagicMock):
    """Test that the start method calls the correct functions"""
    # GIVEN: A bunch of mocks
    mocked_is_win.return_value = True

    # WHEN: start() is called
    start()

    # THEN: The right methods are called
    mocked_fault_handling.assert_called_once()
    mocked_freeze_support.assert_called_once()
    mocked_main.assert_called_once()
