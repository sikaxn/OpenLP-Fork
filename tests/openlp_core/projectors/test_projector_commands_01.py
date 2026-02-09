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
Package to test the openlp.core.projectors.pjlink commands package.
"""
from unittest.mock import MagicMock, call, patch

from openlp.core.projectors.pjlink import PJLink
from openlp.core.projectors.pjlinkcommands import process_command
from openlp.core.projectors.constants import E_ERROR, E_WARN, PJLINK_ERST_DATA, PJLINK_ERST_STATUS, S_OK


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_ackn(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test ackn command (empty test)
    """
    # GIVEN: Test setup
    # WHEN: Called with setting shutter closed and mute on
    process_command(projector=pjlink, cmd='ACKN', data='0')

    # THEN: Shutter should be closed and mute should be True
    mocked_log.debug.assert_has_calls([
        call(f'({pjlink.name}) Processing command "ACKN" with data "0"'),
        call(f'({pjlink.name}) Calling function for ACKN')
    ])


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_erst_all_error(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test test_projector_process_erst_all_error
    """
    # GIVEN: Test object
    chk_data = '{fan}{lamp}{temp}{cover}{filt}{other}'.format(fan=PJLINK_ERST_STATUS[E_ERROR],
                                                              lamp=PJLINK_ERST_STATUS[E_ERROR],
                                                              temp=PJLINK_ERST_STATUS[E_ERROR],
                                                              cover=PJLINK_ERST_STATUS[E_ERROR],
                                                              filt=PJLINK_ERST_STATUS[E_ERROR],
                                                              other=PJLINK_ERST_STATUS[E_ERROR])
    chk_test = {'Fan': E_ERROR,
                'Lamp': E_ERROR,
                'Temperature': E_ERROR,
                'Cover': E_ERROR,
                'Filter': E_ERROR,
                'Other': E_ERROR}
    pjlink.projector_errors = None

    # WHEN: process_erst with status set to WARN
    process_command(projector=pjlink, cmd='ERST', data=chk_data)

    # THEN: PJLink instance errors should match chk_value
    assert pjlink.projector_errors == chk_test, 'Projector errors should be all E_ERROR'
    mocked_log.warning.assert_not_called()
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "ERST" with data "{chk_data}"'),
        call(f'({pjlink.name}) Calling function for ERST')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_erst_all_ok(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test to verify pjlink.projector_errors is set to None when no errors
    """
    # GIVEN: Test object
    chk_data = '0' * PJLINK_ERST_DATA['DATA_LENGTH']

    # WHEN: process_erst with no errors
    process_command(projector=pjlink, cmd='ERST', data=chk_data)

    # THEN: PJLink instance errors should be None
    assert pjlink.projector_errors is None, 'projector_errors should have been set to None'
    mocked_log.warning.assert_not_called()
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "ERST" with data "{chk_data}"'),
        call(f'({pjlink.name}) Calling function for ERST')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_erst_all_warn(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test test_projector_process_erst_all_error
    """
    # GIVEN: Test object
    chk_data = '{fan}{lamp}{temp}{cover}{filt}{other}'.format(fan=PJLINK_ERST_STATUS[E_WARN],
                                                              lamp=PJLINK_ERST_STATUS[E_WARN],
                                                              temp=PJLINK_ERST_STATUS[E_WARN],
                                                              cover=PJLINK_ERST_STATUS[E_WARN],
                                                              filt=PJLINK_ERST_STATUS[E_WARN],
                                                              other=PJLINK_ERST_STATUS[E_WARN])
    chk_test = {
        'Fan': E_WARN,
        'Lamp': E_WARN,
        'Temperature': E_WARN,
        'Cover': E_WARN,
        'Filter': E_WARN,
        'Other': E_WARN
    }
    pjlink.projector_errors = None

    # WHEN: process_erst with status set to WARN
    process_command(projector=pjlink, cmd='ERST', data=chk_data)

    # THEN: PJLink instance errors should match chk_value
    assert pjlink.projector_errors == chk_test, 'Projector errors should be all E_WARN'
    mocked_log.warning.assert_not_called()
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "ERST" with data "{chk_data}"'),
        call(f'({pjlink.name}) Calling function for ERST')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_erst_data_invalid_length(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test test_projector_process_erst_data_invalid_length
    """
    # GIVEN: Test object
    chk_data = '0' * (PJLINK_ERST_DATA['DATA_LENGTH'] + 1)
    pjlink.projector_errors = None

    # WHEN: process_erst called with invalid data (too many values
    process_command(pjlink, cmd='ERST', data=chk_data)

    # THEN: pjlink.projector_errors should be empty and warning logged
    assert not pjlink.projector_errors, 'There should be no errors'
    assert mocked_log.warning.call_args_list == [
        call(f'({pjlink.name}) Invalid error status response "{chk_data}": length != {PJLINK_ERST_DATA["DATA_LENGTH"]}')
    ]
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "ERST" with data "{chk_data}"'),
        call(f'({pjlink.name}) Calling function for ERST')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_erst_data_invalid_nan(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test ERST called with invalid data
    """
    # GIVEN: Test object
    chk_data = 'Z' + ('0' * (PJLINK_ERST_DATA['DATA_LENGTH'] - 1))
    pjlink.projector_errors = None

    # WHEN: process_erst called with invalid data (too many values
    process_command(pjlink, cmd='ERST', data=chk_data)

    # THEN: pjlink.projector_errors should be empty and warning logged
    assert not pjlink.projector_errors, 'There should be no errors'
    mocked_log.warning.assert_called_once_with(f'({pjlink.name}) Invalid error status response "{chk_data}"')
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "ERST" with data "{chk_data}"'),
        call(f'({pjlink.name}) Calling function for ERST')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_erst_warn_cover_only(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test test_projector_process_erst_warn_cover_only
    """
    # GIVEN: Test object
    chk_data = '{fan}{lamp}{temp}{cover}{filt}{other}'.format(fan=PJLINK_ERST_STATUS[S_OK],
                                                              lamp=PJLINK_ERST_STATUS[S_OK],
                                                              temp=PJLINK_ERST_STATUS[S_OK],
                                                              cover=PJLINK_ERST_STATUS[E_WARN],
                                                              filt=PJLINK_ERST_STATUS[S_OK],
                                                              other=PJLINK_ERST_STATUS[S_OK])
    chk_test = {'Cover': E_WARN}
    pjlink.projector_errors = None

    # WHEN: process_erst with status set to WARN
    process_command(projector=pjlink, cmd='ERST', data=chk_data)

    # THEN: PJLink instance errors should match only cover warning
    assert 1 == len(pjlink.projector_errors), 'There should only be 1 error listed in projector_errors'
    assert 'Cover' in pjlink.projector_errors, '"Cover" should be the only error listed'
    assert pjlink.projector_errors['Cover'] == E_WARN, '"Cover" should have E_WARN listed as error'
    assert chk_test == pjlink.projector_errors, 'projector_errors should match test errors'
    mocked_log.warning.assert_not_called()
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "ERST" with data "{chk_data}"'),
        call(f'({pjlink.name}) Calling function for ERST')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_inf1(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test saving INF1 data (manufacturer)
    """
    # GIVEN: Test object
    chk_data = 'TEst INformation MultiCase'
    pjlink.manufacturer = None

    # WHEN: process_inf called with test data
    process_command(projector=pjlink, cmd='INF1', data=chk_data)

    # THEN: Data should be saved
    assert pjlink.manufacturer == chk_data, 'Test data should have been saved'
    mocked_log.warning.assert_not_called()
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "INF1" with data "{chk_data}"'),
        call(f'({pjlink.name}) Calling function for INF1'),
        call(f'({pjlink.name}) Setting projector manufacturer data to "{chk_data}"')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_inf2(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test saving INF2 data (model)
    """
    # GIVEN: Test object
    chk_data = 'TEst moDEl MultiCase'
    pjlink.model = None

    # WHEN: process_inf called with test data
    process_command(projector=pjlink, cmd='INF2', data=chk_data)

    # THEN: Data should be saved
    assert pjlink.model == chk_data, 'Test data should have been saved'
    mocked_log.warning.assert_not_called()
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "INF2" with data "{chk_data}"'),
        call(f'({pjlink.name}) Calling function for INF2'),
        call(f'({pjlink.name}) Setting projector model to "{chk_data}"')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_info(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test saving INF2 data (model)
    """
    # GIVEN: Test object
    chk_data = 'TEst ExtrANEous MultiCase INformatoin that MFGR might Set'
    pjlink.other_info = None

    # WHEN: process_inf called with test data
    process_command(projector=pjlink, cmd='INFO', data=chk_data)

    # THEN: Data should be saved
    assert pjlink.other_info == chk_data, 'Test data should have been saved'
    mocked_log.warning.assert_not_called()
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "INFO" with data "{chk_data}"'),
        call(f'({pjlink.name}) Calling function for INFO'),
        call(f'({pjlink.name}) Setting projector other_info to "{chk_data}"')
    ]
