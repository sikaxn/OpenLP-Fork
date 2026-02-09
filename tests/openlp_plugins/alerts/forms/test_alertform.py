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
Package to test the openlp.plugins.alerts.forms.alertform package.
"""
from unittest.mock import MagicMock, patch

from PySide6 import QtWidgets, QtTest, QtCore

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.alerts.forms.alertform import AlertForm


def test_help(settings: Settings, registry: Registry):
    """
    Test the help button
    """
    # GIVEN: An alert form and a patched help function
    registry.register('main_window', None)
    alert_form = AlertForm(MagicMock())

    # WHEN: The Help button is clicked
    with patch.object(alert_form, 'provide_help') as mocked_help:
        QtTest.QTest.mouseClick(alert_form.button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Help),
                                QtCore.Qt.MouseButton.LeftButton)

    # THEN: The Help function should be called
    mocked_help.assert_called_once()
