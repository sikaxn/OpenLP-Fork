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
Package to test the openlp.core.ui.themeform package.
"""
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.ui.themeprogressform import ThemeProgressForm


@pytest.fixture
def form(qapp, registry: Registry) -> ThemeProgressForm:
    """Common code used to create the ThemeProgressForm object"""
    with patch('openlp.core.ui.themeprogressdialog.ThemePreviewRenderer'), \
            patch('openlp.core.ui.themeprogressdialog.UiThemeProgressDialog.setup_ui'):
        form = ThemeProgressForm()
    return form


def test_init(form: ThemeProgressForm):
    """
    Test that the ThemeProgressForm is created without problems
    """
    # GIVEN: ThemeProgressForm class
    # WHEN: An object is instatiated
    # THEN: There is no problem
    assert form is not None


@patch('openlp.core.ui.themeprogressform.ScreenList')
@patch('openlp.core.ui.themeprogressform.QtWidgets.QDialog.show')
def test_show(mocked_show: MagicMock, MockScreenList: MagicMock, form: ThemeProgressForm, settings: Settings):
    """
    Test that the ThemeProgressForm is created without problems
    """
    # GIVEN: ThemeProgressForm object
    mocked_screen_list = MagicMock()
    mocked_screen_list.current.display_geometry.width.return_value = 1920
    mocked_screen_list.current.display_geometry.height.return_value = 1080
    MockScreenList.return_value = mocked_screen_list
    form.progress_bar = MagicMock()
    form.theme_preview_layout = MagicMock()

    # WHEN: The show() method is called
    form.show()

    # THEN: The correct display ratio is calculated and the form is shown
    expected_ratio = 16 / 9
    form.progress_bar.setValue.assert_called_once_with(0)
    assert form.ratio == expected_ratio
    assert form.theme_preview_layout.aspect_ratio == expected_ratio
    mocked_show.assert_called_once()


@patch('openlp.core.ui.themeprogressform.ScreenList')
@patch('openlp.core.ui.themeprogressform.QtWidgets.QDialog.show')
def test_show_divide_by_zero(mocked_show: MagicMock, MockScreenList: MagicMock, form: ThemeProgressForm,
                             settings: Settings):
    """
    Test that the ThemeProgressForm is created without problems even if there's a divide by zero exception
    """
    # GIVEN: ThemeProgressForm object
    mocked_screen_list = MagicMock()
    mocked_screen_list.current.display_geometry.width.return_value = 1920
    mocked_screen_list.current.display_geometry.height.return_value = 0
    MockScreenList.return_value = mocked_screen_list
    form.progress_bar = MagicMock()
    form.theme_preview_layout = MagicMock()

    # WHEN: The show() method is called
    form.show()

    # THEN: The correct display ratio is calculated and the form is shown
    expected_ratio = 16 / 9
    form.progress_bar.setValue.assert_called_once_with(0)
    assert form.ratio == expected_ratio
    assert form.theme_preview_layout.aspect_ratio == expected_ratio
    mocked_show.assert_called_once()


def test_get_preview(form: ThemeProgressForm, registry: Registry, settings: Settings):
    """
    Test that the get_preview() method returns a preview image
    """
    # GIVEN: ThemeProgressForm object
    mocked_renderer = MagicMock()
    registry.register('renderer', mocked_renderer)
    test_theme_name = 'Test Theme'
    test_theme_data = {'name': test_theme_name}
    form.isVisible = MagicMock(return_value=True)
    form.progress_bar = MagicMock(**{'value.return_value': 0})
    form.label = MagicMock()
    form.theme_display = MagicMock(**{'width.return_value': 192, 'generate_preview.return_value': 'preview'})
    form.renderer.width = MagicMock(return_value=1920)

    # WHEN: get_preview() is called
    preview = form.get_preview(test_theme_name, test_theme_data)

    # THEN: All the correct methods should be called and the correct results should be returned
    form.label.setText.assert_called_once_with(test_theme_name)
    form.progress_bar.value.assert_called_once()
    form.progress_bar.setValue.assert_called_once_with(1)
    form.theme_display.width.assert_called_once()
    form.renderer.width.assert_called_once()
    form.theme_display.set_scale.assert_called_once_with(0.1)
    form.theme_display.generate_preview.assert_called_once_with(test_theme_data, generate_screenshot=True)
    assert preview == 'preview'


def test_get_preview_not_visible(form: ThemeProgressForm, registry: Registry, settings: Settings):
    """
    Test that the get_preview() method does not return a preview image when display is not visible
    """
    # GIVEN: ThemeProgressForm object
    mocked_renderer = MagicMock()
    Registry().register('renderer', mocked_renderer)
    test_theme_name = 'Test Theme'
    test_theme_data = {'name': test_theme_name}
    form.isVisible = MagicMock(return_value=False)
    form.progress_bar = MagicMock(**{'value.return_value': 0})
    form.label = MagicMock()
    form.theme_display = MagicMock(**{'width.return_value': 192, 'generate_preview.return_value': 'preview'})
    form.renderer.width = MagicMock(return_value=1920)

    # WHEN: get_preview() is called
    preview = form.get_preview(test_theme_name, test_theme_data)

    # THEN: Result should be None
    assert preview is None


def test_theme_list(qapp, form: ThemeProgressForm):
    # GIVEN: ThemeProgressForm object and theme list
    test_theme_list = ['Theme 1', 'Theme 2']
    form.progress_bar = MagicMock()

    # WHEN: theme_list is set and get'ed
    form.theme_list = test_theme_list
    theme_list = form.theme_list

    # THEN: The theme list should be correct
    form.progress_bar.setMinimum.assert_called_once_with(0)
    form.progress_bar.setMaximum.assert_called_once_with(2)
    assert theme_list == test_theme_list
