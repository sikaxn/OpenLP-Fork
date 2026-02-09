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
Test process_pjlink method
"""

import logging
import openlp.core.projectors.pjlinkcommands

from openlp.core.projectors.pjlinkcommands import process_pjlink
from openlp.core.projectors.constants import E_AUTHENTICATION, E_NO_AUTHENTICATION, \
    S_AUTHENTICATE, S_CONNECT

from tests.resources.projector.data import TEST_PIN, TEST_SALT

test_module = openlp.core.projectors.pjlinkcommands.__name__


def test_normal_no_authentication_type(fake_pjlink, caplog):
    """
    Test login prompt with not enough parameters
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = ''
    logs = [(f'{test_module}', logging.DEBUG,
            f'({fake_pjlink.entry.name}) Processing PJLINK command'),
            (f'{test_module}', logging.ERROR,
             f'({fake_pjlink.entry.name}) Invalid initial authentication scheme - aborting')
            ]

    # WHEN: Calling function
    caplog.clear()
    t_chk = process_pjlink(projector=fake_pjlink, data=t_data)

    # THEN: Error returned and log entries
    assert t_chk == E_AUTHENTICATION, 'Should have returned E_AUTHENTICATION'
    assert caplog.record_tuples == logs, 'Invalid log entries'


def test_normal_invalid_value(fake_pjlink, caplog):
    """
    Test login prompt with parameter neither 0 (no authentication) or 1 (authenticate)
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = '2'
    logs = [(f'{test_module}', logging.DEBUG,
            f'({fake_pjlink.entry.name}) Processing PJLINK command'),
            (f'{test_module}', logging.ERROR,
             f'({fake_pjlink.entry.name}) Invalid initial authentication scheme - aborting')
            ]

    # WHEN: Calling function
    caplog.clear()
    t_chk = process_pjlink(projector=fake_pjlink, data=t_data)

    # THEN: Error returned and log entries
    assert t_chk == E_AUTHENTICATION, 'Should have returned E_AUTHENTICATION'
    assert caplog.record_tuples == logs, 'Invalid log entries'


def test_normal_extra_data(fake_pjlink, caplog):
    """
    Test login prompt with no authentication but extra data
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = f'0 {TEST_SALT}'
    logs = [(f'{test_module}', logging.DEBUG,
            f'({fake_pjlink.entry.name}) Processing PJLINK command'),
            (f'{test_module}', logging.ERROR,
             f'({fake_pjlink.entry.name}) Normal connection with extra information - aborting')
            ]

    # WHEN: Calling function
    caplog.clear()
    t_chk = process_pjlink(projector=fake_pjlink, data=t_data)

    # THEN: Error returned and log entries
    assert t_chk == E_NO_AUTHENTICATION, 'Should have returned E_NO_AUTHENTICATION'
    assert caplog.record_tuples == logs, 'Invalid log entries'


def test_normal_with_pin(fake_pjlink, caplog):
    """
    Test login prompt with no authentication but pin set
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = '0'
    logs = [(f'{test_module}', logging.DEBUG,
            f'({fake_pjlink.entry.name}) Processing PJLINK command'),
            (f'{test_module}', logging.ERROR,
             f'({fake_pjlink.entry.name}) Normal connection but PIN set - aborting')
            ]
    fake_pjlink.pin = TEST_SALT

    # WHEN: Calling function
    caplog.clear()
    t_chk = process_pjlink(projector=fake_pjlink, data=t_data)

    # THEN: Error returned and log entries
    assert t_chk == E_NO_AUTHENTICATION, 'Should have returned E_NO_AUTHENTICATION'
    assert caplog.record_tuples == logs, 'Invalid log entries'


def test_normal_login(fake_pjlink, caplog):
    """
    Test login prompt with no authentication
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = '0'
    logs = [(f'{test_module}', logging.DEBUG,
            f'({fake_pjlink.entry.name}) Processing PJLINK command'),
            (f'{test_module}', logging.DEBUG,
             f'({fake_pjlink.entry.name}) PJLINK: Returning S_CONNECT')
            ]
    fake_pjlink.pin = None

    # WHEN: Calling function
    caplog.clear()
    t_chk = process_pjlink(projector=fake_pjlink, data=t_data)

    # THEN: Error returned and log entries
    assert t_chk == S_CONNECT, 'Should have returned S_CONNECT'
    assert caplog.record_tuples == logs, 'Invalid log entries'


