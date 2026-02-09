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
Module to test the EditCustomForm.
"""
import pytest
from unittest.mock import MagicMock, patch

from PySide6 import QtCore, QtTest, QtWidgets

from openlp.core.common.settings import Settings
from openlp.plugins.custom.forms.editcustomform import EditCustomForm


@pytest.fixture()
def form(settings: Settings):
    main_window = QtWidgets.QMainWindow()
    media_item = MagicMock()
    manager = MagicMock()
    frm = EditCustomForm(media_item, main_window, manager)
    yield frm
    del frm
    del main_window


def test_load_themes(form: EditCustomForm):
    """
    Test the load_themes() method.
    """
    # GIVEN: A theme list.
    theme_list = ['First Theme', 'Second Theme']

    # WHEN: Show the dialog and add pass a theme list.
    form.load_themes(theme_list)

    # THEN: There should be three items in the combo box.
    assert form.theme_combo_box.count() == 3, 'There should be three items (themes) in the combo box.'


def test_load_custom(form: EditCustomForm):
    """
    Test the load_custom() method.
    """
    # WHEN: Create a new custom item.
    form.load_custom(0)

    # THEN: The line edits should not contain any text.
    assert form.title_edit.text() == '', 'The title edit should be empty'
    assert form.credit_edit.text() == '', 'The credit edit should be empty'


def test_on_add_button_clicked(form: EditCustomForm):
    """
    Test the on_add_button_clicked_test method / add_button button.
    """
    # GIVEN: A mocked QDialog.exec() method
    with patch('PySide6.QtWidgets.QDialog.exec'):
        # WHEN: Add a new slide.
        QtTest.QTest.mouseClick(form.add_button, QtCore.Qt.MouseButton.LeftButton)

        # THEN: One slide should be added.
        assert form.slide_list_view.count() == 1, 'There should be one slide added.'


def test_validate_not_valid_part1(form: EditCustomForm):
    """
    Test the _validate() method.
    """
    # GIVEN: Mocked methods.
    with patch('openlp.plugins.custom.forms.editcustomform.critical_error_message_box') as \
            mocked_critical_error_message_box:
        form.title_edit.displayText = MagicMock(return_value='')
        mocked_setFocus = MagicMock()
        form.title_edit.setFocus = mocked_setFocus

        # WHEN: Call the method.
        result = form._validate()

        # THEN: The validate method should have returned False.
        assert not result, 'The _validate() method should have retured False'
        mocked_setFocus.assert_called_with()
        mocked_critical_error_message_box.assert_called_with(message='You need to type in a title.')


def test_validate_not_valid_part2(form: EditCustomForm):
    """
    Test the _validate() method.
    """
    # GIVEN: Mocked methods.
    with patch('openlp.plugins.custom.forms.editcustomform.critical_error_message_box') as \
            mocked_critical_error_message_box:
        form.title_edit.displayText = MagicMock(return_value='something')
        form.slide_list_view.count = MagicMock(return_value=0)

        # WHEN: Call the method.
        result = form._validate()

        # THEN: The validate method should have returned False.
        assert not result, 'The _validate() method should have retured False'
        mocked_critical_error_message_box.assert_called_with(message='You need to add at least one slide.')


def test_update_slide_list(form: EditCustomForm):
    """
    Test the update_slide_list() method
    """
    # GIVEN: Mocked slide_list_view with a slide with 3 lines
    form.slide_list_view = MagicMock()
    form.slide_list_view.count.return_value = 1
    form.slide_list_view.currentRow.return_value = 0
    form.slide_list_view.item.return_value = MagicMock(return_value='1st Slide\n2nd Slide\n3rd Slide')

    # WHEN: updating the slide by splitting the lines into slides
    form.update_slide_list(['1st Slide', '2nd Slide', '3rd Slide'])

    # THEN: The slides should be created in correct order
    form.slide_list_view.addItems.assert_called_with(['1st Slide', '2nd Slide', '3rd Slide'])


def test_help(settings: Settings):
    """
    Test the help button
    """
    # GIVEN: An edit custom slide form and a patched help function
    main_window = QtWidgets.QMainWindow()
    custom_form = EditCustomForm(MagicMock(), main_window, MagicMock())

    # WHEN: The Help button is clicked
    with patch.object(custom_form, 'provide_help') as mocked_help:
        QtTest.QTest.mouseClick(custom_form.button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Help),
                                QtCore.Qt.MouseButton.LeftButton)

    # THEN: The Help function should be called
    mocked_help.assert_called_once()
