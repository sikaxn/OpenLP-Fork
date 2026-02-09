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
Package to test the openlp.core.ui.shortcutform package.
"""
import pytest
from unittest.mock import MagicMock, patch

from PySide6 import QtCore, QtWidgets

from openlp.core.ui.shortcutlistform import ShortcutListForm


@pytest.fixture()
def form(mock_settings):
    frm = ShortcutListForm()
    return frm


def test_adjust_button(form):
    """
    Test the _adjust_button() method
    """
    # GIVEN: A button.
    button = QtWidgets.QPushButton()
    checked = True
    enabled = True
    text = 'new!'

    # WHEN: Call the method.
    with patch('PySide6.QtWidgets.QPushButton.setChecked') as mocked_check_method:
        form._adjust_button(button, checked, enabled, text)

        # THEN: The button should be changed.
        assert button.text() == text, 'The text should match.'
        mocked_check_method.assert_called_once_with(True)
        assert button.isEnabled() == enabled, 'The button should be disabled.'


def test_space_key_press_event(form):
    """
    Test the keyPressEvent when the spacebar was pressed
    """
    # GIVEN: A key event that is a space
    mocked_event = MagicMock()
    mocked_event.key.return_value = QtCore.Qt.Key.Key_Space

    # WHEN: The event is handled
    with patch.object(form, 'keyReleaseEvent') as mocked_key_release_event:
        form.keyPressEvent(mocked_event)

        # THEN: The key should be released
        mocked_key_release_event.assert_called_with(mocked_event)
        assert 0 == mocked_event.accept.call_count


def test_primary_push_button_checked_key_press_event(form):
    """
    Test the keyPressEvent when the primary push button is checked
    """
    # GIVEN: The primary push button is checked
    with patch.object(form, 'keyReleaseEvent') as mocked_key_release_event, \
            patch.object(form.primary_push_button, 'isChecked') as mocked_is_checked:
        mocked_is_checked.return_value = True
        mocked_event = MagicMock()

        # WHEN: The event is handled
        form.keyPressEvent(mocked_event)

        # THEN: The key should be released
        mocked_key_release_event.assert_called_with(mocked_event)
        assert 0 == mocked_event.accept.call_count


def test_alternate_push_button_checked_key_press_event(form):
    """
    Test the keyPressEvent when the alternate push button is checked
    """
    # GIVEN: The primary push button is checked
    with patch.object(form, 'keyReleaseEvent') as mocked_key_release_event, \
            patch.object(form.alternate_push_button, 'isChecked') as mocked_is_checked:
        mocked_is_checked.return_value = True
        mocked_event = MagicMock()

        # WHEN: The event is handled
        form.keyPressEvent(mocked_event)

        # THEN: The key should be released
        mocked_key_release_event.assert_called_with(mocked_event)
        assert 0 == mocked_event.accept.call_count


def test_escape_key_press_event(form):
    """
    Test the keyPressEvent when the escape key was pressed
    """
    # GIVEN: A key event that is an escape
    mocked_event = MagicMock()
    mocked_event.key.return_value = QtCore.Qt.Key.Key_Escape

    # WHEN: The event is handled
    with patch.object(form, 'close') as mocked_close:
        form.keyPressEvent(mocked_event)

        # THEN: The key should be released
        mocked_event.accept.assert_called_with()
        mocked_close.assert_called_with()


def test_on_default_radio_button_not_toggled(form):
    """
    Test that the default radio button method exits early when the button is not toggled
    """
    # GIVEN: A not-toggled custom radio button
    with patch.object(form, '_current_item_action') as mocked_current_item_action:

        # WHEN: The clicked method is called
        form.on_default_radio_button_clicked(False)

        # THEN: The method should exit early (i.e. the rest of the methods are not called)
        assert 0 == mocked_current_item_action.call_count


def test_on_default_radio_button_clicked_no_action(form):
    """
    Test that nothing happens when an action hasn't been selected and you click the default radio button
    """
    # GIVEN: Some mocked out methods, a current action, and some shortcuts
    with patch.object(form, '_current_item_action') as mocked_current_item_action, \
            patch.object(form, '_action_shortcuts') as mocked_action_shortcuts:
        mocked_current_item_action.return_value = None

        # WHEN: The default radio button is clicked
        form.on_default_radio_button_clicked(True)

        # THEN: The method should exit early (i.e. the rest of the methods are not called)
        mocked_current_item_action.assert_called_with()
        assert 0 == mocked_action_shortcuts.call_count


def test_on_default_radio_button_clicked(form):
    """
    Test that the values are copied across correctly when the default radio button is selected
    """
    # GIVEN: Some mocked out methods, a current action, and some shortcuts
    with patch.object(form, '_current_item_action') as mocked_current_item_action, \
            patch.object(form, '_action_shortcuts') as mocked_action_shortcuts, \
            patch.object(form, 'refresh_shortcut_list') as mocked_refresh_shortcut_list, \
            patch.object(form, 'get_shortcut_string') as mocked_get_shortcut_string, \
            patch.object(form.primary_push_button, 'setText') as mocked_set_text:
        mocked_action = MagicMock()
        mocked_action.default_shortcuts = [QtCore.Qt.Key.Key_Escape]
        mocked_current_item_action.return_value = mocked_action
        mocked_action_shortcuts.return_value = [QtCore.Qt.Key.Key_Escape]
        mocked_get_shortcut_string.return_value = 'Esc'

        # WHEN: The default radio button is clicked
        form.on_default_radio_button_clicked(True)

        # THEN: The shorcuts should be copied across
        mocked_current_item_action.assert_called_with()
        mocked_action_shortcuts.assert_called_with(mocked_action)
        mocked_refresh_shortcut_list.assert_called_with()
        mocked_set_text.assert_called_with('Esc')


def test_on_custom_radio_button_not_toggled(form):
    """
    Test that the custom radio button method exits early when the button is not toggled
    """
    # GIVEN: A not-toggled custom radio button
    with patch.object(form, '_current_item_action') as mocked_current_item_action:

        # WHEN: The clicked method is called
        form.on_custom_radio_button_clicked(False)

        # THEN: The method should exit early (i.e. the rest of the methods are not called)
        assert 0 == mocked_current_item_action.call_count


def test_on_custom_radio_button_clicked(form):
    """
    Test that the values are copied across correctly when the custom radio button is selected
    """
    # GIVEN: Some mocked out methods, a current action, and some shortcuts
    with patch.object(form, '_current_item_action') as mocked_current_item_action, \
            patch.object(form, '_action_shortcuts') as mocked_action_shortcuts, \
            patch.object(form, 'refresh_shortcut_list') as mocked_refresh_shortcut_list, \
            patch.object(form, 'get_shortcut_string') as mocked_get_shortcut_string, \
            patch.object(form.primary_push_button, 'setText') as mocked_set_text:
        mocked_action = MagicMock()
        mocked_current_item_action.return_value = mocked_action
        mocked_action_shortcuts.return_value = [QtCore.Qt.Key.Key_Escape]
        mocked_get_shortcut_string.return_value = 'Esc'

        # WHEN: The custom radio button is clicked
        form.on_custom_radio_button_clicked(True)

        # THEN: The shorcuts should be copied across
        mocked_current_item_action.assert_called_with()
        mocked_action_shortcuts.assert_called_with(mocked_action)
        mocked_refresh_shortcut_list.assert_called_with()
        mocked_set_text.assert_called_with('Esc')
