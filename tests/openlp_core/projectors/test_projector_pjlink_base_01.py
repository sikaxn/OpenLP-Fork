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
Package to test the openlp.core.projectors.pjlink base package part 1.
"""
from unittest.mock import MagicMock, call, patch

from openlp.core.projectors.pjlink import PJLink
from openlp.core.projectors.pjlinkcommands import process_command
from openlp.core.projectors.constants import E_NOT_CONNECTED, E_UNKNOWN_SOCKET_ERROR, QSOCKET_STATE, \
    S_CONNECTED, S_CONNECTING, S_OK, S_ON, STATUS_CODE, STATUS_MSG, S_NOT_CONNECTED


def test_status_change(pjlink: PJLink):
    """
    Test process_command call with ERR2 (Parameter) status
    """
    # GIVEN: Test object
    # WHEN: process_command is called with "ERR2" status from projector
    with patch.object(pjlink, 'changeStatus') as mocked_change_status:
        process_command(projector=pjlink, cmd='POWR', data='ERR2')

    # THEN: change_status should not have been called
    assert mocked_change_status.call_count == 0


def test_socket_abort(pjlink: PJLink):
    """
    Test PJLink.socket_abort calls disconnect_from_host
    """
    # GIVEN: Test object

    # WHEN: Calling socket_abort
    with patch.object(pjlink, 'disconnect_from_host') as mocked_disconnect_from_host:
        pjlink.socket_abort()

    # THEN: disconnect_from_host should be called
    assert mocked_disconnect_from_host.called is True, 'Should have called disconnect_from_host'


def test_poll_loop_not_connected(pjlink: PJLink):
    """
    Test PJLink.poll_loop not connected return
    """
    # GIVEN: Test object
    # WHEN: PJLink.poll_loop called
    with patch.object(pjlink, 'state') as mocked_state, \
            patch.object(pjlink, 'poll_timer') as mocked_timer:
        mocked_state.return_value = QSOCKET_STATE[S_NOT_CONNECTED]
        pjlink.poll_loop()

    # THEN: poll_loop should exit without calling any other method
    mocked_timer.stop.assert_called_once_with()


def test_poll_loop_set_interval(pjlink: PJLink):
    """
    Test PJLink.poll_loop makes correct calls
    """
    # GIVEN: Test object and data
    pjlink.poll_time = 20
    pjlink.power = S_ON
    pjlink.source_available = None
    pjlink.other_info = None
    pjlink.manufacturer = None
    pjlink.model = None
    pjlink.pjlink_name = None

    # WHEN: PJLink.poll_loop is called
    with patch.object(pjlink, 'send_command') as mocked_send_command, \
            patch.object(pjlink, 'state') as mocked_state, \
            patch.object(pjlink, 'poll_timer') as mocked_poll_timer:
        mocked_state.return_value = QSOCKET_STATE[S_CONNECTED]
        mocked_poll_timer.interval.return_value = 10
        pjlink.poll_loop()

    # THEN: proper calls were made to retrieve projector data
    # First, call to update the timer with the next interval
    assert mocked_poll_timer.setInterval.called is True, 'Timer update interval should have been called'
    # Finally, should have called send_command with a list of projetctor status checks
    assert mocked_send_command.call_args_list == [
        call('INST'), call('INFO'), call('INF1'), call('INF2'), call('NAME'), call('POWR'), call('ERST'),
        call('LAMP'), call('AVMT'), call('INPT')
    ]


@patch('openlp.core.projectors.pjlink.log')
def test_projector_change_status_unknown_socket_error(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test change_status with connection error
    """
    # GIVEN: Test object
    pjlink.projector_status = 0
    pjlink.status_connect = 0

    # WHEN: change_status called with unknown socket error
    with patch.object(pjlink, 'projectorUpdateIcons') as mocked_update_icons, \
            patch.object(pjlink, 'changeStatus') as mocked_change_status:
        pjlink.change_status(status=E_UNKNOWN_SOCKET_ERROR)

    # THEN: Proper settings should change and signals sent
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Changing status to {STATUS_CODE[E_UNKNOWN_SOCKET_ERROR]} '
             f'"{STATUS_MSG[E_UNKNOWN_SOCKET_ERROR]}"'),
        call(f'({pjlink.name}) status_connect: {STATUS_CODE[E_NOT_CONNECTED]}: "{STATUS_MSG[E_NOT_CONNECTED]}"'),
        call(f'({pjlink.name}) projector_status: {STATUS_CODE[S_OK]}: "{STATUS_MSG[S_OK]}"'),
        call(f'({pjlink.name}) error_status: {STATUS_CODE[E_UNKNOWN_SOCKET_ERROR]}: '
             f'"{STATUS_MSG[E_UNKNOWN_SOCKET_ERROR]}"'),
        call(f'({pjlink.name}) Signalling error code')
    ]
    assert pjlink.projector_status == S_OK, 'Projector status should not have changed'
    assert pjlink.status_connect == E_NOT_CONNECTED, 'Status connect should be NOT CONNECTED'
    assert mocked_update_icons.emit.called is True, 'Should have called UpdateIcons'
    mocked_change_status.emit.assert_called_once_with(pjlink.ip, E_UNKNOWN_SOCKET_ERROR,
                                                      STATUS_MSG[E_UNKNOWN_SOCKET_ERROR])


