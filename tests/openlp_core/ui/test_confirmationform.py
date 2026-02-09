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
Test the Confirmation Form
"""
from unittest.mock import patch
from PySide6 import QtWidgets, QtTest, QtCore

from openlp.core.ui.confirmationform import ConfirmationForm


def test_confirmation_form_ui_setup(settings):
    """
    Test checking the UI elements are set up correctly
    """
    # GIVEN: A ConfirmationForm class

    # WHEN: A ConfirmationForm object is created
    form = ConfirmationForm(None, "title", ["item1", "item2", "item3"], "confirm?")

    # THEN: The UI elements should reflect the parameters passed
    assert form.windowTitle() == "title"
    assert form.findChild(QtWidgets.QListView, "confirmation listview").model().rowCount() == 3
    assert form.findChild(QtWidgets.QListView, "confirmation listview").model().item(0).text() == "item1"
    assert form.findChild(QtWidgets.QListView, "confirmation listview").model().item(1).text() == "item2"
    assert form.findChild(QtWidgets.QListView, "confirmation listview").model().item(2).text() == "item3"
    assert form.findChild(QtWidgets.QLabel, "message").text() == "confirm?"


@patch('openlp.core.ui.confirmationform.ConfirmationForm.accept')
@patch('openlp.core.ui.confirmationform.ConfirmationForm.reject')
def test_confirmation_form_yes_button(mocked_reject, mocked_accept, settings):
    """
    Test when the Yes button is clicked
    """
    # GIVEN: A ConfirmationForm
    form = ConfirmationForm(None, "title", ["item1", "item2", "item3"], "confirm?")
    form.accept = mocked_accept
    form.reject = mocked_reject

    # WHEN: The Yes button is clicked
    buttons = form.findChildren(QtWidgets.QPushButton)
    for button in buttons:
        if 'Yes' in button.text():
            QtTest.QTest.mouseClick(button, QtCore.Qt.MouseButton.LeftButton)
            break

    # THEN: accept is called
    assert form.accept.call_count == 1
    assert form.reject.call_count == 0


@patch('openlp.core.ui.confirmationform.ConfirmationForm.accept')
@patch('openlp.core.ui.confirmationform.ConfirmationForm.reject')
def test_confirmation_form_no_button(mocked_reject, mocked_accept, settings):
    """
    Test when the No button is clicked
    """
    # GIVEN: A ConfirmationForm
    form = ConfirmationForm(None, "title", ["item1", "item2", "item3"], "confirm?")
    form.accept = mocked_accept
    form.reject = mocked_reject

    # WHEN: The No button is clicked
    buttons = form.findChildren(QtWidgets.QPushButton)
    for button in buttons:
        if 'No' in button.text():
            QtTest.QTest.mouseClick(button, QtCore.Qt.MouseButton.LeftButton)
            break

    # THEN: reject is called
    assert form.accept.call_count == 0
    assert form.reject.call_count == 1
