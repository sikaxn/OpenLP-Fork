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
Package to test the openlp.core.widgets.fontselect package.
"""
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.pages.fontselect import FontSelectPage


def test_init_(settings):
    """
    Test the initialisation of FontSelectPage
    """
    # GIVEN: The FontSelectPage class
    # WHEN: Initialising FontSelectPage
    # THEN: We should have an instance of the widget with no errors
    FontSelectPage()


def test_font_name_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "font_name_changed" signal
    instance = FontSelectPage()
    instance.font_name_changed = MagicMock()

    # WHEN: The font name changes
    instance._on_font_name_changed('Sans serif')

    # THEN: The signal should be emitted with the correct value
    instance.font_name_changed.emit.assert_called_once_with('Sans serif')


def test_font_name_changed_int(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "font_name_changed" signal
    instance = FontSelectPage()
    instance.font_name_changed = MagicMock()

    # WHEN: The font name changes
    instance._on_font_name_changed(5)

    # THEN: The signal should be emitted with the correct value
    assert instance.font_name_changed.emit.call_count == 0


def test_font_color_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "font_color_changed" signal
    instance = FontSelectPage()
    instance.font_color_changed = MagicMock()

    # WHEN: The font color changes
    instance._on_font_color_changed('#fff')

    # THEN: The signal should be emitted with the correct value
    instance.font_color_changed.emit.assert_called_once_with('#fff')


def test_is_bold_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "is_bold_changed" signal
    instance = FontSelectPage()
    instance.is_bold_changed = MagicMock()

    # WHEN: The font name changes
    instance._on_style_bold_toggled(True)

    # THEN: The signal should be emitted with the correct value
    instance.is_bold_changed.emit.assert_called_once_with(True)


def test_is_italic_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "style_italic_changed" signal
    instance = FontSelectPage()
    instance.is_italic_changed = MagicMock()

    # WHEN: The font name changes
    instance._on_style_italic_toggled(False)

    # THEN: The signal should be emitted with the correct value
    instance.is_italic_changed.emit.assert_called_once_with(False)


def test_font_size_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "font_size_changed" signal
    instance = FontSelectPage()
    instance.font_size_changed = MagicMock()

    # WHEN: The font size changes
    instance._on_font_size_changed(14)

    # THEN: The signal should be emitted with the correct value
    instance.font_size_changed.emit.assert_called_once_with(14)


def test_wrap_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "font_size_changed" signal
    instance = FontSelectPage()
    instance.wrap_changed = MagicMock()
    instance.wrap_check_box.isChecked = MagicMock(return_value=True)

    # WHEN: The text-wrap changes
    instance._on_wrap_changed(2)

    # THEN: The signal should be emitted with the correct value
    instance.wrap_changed.emit.assert_called_once_with(True)


def test_line_spacing_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "line_spacing_changed" signal
    instance = FontSelectPage()
    instance.line_spacing_changed = MagicMock()

    # WHEN: The font name changes
    instance._on_line_spacing_changed(1)

    # THEN: The signal should be emitted with the correct value
    instance.line_spacing_changed.emit.assert_called_once_with(1)


def test_is_outline_enabled_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "outline_enabled_changed" signal
    instance = FontSelectPage()
    instance.is_outline_enabled_changed = MagicMock()

    # WHEN: The font name changes
    instance._on_outline_toggled(True)

    # THEN: The signal should be emitted with the correct value
    instance.is_outline_enabled_changed.emit.assert_called_once_with(True)


def test_outline_color_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "outline_color_changed" signal
    instance = FontSelectPage()
    instance.outline_color_changed = MagicMock()

    # WHEN: The font name changes
    instance._on_outline_color_changed('#000')

    # THEN: The signal should be emitted with the correct value
    instance.outline_color_changed.emit.assert_called_once_with('#000')


def test_outline_size_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "outline_size_changed" signal
    instance = FontSelectPage()
    instance.outline_size_changed = MagicMock()

    # WHEN: The font name changes
    instance._on_outline_size_changed(2)

    # THEN: The signal should be emitted with the correct value
    instance.outline_size_changed.emit.assert_called_once_with(2)


def test_is_shadow_enabled_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "is_shadow_enabled_changed" signal
    instance = FontSelectPage()
    instance.is_shadow_enabled_changed = MagicMock()

    # WHEN: The font name changes
    instance._on_shadow_toggled(False)

    # THEN: The signal should be emitted with the correct value
    instance.is_shadow_enabled_changed.emit.assert_called_once_with(False)


def test_shadow_color_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "shadow_color_changed" signal
    instance = FontSelectPage()
    instance.shadow_color_changed = MagicMock()

    # WHEN: The font name changes
    instance._on_shadow_color_changed('#000')

    # THEN: The signal should be emitted with the correct value
    instance.shadow_color_changed.emit.assert_called_once_with('#000')


def test_shadow_size_changed(settings):
    # GIVEN: An instance of FontSelectPage with a mocked out "shadow_size_changed" signal
    instance = FontSelectPage()
    instance.shadow_size_changed = MagicMock()

    # WHEN: The font name changes
    instance._on_shadow_size_changed(5)

    # THEN: The signal should be emitted with the correct value
    instance.shadow_size_changed.emit.assert_called_once_with(5)


def test_enable_features(settings):
    """
    Test that the `enable_features` method correctly enables widgets based on features
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    mock_label = MagicMock()
    mock_control = MagicMock()
    instance.feature_widgets = {'test': [mock_label, mock_control]}

    # WHEN: The "test" feature is enabled
    instance.enable_features('test')

    # THEN: "show()" is called on all the widgets
    mock_label.show.assert_called_once()
    mock_control.show.assert_called_once()


