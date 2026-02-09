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
This module contains tests for the CSV Bible importer.
"""
from unittest.mock import MagicMock

from openlp.plugins.alerts.lib.alertsmanager import AlertsManager


def test_remove_message_text(registry):
    """
    Test that Alerts are not triggered with empty strings
    """
    # GIVEN: A valid Alert Manager
    alert_manager = AlertsManager(None)
    alert_manager.display_alert = MagicMock()

    # WHEN: Called with an empty string
    alert_manager.alert_text('')

    # THEN: the display should not have been triggered
    assert alert_manager.display_alert.called is False, 'The Alert should not have been called'


def test_trigger_message_text(registry):
    """
    Test that Alerts are triggered with a text string
    """
    # GIVEN: A valid Alert Manager
    alert_manager = AlertsManager(None)
    alert_manager.display_alert = MagicMock()

    # WHEN: Called with an empty string
    alert_manager.alert_text(['This is a string'])

    # THEN: the display should have been triggered
    assert alert_manager.display_alert.called is True, 'The Alert should have been called'


def test_line_break_message_text(registry):
    """
    Test that Alerts are triggered with a text string but line breaks are removed
    """
    # GIVEN: A valid Alert Manager
    alert_manager = AlertsManager(None)
    alert_manager.display_alert = MagicMock()

    # WHEN: Called with an empty string
    alert_manager.alert_text(['This is \n a string'])

    # THEN: the display should have been triggered
    assert alert_manager.display_alert.called is True, 'The Alert should have been called'
    alert_manager.display_alert.assert_called_once_with('This is   a string')
