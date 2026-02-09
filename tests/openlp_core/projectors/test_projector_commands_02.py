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
from openlp.core.projectors.constants import PJLINK_POWR_STATUS, S_ON, S_STANDBY


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_inpt_good(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test input source status shows current input
    """
    # GIVEN: Test object
    pjlink.source = '11'
    pjlink.source_available = ['11', '12', '21', '22', '31', '32']

    # WHEN: Called with input source
    process_command(projector=pjlink, cmd='INPT', data='21')

    # THEN: Input selected should reflect current input
    assert pjlink.source == '21', 'Input source should be set to "21"'
    assert mocked_log.warning.call_count == 0, 'log.warning should not have been called'
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "INPT" with data "21"'),
        call(f'({pjlink.name}) Calling function for INPT'),
        call(f'({pjlink.name}) Setting current source to "21"')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_inpt_invalid(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test input source returned not valid according to standard
    """
    # GIVEN: Test object
    pjlink.source = None
    pjlink.source_available = None

    # WHEN: Called with input source
    process_command(projector=pjlink, cmd='INPT', data='91')

    # THEN: Input selected should reflect current input
    assert not pjlink.source, 'Input source should not have changed'
    mocked_log.warning.assert_called_once_with(
        f'({pjlink.name}) Input source not listed as a PJLink valid source - ignoring'
    )
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "INPT" with data "91"'),
        call(f'({pjlink.name}) Calling function for INPT')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_inpt_not_in_list(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test input source not listed in available sources
    """
    # GIVEN: Test object
    pjlink.source = '11'
    chk_source_available = ['11', '12', '21', '22', '31', '32']
    pjlink.source_available = chk_source_available

    # WHEN: Called with input source
    process_command(projector=pjlink, cmd='INPT', data='25')

    # THEN: Input selected should reflect current input
    assert '11' == pjlink.source, 'Input source should not have changed'
    mocked_log.warning.assert_called_once_with(
        f'({pjlink.name}) Input source not listed in available sources - ignoring'
    )
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "INPT" with data "25"'),
        call(f'({pjlink.name}) Calling function for INPT')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_inst_class_1(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test saving video source available information
    """

    # GIVEN: Test object
    pjlink.source_available = []

    chk_data = '21 12 11 22 32 31'  # Although they should already be sorted, use unsorted to check method
    chk_test = ['11', '12', '21', '22', '31', '32']

    # WHEN: process_inst called with test data
    process_command(projector=pjlink, cmd='INST', data=chk_data)

    # THEN: Data should have been sorted and saved properly
    assert mocked_log.warning.call_count == 0
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "INST" with data "21 12 11 22 32 31"'),
        call(f'({pjlink.name}) Calling function for INST'),
        call(f'({pjlink.name}) Setting projector source_available to '
             '"[\'11\', \'12\', \'21\', \'22\', \'31\', \'32\']"')
    ]
    assert pjlink.source_available == chk_test, "Sources should have been sorted and saved"


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_lamp_invalid_missing_data(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test process lamp with 1 lamp reply hours only and no on/off status
    """
    # GIVEN: Test object
    pjlink.lamp = None

    # WHEN: Call process_command with 3 lamps
    process_command(projector=pjlink, cmd='LAMP', data='45')

    # THEN: Lamp should have been set with proper lamp status
    mocked_log.warning.assert_called_once_with(f'({pjlink.name}) process_lamp(): Invalid data "45" - Missing data')
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "LAMP" with data "45"'),
        call(f'({pjlink.name}) Calling function for LAMP')
    ]
    assert not pjlink.lamp, 'Projector lamp info should not have changed'


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_lamp_invalid_nan(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test status multiple lamp on/off and hours
    """
    # GIVEN: Test object
    pjlink.lamp = [{'Hours': 00000, 'On': True}, {'Hours': 11111, 'On': False}]

    # WHEN: Call process_command with invalid lamp data
    process_command(projector=pjlink, cmd='LAMP', data='11111 1 22222 0 333A3 1')

    # THEN: lamps should not have changed
    mocked_log.warning.assert_called_once_with(
        f'({pjlink.name}) process_lamp(): Invalid data "11111 1 22222 0 333A3 1"'
    )
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "LAMP" with data "11111 1 22222 0 333A3 1"'),
        call(f'({pjlink.name}) Calling function for LAMP')
    ]
    assert 2 == len(pjlink.lamp), 'Projector lamp list should not have changed'
    assert pjlink.lamp[0]['On'], 'Lamp 1 power status should not have changed'
    assert 0 == pjlink.lamp[0]['Hours'], 'Lamp 1 hours should not have changed'
    assert not pjlink.lamp[1]['On'], 'Lamp 2 power status should not have changed'
    assert 11111 == pjlink.lamp[1]['Hours'], 'Lamp 2 hours should not have changed'


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_lamp_multiple(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test status multiple lamp on/off and hours
    """
    # GIVEN: Test object
    pjlink.lamp = None

    # WHEN: Call process_command with 3 lamps
    process_command(projector=pjlink, cmd='LAMP', data='11111 1 22222 0 33333 1')

    # THEN: Lamp should have been set with proper lamp status
    assert mocked_log.warning.call_count == 0
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "LAMP" with data "11111 1 22222 0 33333 1"'),
        call(f'({pjlink.name}) Calling function for LAMP')
    ]
    assert 3 == len(pjlink.lamp), 'Projector should have 3 lamps specified'
    assert pjlink.lamp[0]['On'], 'Lamp 1 power status should have been set to TRUE'
    assert 11111 == pjlink.lamp[0]['Hours'], 'Lamp 1 hours should have been set to 11111'
    assert not pjlink.lamp[1]['On'], 'Lamp 2 power status should have been set to FALSE'
    assert 22222 == pjlink.lamp[1]['Hours'], 'Lamp 2 hours should have been set to 22222'
    assert pjlink.lamp[2]['On'], 'Lamp 3 power status should have been set to TRUE'
    assert 33333 == pjlink.lamp[2]['Hours'], 'Lamp 3 hours should have been set to 33333'


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_lamp_single(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test status lamp on/off and hours
    """
    # GIVEN: Test object
    pjlink.lamp = None

    # WHEN: Call process_command with 3 lamps
    process_command(projector=pjlink, cmd='LAMP', data='11111 1')

    # THEN: Lamp should have been set with proper lamp status
    assert mocked_log.warning.call_count == 0
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "LAMP" with data "11111 1"'),
        call(f'({pjlink.name}) Calling function for LAMP')
    ]
    assert 1 == len(pjlink.lamp), 'Projector should have 1 lamp specified'
    assert pjlink.lamp[0]['On'], 'Lamp 1 power status should have been set to TRUE'
    assert 11111 == pjlink.lamp[0]['Hours'], 'Lamp 1 hours should have been set to 11111'


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_name(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test saving NAME data from projector
    """
    # GIVEN: Test object
    chk_data = 'Some Name the End-User Set IN Projector'

    # WHEN: process_name called with test data
    process_command(projector=pjlink, cmd='NAME', data=chk_data)

    # THEN: name should be set and logged
    assert mocked_log.warning.call_count == 0
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "NAME" with data "Some Name the End-User Set IN Projector"'),
        call(f'({pjlink.name}) Calling function for NAME'),
        call(f'({pjlink.name}) Setting projector PJLink name to "Some Name the End-User Set IN Projector"')
    ]
    assert pjlink.pjlink_name == chk_data, 'Name test data should have been saved'


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_powr_invalid(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test process_powr invalid call
    """
    # GIVEN: Test object
    pjlink.power = S_STANDBY

    # WHEN: process_command called with test data
    with patch.object(pjlink, 'send_command') as mocked_send_command, \
            patch.object(pjlink, 'change_status') as mocked_change_status, \
            patch.object(pjlink, 'projectorUpdateIcons') as mocked_update_icons:
        process_command(projector=pjlink, cmd='POWR', data='99')

    # THEN: Projector power should not have changed
    mocked_log.warning.assert_called_once_with(f'({pjlink.name}) Unknown power response: "99"')
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "POWR" with data "99"'),
        call(f'({pjlink.name}) Calling function for POWR'),
        call(f'({pjlink.name}) Processing POWR command')
    ]
    assert S_STANDBY == pjlink.power, 'Power should not have changed'
    mocked_update_icons.emit.assert_not_called()
    mocked_change_status.assert_not_called()
    mocked_send_command.assert_not_called()


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_powr_off(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test status power to OFF
    """
    # GIVEN: Test object
    pjlink.power = S_ON

    # WHEN: process_name called with test data
    with patch.object(pjlink, 'send_command') as mocked_send_command, \
            patch.object(pjlink, 'change_status') as mocked_change_status, \
            patch.object(pjlink, 'projectorUpdateIcons') as mocked_update_icons:
        process_command(projector=pjlink, cmd='POWR', data=PJLINK_POWR_STATUS[S_STANDBY])

    # THEN: Power should be set to ON
    assert mocked_log.warning.call_count == 0, 'log.warning should not have been called'
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "POWR" with data "0"'),
        call(f'({pjlink.name}) Calling function for POWR'),
        call(f'({pjlink.name}) Processing POWR command')
    ]
    assert S_STANDBY == pjlink.power, 'Power should have been set to OFF'
    mocked_update_icons.emit.assert_called_once()
    assert mocked_send_command.call_count == 0, 'send_command should not have been called'
    mocked_change_status.assert_called_once_with(S_STANDBY)


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_powr_on(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test status power to ON
    """
    # GIVEN: Test object
    pjlink.power = S_STANDBY

    # WHEN: process_name called with test data
    with patch.object(pjlink, 'send_command') as mocked_send_command, \
            patch.object(pjlink, 'change_status') as mocked_change_status, \
            patch.object(pjlink, 'projectorUpdateIcons') as mocked_update_icons:
        process_command(projector=pjlink, cmd='POWR', data=PJLINK_POWR_STATUS[S_ON])

    # THEN: Power should be set to ON
    assert mocked_log.warning.call_count == 0, 'log.warning should not have been called'
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "POWR" with data "1"'),
        call(f'({pjlink.name}) Calling function for POWR'),
        call(f'({pjlink.name}) Processing POWR command')
    ]
    assert S_ON == pjlink.power, 'Power should have been set to ON'
    assert mocked_update_icons.emit.called, 'projectorUpdateIcons should have been called'
    mocked_send_command.assert_called_once_with('INST')
    mocked_change_status.assert_called_once_with(S_ON)


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_rfil_save(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test saving filter type
    """
    # GIVEN: Test object
    new_data = 'Filter Type Test'
    pjlink.model_filter = None

    # WHEN: Filter model is received
    process_command(projector=pjlink, cmd='RFIL', data=new_data)

    # THEN: Filter model number should be saved
    assert mocked_log.warning.call_count == 0, 'log.warning should not have been called'
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "RFIL" with data "{new_data}"'),
        call(f'({pjlink.name}) Calling function for RFIL')
    ]
    assert pjlink.model_filter == new_data, 'Filter model should have been saved'


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_rfil_nosave(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test saving filter type previously saved
    """
    # GIVEN: Test object
    old_data = 'Old filter type'
    new_data = 'Filter Type Test'
    pjlink.model_filter = old_data

    # WHEN: Filter model is received
    process_command(projector=pjlink, cmd='RFIL', data=new_data)

    # THEN: Filter model number should be saved
    assert pjlink.model_filter != new_data, 'Filter model should NOT have been saved'
    assert mocked_log.warning.call_args_list == [
        call(f'({pjlink.name}) Filter model already set'),
        call(f'({pjlink.name}) Saved model: "{old_data}"'),
        call(f'({pjlink.name}) New model: "{new_data}"')
    ]
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "RFIL" with data "{new_data}"'),
        call(f'({pjlink.name}) Calling function for RFIL')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_rlmp_save(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test saving lamp type
    """
    # GIVEN: Test object
    new_data = 'Lamp Type Test'
    pjlink.model_lamp = None

    # WHEN: Filter model is received
    process_command(projector=pjlink, cmd='RLMP', data=new_data)

    # THEN: Filter model number should be saved
    assert pjlink.model_lamp == new_data, 'Lamp model should have been saved'
    assert mocked_log.warning.call_count == 0, 'log.warning should not have been called'
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "RLMP" with data "{new_data}"'),
        call(f'({pjlink.name}) Calling function for RLMP')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_rlmp_nosave(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test saving lamp type previously saved
    """
    # GIVEN: Test object
    old_data = 'Old filter type'
    new_data = 'Filter Type Test'
    pjlink.model_lamp = old_data

    # WHEN: Filter model is received
    process_command(projector=pjlink, cmd='RLMP', data=new_data)

    # THEN: Filter model number should be saved
    assert pjlink.model_lamp != new_data, 'Lamp model should NOT have been saved'
    assert mocked_log.warning.call_args_list == [
        call(f'({pjlink.name}) Lamp model already set'),
        call(f'({pjlink.name}) Saved lamp: "{old_data}"'),
        call(f'({pjlink.name}) New lamp: "{new_data}"')
    ]
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "RLMP" with data "{new_data}"'),
        call(f'({pjlink.name}) Calling function for RLMP')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_snum_different(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test projector serial number different than saved serial number
    """
    # GIVEN: Test object
    new_data = 'Test Serial Number'
    old_data = 'Previous serial number'
    pjlink.serial_no = old_data

    # WHEN: No serial number is set and we receive serial number command
    process_command(projector=pjlink, cmd='SNUM', data=new_data)

    # THEN: Serial number should be set
    assert pjlink.serial_no != new_data, 'Projector serial number should NOT have been set'
    assert mocked_log.warning.call_args_list == [
        call(f'({pjlink.name}) Projector serial number does not match saved serial number'),
        call(f'({pjlink.name}) Saved:    "{old_data}"'),
        call(f'({pjlink.name}) Received: "{new_data}"'),
        call(f'({pjlink.name}) NOT saving serial number')
    ]
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "SNUM" with data "{new_data}"'),
        call(f'({pjlink.name}) Calling function for SNUM')
    ]


@patch('openlp.core.projectors.pjlinkcommands.log')
def test_projector_snum_set(mocked_log: MagicMock, pjlink: PJLink):
    """
    Test saving serial number from projector
    """
    # GIVEN: Test object
    new_data = 'Test Serial Number'
    pjlink.serial_no = None

    # WHEN: No serial number is set and we receive serial number command
    process_command(projector=pjlink, cmd='SNUM', data=new_data)

    # THEN: Serial number should be set
    assert pjlink.serial_no == new_data, 'Projector serial number should have been set'
    assert mocked_log.warning.call_count == 0, 'There should be no log.warning calls'
    assert mocked_log.debug.call_args_list == [
        call(f'({pjlink.name}) Processing command "SNUM" with data "{new_data}"'),
        call(f'({pjlink.name}) Calling function for SNUM'),
        call(f'({pjlink.name}) Setting projector serial number to "{new_data}"')
    ]
