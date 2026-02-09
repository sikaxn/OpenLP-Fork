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
Test ProjectorManager.bootstrap_* methods
"""
import logging
import openlp.core.projectors.manager

from unittest.mock import DEFAULT, MagicMock, patch

test_module = openlp.core.projectors.manager.__name__


@patch('openlp.core.projectors.manager.ProjectorDB')
def test_bootstrap_initialise(mock_db, projector_manager, caplog):
    """
    Test ProjectorManager initializes with existing ProjectorDB instance
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Using existing ProjectorDB() instance')]

    with patch.multiple(projector_manager,
                        setup_ui=DEFAULT,
                        get_settings=DEFAULT) as mock_manager:

        # WHEN: we call bootstrap_initialise
        caplog.clear()
        projector_manager.bootstrap_initialise()

        # THEN: Appropriate entries and actions
        assert caplog.record_tuples == logs, 'Invalid log entries'
        mock_manager['setup_ui'].assert_called_once()
        mock_manager['get_settings'].assert_called_once()
        mock_db.assert_not_called()


@patch('openlp.core.projectors.manager.ProjectorDB')
def test_bootstrap_initialise_nodb(mock_db, projector_manager_nodb, caplog):
    """
    Test ProjectorManager initializes with a new ProjectorDB instance
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Creating new ProjectorDB() instance')]

    with patch.multiple(projector_manager_nodb,
                        setup_ui=DEFAULT,
                        get_settings=DEFAULT) as mock_manager:

        # WHEN: we call bootstrap_initialise
        caplog.clear()
        projector_manager_nodb.bootstrap_initialise()

        # THEN: Appropriate entries and actions
        assert caplog.record_tuples == logs, 'Invalid log entries'
        mock_manager['setup_ui'].assert_called_once()
        mock_manager['get_settings'].assert_called_once()
        mock_db.assert_called_once()


@patch('openlp.core.projectors.manager.ProjectorEditForm')
@patch('openlp.core.projectors.manager.QtCore.QTimer')
def test_bootstrap_post_set_up_autostart_false(mock_timer, mocked_edit, projector_manager, settings, caplog):
    """
    Test post-initialize calls proper setups
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Loading all projectors')]

    mock_updateProjectors = MagicMock()
    mock_edit = MagicMock()
    mock_edit.updateProjectors = mock_updateProjectors
    mocked_edit.return_value = mock_edit

    settings.setValue('projector/connect on start', False)
    projector_manager.bootstrap_initialise()

    with patch.multiple(projector_manager,
                        _load_projectors=DEFAULT,
                        projector_list_widget=DEFAULT) as mock_manager:

        # WHEN: Call to initialize is run
        caplog.clear()
        projector_manager.bootstrap_post_set_up()

        # THEN: verify calls and logs
        mock_timer.assert_not_called()
        mock_updateProjectors.connect.assert_called_once()
        mock_manager['_load_projectors'].assert_called_once(),
        mock_manager['projector_list_widget'].itemSelectionChanged.connect.assert_called_once()
        assert caplog.record_tuples == logs, 'Invalid log entries'


@patch('openlp.core.projectors.manager.ProjectorEditForm')
@patch('openlp.core.projectors.manager.QtCore.QTimer')
def test_bootstrap_post_set_up_autostart_true(mock_timer, mocked_edit, projector_manager, settings, caplog):
    """
    Test post-initialize calls proper setups
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Delaying 1.5 seconds before loading all projectors')]

    mock_updateProjectors = MagicMock()
    mock_edit = MagicMock()
    mock_edit.updateProjectors = mock_updateProjectors

    settings.setValue('projector/connect on start', True)
    projector_manager.bootstrap_initialise()

    with patch.multiple(projector_manager,
                        _load_projectors=DEFAULT,
                        projector_list_widget=DEFAULT) as mock_manager:
        mocked_edit.return_value = mock_edit

        # WHEN: Call to initialize is run
        caplog.clear()
        projector_manager.bootstrap_post_set_up()

        # THEN: verify calls and logs
        mock_timer.assert_called_once()
        mock_timer.return_value.singleShot.assert_called_once_with(1500, projector_manager._load_projectors)

        mock_updateProjectors.connect.assert_called_once()
        mock_manager['_load_projectors'].assert_not_called(),
        mock_manager['projector_list_widget'].itemSelectionChanged.connect.assert_called_once()
        assert caplog.record_tuples == logs, 'Invalid log entries'