def test_enable_missing_features(settings):
    """
    Test that the `enable_features` method correctly raises an error on a non-existent feature
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    mock_label = MagicMock()
    mock_control = MagicMock()
    instance.feature_widgets = {'test1': [mock_label, mock_control]}

    # WHEN: The "test" feature is enabled
    with pytest.raises(KeyError, match='No such feature'):
        instance.enable_features('test2')


def test_disable_features(settings):
    """
    Test that the `disable_features` method correctly disables widgets based on features
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    mock_label = MagicMock()
    mock_control = MagicMock()
    instance.feature_widgets = {'test': [mock_label, mock_control]}

    # WHEN: The "test" feature is disabled
    instance.disable_features('test')

    # THEN: "show()" is called on all the widgets
    mock_label.hide.assert_called_once()
    mock_control.hide.assert_called_once()


def test_disable_missing_features(settings):
    """
    Test that the `disable_features` method correctly raises an error on a non-existent feature
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    mock_label = MagicMock()
    mock_control = MagicMock()
    instance.feature_widgets = {'test1': [mock_label, mock_control]}

    # WHEN: The "test" feature is disabled
    with pytest.raises(KeyError, match='No such feature'):
        instance.disable_features('test2')


def test_get_font_name_property(settings):
    """
    Test the `font_name` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.font_name_combobox.currentFont = MagicMock(
        return_value=MagicMock(**{'family.return_value': 'Sans serif'}))

    # WHEN: The `font_name` propert is accessed
    result = instance.font_name

    # THEN: The value should be correct
    assert result == 'Sans serif'


def test_set_font_name_property(settings):
    """
    Test setting the `font_name` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.font_name_combobox.setCurrentFont = MagicMock()

    # WHEN: The `font_name` property is set
    with patch('openlp.core.pages.fontselect.QtGui.QFont') as MockFont:
        mocked_font = MagicMock()
        MockFont.return_value = mocked_font
        instance.font_name = 'Serif'

    # THEN: The correct value should be set
    MockFont.assert_called_once_with('Serif')
    instance.font_name_combobox.setCurrentFont.assert_called_once_with(mocked_font)


def test_get_font_color_property(settings):
    """
    Test the `font_color` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.font_color_button.color = '#000'

    # WHEN: The `font_color` propert is accessed
    result = instance.font_color

    # THEN: The value should be correct
    assert result == '#000'


def test_set_font_color_property(settings):
    """
    Test setting the `font_color` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()

    # WHEN: The `font_color` property is set
    instance.font_color = '#fff'

    # THEN: The correct value should be set
    assert instance.font_color_button.color == '#fff'


def test_get_is_bold_property(settings):
    """
    Test the `is_bold` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.style_bold_button.isChecked = MagicMock(return_value=False)

    # WHEN: The `is_bold` propert is accessed
    result = instance.is_bold

    # THEN: The value should be correct
    assert result is False


def test_set_is_bold_property(settings):
    """
    Test setting the `is_bold` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.style_bold_button.setChecked = MagicMock()

    # WHEN: The `is_bold` property is set
    instance.is_bold = True

    # THEN: The correct value should be set
    instance.style_bold_button.setChecked.assert_called_once_with(True)


def test_get_is_italic_property(settings):
    """
    Test the `is_italic` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.style_italic_button.isChecked = MagicMock(return_value=True)

    # WHEN: The `is_italic` propert is accessed
    result = instance.is_italic

    # THEN: The value should be correct
    assert result is True


def test_set_is_italic_property(settings):
    """
    Test setting the `is_italic` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.style_italic_button.setChecked = MagicMock()

    # WHEN: The `is_italic` property is set
    instance.is_italic = False

    # THEN: The correct value should be set
    instance.style_italic_button.setChecked.assert_called_once_with(False)


def test_get_font_size_property(settings):
    """
    Test the `font_size` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.font_size_spinbox.value = MagicMock(return_value=16)

    # WHEN: The `font_size` propert is accessed
    result = instance.font_size

    # THEN: The value should be correct
    assert result == 16


