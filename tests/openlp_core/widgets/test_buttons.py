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
This module contains tests for the openlp.core.widgets.buttons module
"""
from unittest.mock import MagicMock, patch

from openlp.core.widgets.buttons import ColorButton


def test_constructor(mock_settings: MagicMock):
    """
    Test that constructing a ColorButton object works correctly
    """
    # GIVEN: The ColorButton class
    # WHEN: The ColorButton object is instantiated
    widget = ColorButton()

    # THEN: The widget __init__ method should have the correct properties and methods called
    assert widget.parent is None, 'The parent should be the same as the one that the class was instianted with'


def test_setup(mock_settings: MagicMock):
    """
    Test the _setup() method correctly instantiates the object
    """
    # GIVEN: A ColorButton object
    with patch.object(ColorButton, '_setup'):
        widget = ColorButton()

    # WHEN: _setup() is called
    with patch.object(widget, 'change_color') as mocked_change_color, \
            patch.object(widget, 'setToolTip') as mocked_set_tooltip, \
            patch.object(widget, 'clicked') as mocked_clicked:
        widget._setup()

        # THEN: The correct methods should have been called
        mocked_change_color.assert_called_once_with('#ffffff')
        mocked_set_tooltip.assert_called_once_with('Click to select a color.')
        mocked_clicked.connect.assert_called_once_with(widget.on_clicked)


def test_change_color():
    """
    Test that change_color sets the new color and the stylesheet
    """
    # GIVEN: An instance of the ColorButton object, and a mocked out setStyleSheet
    widget = ColorButton()

    # WHEN: Changing the color
    with patch.object(widget, 'setStyleSheet') as mocked_set_style_sheet:
        widget.change_color('#000000')

    # THEN: The _color attribute should be set to #000000 and setStyleSheet should have been called twice
    assert widget._color == '#000000', '_color should have been set to #000000'
    mocked_set_style_sheet.assert_called_once_with('background-color: #000000')


def test_color():
    """
    Test that the color property method returns the set color
    """
    # GIVEN: An instance of ColorButton, with a set _color attribute
    widget = ColorButton()
    widget._color = '#000000'

    # WHEN: Accesing the color property
    value = widget.color

    # THEN: The value set in _color should be returned
    assert value == '#000000', 'The value returned should be equal to the one we set'


def test_color_setter():
    """
    Test that the color property setter method sets the color
    """
    # GIVEN: An instance of ColorButton, with a mocked __init__
    widget = ColorButton()

    # WHEN: Setting the color property
    with patch.object(widget, 'change_color') as mocked_change_color:
        widget.color = '#000000'

    # THEN: Then change_color should have been called with the value we set
    mocked_change_color.assert_called_with('#000000')


@patch('openlp.core.widgets.buttons.QtWidgets.QColorDialog.getColor')
def test_on_clicked_invalid_color(mocked_get_color: MagicMock):
    """
    Test the on_click method when an invalid color has been supplied
    """
    # GIVEN: An instance of ColorButton, and a set _color attribute
    mocked_get_color.return_value = MagicMock(**{'isValid.return_value': False})
    widget = ColorButton()
    widget._color = '#000000'

    # WHEN: The on_clicked method is called, and the color is invalid
    with patch.object(widget, 'colorChanged') as mocked_color_changed, \
            patch.object(widget, 'change_color') as mocked_change_color:
        widget.on_clicked()

    # THEN: change_color should not have been called and the colorChanged signal should not have been emitted
    assert mocked_change_color.called is False, \
        'change_color should not have been called with an invalid color'
    assert mocked_color_changed.emit.called is False, \
        'colorChange signal should not have been emitted with an invalid color'


@patch('openlp.core.widgets.buttons.QtWidgets.QColorDialog.getColor')
def test_on_clicked_same_color(mocked_get_color: MagicMock):
    """
    Test the on_click method when a new color has not been chosen
    """
    # GIVEN: An instance of ColorButton, and a set _color attribute
    mocked_get_color.return_value = MagicMock(**{'isValid.return_value': True, 'name.return_value': '#000000'})
    widget = ColorButton()
    widget._color = '#000000'

    # WHEN: The on_clicked method is called, and the color is valid, but the same as the existing color
    with patch.object(widget, 'colorChanged') as mocked_color_changed, \
            patch.object(widget, 'change_color') as mocked_change_color:
        widget.on_clicked()

    # THEN: change_color should not have been called and the colorChanged signal should not have been emitted
    assert mocked_change_color.called is False, \
        'change_color should not have been called when the color has not changed'
    assert mocked_color_changed.emit.called is False, \
        'colorChange signal should not have been emitted when the color has not changed'


@patch('openlp.core.widgets.buttons.QtWidgets.QColorDialog.getColor')
def test_on_clicked_new_color(mocked_get_color: MagicMock):
    """
    Test the on_click method when a new color has been chosen and is valid
    """
    # GIVEN: An instance of ColorButton, and a set _color attribute
    mocked_get_color.return_value = MagicMock(**{'isValid.return_value': True, 'name.return_value': '#ffffff'})
    widget = ColorButton()
    widget._color = '#000000'

    # WHEN: The on_clicked method is called, and the color is valid, and different to the existing color
    with patch.object(widget, 'colorChanged') as mocked_color_changed, \
            patch.object(widget, 'change_color') as mocked_change_color:
        widget.on_clicked()

    # THEN: change_color should have been called and the colorChanged signal should have been emitted
    mocked_change_color.assert_called_once_with('#ffffff')
    mocked_color_changed.emit.assert_called_once_with('#ffffff')
