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
Package to test the openlp.core.ui.shortcutlistdialog package.
"""
from unittest.mock import MagicMock

from PySide6 import QtCore

from openlp.core.ui.shortcutlistdialog import CaptureShortcutButton, ShortcutTreeWidget


def test_key_press_event(mock_settings):
    """
    Test the keyPressEvent method
    """
    # GIVEN: A checked button and a mocked event
    button = CaptureShortcutButton()
    button.setChecked(True)
    mocked_event = MagicMock()
    mocked_event.key.return_value = QtCore.Qt.Key.Key_Space

    # WHEN: keyPressEvent is called with an event that should be ignored
    button.keyPressEvent(mocked_event)

    # THEN: The ignore() method on the event should have been called
    mocked_event.ignore.assert_called_once_with()


def test_keyboard_search(mock_settings):
    """
    Test the keyboardSearch method of the ShortcutTreeWidget
    """
    # GIVEN: A ShortcutTreeWidget
    widget = ShortcutTreeWidget()

    # WHEN: keyboardSearch() is called
    widget.keyboardSearch('')

    # THEN: Nothing happens
    assert True