def test_authenticate_no_salt(fake_pjlink, caplog):
    """
    Test authenticate login prompt with no salt
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = '1'
    logs = [(f'{test_module}', logging.DEBUG,
            f'({fake_pjlink.entry.name}) Processing PJLINK command'),
            (f'{test_module}', logging.ERROR,
             f'({fake_pjlink.entry.name}) Authenticated connection but not enough info - aborting')
            ]

    # WHEN: Calling function
    caplog.clear()
    t_chk = process_pjlink(projector=fake_pjlink, data=t_data)

    # THEN: Error returned and log entries
    assert t_chk == E_NO_AUTHENTICATION, 'Should have returned E_NO_AUTHENTICATION'
    assert caplog.record_tuples == logs, 'Invalid log entries'


def test_authenticate_short_salt(fake_pjlink, caplog):
    """
    Test authenticate login prompt with salt length too short
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = f'1 {TEST_SALT[:-1]}'
    logs = [(f'{test_module}', logging.DEBUG,
            f'({fake_pjlink.entry.name}) Processing PJLINK command'),
            (f'{test_module}', logging.ERROR,
             f'({fake_pjlink.entry.name}) Authentication token invalid (size) - aborting')
            ]

    # WHEN: Calling function
    caplog.clear()
    t_chk = process_pjlink(projector=fake_pjlink, data=t_data)

    # THEN: Error returned and log entries
    assert t_chk == E_NO_AUTHENTICATION, 'Should have returned E_NO_AUTHENTICATION'
    assert caplog.record_tuples == logs, 'Invalid log entries'


def test_authenticate_long_salt(fake_pjlink, caplog):
    """
    Test authenticate login prompt with salt length too long
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = f'1 {TEST_SALT}Z'
    logs = [(f'{test_module}', logging.DEBUG,
            f'({fake_pjlink.entry.name}) Processing PJLINK command'),
            (f'{test_module}', logging.ERROR,
             f'({fake_pjlink.entry.name}) Authentication token invalid (size) - aborting')
            ]

    # WHEN: Calling function
    caplog.clear()
    t_chk = process_pjlink(projector=fake_pjlink, data=t_data)

    # THEN: Error returned and log entries
    assert t_chk == E_NO_AUTHENTICATION, 'Should have returned E_NO_AUTHENTICATION'
    assert caplog.record_tuples == logs, 'Invalid log entries'


def test_authenticate_invalid_salt(fake_pjlink, caplog):
    """
    Test authenticate login prompt with salt not a hexadecimal number
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = '1 1a2b3c4g'
    logs = [(f'{test_module}', logging.DEBUG,
            f'({fake_pjlink.entry.name}) Processing PJLINK command'),
            (f'{test_module}', logging.ERROR,
             f'({fake_pjlink.entry.name}) Authentication token invalid (not a hexadecimal number) - aborting')
            ]

    # WHEN: Calling function
    caplog.clear()
    t_chk = process_pjlink(projector=fake_pjlink, data=t_data)

    # THEN: Error returned and log entries
    assert t_chk == E_NO_AUTHENTICATION, 'Should have returned E_NO_AUTHENTICATION'
    assert caplog.record_tuples == logs, 'Invalid log entries'


def test_authenticate_no_pin(fake_pjlink, caplog):
    """
    Test authenticate login prompt with no PIN set
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = f'1 {TEST_SALT}'
    logs = [(f'{test_module}', logging.DEBUG,
            f'({fake_pjlink.entry.name}) Processing PJLINK command'),
            (f'{test_module}', logging.ERROR,
             f'({fake_pjlink.entry.name}) Authenticate connection but no PIN - aborting')
            ]
    fake_pjlink.pin = None

    # WHEN: Calling function
    caplog.clear()
    t_chk = process_pjlink(projector=fake_pjlink, data=t_data)

    # THEN: Error returned and log entries
    assert t_chk == E_NO_AUTHENTICATION, 'Should have returned E_NO_AUTHENTICATION'
    assert caplog.record_tuples == logs, 'Invalid log entries'


def test_authenticate_login(fake_pjlink, caplog):
    """
    Test authenticate login prompt with PIN set
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = f'1 {TEST_SALT}'
    logs = [(f'{test_module}', logging.DEBUG,
            f'({fake_pjlink.entry.name}) Processing PJLINK command'),
            (f'{test_module}', logging.DEBUG,
             f'({fake_pjlink.entry.name}) PJLINK: Returning S_AUTHENTICATE')
            ]
    fake_pjlink.pin = TEST_PIN

    # WHEN: Calling function
    caplog.clear()
    t_chk = process_pjlink(projector=fake_pjlink, data=t_data)

    # THEN: Error returned and log entries
    assert t_chk == S_AUTHENTICATE, 'Should have returned S_AUTHENTICATE'
    assert caplog.record_tuples == logs, 'Invalid log entries'
