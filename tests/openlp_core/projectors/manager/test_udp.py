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
Test ProjectorManager udp methods
"""
import logging

from unittest.mock import MagicMock, patch


from tests.helpers.projector import FakePJLinkUDP, FakeProjector


def test_udp_listen_add_duplicate(projector_manager, caplog):
    """
    Test adding UDP port listener to port already registered
    """
    # GIVEN: Initial setup
    caplog.set_level(logging.DEBUG)
    log_entries = ['UDP Listener for port 10 already added - skipping']
    port_list = {10: 'port1', 20: 'port2'}
    projector_manager.pjlink_udp = port_list

    # WHEN: udp_listen_add is called with duplicate port number
    caplog.clear()
    projector_manager.udp_listen_add(port=10)

    # THEN: Verify log entry and registry entry not called
    assert projector_manager.pjlink_udp == port_list, "Invalid ports in list"
    assert caplog.messages == log_entries, "Invalid log entries"


@patch('openlp.core.projectors.manager.PJLinkUDP')
@patch('openlp.core.projectors.manager.Registry')
def test_udp_listen_add_new(mock_registry, mock_udp, projector_manager, caplog):
    """
    Test adding new UDP port listener
    """
    # GIVEN: Initial setup
    caplog.set_level(logging.DEBUG)
    mocked_registry = MagicMock()
    mock_registry.return_value = mocked_registry
    mock_udp.return_value = FakePJLinkUDP()
    log_entries = ['Adding UDP listener on port 20']
    projector_manager.pjlink_udp = {10: 'port1'}
    # WHEN: Adding new listener
    caplog.clear()
    projector_manager.udp_listen_add(port=20)
    # THEN: Appropriate listener and log entries
    assert 20 in projector_manager.pjlink_udp, "Port not added"
    assert 2 == len(projector_manager.pjlink_udp), "Invalid ports in list"
    assert isinstance(projector_manager.pjlink_udp[20], FakePJLinkUDP), 'PJLinkUDP instance should have been added'
    assert mocked_registry.execute.has_call('udp_broadcast_add', port=20)
    assert caplog.messages == log_entries, 'Invalid log entries'


def test_udp_listen_delete_missing(projector_manager, caplog):
    """
    Test deleting UDP port listener not in list
    """
    # GIVEN: Initial setup
    caplog.set_level(logging.DEBUG)
    projector_manager.pjlink_udp = {10: 'port1'}
    log_entries = ['Checking for UDP port 20 listener deletion',
                   'UDP listener for port 20 not there - skipping delete']
    # WHEN: Deleting port listener from dictinary
    projector_manager.udp_listen_delete(port=20)
    # THEN: Log missing port and exit method
    assert projector_manager.pjlink_udp == {10: 'port1'}, "Invalid ports in list"
    assert caplog.messages == log_entries, "Invalid log entries"


@patch('openlp.core.projectors.manager.Registry')
def test_udp_listen_delete_single(mock_registry, projector_manager, caplog):
    """
    Test deleting UDP listener
    """
    # GIVEN: Initial setup
    mocked_registry = MagicMock()
    mock_registry.return_value = mocked_registry
    caplog.set_level(logging.DEBUG)
    log_entries = ['Checking for UDP port 10 listener deletion',
                   'UDP listener for port 10 deleted']
    port_list = {20: 'port2'}
    projector_manager.pjlink_udp = {10: 'port1', **port_list}
    projector_manager.projector_list = [FakeProjector(port=20)]
    # WHEN: deleting a listener
    caplog.clear()
    projector_manager.udp_listen_delete(port=10)
    # THEN: pjlink_udp and logs should have appropriate entries
    assert caplog.messages == log_entries, 'Invalid log entries'
    assert projector_manager.pjlink_udp == port_list, 'Invalid ports in list'
    assert mocked_registry.execute.has_call('udp_broadcast_delete', port=10)


def test_udp_listen_delete_skip(projector_manager, caplog):
    """
    Test not deleting UDP listener
    """
    # GIVEN: Initial setup
    caplog.set_level(logging.DEBUG)
    log_entries = ['Checking for UDP port 10 listener deletion',
                   'UDP listener for port 10 needed for other projectors - skipping delete']
    port_list = {10: 'port1', 20: 'port2'}
    projector_manager.pjlink_udp = port_list
    projector_manager.projector_list = [FakeProjector(port=10),
                                        FakeProjector(port=20)]
    # WHEN: deleting a listener
    caplog.clear()
    projector_manager.udp_listen_delete(port=10)

    # THEN: pjlink_udp and logs should have appropriate entries
    assert caplog.messages == log_entries, 'Invalid log entries'
    assert projector_manager.pjlink_udp == port_list, 'Invalid ports in list'
