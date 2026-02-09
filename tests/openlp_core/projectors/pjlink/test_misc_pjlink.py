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
Test PJLink._get_status()
"""

import logging

import openlp.core.projectors.pjlink

from PySide6 import QtNetwork
from unittest.mock import DEFAULT, MagicMock, patch

from openlp.core.projectors.constants import QSOCKET_STATE, STATUS_CODE, STATUS_MSG, \
    E_GENERAL, S_CONNECTED, S_NOT_CONNECTED, S_CONNECTING, S_OK, \
    PJLINK_PORT

from tests.resources.projector.data import TEST2_DATA

test_module = openlp.core.projectors.pjlink.__name__


def test_connect_to_host_connected(pjlink, caplog):
    """
    Test connect_to_host returns when already connected
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({pjlink.entry.name}) connect_to_host(): Starting connection'),
            (test_module, logging.WARNING, f'({pjlink.entry.name}) connect_to_host(): Already connected - returning')
            ]

    mock_state = MagicMock()
    mock_state.return_value = QSOCKET_STATE[S_CONNECTED]
    # Set error_status to something not normally used for this test
    pjlink.error_status = E_GENERAL

    with patch.multiple(pjlink,
                        state=mock_state,
                        change_status=DEFAULT,
                        connectToHost=DEFAULT) as mock_pjlink:
        # WHEN: Called
        caplog.clear()
        pjlink.connect_to_host()

        # THEN: Appropriate entries and calls
        assert caplog.record_tuples == logs, 'Invalid log entries'
        assert pjlink.error_status == E_GENERAL, 'Error status should not have change'
        mock_pjlink['change_status'].assert_not_called()
        mock_pjlink['connectToHost']. assert_not_called()


