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
Tests for commands that do not need much testing
"""

import logging
import openlp.core.projectors.pjlinkcommands

from copy import deepcopy

from openlp.core.projectors.constants import PJLINK_SVER_MAX_LEN

from tests.resources.projector.data import TEST1_DATA, TEST2_DATA

test_module = openlp.core.projectors.pjlinkcommands.__name__
_process_sver = openlp.core.projectors.pjlinkcommands._process_sver


def test_sver_none(fake_pjlink, caplog):
    """
    Test SVER update when saved version is None
    """
    # GIVEN: Test setup
    fake_pjlink.sw_version = None
    fake_pjlink.db_update = False
    t_data = deepcopy(TEST1_DATA['sw_version'])
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({fake_pjlink.name}) Setting projector software version to "{t_data}"')]

    # WHEN: Called
    _process_sver(projector=fake_pjlink, data=t_data)

    # THEN: Only log entry made
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert fake_pjlink.sw_version == t_data, 'sw_version should have updated'
    assert fake_pjlink.db_update is True, 'db_update should be set'


def test_sver_same(fake_pjlink, caplog):
    """
    Test SVER same as saved version
    """
    # GIVEN: Test setup
    fake_pjlink.sw_version = deepcopy(TEST1_DATA['sw_version'])
    fake_pjlink.db_update = False
    t_data = fake_pjlink.sw_version
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({fake_pjlink.name}) Software version unchanged - returning')]

    # WHEN: Called
    _process_sver(projector=fake_pjlink, data=t_data)

    # THEN: Only log entry made
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert fake_pjlink.sw_version == t_data, 'sw_version should not have changed'
    assert fake_pjlink.db_update is False, 'db_update should not have changed'


def test_sver_too_long(fake_pjlink, caplog):
    """
    Test SVER too long
    """
    # GIVEN: Test setup
    fake_pjlink.sw_version = None
    fake_pjlink.db_update = False
    t_data = '1' * PJLINK_SVER_MAX_LEN
    t_data += 'z'  # One longer than max length
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.WARNING, f'({fake_pjlink.name}) Invalid software version - too long')]

    # WHEN: Called
    caplog.clear()
    _process_sver(projector=fake_pjlink, data=t_data)

    # THEN: Only log entry made
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert fake_pjlink.sw_version is None, 'sw_version should not have changed'
    assert fake_pjlink.db_update is False, 'db_update should not have changed'


def test_sver_update(fake_pjlink, caplog):
    """
    Test SVER update when saved version is different than received version
    """
    # GIVEN: Test setup
    fake_pjlink.sw_version = deepcopy(TEST1_DATA['sw_version'])
    fake_pjlink.db_update = False
    t_data = deepcopy(TEST2_DATA['sw_version'])
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({fake_pjlink.name}) Old software version "{fake_pjlink.sw_version}"'),
            (test_module, logging.DEBUG, f'({fake_pjlink.name}) New software version "{t_data}"'),
            (test_module, logging.DEBUG, f'({fake_pjlink.name}) Setting projector software version to "{t_data}"')]

    # WHEN: Called
    _process_sver(projector=fake_pjlink, data=t_data)

    # THEN: Only log entry made
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert fake_pjlink.sw_version == t_data, 'sw_version should have updated'
    assert fake_pjlink.db_update is True, 'db_update should be set'
