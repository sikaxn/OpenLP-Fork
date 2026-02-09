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
Package to test the openlp.core.common.actions package.
"""
import pytest
from unittest.mock import MagicMock

from PySide6 import QtCore, QtGui

from openlp.core.common.actions import ActionList, CategoryActionList
from openlp.core.common.registry import Registry


MOCK_ACTION1 = MagicMock(**{'text.return_value': 'first'})
MOCK_ACTION2 = MagicMock(**{'text.return_value': 'second'})


@pytest.fixture
def action_list(settings):
    act_list = ActionList.get_instance()
    yield act_list


def test_action_list_contains():
    """
    Test the __contains__() method
    """
    # GIVEN: The list and 2 actions
    category_list = CategoryActionList()

    # WHEN: Add an action
    category_list.append(MOCK_ACTION1)

    # THEN: The actions should (not) be in the list.
    assert MOCK_ACTION1 in category_list
    assert MOCK_ACTION2 not in category_list


def test_action_list_empty_len():
    """
    Test the __len__ method when the list is empty
    """
    # GIVEN: The list without any actions
    category_list = CategoryActionList()

    # WHEN: Do nothing.
    list_len = len(category_list)

    # THEN: Check the length.
    assert list_len == 0, 'The length should be 0.'


def test_action_list_len():
    """
    Test the __len__ method when the list is not empty
    """
    # GIVEN: The list with 2 items in it
    category_list = CategoryActionList()
    category_list.append(MOCK_ACTION1)
    category_list.append(MOCK_ACTION2)

    # WHEN: The length of the list is calculated
    list_len = len(category_list)

    # THEN: It should have 2 items
    assert list_len == 2, 'The list should have 2 items in it'


def test_action_list_append():
    """
    Test the append() method
    """
    # GIVEN: The list.
    category_list = CategoryActionList()

    # WHEN: Append an action.
    category_list.append(MOCK_ACTION1)
    category_list.append(MOCK_ACTION2)

    # THEN: Check if the actions are in the list and check if they have the correct weights.
    assert MOCK_ACTION1 in category_list
    assert MOCK_ACTION2 in category_list
    assert category_list.actions[0] == (0, MOCK_ACTION1)
    assert category_list.actions[1] == (1, MOCK_ACTION2)


def test_action_list_add():
    """
    Test the add() method
    """
    # GIVEN: The list and weights.
    action1_weight = 42
    action2_weight = 41
    category_list = CategoryActionList()

    # WHEN: Add actions and their weights.
    category_list.add(MOCK_ACTION1, action1_weight)
    category_list.add(MOCK_ACTION2, action2_weight)

    # THEN: Check if they were added and have the specified weights.
    assert MOCK_ACTION1 in category_list
    assert MOCK_ACTION2 in category_list
    assert category_list.actions[0] == (41, MOCK_ACTION2)
    assert category_list.actions[1] == (42, MOCK_ACTION1)


def test_action_list_iterator():
    """
    Test the __iter__ and __next__ methods
    """
    # GIVEN: The list including two actions
    category_list = CategoryActionList()
    category_list.append(MOCK_ACTION1)
    category_list.append(MOCK_ACTION2)

    # WHEN: Iterating over the list
    local_list = [a for a in category_list]

    # THEN: Make sure they are returned in correct order
    assert len(category_list) == 2
    assert local_list[0] is MOCK_ACTION1
    assert local_list[1] is MOCK_ACTION2


def test_action_list_remove():
    """
    Test the remove() method
    """
    # GIVEN: The list
    category_list = CategoryActionList()
    category_list.append(MOCK_ACTION1)

    # WHEN: Delete an item from the list.
    category_list.remove(MOCK_ACTION1)

    # THEN: Now the element should not be in the list anymore.
    assert MOCK_ACTION1 not in category_list


def test_add_action_same_parent(action_list):
    """
    ActionList test - Tests the add_action method. The actions have the same parent, the same shortcuts and both
    have the QtCore.Qt.ShortcutContext.WindowShortcut shortcut context set.
    """
    # GIVEN: Two actions with the same shortcuts.
    parent = QtCore.QObject()
    action1 = QtGui.QAction(parent)
    action1.setObjectName('action1')
    action_with_same_shortcuts1 = QtGui.QAction(parent)
    action_with_same_shortcuts1.setObjectName('action_with_same_shortcuts1')
    # Add default shortcuts to Settings class.
    default_shortcuts = {
        'shortcuts/action1': [QtGui.QKeySequence(QtCore.Qt.Key.Key_A), QtGui.QKeySequence(QtCore.Qt.Key.Key_B)],
        'shortcuts/action_with_same_shortcuts1': [QtGui.QKeySequence(QtCore.Qt.Key.Key_B),
                                                  QtGui.QKeySequence(QtCore.Qt.Key.Key_A)]
    }
    Registry().get('settings').extend_default_settings(default_shortcuts)

    # WHEN: Add the two actions to the action list.
    action_list.add_action(action1, 'example_category')
    action_list.add_action(action_with_same_shortcuts1, 'example_category')
    # Remove the actions again.
    action_list.remove_action(action1, 'example_category')
    action_list.remove_action(action_with_same_shortcuts1, 'example_category')

    # THEN: As both actions have the same shortcuts, they should be removed from one action.
    assert len(action1.shortcuts()) == 2, 'The action should have two shortcut assigned.'
    assert len(action_with_same_shortcuts1.shortcuts()) == 0, 'The action should not have a shortcut assigned.'


def test_add_action_different_parent(action_list):
    """
    ActionList test - Tests the add_action method. The actions have the different parent, the same shortcuts and
    both have the QtCore.Qt.ShortcutContext.WindowShortcut shortcut context set.
    """
    # GIVEN: Two actions with the same shortcuts.
    parent = QtCore.QObject()
    action2 = QtGui.QAction(parent)
    action2.setObjectName('action2')
    second_parent = QtCore.QObject()
    action_with_same_shortcuts2 = QtGui.QAction(second_parent)
    action_with_same_shortcuts2.setObjectName('action_with_same_shortcuts2')
    # Add default shortcuts to Settings class.
    default_shortcuts = {
        'shortcuts/action2': [QtGui.QKeySequence(QtCore.Qt.Key.Key_C), QtGui.QKeySequence(QtCore.Qt.Key.Key_D)],
        'shortcuts/action_with_same_shortcuts2': [QtGui.QKeySequence(QtCore.Qt.Key.Key_D),
                                                  QtGui.QKeySequence(QtCore.Qt.Key.Key_C)]
    }
    Registry().get('settings').extend_default_settings(default_shortcuts)

    # WHEN: Add the two actions to the action list.
    action_list.add_action(action2, 'example_category')
    action_list.add_action(action_with_same_shortcuts2, 'example_category')
    # Remove the actions again.
    action_list.remove_action(action2, 'example_category')
    action_list.remove_action(action_with_same_shortcuts2, 'example_category')

    # THEN: As both actions have the same shortcuts, they should be removed from one action.
    assert len(action2.shortcuts()) == 2, 'The action should have two shortcut assigned.'
    assert len(action_with_same_shortcuts2.shortcuts()) == 0, 'The action should not have a shortcut assigned.'


def test_add_action_different_context(action_list):
    """
    ActionList test - Tests the add_action method. The actions have the different parent, the same shortcuts and
    both have the QtCore.Qt.ShortcutContext.WidgetShortcut shortcut context set.
    """
    # GIVEN: Two actions with the same shortcuts.
    parent = QtCore.QObject()
    action3 = QtGui.QAction(parent)
    action3.setObjectName('action3')
    action3.setShortcutContext(QtCore.Qt.ShortcutContext.WidgetShortcut)
    second_parent = QtCore.QObject()
    action_with_same_shortcuts3 = QtGui.QAction(second_parent)
    action_with_same_shortcuts3.setObjectName('action_with_same_shortcuts3')
    action_with_same_shortcuts3.setShortcutContext(QtCore.Qt.ShortcutContext.WidgetShortcut)
    # Add default shortcuts to Settings class.
    default_shortcuts = {
        'shortcuts/action3': [QtGui.QKeySequence(QtCore.Qt.Key.Key_E), QtGui.QKeySequence(QtCore.Qt.Key.Key_F)],
        'shortcuts/action_with_same_shortcuts3': [QtGui.QKeySequence(QtCore.Qt.Key.Key_E),
                                                  QtGui.QKeySequence(QtCore.Qt.Key.Key_F)]
    }
    Registry().get('settings').extend_default_settings(default_shortcuts)

    # WHEN: Add the two actions to the action list.
    action_list.add_action(action3, 'example_category2')
    action_list.add_action(action_with_same_shortcuts3, 'example_category2')
    # Remove the actions again.
    action_list.remove_action(action3, 'example_category2')
    action_list.remove_action(action_with_same_shortcuts3, 'example_category2')

    # THEN: Both action should keep their shortcuts.
    assert len(action3.shortcuts()) == 2, 'The action should have two shortcut assigned.'
    assert len(action_with_same_shortcuts3.shortcuts()) == 2, 'The action should have two shortcuts assigned.'
