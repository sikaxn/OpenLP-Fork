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
This module contains tests for the settings tab for the Presentations plugin.
"""
from unittest.mock import MagicMock

from PySide6 import QtCore, QtTest

from openlp.core.common.registry import Registry
from openlp.plugins.presentations.lib.presentationtab import PresentationTab

__default_settings__ = {
    'presentations/powerpoint slide click advance': QtCore.Qt.CheckState.Unchecked,
    'presentations/powerpoint control window': QtCore.Qt.CheckState.Unchecked,
    'presentations/impress use display setting': QtCore.Qt.CheckState.Unchecked
}


def Mocked_Controllers(impress_available, powerpoint_available):
    impress_controller = MagicMock()
    impress_controller.name = 'Impress'
    impress_controller.display_name = 'Impress'
    impress_controller.is_available.return_value = impress_available
    powerpoint_controller = MagicMock()
    powerpoint_controller.name = 'Powerpoint'
    powerpoint_controller.display_name = 'Powerpoint'
    powerpoint_controller.is_available.return_value = powerpoint_available
    return {'Impress': impress_controller, 'Powerpoint': powerpoint_controller}


def test_check_boxes(settings):
    """
    Test check box options are correctly saved
    """
    # GIVEN: A presentations tab fixture
    Registry().register('settings_form', MagicMock())
    Registry().get('settings').extend_default_settings(__default_settings__)
    form = PresentationTab(None, 'Presentations', None, Mocked_Controllers(True, True), None)

    # WHEN: The presentations tab checkboxes are checked and the form saved
    QtTest.QTest.mouseClick(form.ppt_slide_click_check_box, QtCore.Qt.MouseButton.LeftButton)
    QtTest.QTest.mouseClick(form.ppt_window_check_box, QtCore.Qt.MouseButton.LeftButton)
    QtTest.QTest.mouseClick(form.odp_display_check_box, QtCore.Qt.MouseButton.LeftButton)
    form.activated = True
    form.save()
    # THEN: The updated values should be stored in the settings
    assert form.settings.value('presentations/powerpoint slide click advance') == QtCore.Qt.CheckState.Checked
    assert form.settings.value('presentations/powerpoint control window') == QtCore.Qt.CheckState.Checked
    assert form.settings.value('presentations/impress use display setting') == QtCore.Qt.CheckState.Checked


def test_check_boxes_when_controllers_unavailable(settings):
    """
    Test settings related check box options are unchanged when controllers aren't available
    """
    # GIVEN: A presentations tab fixture
    Registry().register('settings_form', MagicMock())
    Registry().get('settings').extend_default_settings(__default_settings__)
    form = PresentationTab(None, 'Presentations', None, Mocked_Controllers(False, False), None)

    # WHEN: The presentations tab checkboxes are checked and the form saved
    QtTest.QTest.mouseClick(form.ppt_slide_click_check_box, QtCore.Qt.MouseButton.LeftButton)
    QtTest.QTest.mouseClick(form.ppt_window_check_box, QtCore.Qt.MouseButton.LeftButton)
    QtTest.QTest.mouseClick(form.odp_display_check_box, QtCore.Qt.MouseButton.LeftButton)
    form.activated = True
    form.save()
    # THEN: The updated values should be unchanged
    assert form.settings.value('presentations/powerpoint slide click advance') == QtCore.Qt.CheckState.Unchecked
    assert form.settings.value('presentations/powerpoint control window') == QtCore.Qt.CheckState.Unchecked
    assert form.settings.value('presentations/impress use display setting') == QtCore.Qt.CheckState.Unchecked
