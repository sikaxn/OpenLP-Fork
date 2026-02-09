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
Tests for choosegroupform from the openlp.plugins.images.forms package.
"""
import pytest
from unittest.mock import MagicMock

from PySide6 import QtWidgets

from openlp.core.common.registry import Registry
from openlp.plugins.images.forms.choosegroupform import ChooseGroupForm


@pytest.fixture()
def form(settings):
    main_window = QtWidgets.QMainWindow()
    Registry().register('main_window', main_window)
    frm = ChooseGroupForm(main_window)
    yield frm
    del frm
    del main_window


def test_no_group_selected_by_default(form):
    """
    Tests that the No Group option is the default selection
    """
    assert form.nogroup_radio_button.isChecked()


def test_provided_group_is_selected(form):
    """
    Tests preselected group initialization
    """
    # GIVEN: There are some existing groups
    QtWidgets.QDialog.exec = MagicMock(return_value=QtWidgets.QDialog.DialogCode.Accepted)
    form.group_combobox.addItem('Group 1', 0)
    form.group_combobox.addItem('Group 2', 1)

    # WHEN: The form is displayed with preselected group index 1
    form.exec(1)

    # THEN: The Existing Group should be selected along with the radio button
    assert form.group_combobox.currentIndex() == 1
    assert form.existing_radio_button.isChecked()


def test_auto_select_existing_group_on_combo_selection(form):
    """
    Tests that the Existing Group option becomes selected when changing the combobox
    """
    # GIVEN: No preselected group was provided during initialization
    assert not form.existing_radio_button.isChecked()

    # WHEN: An existing group is selected from the combo box
    form.on_group_combobox_selected(0)

    # THEN: The Existing Group radio button should also be selected
    assert form.existing_radio_button.isChecked()


def test_auto_select_new_group_on_edit(form):
    """
    Tests that the New Group option becomes selected when changing the text field
    """
    # GIVEN: The New Group option has not already been selected
    assert not form.new_radio_button.isChecked()

    # WHEN: The user enters text into the new group name text field
    form.on_new_group_edit_changed('Test Group')

    # THEN: The New Group radio button should also be selected
    assert form.new_radio_button.isChecked()
