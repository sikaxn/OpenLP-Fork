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
Package to test the openlp.core.ui package.
"""
import pytest
from unittest.mock import MagicMock, patch

from PySide6 import QtCore, QtTest

from openlp.core.common.registry import Registry
from openlp.core.ui.starttimeform import StartTimeForm


@pytest.fixture()
def form(registry: Registry, mock_settings: MagicMock):
    registry.register('main_window', None)
    frm = StartTimeForm()
    return frm


def test_ui_defaults(form: StartTimeForm):
    """
    Test StartTimeDialog are defaults correct
    """
    assert form.hour_spin_box.minimum() == 0, 'The minimum hour should stay the same as the dialog'
    assert form.hour_spin_box.maximum() == 4, 'The maximum hour should stay the same as the dialog'
    assert form.minute_spin_box.minimum() == 0, 'The minimum minute should stay the same as the dialog'
    assert form.minute_spin_box.maximum() == 59, 'The maximum minute should stay the same as the dialog'
    assert form.second_spin_box.minimum() == 0, 'The minimum second should stay the same as the dialog'
    assert form.second_spin_box.maximum() == 59, 'The maximum second should stay the same as the dialog'
    assert form.hour_finish_spin_box.minimum() == 0, \
        'The minimum finish hour should stay the same as the dialog'
    assert form.hour_finish_spin_box.maximum() == 4, \
        'The maximum finish hour should stay the same as the dialog'
    assert form.minute_finish_spin_box.minimum() == 0, \
        'The minimum finish minute should stay the same as the dialog'
    assert form.minute_finish_spin_box.maximum() == 59, \
        'The maximum finish minute should stay the same as the dialog'
    assert form.second_finish_spin_box.minimum() == 0, \
        'The minimum finish second should stay the same as the dialog'
    assert form.second_finish_spin_box.maximum() == 59, \
        'The maximum finish second should stay the same as the dialog'


def test_time_display(form: StartTimeForm):
    """
    Test StartTimeDialog display functionality
    """
    # GIVEN: A service item with with time
    mocked_serviceitem = MagicMock()
    mocked_serviceitem.start_time = 61000
    mocked_serviceitem.end_time = 3701000
    mocked_serviceitem.media_length = 3701000

    # WHEN displaying the UI and pressing enter
    form.item = {'service_item': mocked_serviceitem}
    with patch('PySide6.QtWidgets.QDialog.exec'):
        form.exec()
    ok_widget = form.button_box.button(form.button_box.StandardButton.Ok)
    QtTest.QTest.mouseClick(ok_widget, QtCore.Qt.MouseButton.LeftButton)

    # THEN the following input values are returned
    assert form.hour_spin_box.value() == 0
    assert form.minute_spin_box.value() == 1
    assert form.second_spin_box.value() == 1
    assert form.item['service_item'].start_time == 61000, 'The start time should stay the same'

    # WHEN displaying the UI, changing the time to 2min 3secs and pressing enter
    form.item = {'service_item': mocked_serviceitem}
    with patch('PySide6.QtWidgets.QDialog.exec'):
        form.exec()
    form.minute_spin_box.setValue(2)
    form.second_spin_box.setValue(3)
    ok_widget = form.button_box.button(form.button_box.StandardButton.Ok)
    QtTest.QTest.mouseClick(ok_widget, QtCore.Qt.MouseButton.LeftButton)

    # THEN the following values are returned
    assert form.hour_spin_box.value() == 0
    assert form.minute_spin_box.value() == 2
    assert form.second_spin_box.value() == 3
    assert form.item['service_item'].start_time == 123000, 'The start time should have changed'