def test_set_font_size_property(settings):
    """
    Test setting the `font_size` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.font_size_spinbox.setValue = MagicMock()

    # WHEN: The `font_size` property is set
    instance.font_size = 18

    # THEN: The correct value should be set
    instance.font_size_spinbox.setValue.assert_called_once_with(18)


def test_get_wrap_property(settings):
    """
    Test the `wrap` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.wrap_check_box.isChecked = MagicMock(return_value=True)

    # WHEN: The `wrap` propert is accessed
    result = instance.wrap

    # THEN: The value should be correct
    assert result is True


def test_set_wrap_property(settings):
    """
    Test setting the `wrap` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.wrap_check_box.setChecked = MagicMock()

    # WHEN: The `wrap` property is set
    instance.wrap = True

    # THEN: The correct value should be set
    instance.wrap_check_box.setChecked.assert_called_once_with(True)


def test_get_line_spacing_property(settings):
    """
    Test the `line_spacing` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.line_spacing_spinbox.value = MagicMock(return_value=1)

    # WHEN: The `line_spacing` propert is accessed
    result = instance.line_spacing

    # THEN: The value should be correct
    assert result == 1


def test_set_line_spacing_property(settings):
    """
    Test setting the `line_spacing` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.line_spacing_spinbox.setValue = MagicMock()

    # WHEN: The `line_spacing` property is set
    instance.line_spacing = 2

    # THEN: The correct value should be set
    instance.line_spacing_spinbox.setValue.assert_called_once_with(2)


def test_get_is_outline_enabled_property(settings):
    """
    Test the `is_outline_enabled` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.outline_groupbox.isChecked = MagicMock(return_value=True)

    # WHEN: The `is_outline_enabled` propert is accessed
    result = instance.is_outline_enabled

    # THEN: The value should be correct
    assert result is True


def test_set_is_outline_enabled_property(settings):
    """
    Test setting the `is_outline_enabled` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.outline_groupbox.setChecked = MagicMock()

    # WHEN: The `is_outline_enabled` property is set
    instance.is_outline_enabled = False

    # THEN: The correct value should be set
    instance.outline_groupbox.setChecked.assert_called_once_with(False)


def test_get_outline_color_property(settings):
    """
    Test the `outline_color` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.outline_color_button.color = '#fff'

    # WHEN: The `outline_color` propert is accessed
    result = instance.outline_color

    # THEN: The value should be correct
    assert result == '#fff'


def test_set_outline_color_property(settings):
    """
    Test setting the `outline_color` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()

    # WHEN: The `outline_color` property is set
    instance.outline_color = '#000'

    # THEN: The correct value should be set
    assert instance.outline_color_button.color == '#000'


def test_get_outline_size_property(settings):
    """
    Test the `outline_size` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.outline_size_spinbox.value = MagicMock(return_value=2)

    # WHEN: The `outline_size` propert is accessed
    result = instance.outline_size

    # THEN: The value should be correct
    assert result == 2


def test_set_outline_size_property(settings):
    """
    Test setting the `outline_size` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.outline_size_spinbox.setValue = MagicMock()

    # WHEN: The `outline_size` property is set
    instance.outline_size = 1

    # THEN: The correct value should be set
    instance.outline_size_spinbox.setValue.assert_called_once_with(1)


def test_get_is_shadow_enabled_property(settings):
    """
    Test the `is_shadow_enabled` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.shadow_groupbox.isChecked = MagicMock(return_value=False)

    # WHEN: The `is_shadow_enabled` propert is accessed
    result = instance.is_shadow_enabled

    # THEN: The value should be correct
    assert result is False


def test_set_is_shadow_enabled_property(settings):
    """
    Test setting the `is_shadow_enabled` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.shadow_groupbox.setChecked = MagicMock()

    # WHEN: The `is_shadow_enabled` property is set
    instance.is_shadow_enabled = True

    # THEN: The correct value should be set
    instance.shadow_groupbox.setChecked.assert_called_once_with(True)


def test_get_shadow_color_property(settings):
    """
    Test the `shadow_color` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.shadow_color_button.color = '#000'

    # WHEN: The `shadow_color` propert is accessed
    result = instance.shadow_color

    # THEN: The value should be correct
    assert result == '#000'


def test_set_shadow_color_property(settings):
    """
    Test setting the `shadow_color` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()

    # WHEN: The `shadow_color` property is set
    instance.shadow_color = '#fff'

    # THEN: The correct value should be set
    instance.shadow_color_button.color == '#fff'


def test_get_shadow_size_property(settings):
    """
    Test the `shadow_size` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.shadow_size_spinbox.value = MagicMock(return_value=5)

    # WHEN: The `shadow_size` propert is accessed
    result = instance.shadow_size

    # THEN: The value should be correct
    assert result == 5


def test_set_shadow_size_property(settings):
    """
    Test setting the `shadow_size` property
    """
    # GIVEN: An instance of FontSelectPage with some mocks
    instance = FontSelectPage()
    instance.shadow_size_spinbox.setValue = MagicMock()

    # WHEN: The `shadow_size` property is set
    instance.shadow_size = 10

    # THEN: The correct value should be set
    instance.shadow_size_spinbox.setValue.assert_called_once_with(10)
