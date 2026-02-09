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
Tests for PJLink command routing
"""

import logging
import openlp.core.projectors.pjlinkcommands

from unittest.mock import MagicMock, patch

from openlp.core.projectors.pjlinkcommands import process_command
from openlp.core.projectors.constants import PJLINK_ERRORS, STATUS_CODE, \
    E_AUTHENTICATION, E_UNDEFINED, E_PARAMETER, E_UNAVAILABLE, E_PROJECTOR, \
    S_DATA_OK, STATUS_MSG

test_module = openlp.core.projectors.pjlinkcommands.__name__


def test_valid_command(pjlink, caplog):
    """
    Test valid command routing
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    test_cmd = "CLSS"
    test_data = "1"
    test_return = None
    logs = [(f'{test_module}', logging.DEBUG,
             f'({pjlink.name}) Processing command "{test_cmd}" with data "{test_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.name}) Calling function for {test_cmd}')
            ]
    caplog.clear()
    with patch.dict(openlp.core.projectors.pjlinkcommands.pjlink_functions,
                    {test_cmd: MagicMock(return_value=None)}) as mock_clss:
        # WHEN: called with CLSS command
        chk = process_command(projector=pjlink, cmd=test_cmd, data=test_data)

        # THEN: Appropriate log entries should have been made and methods called/not called
        assert chk is test_return, f'"{test_data}" reply should have returned {STATUS_CODE[test_return]}'
        mock_clss[test_cmd].assert_called_with(projector=pjlink, data=test_data)
        assert caplog.record_tuples == logs, 'Log entries mismatch'


def test_invalid_command(pjlink, caplog):
    """
    Test invalid command
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    test_cmd = "DONTCARE"
    test_data = "1"
    test_return = None
    logs = [(f'{test_module}', logging.DEBUG,
             f'({pjlink.name}) Processing command "{test_cmd}" with data "{test_data}"'),
            (f'{test_module}', logging.WARNING,
             f'({pjlink.name}) Unable to process command="DONTCARE" (Future option?)'),
            ]

    # WHEN: called with invalid command and data
    caplog.clear()
    chk = process_command(projector=pjlink, cmd=test_cmd, data=test_data)

    # THEN: Appropriate log entries should have been made and methods called/not called
    assert chk is test_return, 'Invalid command should have returned None'
    assert caplog.record_tuples == logs, 'Log entries mismatch'


def test_data_ok(pjlink, caplog):
    """
    Test data == 'OK'
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    test_cmd = "CLSS"
    test_data = "OK"
    test_reply = "OK"
    test_return = S_DATA_OK
    logs = [(f'{test_module}', logging.DEBUG,
             f'({pjlink.name}) Processing command "{test_cmd}" with data "{test_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.name}) Command "{test_cmd}" returned {test_reply}')
            ]

    # WHEN: called with OK
    caplog.clear()
    chk = process_command(projector=pjlink, cmd=test_cmd, data=test_data)

    # THEN: Appropriate log entries should have been made and methods called/not called
    assert chk is test_return, f'"{test_data}" reply should have returned {STATUS_CODE[test_return]}'
    assert caplog.record_tuples == logs, 'Log entries mismatch'