def test_connect_to_host_not_connected(pjlink, caplog):
    """
    Test connect_to_host calls appropriate methods to connect
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({pjlink.entry.name}) connect_to_host(): Starting connection'),
            ]

    mock_state = MagicMock()
    mock_state.return_value = QSOCKET_STATE[S_NOT_CONNECTED]
    pjlink.error_status = E_GENERAL

    with patch.multiple(pjlink,
                        state=mock_state,
                        change_status=DEFAULT,
                        connectToHost=DEFAULT) as mock_pjlink:
        # WHEN: Called
        caplog.clear()
        pjlink.connect_to_host()

        # THEN: Appropriate entries and calls
        assert caplog.record_tuples == logs, 'Invalid log entries'
        assert pjlink.error_status == S_OK, 'Error status should have changed to S_OK'
        mock_pjlink['change_status'].assert_called_with(S_CONNECTING)
        mock_pjlink['connectToHost'].assert_called_with(pjlink.ip, pjlink.port)


def test_get_buffer_me(pjlink, caplog):
    """
    Test get_buffer() calls get_data()
    """
    # NOTE: Verify pjlink.qhost == host.isEqual() works as expected
    # NOTE: May have to fix get_buffer() on this test
    # GIVEN: Test setup
    t_host = pjlink.qhost
    t_port = pjlink.port
    t_data = "Test me with a spoon"

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({pjlink.entry.name}) Received data from {t_host.toString()}'),
            (test_module, logging.DEBUG, f'({pjlink.entry.name}) get_buffer(data="{t_data}")')
            ]

    with patch.object(pjlink, 'get_data') as mock_data:

        # WHEN: Called
        pjlink.get_buffer(host=t_host, port=t_port, data=t_data)

        # THEN: Appropriate logs and calls
        assert caplog.record_tuples == logs, 'Invalid log entries'
        mock_data.assert_called_with(buff=t_data)


def test_get_buffer_not_me(pjlink, caplog):
    """
    Test get_buffer() returns without calls
    """
    # GIVEN: Test setup
    t_host = QtNetwork.QHostAddress(TEST2_DATA['ip'])
    t_port = pjlink.port
    t_data = "Test me with a spoon"

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({pjlink.entry.name}) Ignoring data for {t_host.toString()} - not me')]

    with patch.object(pjlink, 'get_data') as mock_data:

        # WHEN: Called
        pjlink.get_buffer(host=t_host, port=t_port, data=t_data)

        # THEN: Appropriate logs and calls
        assert caplog.record_tuples == logs, 'Invalid log entries'
        mock_data.assert_not_called()


def test_get_buffer_wrong_port(pjlink, caplog):
    """
    Test get_buffer() returns without calls
    """
    # GIVEN: Test setup
    t_host = pjlink.qhost
    t_port = PJLINK_PORT
    t_data = "Test me with a spoon"

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({pjlink.entry.name}) Ignoring data for {t_host.toString()} - not me')]

    with patch.object(pjlink, 'get_data') as mock_data:

        # WHEN: Called
        pjlink.get_buffer(host=t_host, port=t_port, data=t_data)

        # THEN: Appropriate logs and calls
        assert caplog.record_tuples == logs, 'Invalid log entries'
        mock_data.assert_not_called()


def test_get_status_invalid_string(pjlink):
    """
    Test get_status returns invalid when given a string
    """
    # GIVEN: Test setup
    t_status = "String"

    # WHEN: Called with a string
    t_code, t_msg = pjlink._get_status(status=t_status)

    # THEN: Appropriate return values
    assert t_code == -1, 'Should have returned code -1'
    assert t_msg is None, 'Should have returned message None'


def test_get_status_invalid_string_digit(pjlink):
    """
    Test get_status returns invalid when given a digit in a string
    """
    # GIVEN: Test setup
    t_status = "1"

    # WHEN: Called with a string
    t_code, t_msg = pjlink._get_status(status=t_status)

    # THEN: Appropriate return values
    assert t_code == -1, 'Should have returned code -1'
    assert t_msg is None, 'Should have returned message None'


def test_get_status_invalid_code(pjlink):
    """
    Test get_status returns invalid when given an invalid code
    """
    # GIVEN: Test setup
    t_status = E_GENERAL - 1

    # WHEN: Called with a string
    t_code, t_msg = pjlink._get_status(status=t_status)

    # THEN: Appropriate return values
    assert t_code is None, 'hould have returned code None'
    assert t_msg is None, 'Should have returned message None'


def test_get_status_valid(pjlink):
    """
    Test get_status returns valid status message
    """
    # GIVEN: Test setup
    t_status = E_GENERAL

    # WHEN: Called with a string
    t_code, t_msg = pjlink._get_status(status=t_status)

    # THEN: Appropriate return values
    assert t_code == STATUS_CODE[E_GENERAL], f'Should have returned "{STATUS_CODE[t_status]}"'
    assert t_msg == STATUS_MSG[E_GENERAL], f'Should have returned "{STATUS_MSG[t_status]}"'


def test_receive_data_signal(pjlink):
    """
    Test PJLink.receive_data_signal sets and sends valid signal
    """
    # GIVEN: Test setup
    pjlink.send_busy = True

    with patch.object(pjlink, 'projectorReceivedData') as mock_receive:

        # WHEN: Called
        pjlink.receive_data_signal()

        # THEN: Appropriate calls and settings
        assert pjlink.send_busy is False, 'Did not clear send_busy'
        mock_receive.emit.assert_called_once()


def test_status_timer_update_two_callbacks(pjlink, caplog):
    """
    Test status_timer_update calls status_timer.stop when no updates listed
    """
    # GIVEN: Test setup
    t_cb1 = MagicMock()
    t_cb2 = MagicMock()

    pjlink.status_timer_checks = {'ONE': t_cb1,
                                  'TWO': t_cb2}

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({pjlink.entry.name}) Status update call for ONE'),
            (test_module, logging.DEBUG, f'({pjlink.entry.name}) Status update call for TWO')]

    with patch.object(pjlink, 'status_timer') as mock_timer:

        # WHEN: Called
        caplog.clear()
        pjlink.status_timer_update()

        # THEN: Returns with timer stop called
        assert caplog.record_tuples == logs, 'Invalid log entries'
        mock_timer.stop.assert_not_called()
        t_cb1.assert_called_once_with(priority=True)
        t_cb2.assert_called_once_with(priority=True)


def test_status_timer_update_empty(pjlink, caplog):
    """
    Test status_timer_update calls status_timer.stop when no updates listed
    """
    # GIVEN: Test setup
    pjlink.status_timer_checks = {}

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.WARNING,
             f'({pjlink.entry.name}) status_timer_update() called when no callbacks - Race condition?')]

    with patch.object(pjlink, 'status_timer') as mock_timer:

        # WHEN: Called
        caplog.clear()
        pjlink.status_timer_update()

        # THEN: Returns with timer stop called
        assert caplog.record_tuples == logs, 'Invalid log entries'
        mock_timer.stop.assert_called_once()
