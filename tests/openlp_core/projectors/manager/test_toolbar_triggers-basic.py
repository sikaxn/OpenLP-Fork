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
Test methods called by toolbar icons with minimal flow paths and tests

on_add_projector()
on_doubleclick_item()
on_edit_input()

"""

import logging
import openlp.core.projectors.manager

from unittest.mock import DEFAULT, patch

from openlp.core.projectors.constants import QSOCKET_STATE, \
    S_CONNECTED, S_NOT_CONNECTED

from tests.helpers.projector import FakePJLink

test_module = openlp.core.projectors.manager.__name__


def test_on_add_projector(projector_manager):
    """
    Test add new projector edit GUI is called properly
    """
    # GIVEN: Test environment
    # Mock to keep from getting event not registered error in Registry()
    # during bootstrap_post_set_up()
    with patch.multiple(projector_manager,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT):
        projector_manager.bootstrap_initialise()
        projector_manager.bootstrap_post_set_up()

    # Have to wait for projector_manager.bootstrap_post_set_up() before projector_form is initialized
    with patch.object(projector_manager, 'projector_form') as mock_form:

        # WHEN called
        projector_manager.on_add_projector()

        # THEN: projector form called
        mock_form.exec.assert_called_once()


def test_on_edit_input(projector_manager, pjlink):
    """
    Test on_edit_input calls on_select_input properly
    """
    # GIVEN: Test setup
    with patch.object(projector_manager, 'on_select_input') as mock_input:

        # WHEN: Called with pjlink instance
        projector_manager.on_edit_input(opt=pjlink)

        # THEN: appropriate call made
        mock_input.assert_called_with(opt=pjlink, edit=True)


def test_on_doubleclick_item_connected(projector_manager_mtdb, caplog):
    """
    Test projector.connect_to_host() not called when status is S_CONNECTED
    """
    t_1 = FakePJLink()
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG,
             f'ProjectorManager: "{t_1.pjlink.name}" already connected - skipping')]

    with patch.multiple(projector_manager_mtdb,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT,
                        update_icons=DEFAULT,
                        _add_projector=DEFAULT) as mock_manager:

        projector_manager_mtdb.bootstrap_initialise()
        # projector_list_widget created here
        projector_manager_mtdb.bootstrap_post_set_up()

        # Add ProjectorItem instances to projector_list_widget
        mock_manager['_add_projector'].return_value = t_1
        projector_manager_mtdb.add_projector(projector=t_1)

        # WHEN: Called
        t_1.state.return_value = QSOCKET_STATE[S_CONNECTED]
        caplog.clear()
        projector_manager_mtdb.on_doubleclick_item(projector_manager_mtdb.projector_list_widget.item(0))

        assert caplog.record_tuples == logs, 'Invalid log entries'
        t_1.connect_to_host.assert_not_called()


def test_on_doubleclick_item_not_connected(projector_manager_mtdb, caplog):
    """
    Test projector.connect_to_host() called
    """
    t_1 = FakePJLink()
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG,
             f'ProjectorManager: "{t_1.pjlink.name}" calling connect_to_host()')]

    with patch.multiple(projector_manager_mtdb,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT,
                        update_icons=DEFAULT,
                        _add_projector=DEFAULT) as mock_manager:

        projector_manager_mtdb.bootstrap_initialise()
        # projector_list_widget created here
        projector_manager_mtdb.bootstrap_post_set_up()

        # Add ProjectorItem instances to projector_list_widget
        mock_manager['_add_projector'].return_value = t_1
        projector_manager_mtdb.add_projector(projector=t_1)

        # WHEN: Called
        t_1.state.return_value = QSOCKET_STATE[S_NOT_CONNECTED]
        caplog.clear()
        projector_manager_mtdb.on_doubleclick_item(projector_manager_mtdb.projector_list_widget.item(0))

        assert caplog.record_tuples == logs, 'Invalid log entries'
        t_1.connect_to_host.assert_called_once()