def test_e_authentication(pjlink, caplog):
    """
    Test data == ERRA
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    test_error = E_AUTHENTICATION
    test_cmd = 'CLSS'
    test_data = PJLINK_ERRORS[test_error]
    test_reply = STATUS_MSG[test_error]
    test_return = test_error
    logs = [(f'{test_module}', logging.DEBUG,
             f'({pjlink.name}) Processing command "{test_cmd}" with data "{test_data}"'),
            (f'{test_module}', logging.ERROR,
             f'({pjlink.name}) {test_cmd}: {test_reply}')
            ]
    # WHEN: called with error
    caplog.clear()
    chk = process_command(projector=pjlink, cmd=test_cmd, data=test_data)

    # THEN: Appropriate log entries should have been made and methods called/not called
    assert chk is test_return, f'"{PJLINK_ERRORS[test_error]}" reply should have returned {STATUS_CODE[test_error]}'
    assert caplog.record_tuples == logs, 'Log entries mismatch'


def test_e_undefined(pjlink, caplog):
    """
    Test data == ERR1
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    test_error = E_UNDEFINED
    test_cmd = 'CLSS'
    test_data = PJLINK_ERRORS[test_error]
    test_reply = STATUS_MSG[test_error]
    test_return = test_error
    logs = [(f'{test_module}', logging.DEBUG,
             f'({pjlink.name}) Processing command "{test_cmd}" with data "{test_data}"'),
            (f'{test_module}', logging.ERROR,
             f'({pjlink.name}) {test_cmd}: {test_reply}')
            ]
    # WHEN: called with error
    caplog.clear()
    chk = process_command(projector=pjlink, cmd=test_cmd, data=test_data)

    # THEN: Appropriate log entries should have been made and methods called/not called
    assert chk is test_return, f'"{PJLINK_ERRORS[test_error]}" reply should have returned {STATUS_CODE[test_error]}'
    assert caplog.record_tuples == logs, 'Log entries mismatch'


def test_e_parameter(pjlink, caplog):
    """
    Test data == ERR2
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    test_error = E_PARAMETER
    test_cmd = 'CLSS'
    test_data = PJLINK_ERRORS[test_error]
    test_reply = STATUS_MSG[test_error]
    test_return = test_error
    logs = [(f'{test_module}', logging.DEBUG,
             f'({pjlink.name}) Processing command "{test_cmd}" with data "{test_data}"'),
            (f'{test_module}', logging.ERROR,
             f'({pjlink.name}) {test_cmd}: {test_reply}')
            ]
    # WHEN: called with error
    caplog.clear()
    chk = process_command(projector=pjlink, cmd=test_cmd, data=test_data)

    # THEN: Appropriate log entries should have been made and methods called/not called
    assert chk is test_return, f'"{PJLINK_ERRORS[test_error]}" reply should have returned {STATUS_CODE[test_error]}'
    assert caplog.record_tuples == logs, 'Log entries mismatch'


def test_e_unavailable(pjlink, caplog):
    """
    Test data == ERR3
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    test_error = E_UNAVAILABLE
    test_cmd = 'CLSS'
    test_data = PJLINK_ERRORS[test_error]
    test_reply = STATUS_MSG[test_error]
    test_return = test_error
    logs = [(f'{test_module}', logging.DEBUG,
             f'({pjlink.name}) Processing command "{test_cmd}" with data "{test_data}"'),
            (f'{test_module}', logging.ERROR,
             f'({pjlink.name}) {test_cmd}: {test_reply}')
            ]
    # WHEN: called with error
    caplog.clear()
    chk = process_command(projector=pjlink, cmd=test_cmd, data=test_data)

    # THEN: Appropriate log entries should have been made and methods called/not called
    assert chk is test_return, f'"{PJLINK_ERRORS[test_error]}" reply should have returned {STATUS_CODE[test_error]}'
    assert caplog.record_tuples == logs, 'Log entries mismatch'


def test_e_projector(pjlink, caplog):
    """
    Test data == ERR4
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    test_error = E_PROJECTOR
    test_cmd = 'CLSS'
    test_data = PJLINK_ERRORS[test_error]
    test_reply = STATUS_MSG[test_error]
    test_return = test_error
    logs = [(f'{test_module}', logging.DEBUG,
             f'({pjlink.name}) Processing command "{test_cmd}" with data "{test_data}"'),
            (f'{test_module}', logging.ERROR,
             f'({pjlink.name}) {test_cmd}: {test_reply}')
            ]
    # WHEN: called with error
    caplog.clear()
    chk = process_command(projector=pjlink, cmd=test_cmd, data=test_data)

    # THEN: Appropriate log entries should have been made and methods called/not called
    assert chk is test_return, f'"{PJLINK_ERRORS[test_error]}" reply should have returned {STATUS_CODE[test_error]}'
    assert caplog.record_tuples == logs, 'Log entries mismatch'