@patch('openlp.core.projectors.pjlink.log')
def test_projector_change_status_connection_status_connecting(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test change_status with connecting status
    """
    # GIVEN: Test object
    pjlink.projector_status = 0
    pjlink.status_connect = 0

    # WHEN: change_status called with CONNECTING
    with patch.object(pjlink, 'projectorUpdateIcons') as mocked_update_icons, \
            patch.object(pjlink, 'changeStatus') as mocked_change_status:
        pjlink.change_status(status=S_CONNECTING)

    # THEN: Proper settings should change and signals sent
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Changing status to {STATUS_CODE[S_CONNECTING]} "{STATUS_MSG[S_CONNECTING]}"'),
        call(f'({pjlink.name}) status_connect: {STATUS_CODE[S_CONNECTING]}: "{STATUS_MSG[S_CONNECTING]}"'),
        call(f'({pjlink.name}) projector_status: {STATUS_CODE[S_OK]}: "{STATUS_MSG[S_OK]}"'),
        call(f'({pjlink.name}) error_status: {STATUS_CODE[S_OK]}: "{STATUS_MSG[S_OK]}"'),
        call(f'({pjlink.name}) Signalling status code')
    ]
    mocked_change_status.emit.assert_called_once_with(pjlink.ip, S_CONNECTING, STATUS_MSG[S_CONNECTING])
    assert pjlink.projector_status == S_OK, 'Projector status should not have changed'
    assert pjlink.status_connect == S_CONNECTING, 'Status connect should be CONNECTING'
    assert mocked_update_icons.emit.called is True, 'Should have called UpdateIcons'


@patch('openlp.core.projectors.pjlink.log')
def test_projector_change_status_connection_status_connected(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test change_status with connected status
    """
    # GIVEN: Test object
    pjlink.projector_status = 0
    pjlink.status_connect = 0

    # WHEN: change_status called with CONNECTED
    with patch.object(pjlink, 'changeStatus') as mocked_change_status:
        pjlink.change_status(status=S_CONNECTED)

    # THEN: Proper settings should change and signals sent
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Changing status to {STATUS_CODE[S_CONNECTED]} "{STATUS_MSG[S_CONNECTED]}"'),
        call(f'({pjlink.name}) status_connect: {STATUS_CODE[S_CONNECTED]}: "{STATUS_MSG[S_CONNECTED]}"'),
        call(f'({pjlink.name}) projector_status: {STATUS_CODE[S_OK]}: "{STATUS_MSG[S_OK]}"'),
        call(f'({pjlink.name}) error_status: {STATUS_CODE[S_OK]}: "{STATUS_MSG[S_OK]}"'),
        call(f'({pjlink.name}) Signalling status code')
    ]
    mocked_change_status.emit.assert_called_once_with(pjlink.ip, S_CONNECTED, 'Connected')
    assert pjlink.projector_status == S_OK, 'Projector status should not have changed'
    assert pjlink.status_connect == S_CONNECTED, 'Status connect should be CONNECTED'


