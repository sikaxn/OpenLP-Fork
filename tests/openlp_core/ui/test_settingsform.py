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
Package to test the openlp.core.ui.settingsform package.
"""
from unittest.mock import MagicMock, patch

from PySide6 import QtCore, QtWidgets, QtTest

from openlp.core.common.registry import Registry
from openlp.core.ui.settingsform import SettingsForm


class MockTab(QtWidgets.QWidget):
    """A mocked tab object, to make MyPy happy"""
    def __init__(self, parent, tab_title: str, tab_title_visible: str, icon_path: str):
        super().__init__(parent)
        self.tab_title = tab_title
        self.tab_title_visible = tab_title_visible
        self.icon_path = icon_path
        self.save = MagicMock()
        self.load = MagicMock()
        self.cancel = MagicMock()


def test_insert_tab_visible(registry: Registry, mock_settings: MagicMock):
    """
    Test that the insert_tab() method works correctly when a visible tab is inserted
    """
    # GIVEN: A mocked tab and a Settings Form
    settings_form = SettingsForm(None)
    general_tab = MagicMock()
    general_tab.tab_title = 'mock'
    general_tab.tab_title_visible = 'Mock'
    general_tab.icon_path = ':/icon/openlp-logo.svg'

    # WHEN: We insert the general tab
    with patch.object(settings_form.stacked_layout, 'addWidget') as mocked_add_widget, \
            patch.object(settings_form.setting_list_widget, 'addItem') as mocked_add_item:
        settings_form.insert_tab(general_tab, is_visible=True)

        # THEN: The general tab should have been inserted into the stacked layout and an item inserted into the list
        mocked_add_widget.assert_called_with(general_tab)
        assert 1 == mocked_add_item.call_count, 'addItem should have been called'


def test_insert_tab_not_visible(registry: Registry, mock_settings: MagicMock):
    """
    Test that the insert_tab() method works correctly when a tab that should not be visible is inserted
    """
    # GIVEN: A general tab and a Settings Form
    settings_form = SettingsForm(None)
    general_tab = MagicMock()
    general_tab.tab_title = 'mock'

    # WHEN: We insert the general tab
    with patch.object(settings_form.stacked_layout, 'addWidget') as mocked_add_widget, \
            patch.object(settings_form.setting_list_widget, 'addItem') as mocked_add_item:
        settings_form.insert_tab(general_tab, is_visible=False)

        # THEN: The general tab should have been inserted, but no list item should have been inserted into the list
        mocked_add_widget.assert_called_with(general_tab)
        assert 0 == mocked_add_item.call_count, 'addItem should not have been called'


def test_accept_with_inactive_plugins(registry: Registry, mock_settings: MagicMock):
    """
    Test that the accept() method works correctly when some of the plugins are inactive
    """
    # GIVEN: A visible general tab and an invisible theme tab in a Settings Form

    settings_form = SettingsForm(None)
    general_tab = MockTab(None, 'mock-general', 'Mock General', ':/icon/openlp-logo.svg')
    settings_form.insert_tab(general_tab, is_visible=True)
    themes_tab = MockTab(None, 'mock-themes', 'Mock Themes', ':/icon/openlp-logo.svg')
    settings_form.insert_tab(themes_tab, is_visible=False)

    # WHEN: The accept() method is called
    settings_form.accept()

    # THEN: The general tab's save() method should have been called, but not the themes tab
    general_tab.save.assert_called_with()
    assert 0 == themes_tab.save.call_count, 'The Themes tab\'s save() should not have been called'


def test_list_item_changed_invalid_item(registry: Registry, mock_settings: MagicMock):
    """
    Test that the list_item_changed() slot handles a non-existent item
    """
    # GIVEN: A mocked tab inserted into a Settings Form
    settings_form = SettingsForm(None)
    general_tab = MockTab(None, 'mock', 'Mock', ':/icon/openlp-logo.svg')
    settings_form.insert_tab(general_tab, is_visible=True)

    with patch.object(settings_form.stacked_layout, 'count') as mocked_count:
        # WHEN: The list_item_changed() slot is called with an invalid item index
        settings_form.list_item_changed(100)

        # THEN: The rest of the method should not have been called
        assert 0 == mocked_count.call_count, 'The count method of the stacked layout should not be called'


def test_reject_with_inactive_items(registry: Registry, mock_settings: MagicMock):
    """
    Test that the reject() method works correctly when some of the plugins are inactive
    """
    # GIVEN: A visible general tab and an invisible theme tab in a Settings Form
    settings_form = SettingsForm(None)
    general_tab = MockTab(None, 'mock-general', 'Mock General', ':/icon/openlp-logo.svg')
    settings_form.insert_tab(general_tab, is_visible=True)
    themes_tab = MockTab(None, 'mock-themes', 'Mock Themes', ':/icon/openlp-logo.svg')
    settings_form.insert_tab(themes_tab, is_visible=False)

    # WHEN: The reject() method is called
    settings_form.reject()

    # THEN: The general tab's cancel() method should have been called, but not the themes tab
    general_tab.cancel.assert_called_with()
    assert 0 == themes_tab.cancel.call_count, 'The Themes tab\'s cancel() should not have been called'


def test_register_post_process(registry: Registry, mock_settings: MagicMock):
    """
    Test that the register_post_process() method works correctly
    """
    # GIVEN: A settings form instance
    settings_form = SettingsForm(None)
    fake_function = MagicMock()

    # WHEN: register_post_process() is called
    settings_form.register_post_process(fake_function)

    # THEN: The fake function should be in the settings form's list
    assert fake_function in settings_form.processes


def test_help(mock_settings: MagicMock):
    """
    Test the help button
    """
    # GIVEN: An initialised Settings form and a patched help function
    settings_form = SettingsForm(None)

    # WHEN: The Help button is clicked
    with patch.object(settings_form, 'provide_help') as mocked_help:
        QtTest.QTest.mouseClick(settings_form.button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Help),
                                QtCore.Qt.MouseButton.LeftButton)

    # THEN: The Help function should be called
    mocked_help.assert_called_once()
