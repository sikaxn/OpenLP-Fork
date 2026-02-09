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
Test PJLink.check_login
"""

import logging

import openlp.core.projectors.pjlink

from unittest.mock import DEFAULT, patch
from openlp.core.projectors.constants import PJLINK_PREFIX, E_SOCKET_TIMEOUT
from tests.resources.projector.data import TEST_SALT
test_module = openlp.core.projectors.pjlink.__name__


def test_socket_timeout(pjlink, caplog):
    """
    Test return when socket timeout
    """
    # GIVEN: Test setup
    t_data = None
    t_readLine = None

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({pjlink.name}) check_login(data="{t_data}")'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() Waiting for readyRead()'),
            (test_module, logging.ERROR, f'({pjlink.name}) Socket timeout waiting for login'),
            ]

    with patch.multiple(pjlink,
                        waitForReadyRead=DEFAULT,
                        get_data=DEFAULT,
                        change_status=DEFAULT,
                        readLine=DEFAULT,
                        read=DEFAULT,
                        disconnect_from_host=DEFAULT,
                        write=DEFAULT) as mock_pjlink:
        mock_pjlink['waitForReadyRead'].return_value = False
        mock_pjlink['readLine'].return_value = t_readLine

        # WHEN: Called with no data
        caplog.clear()
        pjlink.check_login(data=None)

        # THEN: Log entries and get_data not called
        assert caplog.record_tuples == logs, 'Invalid log entires'
        mock_pjlink['change_status'].assert_called_with(E_SOCKET_TIMEOUT)
        mock_pjlink['get_data'].assert_not_called()
        mock_pjlink['read'].assert_not_called()
        mock_pjlink['disconnect_from_host'].assert_not_called()


def test_readLine_no_data(pjlink, caplog):
    """
    Test return when readLine data is None
    """
    # GIVEN: Test setup
    t_data = None
    t_readLine = None

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({pjlink.name}) check_login(data="{t_data}")'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() Waiting for readyRead()'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() Checking for data'),
            (test_module, logging.WARNING, f'({pjlink.name}) read is None - socket error?'),
            ]

    with patch.multiple(pjlink,
                        waitForReadyRead=DEFAULT,
                        get_data=DEFAULT,
                        change_status=DEFAULT,
                        readLine=DEFAULT,
                        read=DEFAULT,
                        disconnect_from_host=DEFAULT,
                        write=DEFAULT) as mock_pjlink:
        mock_pjlink['waitForReadyRead'].return_value = True
        mock_pjlink['readLine'].return_value = t_readLine

        # WHEN: Called with no data
        caplog.clear()
        pjlink.check_login(data=None)

        # THEN: Log entries and get_data not called
        assert caplog.record_tuples == logs, 'Invalid log entires'
        mock_pjlink['change_status'].assert_not_called()
        mock_pjlink['get_data'].assert_not_called()
        mock_pjlink['read'].assert_not_called()
        mock_pjlink['disconnect_from_host'].assert_not_called()


def test_readLine_short_data(pjlink, caplog):
    """
    Test return when readLine data < minimum packet size
    """
    # GIVEN: Test setup
    t_data = None
    t_readLine = 'PJLink'

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({pjlink.name}) check_login(data="{t_data}")'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() Waiting for readyRead()'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() Checking for data'),
            (test_module, logging.WARNING, f'({pjlink.name}) Not enough data read - skipping'),
            ]

    with patch.multiple(pjlink,
                        waitForReadyRead=DEFAULT,
                        get_data=DEFAULT,
                        change_status=DEFAULT,
                        readLine=DEFAULT,
                        read=DEFAULT,
                        disconnect_from_host=DEFAULT,
                        write=DEFAULT) as mock_pjlink:
        mock_pjlink['waitForReadyRead'].return_value = True
        mock_pjlink['readLine'].return_value = t_readLine

        # WHEN: Called with no data
        caplog.clear()
        pjlink.check_login(data=None)

        # THEN: Log entries and get_data not called
        assert caplog.record_tuples == logs, 'Invalid log entires'
        mock_pjlink['change_status'].assert_not_called()
        mock_pjlink['get_data'].assert_not_called()
        mock_pjlink['read'].assert_not_called()
        mock_pjlink['disconnect_from_host'].assert_not_called()


def test_readLine_invalid_data(pjlink, caplog):
    """
    Test return when readLine data < minimum packet size
    """
    # GIVEN: Test setup
    t_data = None
    t_readLine = 'SOMETHING 0'

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({pjlink.name}) check_login(data="{t_data}")'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() Waiting for readyRead()'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() Checking for data'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() read "{t_readLine}"'),
            (test_module, logging.ERROR, f'({pjlink.name}) Invalid initial packet received - closing socket')
            ]

    with patch.multiple(pjlink,
                        waitForReadyRead=DEFAULT,
                        get_data=DEFAULT,
                        change_status=DEFAULT,
                        readLine=DEFAULT,
                        read=DEFAULT,
                        disconnect_from_host=DEFAULT,
                        write=DEFAULT) as mock_pjlink:
        mock_pjlink['waitForReadyRead'].return_value = True
        mock_pjlink['readLine'].return_value = t_readLine

        # WHEN: Called with no data
        caplog.clear()
        pjlink.check_login(data=None)

        print(caplog.record_tuples)

        # THEN: Log entries and get_data not called
        assert caplog.record_tuples == logs, 'Invalid log entires'
        mock_pjlink['change_status'].assert_not_called()
        mock_pjlink['get_data'].assert_not_called()
        mock_pjlink['read'].assert_called_once()
        mock_pjlink['disconnect_from_host'].assert_called_once()


def test_readLine_no_authentication(pjlink, caplog):
    """
    Test return when readLine data < minimum packet size
    """
    # GIVEN: Test setup
    t_data = None
    t_readLine = 'PJLink 0'
    t_return = f'{PJLINK_PREFIX}1PJLink=0'

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({pjlink.name}) check_login(data="{t_data}")'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() Waiting for readyRead()'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() Checking for data'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() read "{t_readLine}"'),
            (test_module, logging.DEBUG,
             f'({pjlink.name}) check_login(): Formatting initial connection prompt to PJLink packet')
            ]

    with patch.multiple(pjlink,
                        waitForReadyRead=DEFAULT,
                        get_data=DEFAULT,
                        change_status=DEFAULT,
                        readLine=DEFAULT,
                        read=DEFAULT,
                        disconnect_from_host=DEFAULT,
                        write=DEFAULT) as mock_pjlink:
        mock_pjlink['waitForReadyRead'].return_value = True
        mock_pjlink['readLine'].return_value = t_readLine

        # WHEN: Called with no data
        caplog.clear()
        pjlink.check_login(data=None)

        print(caplog.record_tuples)

        # THEN: Log entries and get_data not called
        assert caplog.record_tuples == logs, 'Invalid log entires'
        mock_pjlink['change_status'].assert_not_called()
        mock_pjlink['read'].assert_called_once()
        mock_pjlink['disconnect_from_host'].assert_not_called()
        mock_pjlink['get_data'].assert_called_with(t_return)


def test_readLine_with_authentication(pjlink, caplog):
    """
    Test return when readLine data < minimum packet size
    """
    # GIVEN: Test setup
    t_data = None
    t_readLine = f'PJLink 1 {TEST_SALT}'
    t_return = f'{PJLINK_PREFIX}1PJLink=1 {TEST_SALT}'

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({pjlink.name}) check_login(data="{t_data}")'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() Waiting for readyRead()'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() Checking for data'),
            (test_module, logging.DEBUG, f'({pjlink.name}) check_login() read "{t_readLine}"'),
            (test_module, logging.DEBUG,
             f'({pjlink.name}) check_login(): Formatting initial connection prompt to PJLink packet')
            ]

    with patch.multiple(pjlink,
                        waitForReadyRead=DEFAULT,
                        get_data=DEFAULT,
                        change_status=DEFAULT,
                        readLine=DEFAULT,
                        read=DEFAULT,
                        disconnect_from_host=DEFAULT,
                        write=DEFAULT) as mock_pjlink:
        mock_pjlink['waitForReadyRead'].return_value = True
        mock_pjlink['readLine'].return_value = t_readLine

        # WHEN: Called with no data
        caplog.clear()
        pjlink.check_login(data=None)

        print(caplog.record_tuples)

        # THEN: Log entries and get_data not called
        assert caplog.record_tuples == logs, 'Invalid log entires'
        mock_pjlink['change_status'].assert_not_called()
        mock_pjlink['read'].assert_called_once()
        mock_pjlink['disconnect_from_host'].assert_not_called()
        mock_pjlink['get_data'].assert_called_with(t_return)
