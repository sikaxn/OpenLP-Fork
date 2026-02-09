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
Package to test the :mod:`~openlp.core.ui.serviceitemeditform` package.
"""
import pytest
from unittest.mock import MagicMock, call, patch

from PySide6 import QtCore, QtTest

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.ui.serviceitemeditform import ServiceItemEditForm


@pytest.fixture
def form(registry: Registry, settings: Settings):
    Registry().register('main_window', None)
    frm = ServiceItemEditForm()
    return frm


def test_basic_display(form: ServiceItemEditForm):
    """Test that the ServiceItemEditForm is displayed"""
    # GIVEN: A dialog
    # WHEN: Displaying the UI
    with patch('openlp.core.ui.serviceitemeditform.QtWidgets.QDialog.exec'):
        form.exec()
    ok_widget = form.button_box.button(form.button_box.StandardButton.Save)
    QtTest.QTest.mouseClick(ok_widget, QtCore.Qt.MouseButton.LeftButton)

    # THEN: Everything should be fine
    assert form.item_list == [], 'The item list should be empty'


def test_set_service_item(form: ServiceItemEditForm):
    """Test that the ServiceItemEditForm.set_service_item() method works correctly"""
    # GIVEN: A form with some methods mocked out
    mocked_item = MagicMock(**{'is_image.return_value': True, 'slides': ['slide1.jpg']})
    form.load_data = MagicMock()
    form.list_widget.setCurrentItem = MagicMock()

    # WHEN: set_service_item() is called
    form.set_service_item(mocked_item)

    # THEN: The item should be set and the correct methods called
    assert form.item is mocked_item, 'form.item should be mocked_item'
    mocked_item.is_image.assert_called_once_with()
    assert form.data is True, 'The data attribute should be true'
    assert form.item_list == ['slide1.jpg'], 'form.item_list should be a list of 1 item'
    form.load_data.assert_called_once_with()
    form.list_widget.setCurrentItem.assert_called_once_with(None)


def test_get_service_item(form: ServiceItemEditForm):
    """Test that the ServiceItemEditForm.get_service_item() works correctly"""
    # GIVEN: A form with some methods mocked out
    form.data = True
    form.item = MagicMock(slides=['slide1.jpg', 'slide2.jpg'])
    form.item_list = [
        {'path': '../slide1.jpg', 'title': 'slide1.jpg'},
        {'path': '../slide2.jpg', 'title': 'slide2.jpg'}
    ]

    # WHEN: get_service_item() is called
    item = form.get_service_item()

    # THEN: The item should be returned and the correct methods called
    assert item is form.item, 'The returned item should be form.item'
    # FYI: list should be empty because it was cleared but never filled again due to the mock
    assert item.slides == [], 'The list of slides should have been cleared'
    assert item.add_from_image.call_args_list == [call('../slide1.jpg', 'slide1.jpg', None, None),
                                                  call('../slide2.jpg', 'slide2.jpg', None, None)]


@patch('openlp.core.ui.serviceitemeditform.QtWidgets.QListWidgetItem')
def test_load_data(MockQListWidgetItem: MagicMock, form: ServiceItemEditForm):
    """Test that the ServiceItemEditForm.load_data() works correctly"""
    # GIVEN: A form with some methods mocked out
    MockQListWidgetItem.side_effect = lambda x: x
    form.list_widget.clear = MagicMock()
    form.list_widget.addItem = MagicMock()
    form.item_list = [
        {'path': '../slide1.jpg', 'title': 'slide1.jpg'},
        {'path': '../slide2.jpg', 'title': 'slide2.jpg'}
    ]

    # WHEN: load_data() is called
    form.load_data()

    # THEN: The list widget should have the correct items added
    form.list_widget.clear.assert_called_once_with()
    assert form.list_widget.addItem.call_args_list == [call('slide1.jpg'), call('slide2.jpg')]


def test_on_delete_button_clicked_no_item(form: ServiceItemEditForm):
    """Test that nothing happens when the delete button is clicked but no item is selected"""
    # GIVEN: A form with the currentItem() method mocked
    form.list_widget.currentItem = MagicMock(return_value=None)
    form.list_widget.row = MagicMock()

    # WHEN: on_delete_button_clicked() is called but no items are selected
    form.on_delete_button_clicked()

    # THEN: Nothing should have happened
    assert form.list_widget.row.call_count == 0, 'The row method should not have been called'


def test_on_delete_button_clicked(form: ServiceItemEditForm):
    """Test that clicking the delete button removes a row from the list"""
    # GIVEN: A form with some items mocked out
    mocked_list_item = MagicMock()
    form.item_list = ['slide1', 'slide2']
    form.list_widget.currentItem = MagicMock(return_value=mocked_list_item)
    form.list_widget.row = MagicMock(return_value=1)
    form.load_data = MagicMock()
    form.list_widget.count = MagicMock(return_value=1)
    form.list_widget.setCurrentRow = MagicMock()

    # WHEN: on_delete_button_clicked() is called
    form.on_delete_button_clicked()

    # THEN: The correct methods should have been called
    form.list_widget.currentItem.assert_called_once_with()
    form.list_widget.row.assert_called_once_with(mocked_list_item)
    assert form.item_list == ['slide1'], 'There should be only 1 slide in the list'
    form.load_data.assert_called_once_with()
    form.list_widget.count.assert_called_once_with()
    form.list_widget.setCurrentRow.assert_called_once_with(0)


def test_on_up_button_clicked(form: ServiceItemEditForm):
    """Test that the the up button click calls the correct method"""
    # GIVEN: A form with a mocked out method
    form._ServiceItemEditForm__move_item = MagicMock()

    # WHEN: The event handler is called
    form.on_up_button_clicked()

    # THEN: The method should be called correctly
    form._ServiceItemEditForm__move_item.assert_called_once_with('up')


def test_on_down_button_clicked(form: ServiceItemEditForm):
    """Test that the the down button click calls the correct method"""
    # GIVEN: A form with a mocked out method
    form._ServiceItemEditForm__move_item = MagicMock()

    # WHEN: The event handler is called
    form.on_down_button_clicked()

    # THEN: The method should be called correctly
    form._ServiceItemEditForm__move_item.assert_called_once_with('down')


def test_move_item_no_direction(form: ServiceItemEditForm):
    """Test that the __move_item() method exits early if no direction is specified"""
    # GIVEN: A form with am ocked out method
    form.list_widget.currentItem = MagicMock()

    # WHEN: __move_item() is called without a direction
    form._ServiceItemEditForm__move_item()

    # THEN: The method should exit early, thus currentItem() should not have been called
    assert form.list_widget.currentItem.call_count == 0, 'currentItem() should not have been called'


def test_move_item_no_item(form: ServiceItemEditForm):
    """Test that the __move_item() method exits early if no item in the list is selected"""
    # GIVEN: A form with am ocked out method
    form.list_widget.currentItem = MagicMock(return_value=None)
    form.list_widget.row = MagicMock()

    # WHEN: __move_item() is called with a direction
    form._ServiceItemEditForm__move_item('up')

    # THEN: The method should exit early, thus row() should not have been called
    assert form.list_widget.row.call_count == 0, 'row() should not have been called'


def test_move_item_up(form: ServiceItemEditForm):
    """Test that the __move_item() method moves an item up"""
    # GIVEN: A form with am ocked out method
    mocked_list_item = MagicMock()
    form.item_list = ['slide1', 'slide2']
    form.list_widget.currentItem = MagicMock(return_value=mocked_list_item)
    form.list_widget.row = MagicMock(return_value=1)
    form.load_data = MagicMock()
    form.list_widget.setCurrentRow = MagicMock()

    # WHEN: __move_item() is called with the direction set to "up"
    form._ServiceItemEditForm__move_item('up')

    # THEN: The internal list should be swapped around, and other methods should have been called
    assert form.item_list == ['slide2', 'slide1'], 'The list should be swapped around'
    form.list_widget.setCurrentRow.assert_called_once_with(0)


def test_move_item_down(form: ServiceItemEditForm):
    """Test that the __move_item() method moves an item down"""
    # GIVEN: A form with am ocked out method
    mocked_list_item = MagicMock()
    form.item_list = ['slide1', 'slide2']
    form.list_widget.currentItem = MagicMock(return_value=mocked_list_item)
    form.list_widget.row = MagicMock(return_value=0)
    form.load_data = MagicMock()
    form.list_widget.setCurrentRow = MagicMock()

    # WHEN: __move_item() is called with the direction set to "up"
    form._ServiceItemEditForm__move_item('down')

    # THEN: The internal list should be swapped around, and other methods should have been called
    assert form.item_list == ['slide2', 'slide1'], 'The list should be swapped around'
    form.list_widget.setCurrentRow.assert_called_once_with(1)


def test_on_current_row_changed_no_selection(form: ServiceItemEditForm):
    """Test that all buttons are disabled when there is no selected item"""
    # GIVEN: A form and a row of -1
    row = -1

    # WHEN: on_current_row_changed() is called with the row
    form.on_current_row_changed(row)

    # THEN: All the buttons should be disabled
    assert form.down_button.isEnabled() is False, 'Down button should be disabled'
    assert form.up_button.isEnabled() is False, 'Up button should be disabled'
    assert form.delete_button.isEnabled() is False, 'Delete button should be disabled'


def test_on_current_row_changed_end_of_list(form: ServiceItemEditForm):
    """Test that the down button is disabled at the end of the list"""
    # GIVEN: A form with a couple of mocked methods and a row of 5
    row = 5
    form.list_widget.count = MagicMock(return_value=6)

    # WHEN: on_current_row_changed() is called with the row
    form.on_current_row_changed(row)

    # THEN: Down button should be disabled, up and delete should be enabled
    assert form.down_button.isEnabled() is False, 'Down button should be disabled'
    assert form.up_button.isEnabled() is True, 'Up button should be enabled'
    assert form.delete_button.isEnabled() is True, 'Delete button should be enabled'


def test_on_current_row_changed_beginning_of_list(form: ServiceItemEditForm):
    """Test that the up button is disabled at the top of the list"""
    # GIVEN: A form with a couple of mocked methods and a row of 0
    row = 0
    form.list_widget.count = MagicMock(return_value=6)

    # WHEN: on_current_row_changed() is called with the row
    form.on_current_row_changed(row)

    # THEN: Up button should be disabled, down and delete should be enabled
    assert form.down_button.isEnabled() is True, 'Down button should be enabled'
    assert form.up_button.isEnabled() is False, 'Up button should be disabled'
    assert form.delete_button.isEnabled() is True, 'Delete button should be enabled'
