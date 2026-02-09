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
Package to test the openlp.core.lib.settingsform package.
"""
import pytest
from unittest.mock import MagicMock, patch

from PySide6 import QtCore, QtTest

from openlp.core.ui.settingsform import SettingsForm


@pytest.fixture()
def form(mock_settings):
    frm = SettingsForm()
    return frm


@pytest.fixture()
def dummy():
    return MagicMock(), MagicMock(), MagicMock()


def test_basic_cancel(form):
    """
    Test running the settings form and pressing Cancel
    """
    # GIVEN: An initial form

    # WHEN displaying the UI and pressing cancel
    with patch('PySide6.QtWidgets.QDialog.reject') as mocked_reject:
        cancel_widget = form.button_box.button(form.button_box.StandardButton.Cancel)
        QtTest.QTest.mouseClick(cancel_widget, QtCore.Qt.MouseButton.LeftButton)

        # THEN the dialog reject should have been called
        assert mocked_reject.call_count == 1, 'The QDialog.reject should have been called'


def test_basic_accept(form):
    """
    Test running the settings form and pressing Ok
    """
    # GIVEN: An initial form

    # WHEN displaying the UI and pressing Ok
    with patch('PySide6.QtWidgets.QDialog.accept') as mocked_accept:
        ok_widget = form.button_box.button(form.button_box.StandardButton.Ok)
        QtTest.QTest.mouseClick(ok_widget, QtCore.Qt.MouseButton.LeftButton)

        # THEN the dialog reject should have been called
        assert mocked_accept.call_count == 1, 'The QDialog.accept should have been called'


def test_basic_register(form):
    """
    Test running the settings form and adding a single function
    """
    # GIVEN: An initial form add a register function
    form.register_post_process('function1')

    # WHEN displaying the UI and pressing Ok
    with patch('PySide6.QtWidgets.QDialog.accept'):
        ok_widget = form.button_box.button(form.button_box.StandardButton.Ok)
        QtTest.QTest.mouseClick(ok_widget, QtCore.Qt.MouseButton.LeftButton)

        # THEN the processing stack should be empty
        assert len(form.processes) == 0, 'The one requested process should have been removed from the stack'


def test_register_multiple_functions(form):
    """
    Test running the settings form and adding multiple functions
    """
    # GIVEN: Registering a single function
    form.register_post_process('function1')

    # WHEN testing the processing stack
    # THEN the processing stack should have one item
    assert len(form.processes) == 1, 'The one requested process should have been added to the stack'

    # GIVEN: Registering a new function
    form.register_post_process('function2')

    # WHEN testing the processing stack
    # THEN the processing stack should have two items
    assert len(form.processes) == 2, 'The two requested processes should have been added to the stack'

    # GIVEN: Registering a process for the second time
    form.register_post_process('function1')

    # WHEN testing the processing stack
    # THEN the processing stack should still have two items
    assert len(form.processes) == 2, 'No new processes should have been added to the stack'