@patch('openlp.core.projectors.pjlink.log')
def test_projector_change_status_connection_status_with_message(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test change_status with connection status
    """
    # GIVEN: Test object
    pjlink.projector_status = 0
    pjlink.status_connect = 0
    test_message = 'Different Status Message than default'

    # WHEN: change_status called with projector ON status
    with patch.object(pjlink, 'changeStatus') as mocked_change_status:
        pjlink.change_status(status=S_ON, msg=test_message)

    # THEN: Proper settings should change and signals sent
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Changing status to {STATUS_CODE[S_ON]} "{test_message}"'),
        call(f'({pjlink.name}) status_connect: {STATUS_CODE[S_OK]}: "{test_message}"'),
        call(f'({pjlink.name}) projector_status: {STATUS_CODE[S_ON]}: "{test_message}"'),
        call(f'({pjlink.name}) error_status: {STATUS_CODE[S_OK]}: "{test_message}"'),
        call(f'({pjlink.name}) Signalling status code')
    ]
    mocked_change_status.emit.assert_called_once_with(pjlink.ip, S_ON, test_message)
    assert pjlink.projector_status == S_ON, 'Projector status should be ON'
    assert pjlink.status_connect == S_OK, 'Status connect should not have changed'


@patch('openlp.core.projectors.pjlink.log')
def test_projector_get_av_mute_status(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test sending command to retrieve shutter/audio state
    """
    # GIVEN: Test object
    cmd = 'AVMT'

    # WHEN: get_av_mute_status is called
    with patch.object(pjlink, 'send_command') as mocked_send_command:
        pjlink.get_av_mute_status()

    # THEN: log data and send_command should have been called
    mocked_log.debug.assert_called_once_with(f'({pjlink.name}) Sending {cmd} command')
    mocked_send_command.assert_called_once_with(cmd=cmd, priority=False)


@patch('openlp.core.projectors.pjlink.log')
def test_projector_get_available_inputs(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test sending command to retrieve avaliable inputs
    """
    # GIVEN: Test object
    cmd = 'INST'

    # WHEN: get_available_inputs is called
    with patch.object(pjlink, 'send_command') as mocked_send_command:
        pjlink.get_available_inputs()

    # THEN: log data and send_command should have been called
    mocked_log.debug.assert_called_once_with(f'({pjlink.name}) Sending {cmd} command')
    mocked_send_command.assert_called_once_with(cmd=cmd)


@patch('openlp.core.projectors.pjlink.log')
def test_projector_get_error_status(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test sending command to retrieve projector error status
    """
    # GIVEN: Test object
    cmd = 'ERST'

    # WHEN: get_error_status is called
    with patch.object(pjlink, 'send_command') as mocked_send_command:
        pjlink.get_error_status()

    # THEN: log data and send_command should have been called
    mocked_log.debug.assert_called_once_with(f'({pjlink.name}) Sending {cmd} command')
    mocked_send_command.assert_called_once_with(cmd=cmd)


@patch('openlp.core.projectors.pjlink.log')
def test_projector_get_input_source(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test sending command to retrieve current input
    """
    # GIVEN: Test object
    cmd = 'INPT'

    # WHEN: get_input_source is called
    with patch.object(pjlink, 'send_command') as mocked_send_command:
        pjlink.get_input_source()

    # THEN: log data and send_command should have been called
    mocked_log.debug.assert_called_once_with(f'({pjlink.name}) Sending {cmd} command')
    mocked_send_command.assert_called_once_with(cmd=cmd)


@patch('openlp.core.projectors.pjlink.log')
def test_projector_get_lamp_status(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test sending command to retrieve lamp(s) status
    """
    # GIVEN: Test object
    cmd = 'LAMP'

    # WHEN: get_input_source is called
    with patch.object(pjlink, 'send_command') as mocked_send_command:
        pjlink.get_lamp_status()

    # THEN: log data and send_command should have been called
    mocked_log.debug.assert_called_once_with(f'({pjlink.name}) Sending {cmd} command')
    mocked_send_command.assert_called_once_with(cmd=cmd)


@patch('openlp.core.projectors.pjlink.log')
def test_projector_get_manufacturer(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test sending command to retrieve manufacturer name
    """
    # GIVEN: Test object
    cmd = 'INF1'

    # WHEN: get_input_source is called
    with patch.object(pjlink, 'send_command') as mocked_send_command:
        pjlink.get_manufacturer()

    # THEN: log data and send_command should have been called
    mocked_log.debug.assert_called_once_with(f'({pjlink.name}) Sending {cmd} command')
    mocked_send_command.assert_called_once_with(cmd=cmd)


@patch('openlp.core.projectors.pjlink.log')
def test_projector_get_model(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test sending command to get model information
    """
    # GIVEN: Test object
    cmd = 'INF2'

    # WHEN: get_input_source is called
    with patch.object(pjlink, 'send_command') as mocked_send_command:
        pjlink.get_model()

    # THEN: log data and send_command should have been called
    mocked_log.debug.assert_called_once_with(f'({pjlink.name}) Sending {cmd} command')
    mocked_send_command.assert_called_once_with(cmd=cmd)


@patch('openlp.core.projectors.pjlink.log')
def test_projector_get_name(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test sending command to get user-assigned name
    """
    # GIVEN: Test object
    cmd = 'NAME'

    # WHEN: get_input_source is called
    with patch.object(pjlink, 'send_command') as mocked_send_command:
        pjlink.get_name()

    # THEN: log data and send_command should have been called
    mocked_log.debug.assert_called_once_with(f'({pjlink.name}) Sending {cmd} command')
    mocked_send_command.assert_called_once_with(cmd=cmd)


@patch('openlp.core.projectors.pjlink.log')
def test_projector_get_other_info(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test sending command to retrieve other information
    """
    # GIVEN: Test object
    cmd = 'INFO'

    # WHEN: get_input_source is called
    with patch.object(pjlink, 'send_command') as mocked_send_command:
        pjlink.get_other_info()

    # THEN: log data and send_command should have been called
    mocked_log.debug.assert_called_once_with(f'({pjlink.name}) Sending {cmd} command')
    mocked_send_command.assert_called_once_with(cmd=cmd)


@patch('openlp.core.projectors.pjlink.log')
def test_projector_get_power_status(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test sending command to retrieve current power state
    """
    # GIVEN: Test object
    cmd = 'POWR'
    # WHEN: get_input_source is called
    with patch.object(pjlink, 'send_command') as mocked_send_command:
        pjlink.get_power_status()

    # THEN: log data and send_command should have been called
    mocked_log.debug.assert_called_once_with(f'({pjlink.name}) Sending {cmd} command')
    mocked_send_command.assert_called_once_with(cmd=cmd, priority=False)
