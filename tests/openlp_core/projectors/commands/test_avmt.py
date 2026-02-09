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
Test _process_avmt
"""

import logging

import openlp.core.projectors.pjlinkcommands

from unittest.mock import patch

test_module = openlp.core.projectors.pjlinkcommands.__name__
_process_avmt = openlp.core.projectors.pjlinkcommands._process_avmt


def test_avmt_mute(fake_pjlink):
    """
    Test _proces_avmt_mute helper
    """
    # GIVEN: Test setup
    fake_pjlink.mute = False

    # WHEN: Called
    openlp.core.projectors.pjlinkcommands._process_avmt_mute(projector=fake_pjlink, data=True)

    # THEN: mute should have been changed
    assert fake_pjlink.mute is True, 'Mute did not change'


def test_avmt_shutter(fake_pjlink):
    """
    Test _proces_avmt_shutter helper
    """
    # GIVEN: Test setup
    fake_pjlink.shutter = False

    # WHEN: Called
    openlp.core.projectors.pjlinkcommands._process_avmt_shutter(projector=fake_pjlink, data=True)

    # THEN: mute should have been changed
    assert fake_pjlink.shutter is True, 'Mute did not change'


@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_mute')
@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_shutter')
def test_avmt_bad_data(mock_shutter, mock_mute, fake_pjlink, caplog):
    """
    Test avmt bad data fail
    """
    # GIVEN: Test setup
    t_data = '36'
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.WARNING, f'({fake_pjlink.name}) Invalid av mute response: {t_data}')]

    # WHEN: Called with an invalid setting
    caplog.clear()
    _process_avmt(projector=fake_pjlink, data=t_data)

    # THEN: No other calls made
    assert caplog.record_tuples == logs, 'Invalid log entries'
    mock_mute.assert_not_called()
    mock_shutter.assert_not_called()
    fake_pjlink.projectorUpdateIcons.assert_not_called()
    fake_pjlink.status_timer_delete.assert_not_called()


@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_mute')
@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_shutter')
def test_avmt_10(mock_shutter, mock_mute, fake_pjlink, caplog):
    """
    Test 10 = Shutter open, audio unchanged
    """
    # GIVEN: Test setup
    t_data = '10'

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({fake_pjlink.name}) Setting shutter to open')]

    # WHEN: Called
    _process_avmt(projector=fake_pjlink, data=t_data)

    # THEN: Shutter and mute should be set correctly
    assert caplog.record_tuples == logs, 'Invalid log entries'
    mock_mute.assert_not_called()
    mock_shutter.assert_called_with(projector=fake_pjlink, data=False)
    fake_pjlink.projectorUpdateIcons.emit.assert_called_once()
    fake_pjlink.status_timer_delete.assert_called_once_with('AVMT')


@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_mute')
@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_shutter')
def test_avmt_11(mock_shutter, mock_mute, fake_pjlink, caplog):
    """
    Test 11 = Shutter closed, audio unchanged
    """
    # GIVEN: Test setup
    t_data = '11'
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({fake_pjlink.name}) Setting shutter to closed')]

    # WHEN: Called with setting shutter closed and mute on
    _process_avmt(projector=fake_pjlink, data=t_data)

    # THEN: Shutter and mute should be set correctly
    assert caplog.record_tuples == logs, 'Invalid log entries'
    mock_mute.assert_not_called()
    mock_shutter.assert_called_once_with(projector=fake_pjlink, data=True)
    fake_pjlink.projectorUpdateIcons.emit.assert_called_once()
    fake_pjlink.status_timer_delete.assert_called_once_with('AVMT')


@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_mute')
@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_shutter')
def test_avmt_20(mock_shutter, mock_mute, fake_pjlink, caplog):
    """
    Test 20 = Shutter unchanged, audio normal
    """
    # GIVEN: Test setup
    t_data = '20'
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({fake_pjlink.name}) Setting speaker to normal')]

    # WHEN: Called with setting shutter closed and mute on
    _process_avmt(projector=fake_pjlink, data=t_data)

    # THEN: Shutter and mute should be set correctly
    assert caplog.record_tuples == logs, 'Invalid log entries'
    mock_mute.assert_called_once_with(projector=fake_pjlink, data=False)
    mock_shutter.assert_not_called()
    fake_pjlink.projectorUpdateIcons.emit.assert_called_once()
    fake_pjlink.status_timer_delete.assert_called_once_with('AVMT')


@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_mute')
@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_shutter')
def test_avmt_21(mock_shutter, mock_mute, fake_pjlink, caplog):
    """
    Test 21 = Shutter unchanged, audio mute
    """
    # GIVEN: Test setup
    t_data = '21'
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({fake_pjlink.name}) Setting speaker to muted')]

    # WHEN: Called with setting shutter closed and mute on
    _process_avmt(projector=fake_pjlink, data=t_data)

    # THEN: Shutter and mute should be set correctly
    assert caplog.record_tuples == logs, 'Invalid log entries'
    mock_mute.assert_called_once_with(projector=fake_pjlink, data=True)
    mock_shutter.assert_not_called()
    fake_pjlink.projectorUpdateIcons.emit.assert_called_once()
    fake_pjlink.status_timer_delete.assert_called_once_with('AVMT')


@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_mute')
@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_shutter')
def test_avmt_30(mock_shutter, mock_mute, fake_pjlink, caplog):
    """
    Test 30 = Shutter open, audio normal
    """
    # GIVEN: Test setup
    t_data = '30'

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({fake_pjlink.name}) Setting shutter to open'),
            (test_module, logging.DEBUG, f'({fake_pjlink.name}) Setting speaker to normal')
            ]

    # WHEN: Called
    _process_avmt(projector=fake_pjlink, data=t_data)

    # THEN: Shutter and mute should be set correctly
    assert caplog.record_tuples == logs, 'Invalid log entries'
    mock_mute.assert_called_once_with(projector=fake_pjlink, data=False)
    mock_shutter.assert_called_once_with(projector=fake_pjlink, data=False)
    fake_pjlink.projectorUpdateIcons.emit.assert_called_once()
    fake_pjlink.status_timer_delete.assert_called_once_with('AVMT')


@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_mute')
@patch.object(openlp.core.projectors.pjlinkcommands, '_process_avmt_shutter')
def test_avmt_31(mock_shutter, mock_mute, fake_pjlink, caplog):
    """
    Test 31 = Shutter closed, audio mute
    """
    # GIVEN: Test object
    t_data = '31'

    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, f'({fake_pjlink.name}) Setting shutter to closed'),
            (test_module, logging.DEBUG, f'({fake_pjlink.name}) Setting speaker to muted')
            ]
    # WHEN: Called
    _process_avmt(projector=fake_pjlink, data=t_data)

    # THEN: Shutter and mute should be set correctly
    assert caplog.record_tuples == logs, 'Invalid log entries'
    mock_mute.assert_called_once_with(projector=fake_pjlink, data=True)
    mock_shutter.assert_called_once_with(projector=fake_pjlink, data=True)
    fake_pjlink.projectorUpdateIcons.emit.assert_called_once()
    fake_pjlink.status_timer_delete.assert_called_once_with('AVMT')
