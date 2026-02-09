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
Test PJLink.get_data 01
"""

import logging
import openlp.core.common
import openlp.core.projectors.pjlink

from unittest.mock import DEFAULT, patch
from openlp.core.projectors.constants import PJLINK_MAX_PACKET, PJLINK_PREFIX, \
    E_AUTHENTICATION, S_AUTHENTICATE, S_CONNECT, S_CONNECTED, S_DATA_OK
from tests.resources.projector.data import TEST_HASH, TEST_PIN, TEST_SALT

test_module = openlp.core.projectors.pjlink.__name__
test_qmd5 = openlp.core.common.__name__


def test_buff_short(pjlink, caplog):
    """
    Test method with invalid short buffer
    """
    # GIVEN: Initial setup
    t_buff = "short"
    t_err = 'get_data(): Invalid packet - length'
    logs = [(f"{test_module}", logging.DEBUG,
             f'({pjlink.entry.name}) get_data(buffer="{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting ignore_class to "False"')]

    with patch.object(openlp.core.projectors.pjlink, "process_command") as mock_command, \
         patch.multiple(pjlink,
                        _trash_buffer=DEFAULT,
                        receive_data_signal=DEFAULT) as mock_pjlink:
        # WHEN: get_data called
        caplog.set_level(logging.DEBUG)
        t_check = pjlink.get_data(buff=t_buff)

        # THEN: t_check should be None and log entry made
        assert t_check is None, "Invalid return code"
        assert caplog.record_tuples == logs, "Invalid log entries"
        mock_pjlink['_trash_buffer'].assert_called_once_with(msg=t_err)
        mock_pjlink['receive_data_signal'].assert_called_once()
        mock_command.assert_not_called()


def test_buff_long(pjlink, caplog):
    """
    Test method with invalid long buffer
    """
    # GIVEN: Initial setup
    t_buff = "X" * (PJLINK_MAX_PACKET + 10)
    t_err = f'get_data(): Invalid packet - too long ({len(t_buff)} bytes)'
    logs = [(f"{test_module}", logging.DEBUG,
             f'({pjlink.entry.name}) get_data(buffer="{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting ignore_class to "False"')]

    with patch.object(openlp.core.projectors.pjlink, "process_command") as mock_command, \
         patch.multiple(pjlink,
                        _trash_buffer=DEFAULT,
                        receive_data_signal=DEFAULT) as mock_pjlink:
        # WHEN: get_data called
        caplog.set_level(logging.DEBUG)
        t_check = pjlink.get_data(buff=t_buff)

        # THEN: t_check should be None and log entry made
        assert t_check is None, "Invalid return code"
        assert caplog.record_tuples == logs, "Invalid log entries"
        mock_pjlink['_trash_buffer'].assert_called_once_with(msg=t_err)
        mock_pjlink['receive_data_signal'].assert_called_once()
        mock_command.assert_not_called()


def test_invalid_prefix(pjlink, caplog):
    """
    Test method with invalid PJLink prefix character
    """
    # GIVEN: Initial setup
    t_buff = "#1CLSS=OK"
    t_err = 'get_data(): Invalid packet - PJLink prefix missing'
    logs = [(f"{test_module}", logging.DEBUG,
             f'({pjlink.entry.name}) get_data(buffer="{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting ignore_class to "False"')]

    with patch.object(openlp.core.projectors.pjlink, "process_command") as mock_command, \
         patch.multiple(pjlink,
                        _trash_buffer=DEFAULT,
                        receive_data_signal=DEFAULT) as mock_pjlink:
        # WHEN: get_data called
        caplog.set_level(logging.DEBUG)
        t_check = pjlink.get_data(buff=t_buff)

        # THEN: t_check should be None and log entry made
        assert t_check is None, "Invalid return code"
        assert caplog.record_tuples == logs, "Invalid log entries"
        mock_pjlink['_trash_buffer'].assert_called_once_with(msg=t_err)
        mock_pjlink['receive_data_signal'].assert_called_once()
        mock_command.assert_not_called()


def test_missing_equal(pjlink, caplog):
    """
    Test method with missing command/data separator
    """
    # GIVEN: Initial setup
    t_buff = f"{PJLINK_PREFIX}1CLSS OK"
    t_err = 'get_data(): Invalid reply - Does not have "="'
    logs = [(f"{test_module}", logging.DEBUG,
             f'({pjlink.entry.name}) get_data(buffer="{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting ignore_class to "False"')]

    with patch.object(openlp.core.projectors.pjlink, "process_command") as mock_command, \
         patch.multiple(pjlink,
                        _trash_buffer=DEFAULT,
                        receive_data_signal=DEFAULT) as mock_pjlink:

        # WHEN: get_data called
        caplog.set_level(logging.DEBUG)
        t_check = pjlink.get_data(buff=t_buff)

        # THEN: t_check should be None and log entry made
        assert t_check is None, "Invalid return code"
        assert caplog.record_tuples == logs, "Invalid log entries"
        mock_pjlink['_trash_buffer'].assert_called_once_with(msg=t_err)
        mock_pjlink['receive_data_signal'].assert_called_once()
        mock_command.assert_not_called()


def test_invalid_command(pjlink, caplog):
    """
    Test method with invalid command
    """
    # GIVEN: Initial setup
    t_cmd = "CLASSS"
    t_ver = "1"
    t_data = "1"
    t_buff = f"{PJLINK_PREFIX}{t_ver}{t_cmd}={t_data}"
    t_err = f'get_data(): Invalid packet - unknown command "{t_cmd}"'
    logs = [(f"{test_module}", logging.DEBUG,
             f'({pjlink.entry.name}) get_data(buffer="{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting ignore_class to "False"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data(): Checking new data "{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() header="{PJLINK_PREFIX}{t_ver}{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() version="{t_ver}" cmd="{t_cmd}" data="{t_data}"')
            ]
    with patch.object(openlp.core.projectors.pjlink, "process_command") as mock_command, \
         patch.multiple(pjlink,
                        _trash_buffer=DEFAULT,
                        receive_data_signal=DEFAULT) as mock_pjlink:

        # WHEN: get_data called
        caplog.set_level(logging.DEBUG)
        t_check = pjlink.get_data(buff=t_buff)

        # THEN: t_check should be None and log entry made
        assert t_check is None, "Invalid return code"
        assert caplog.record_tuples == logs, "Invalid log entries"
        mock_pjlink['_trash_buffer'].assert_called_once_with(msg=t_err)
        mock_pjlink['receive_data_signal'].assert_called_once()
        mock_command.assert_not_called()


def test_mismatch_command_versions(pjlink, caplog):
    """
    Test method with pjlink.pjlink_class < cmd.class
    """
    # GIVEN: Initial setup
    t_cmd = "CLSS"
    t_ver = "2"
    t_data = "1"
    t_buff = f"{PJLINK_PREFIX}{t_ver}{t_cmd}={t_data}"
    t_err = 'get_data() Command reply version does not match a valid command version'
    logs = [(f"{test_module}", logging.DEBUG,
             f'({pjlink.entry.name}) get_data(buffer="{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting ignore_class to "False"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data(): Checking new data "{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() header="{PJLINK_PREFIX}{t_ver}{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() version="{t_ver}" cmd="{t_cmd}" data="{t_data}"')
            ]

    with patch.object(openlp.core.projectors.pjlink, "process_command") as mock_command, \
         patch.multiple(pjlink,
                        _trash_buffer=DEFAULT,
                        receive_data_signal=DEFAULT) as mock_pjlink:

        # WHEN: get_data called
        caplog.set_level(logging.DEBUG)
        t_check = pjlink.get_data(buff=t_buff)

        # THEN: t_check should be None and log entry made
        assert t_check is None, "Invalid return code"
        assert caplog.record_tuples == logs, "Invalid log entries"
        mock_pjlink['receive_data_signal'].assert_called_once()
        mock_pjlink['_trash_buffer'].assert_called_once_with(msg=t_err)
        mock_command.assert_not_called()


def test_mismatch_class_versions(pjlink, caplog):
    """
    Test method with pjlink.pjlink_class < cmd.class
    """
    # GIVEN: Initial setup
    t_cmd = "FILT"
    t_ver = "2"
    t_data = "2"
    t_buff = f"{PJLINK_PREFIX}{t_ver}{t_cmd}={t_data}"
    logs = [(f"{test_module}", logging.DEBUG,
             f'({pjlink.entry.name}) get_data(buffer="{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting ignore_class to "False"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data(): Checking new data "{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() header="{PJLINK_PREFIX}{t_ver}{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() version="{t_ver}" cmd="{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.WARNING,
             f'({pjlink.entry.name}) get_data(): pjlink_class={pjlink.pjlink_class} packet={t_ver}'),
            (f'{test_module}', logging.WARNING,
             f'({pjlink.entry.name}) get_data(): Projector returned class reply higher than projector stated class')
            ]
    with patch.object(openlp.core.projectors.pjlink, "process_command") as mock_command, \
         patch.multiple(pjlink,
                        _trash_buffer=DEFAULT,
                        receive_data_signal=DEFAULT) as mock_pjlink:
        pjlink.pjlink_class = 1  # Set class to 1 and call with cmd class = 2

        # WHEN: get_data called
        caplog.set_level(logging.DEBUG)
        t_check = pjlink.get_data(buff=t_buff)

        # THEN: t_check should be None and log entry made
        assert t_check is None, "Invalid return code"
        assert caplog.record_tuples == logs, "Invalid log entries"
        mock_pjlink['receive_data_signal'].assert_called_once()
        mock_command.assert_not_called()


def test_ignore_class_versions(pjlink, caplog):
    """
    Test method with pjlink.pjlink_class < cmd.class
    """
    # GIVEN: Initial setup
    t_cmd = "FILT"
    t_ver = "2"
    t_data = "2"
    t_buff = f"{PJLINK_PREFIX}{t_ver}{t_cmd}={t_data}"
    logs = [(f"{test_module}", logging.DEBUG,
             f'({pjlink.entry.name}) get_data(buffer="{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting ignore_class to "True"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data(): Checking new data "{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() header="{PJLINK_PREFIX}{t_ver}{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() version="{t_ver}" cmd="{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.WARNING,
             f'({pjlink.entry.name}) get_data(): pjlink_class={pjlink.pjlink_class} packet={t_ver}')
            ]
    with patch.object(openlp.core.projectors.pjlink, "process_command") as mock_command, \
         patch.multiple(pjlink,
                        _trash_buffer=DEFAULT,
                        receive_data_signal=DEFAULT) as mock_pjlink:
        pjlink.pjlink_class = 1  # Set class to 1 and call with cmd class = 2
        mock_command.return_value = None

        # WHEN: get_data called with ignore_class=True
        caplog.set_level(logging.DEBUG)
        t_check = pjlink.get_data(buff=t_buff, ignore_class=True)

        # THEN: t_check should be None and log entry made
        assert t_check is None, "Invalid return code"
        assert caplog.record_tuples == logs, "Invalid log entries"
        mock_pjlink['receive_data_signal'].assert_called_once()
        mock_command.assert_called_with(pjlink, t_cmd, t_data)


def test_s_data_ok(pjlink, caplog):
    """
    Test projector returns "OK"
    """
    t_cmd = "INPT"
    t_ver = "1"
    t_data = "OK"
    t_buff = f"{PJLINK_PREFIX}{t_ver}{t_cmd}={t_data}"
    logs = [(f"{test_module}", logging.DEBUG,
             f'({pjlink.entry.name}) get_data(buffer="{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting ignore_class to "False"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data(): Checking new data "{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() header="{PJLINK_PREFIX}{t_ver}{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() version="{t_ver}" cmd="{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) OK returned - resending command')
            ]
    with patch.object(openlp.core.projectors.pjlink, "process_command") as mock_command, \
         patch.multiple(pjlink,
                        _trash_buffer=DEFAULT,
                        receive_data_signal=DEFAULT,
                        send_command=DEFAULT) as mock_pjlink:
        mock_command.return_value = S_DATA_OK

        # WHEN: get_data called with OK
        caplog.set_level(logging.DEBUG)
        t_check = pjlink.get_data(buff=t_buff)

        # THEN: t_check should be None and log entry made
        assert t_check is None, "Invalid return code"
        assert caplog.record_tuples == logs, "Invalid log entries"
        mock_pjlink['receive_data_signal'].assert_called_once()
        mock_pjlink['_trash_buffer'].assert_not_called()
        mock_pjlink['send_command'].assert_called_with(cmd=t_cmd, priority=True)
        mock_command.assert_called_with(pjlink, t_cmd, t_data)


def test_s_connect(pjlink, caplog):
    """
    Test projector connect with no authenticate
    """
    t_cmd = "PJLINK"
    t_ver = "1"
    t_data = "0"
    t_buff = f"{PJLINK_PREFIX}{t_ver}{t_cmd}={t_data}"
    logs = [(f"{test_module}", logging.DEBUG,
             f'({pjlink.entry.name}) get_data(buffer="{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting ignore_class to "False"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data(): Checking new data "{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() header="{PJLINK_PREFIX}{t_ver}{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() version="{t_ver}" cmd="{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Connecting normal')
            ]
    with patch.object(openlp.core.projectors.pjlink, "process_command") as mock_command, \
         patch.multiple(pjlink,
                        _trash_buffer=DEFAULT,
                        receive_data_signal=DEFAULT,
                        send_command=DEFAULT,
                        change_status=DEFAULT,
                        readyRead=DEFAULT,
                        get_socket=DEFAULT) as mock_pjlink:
        mock_command.return_value = S_CONNECT

        # WHEN: get_data called with OK
        caplog.set_level(logging.DEBUG)
        t_check = pjlink.get_data(buff=t_buff)

        # THEN: t_check should be None and log entry made
        assert t_check is None, "Invalid return code"
        assert caplog.record_tuples == logs, "Invalid log entries"
        mock_pjlink['receive_data_signal'].assert_called_once()
        mock_pjlink['_trash_buffer'].assert_not_called()
        mock_pjlink['send_command'].assert_called_with(cmd='CLSS', priority=True)
        mock_pjlink['change_status'].assert_called_with(S_CONNECTED)
        mock_pjlink['readyRead'].connect.assert_called_once_with(mock_pjlink['get_socket'])
        mock_command.assert_called_with(pjlink, t_cmd, t_data)


def test_s_authenticate(pjlink, caplog):
    """
    Test projector connect with no authenticate
    """
    '''
    Projector sends "PJLINK 1 <salt>"
    Combine salt+pin
    Send first command "<hash><PJLINK_PREFIX><CLASS><CMD><sp><OPTS>"
    Projector will either:
        - Not reply (socket timeout) indicating invalid hash
        - Reply with command reply
    Example in documentation:
        - Send "<cr>"
        - Received "PJLINK 1 498e4a67"
            - Prefix = "%"
            - Salt = "498e4a67"
            - Pin  = "JBMIAProjectorLink"
            - Hash = "5d8409bc1c3fa39749434aa3a5c38682"
        - Send "5d8409bc1c3fa39749434aa3a5c38682%1CLSS<sp>?"
        - Reply "%1CLSS=1"
    '''
    # GIVEN: Initial setup
    t_cmd = "PJLINK"
    t_ver = "1"
    t_data = f"1 {TEST_SALT}"
    t_buff = f"{PJLINK_PREFIX}{t_ver}{t_cmd}={t_data}"
    logs = [(f"{test_module}", logging.DEBUG,
             f'({pjlink.entry.name}) get_data(buffer="{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting ignore_class to "False"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data(): Checking new data "{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() header="{PJLINK_PREFIX}{t_ver}{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() version="{t_ver}" cmd="{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Connecting with pin'),
            (f'{test_qmd5}.__init__', logging.DEBUG,
             f'qmd5_hash(salt="b\'{TEST_SALT}\'"'),
            (f'{test_qmd5}.__init__', logging.DEBUG,
             f'qmd5_hash() returning "b\'{TEST_HASH}\'"')
            ]
    with patch.object(openlp.core.projectors.pjlink, "process_command") as mock_command, \
         patch.multiple(pjlink,
                        _trash_buffer=DEFAULT,
                        receive_data_signal=DEFAULT,
                        send_command=DEFAULT,
                        change_status=DEFAULT,
                        readyRead=DEFAULT,
                        get_socket=DEFAULT) as mock_pjlink:
        mock_command.return_value = S_AUTHENTICATE
        pjlink.pin = TEST_PIN

        # WHEN: get_data called with OK
        caplog.set_level(logging.DEBUG)
        t_check = pjlink.get_data(buff=t_buff)

        # THEN: t_check should be None and log entry made
        assert t_check is None, "Invalid return code"
        assert caplog.record_tuples == logs, "Invalid log entries"
        mock_pjlink['receive_data_signal'].assert_called_once()
        mock_pjlink['_trash_buffer'].assert_not_called()
        mock_pjlink['send_command'].assert_called_with(cmd='CLSS', salt=TEST_HASH, priority=True)
        mock_pjlink['change_status'].assert_called_with(S_CONNECTED)
        mock_pjlink['readyRead'].connect.assert_called_once_with(mock_pjlink['get_socket'])
        mock_command.assert_called_with(pjlink, t_cmd, t_data)


def test_e_authenticate(pjlink, caplog):
    """
    Test projector connect with invalid pin
    """
    t_salt = '498e4a67'
    t_cmd = "PJLINK"
    t_ver = "1"
    t_data = f"1 {t_salt}"
    t_buff = f"{PJLINK_PREFIX}{t_ver}{t_cmd}={t_data}"
    logs = [(f"{test_module}", logging.DEBUG,
             f'({pjlink.entry.name}) get_data(buffer="{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting ignore_class to "False"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data(): Checking new data "{t_buff}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() header="{PJLINK_PREFIX}{t_ver}{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) get_data() version="{t_ver}" cmd="{t_cmd}" data="{t_data}"'),
            (f'{test_module}', logging.WARNING,
             f'({pjlink.entry.name}) Failed authentication - disconnecting')
            ]
    with patch.object(openlp.core.projectors.pjlink, "process_command") as mock_command, \
         patch.multiple(pjlink,
                        _trash_buffer=DEFAULT,
                        receive_data_signal=DEFAULT,
                        disconnect_from_host=DEFAULT,
                        change_status=DEFAULT,
                        projectorAuthentication=DEFAULT) as mock_pjlink:
        mock_command.return_value = E_AUTHENTICATION

        # WHEN: get_data called with OK
        caplog.set_level(logging.DEBUG)
        t_check = pjlink.get_data(buff=t_buff)

        # THEN: t_check should be None and log entry made
        assert t_check is None, "Invalid return code"
        assert caplog.record_tuples == logs, "Invalid log entries"
        mock_pjlink['receive_data_signal'].assert_called_once()
        mock_pjlink['_trash_buffer'].assert_not_called()
        mock_pjlink['change_status'].assert_called_with(status=E_AUTHENTICATION)
        mock_pjlink['projectorAuthentication'].emit.assert_called_with(pjlink.entry.name)
        mock_command.assert_called_with(pjlink, t_cmd, t_data)
