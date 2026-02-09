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
Package to test the openlp.core.projectors.pjlink base package part 3.
"""
from unittest.mock import call, patch

import openlp.core.projectors.pjlink
from openlp.core.projectors.constants import PJLINK_CLASS, STATUS_CODE, \
    S_NOT_CONNECTED, S_OFF, S_ON, QSOCKET_STATE


@patch.object(openlp.core.projectors.pjlink, 'log')
def test_projector_reset_information(mock_log, pjlink):
    """
    Test reset_information() resets all information and stops timers
    """
    # GIVEN: Test object
    log_debug_calls = [call('({ip}) reset_information() connect status is '
                            'S_NOT_CONNECTED'.format(ip=pjlink.name)),
                       call('({ip}): Calling poll_timer.stop()'.format(ip=pjlink.name)),
                       call('({ip}): Calling socket_timer.stop()'.format(ip=pjlink.name)),
                       call('({ip}): Calling status_timer.stop()'.format(ip=pjlink.name))]

    # Attributes not available until instantiation, so mock here
    with patch.object(pjlink, 'socket_timer') as mock_socket_timer, \
            patch.object(pjlink, 'status_timer') as mock_status_timer, \
            patch.object(pjlink, 'poll_timer') as mock_poll_timer, \
            patch.object(pjlink, 'state') as mock_state:
        mock_state.return_value.value = QSOCKET_STATE[S_NOT_CONNECTED]
        # Set attributes to something other than None or {} or []
        pjlink.fan = True
        pjlink.filter_time = True
        pjlink.lamp = True
        pjlink.mac_adx_received = 'Some random MAC'
        pjlink.manufacturer = 'PJLINK'
        pjlink.model = '1'
        pjlink.model_filter = 'Filter'
        pjlink.model_lamp = 'Lamp'
        pjlink.mute = True
        pjlink.other_info = 'Another Test'
        pjlink.pjlink_class = 2
        pjlink.pjlink_name = 'OPENLPTEST'
        pjlink.power = S_ON
        pjlink.projector_errors = {'test1': True, 'test2': False}
        pjlink.serial_no = 'Some Number'
        pjlink.serial_no_received = 'Some Other Number'
        pjlink.sw_version = 'Some Version'
        pjlink.sw_version_received = 'Some Other Version'
        pjlink.shutter = True
        pjlink.source_available = True
        pjlink.source = True
        pjlink.status_timer_checks = {'test1': object(), 'test2': object()}
        pjlink.send_busy = False
        pjlink.send_queue = ['test1', 'test2']
        pjlink.priority_queue = ['test1', 'test2']

        # WHEN: reset_information() is called
        pjlink.reset_information()

        # THEN: All information should be reset and timers stopped
        mock_log.debug.assert_has_calls(log_debug_calls)
        assert pjlink.fan is None, 'fan should be None'
        assert pjlink.filter_time is None, 'filter_time should be None'
        assert pjlink.lamp is None, 'lamp should be None'
        assert pjlink.mac_adx_received is None, 'mac_adx_received should be None'
        assert pjlink.manufacturer is None, 'manufacturer should be None'
        assert pjlink.model is None, 'model should be None'
        assert pjlink.model_filter is None, 'model_filter should be None'
        assert pjlink.model_lamp is None, 'model_lamp should be None'
        assert not pjlink.mute, 'mute should be False'
        assert pjlink.other_info is None, 'other should be None'
        assert pjlink.pjlink_class == PJLINK_CLASS, 'pjlink_class should be {cls}'.format(cls=PJLINK_CLASS)
        assert pjlink.pjlink_name is None, 'pjlink_name should be None'
        assert pjlink.power == S_OFF, 'power should be {data}'.format(data=STATUS_CODE[S_OFF])
        assert pjlink.projector_errors == {}, 'projector_errors should be an empty dict'
        assert pjlink.serial_no is None, 'serial_no should be None'
        assert pjlink.serial_no_received is None, 'serial_no_received should be None'
        assert pjlink.sw_version is None, 'sw_version should be None'
        assert pjlink.sw_version_received is None, 'sw_version_received should be None'
        assert not pjlink.shutter, 'shutter should be False'
        assert pjlink.source_available is None, 'source_available should be None'
        assert pjlink.source is None, 'source should be None'
        assert pjlink.status_timer_checks == {}, 'status_timer_checks should be an empty dict'
        assert not pjlink.send_busy, 'send_busy should be False'
        assert pjlink.send_queue == [], 'send_queue should be an empty list'
        assert pjlink.priority_queue == [], 'priority_queue should be an empty list'
        assert mock_socket_timer.stop.called, 'socket_timer.stop() should have been called'
        assert mock_status_timer.stop.called, 'status_timer.stop() should have been called'
        assert mock_poll_timer.stop.called, 'poll_timer.stop() should have been called'
