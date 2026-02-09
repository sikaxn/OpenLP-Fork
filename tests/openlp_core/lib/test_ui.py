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
Package to test the openlp.core.lib.ui package.
"""
from unittest.mock import MagicMock, call, patch

from PySide6 import QtCore, QtGui, QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.lib.ui import MultipleViewModeList, add_list_view_mode_items_to_toolbar, add_welcome_page, \
    create_action, create_button, create_button_box, create_horizontal_adjusting_combo_box, \
    create_valign_selection_widgets, create_widget_action, critical_error_message_box, find_and_set_in_combo_box, \
    set_case_insensitive_completer, set_list_view_mode_toolbar_state
from openlp.core.widgets.toolbar import OpenLPToolbar


def test_add_welcome_page():
    """
    Test appending a welcome page to a wizard
    """
    # GIVEN: A wizard
    wizard = QtWidgets.QWizard()

    # WHEN: A welcome page has been added to the wizard
    add_welcome_page(wizard, ':/wizards/wizard_firsttime.bmp')

    # THEN: The wizard should have one page with a pixmap.
    assert 1 == len(wizard.pageIds()), 'The wizard should have one page.'
    assert isinstance(wizard.page(0).pixmap(QtWidgets.QWizard.WizardPixmap.WatermarkPixmap), QtGui.QPixmap)


def test_create_button_box():
    """
    Test creating a button box for a dialog
    """
    # GIVEN: A dialog
    dialog = QtWidgets.QDialog()

    # WHEN: We create the button box with five buttons
    btnbox = create_button_box(dialog, 'my_btns', ['ok', 'save', 'cancel', 'close', 'defaults'])

    # THEN: We should get a QDialogButtonBox with five buttons
    assert isinstance(btnbox, QtWidgets.QDialogButtonBox)
    assert 5 == len(btnbox.buttons())

    # WHEN: We create the button box with a custom button
    btnbox = create_button_box(dialog, 'my_btns', None, [QtWidgets.QPushButton('Custom')])
    # THEN: We should get a QDialogButtonBox with one button
    assert isinstance(btnbox, QtWidgets.QDialogButtonBox)
    assert 1 == len(btnbox.buttons())

    # WHEN: We create the button box with a custom button and a custom role
    btnbox = create_button_box(dialog, 'my_btns', None,
                               [(QtWidgets.QPushButton('Help'), QtWidgets.QDialogButtonBox.ButtonRole.HelpRole)])
    # THEN: We should get a QDialogButtonBox with one button with a certain role
    assert isinstance(btnbox, QtWidgets.QDialogButtonBox)
    assert 1 == len(btnbox.buttons())
    assert QtWidgets.QDialogButtonBox.ButtonRole.HelpRole, btnbox.buttonRole(btnbox.buttons()[0])


@patch('openlp.core.lib.ui.Registry')
def test_critical_error_message_box(MockRegistry):
    """
    Test the critical_error_message_box() function
    """
    # GIVEN: A mocked Registry
    # WHEN: critical_error_message_box() is called
    critical_error_message_box('Error', 'This is an error')

    # THEN: The error_message() method on the main window should be called
    MockRegistry.return_value.get.return_value.error_message.assert_called_once_with('Error', 'This is an error')


@patch('openlp.core.lib.ui.Registry')
@patch('openlp.core.lib.ui.QtWidgets.QMessageBox.critical')
def test_critical_error_message_box_without_mainwindow(mocked_critical, MockRegistry):
    """
    Test the critical_error_message_box() function
    """
    # GIVEN: A mocked Registry with no MainWindow
    MockRegistry.return_value.get.return_value = None

    # WHEN: critical_error_message_box() is called
    critical_error_message_box('Error', 'This is an error')

    # THEN: The error_message() method on the main window should be called
    mocked_critical.assert_called_once_with(None, 'Error', 'This is an error')


@patch('openlp.core.lib.ui.QtWidgets.QMessageBox.critical')
def test_critical_error_question(mocked_critical):
    """
    Test the critical_error_message_box() function
    """
    # GIVEN: A mocked critical() method and some other mocks
    mocked_parent = MagicMock()

    # WHEN: critical_error_message_box() is called
    critical_error_message_box(None, 'This is a question', mocked_parent, True)

    # THEN: The error_message() method on the main window should be called
    mocked_critical.assert_called_once_with(mocked_parent, 'Error', 'This is a question',
                                            QtWidgets.QMessageBox.StandardButton(
                                                QtWidgets.QMessageBox.StandardButton.Yes |
                                                QtWidgets.QMessageBox.StandardButton.No))


def test_create_horizontal_adjusting_combo_box():
    """
    Test creating a horizontal adjusting combo box
    """
    # GIVEN: A dialog
    dialog = QtWidgets.QDialog()

    # WHEN: We create the combobox
    combo = create_horizontal_adjusting_combo_box(dialog, 'combo1')

    # THEN: We should get a ComboBox
    assert isinstance(combo, QtWidgets.QComboBox)
    assert combo.objectName() == 'combo1'
    assert QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon == combo.sizeAdjustPolicy()


@patch('openlp.core.lib.ui.log')
def test_create_button(mocked_log):
    """
    Test creating a button
    """
    # GIVEN: A dialog
    dialog = QtWidgets.QDialog()

    # WHEN: We create a button with some attributes
    btn = create_button(dialog, 'my_btn', text='Hello', tooltip='How are you?', enabled=False, role='test', test=1)

    # THEN: We should get a button with those attributes
    assert isinstance(btn, QtWidgets.QPushButton)
    assert btn.objectName() == 'my_btn'
    assert btn.text() == 'Hello'
    assert btn.toolTip() == 'How are you?'
    assert btn.isEnabled() is False
    assert mocked_log.warning.call_args_list == [call('The role "test" is not defined in create_push_button().'),
                                                 call('Parameter test was not consumed in create_button().')]


def test_create_tool_button():
    """
    Test creating a toolbutton
    """
    # GIVEN: A dialog
    dialog = QtWidgets.QDialog()

    # WHEN: We create a toolbutton
    btn = create_button(dialog, 'my_btn', btn_class='toolbutton')

    # THEN: We should get a toolbutton
    assert isinstance(btn, QtWidgets.QToolButton)
    assert btn.objectName() == 'my_btn'
    assert btn.isEnabled() is True


@patch('openlp.core.lib.ui.log')
def test_create_action(mocked_log):
    """
    Test creating an action
    """
    # GIVEN: A dialog
    dialog = QtWidgets.QDialog()

    # WHEN: We create an action with some properties
    action = create_action(dialog, 'my_action', text='my text', icon=':/wizards/wizard_firsttime.bmp',
                           tooltip='my tooltip', statustip='my statustip', test=1)

    # THEN: These properties should be set
    assert isinstance(action, QtGui.QAction)
    assert action.objectName() == 'my_action'
    assert action.text() == 'my text'
    assert isinstance(action.icon(), QtGui.QIcon)
    assert action.toolTip() == 'my tooltip'
    assert action.statusTip() == 'my statustip'
    mocked_log.warning.assert_called_once_with('Parameter test was not consumed in create_action().')


def test_create_action_on_mac_osx():
    """
    Test creating an action on OS X calls the correct method
    """
    # GIVEN: A dialog and a mocked out is_macosx() method to always return True
    with patch('openlp.core.lib.ui.is_macosx') as mocked_is_macosx, \
            patch('openlp.core.lib.ui.QtGui.QAction') as MockedQAction:
        mocked_is_macosx.return_value = True
        mocked_action = MagicMock()
        MockedQAction.return_value = mocked_action
        dialog = QtWidgets.QDialog()

        # WHEN: An action is created
        create_action(dialog, 'my_action')

        # THEN: setIconVisibleInMenu should be called
        mocked_action.setIconVisibleInMenu.assert_called_with(False)


def test_create_action_not_on_mac_osx():
    """
    Test creating an action on something other than OS X doesn't call the method
    """
    # GIVEN: A dialog and a mocked out is_macosx() method to always return True
    with patch('openlp.core.lib.ui.is_macosx') as mocked_is_macosx, \
            patch('openlp.core.lib.ui.QtGui.QAction') as MockedQAction:
        mocked_is_macosx.return_value = False
        mocked_action = MagicMock()
        MockedQAction.return_value = mocked_action
        dialog = QtWidgets.QDialog()

        # WHEN: An action is created
        create_action(dialog, 'my_action')

        # THEN: setIconVisibleInMenu should not be called
        assert 0 == mocked_action.setIconVisibleInMenu.call_count, \
            'setIconVisibleInMenu should not have been called'


def test_create_checked_disabled_invisible_action():
    """
    Test that an invisible, disabled, checked action is created correctly
    """
    # GIVEN: A dialog
    dialog = QtWidgets.QDialog()

    # WHEN: We create an action with some properties
    action = create_action(dialog, 'my_action', checked=True, enabled=False, visible=False)

    # THEN: These properties should be set
    assert action.isChecked() is True, 'The action should be checked'
    assert action.isEnabled() is False, 'The action should be disabled'
    assert action.isVisible() is False, 'The action should be invisble'


def test_create_action_separator():
    """
    Test creating an action as separator
    """
    # GIVEN: A dialog
    dialog = QtWidgets.QDialog()

    # WHEN: We create an action as a separator
    action = create_action(dialog, 'my_action', separator=True)

    # THEN: The action should be a separator
    assert action.isSeparator() is True, 'The action should be a separator'


def test_create_valign_selection_widgets():
    """
    Test creating a combo box for valign selection
    """
    # GIVEN: A dialog
    dialog = QtWidgets.QDialog()

    # WHEN: We create the widgets
    label, combo = create_valign_selection_widgets(dialog)

    # THEN: We should get a label and a combobox.
    assert translate('OpenLP.Ui', '&Vertical Align:') == label.text()
    assert isinstance(combo, QtWidgets.QComboBox)
    assert combo == label.buddy()
    for text in [UiStrings().Top, UiStrings().Middle, UiStrings().Bottom]:
        assert combo.findText(text) >= 0


def test_find_and_set_in_combo_box():
    """
    Test finding a string in a combo box and setting it as the selected item if present
    """
    # GIVEN: A ComboBox
    combo = QtWidgets.QComboBox()
    combo.addItems(['One', 'Two', 'Three'])
    combo.setCurrentIndex(1)

    # WHEN: We call the method with a non-existing value and set_missing=False
    find_and_set_in_combo_box(combo, 'Four', set_missing=False)

    # THEN: The index should not have changed
    assert 1 == combo.currentIndex()

    # WHEN: We call the method with a non-existing value
    find_and_set_in_combo_box(combo, 'Four')

    # THEN: The index should have been reset
    assert 0 == combo.currentIndex()

    # WHEN: We call the method with the default behavior
    find_and_set_in_combo_box(combo, 'Three')

    # THEN: The index should have changed
    assert 2 == combo.currentIndex()


def test_create_widget_action():
    """
    Test creating an action for a widget
    """
    # GIVEN: A button
    button = QtWidgets.QPushButton()

    # WHEN: We call the function
    action = create_widget_action(button, 'some action')

    # THEN: The action should be returned
    assert isinstance(action, QtGui.QAction)
    assert action.objectName() == 'some action'


def test_set_case_insensitive_completer():
    """
    Test setting a case insensitive completer on a widget
    """
    # GIVEN: A QComboBox and a list of completion items
    line_edit = QtWidgets.QLineEdit()
    suggestions = ['one', 'Two', 'THRee', 'FOUR']

    # WHEN: We call the function
    set_case_insensitive_completer(suggestions, line_edit)

    # THEN: The Combobox should have a completer which is case insensitive
    completer = line_edit.completer()
    assert isinstance(completer, QtWidgets.QCompleter)
    assert completer.caseSensitivity() == QtCore.Qt.CaseInsensitive


def test_multiple_view_mode_list(settings):
    """
    Tests if MultipleViewModeList works and have the default ViewMode
    """
    # GIVEN: MultipleViewModeList

    # WHEN: It's built
    list = MultipleViewModeList(None)

    # THEN: It's should be build sucessfully, with default ListMode
    assert list.viewMode() == QtWidgets.QListWidget.ViewMode.ListMode


def test_multiple_view_mode_list_set_icon_size_by_view_mode_icon_mode(settings):
    """
    Tests if MultipleViewModeList's set_icon_size_by_view_mode works with a IconMode default value
    """
    # GIVEN: a MultipleViewModeList instance and a custom icon size
    list = MultipleViewModeList(None)
    icon_size = QtCore.QSize(93, 37)

    # WHEN: set_icon_size_by_view_mode is called with IconMode and mode is changed
    list.set_icon_size_by_view_mode(QtWidgets.QListWidget.ViewMode.IconMode, icon_size)
    list.setViewMode(QtWidgets.QListWidget.ViewMode.IconMode)

    # THEN: New icon size should be set successfully
    assert list.iconSize() == icon_size


def test_multiple_view_mode_list_set_icon_size_by_view_mode_list_mode(settings):
    """
    Tests if MultipleViewModeList's set_icon_size_by_view_mode works with a ListMode default value
    """
    # GIVEN: a MultipleViewModeList instance and a custom icon size
    list = MultipleViewModeList(None, QtWidgets.QListWidget.ViewMode.IconMode)
    icon_size = QtCore.QSize(93, 37)

    # WHEN: set_icon_size_by_view_mode is called with ListMode and mode is changed
    list.set_icon_size_by_view_mode(QtWidgets.QListWidget.ViewMode.ListMode, icon_size)
    list.setViewMode(QtWidgets.QListWidget.ViewMode.ListMode)

    # THEN: New icon size should be set successfully
    assert list.iconSize() == icon_size


def test_multiple_view_mode_list_set_icon_size_by_view_mode_changes_current_size(settings):
    """
    Tests if MultipleViewModeList's set_icon_size_by_view_mode changes the current value if provided mode is the same
    as current List's ViewMode.
    """
    # GIVEN: a MultipleViewModeList instance and a custom icon size
    list = MultipleViewModeList(None, QtWidgets.QListWidget.ViewMode.IconMode)
    icon_size = QtCore.QSize(93, 37)

    # WHEN: set_icon_size_by_view_mode is called with IconMode and mode is changed
    list.set_icon_size_by_view_mode(QtWidgets.QListWidget.ViewMode.IconMode, icon_size)

    # THEN: New icon size should be set successfully
    assert list.iconSize() == icon_size


def test_multiple_view_mode_list_set_view_mode_preserves_last_icon_size(settings):
    """
    Tests if MultipleViewModeList's preserves the last iconSize when no equivalent
    default icon size is present
    """
    # GIVEN: a MultipleViewModeList instance and a custom icon size
    list = MultipleViewModeList(None, QtWidgets.QListWidget.ViewMode.IconMode)
    icon_size = QtCore.QSize(93, 37)
    last_icon_size = list.iconSize()
    list.set_icon_size_by_view_mode(QtWidgets.QListWidget.ViewMode.ListMode, icon_size)

    # WHEN: viewMode() is changed and reverted
    list.setViewMode(QtWidgets.QListWidget.ViewMode.ListMode)
    list.setViewMode(QtWidgets.QListWidget.ViewMode.IconMode)

    # THEN: Old icon size should be restored
    assert list.iconSize() == last_icon_size


def test_add_list_view_mode_items_to_toolbar_creates_items(settings):
    """
    Tests if add_list_view_mode_items_to_toolbar creates the list view items.
    """
    # GIVEN: an OpenLPToolbar
    toolbar = OpenLPToolbar(None)

    # WHEN: add_list_view_mode_items_to_toolbar is called
    add_list_view_mode_items_to_toolbar(toolbar, MagicMock())

    # THEN: Assert correct icons are created
    assert isinstance(toolbar.actions_map['listView'], QtGui.QAction) is True
    assert isinstance(toolbar.actions_map['gridView'], QtGui.QAction) is True


def test_add_list_view_mode_items_to_toolbar_click_calls_handlers(settings):
    """
    Tests if add_list_view_mode_items_to_toolbar created items calls the handlers
    """
    # GIVEN: an OpenLPToolbar with ListView items
    toolbar = OpenLPToolbar(None)
    handler = MagicMock()
    add_list_view_mode_items_to_toolbar(toolbar, handler)

    # WHEN: handler items is called
    toolbar.actions_map['listView'].trigger()
    toolbar.actions_map['gridView'].trigger()

    # THEN: Assert correct handlers were called
    handler.on_set_view_mode_list.assert_called_once()
    handler.on_set_view_mode_grid.assert_called_once()


def test_set_list_view_mode_toolbar_state_view_mode_list_mode(settings):
    """
    Tests if set_list_view_mode_toolbar_state changes the toolbar items state to List Mode correctly
    """
    # GIVEN: an OpenLPToolbar with checkable List View items
    toolbar = OpenLPToolbar(None)
    add_list_view_mode_items_to_toolbar(toolbar, MagicMock())

    # WHEN: set_list_view_mode_toolbar_state is called with ListMode
    set_list_view_mode_toolbar_state(toolbar, QtWidgets.QListWidget.ViewMode.ListMode)

    # THEN: Assert correct icons are checked or not
    assert toolbar.actions_map['listView'].isChecked() is True
    assert toolbar.actions_map['gridView'].isChecked() is False


def test_set_list_view_mode_toolbar_state_view_mode_icon_mode(settings):
    """
    Tests if set_list_view_mode_toolbar_state changes the toolbar items state to Grid Mode correctly
    """
    # GIVEN: an OpenLPToolbar with checkable List View items
    toolbar = OpenLPToolbar(None)
    add_list_view_mode_items_to_toolbar(toolbar, MagicMock())

    # WHEN: set_list_view_mode_toolbar_state is called with ListMode
    set_list_view_mode_toolbar_state(toolbar, QtWidgets.QListWidget.ViewMode.IconMode)

    # THEN: Assert correct icons are checked or not
    assert toolbar.actions_map['listView'].isChecked() is False
    assert toolbar.actions_map['gridView'].isChecked() is True
