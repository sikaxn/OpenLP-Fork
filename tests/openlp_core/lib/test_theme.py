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
Package to test the openlp.core.lib.theme package.
"""
import pytest
from PySide6 import QtCore
from pathlib import Path
from unittest.mock import MagicMock, patch

from openlp.core.lib.theme import BackgroundType, BackgroundGradientType, TransitionType, TransitionSpeed, Theme


@pytest.fixture
def mock_geometry():
    mocked_screen = MagicMock()
    mocked_screen.display_geometry = QtCore.QRect(10, 20, 400, 600)
    mocked_screenlist = MagicMock()
    mocked_screenlist.current = mocked_screen
    screenlist_patcher = patch('openlp.core.lib.theme.ScreenList', return_value=mocked_screenlist)
    screenlist_patcher.start()
    yield
    screenlist_patcher.stop()


def test_background_type_to_string():
    """
    Test the to_string method of :class:`BackgroundType`
    """
    # GIVEN: The BackgroundType members
    background_type_solid = BackgroundType.Solid
    background_type_gradient = BackgroundType.Gradient
    background_type_image = BackgroundType.Image
    background_type_transparent = BackgroundType.Transparent
    background_type_video = BackgroundType.Video
    background_type_stream = BackgroundType.Stream

    # WHEN: Calling BackgroundType.to_string
    # THEN: The string equivalents should be returned
    assert BackgroundType.to_string(background_type_solid) == 'solid'
    assert BackgroundType.to_string(background_type_gradient) == 'gradient'
    assert BackgroundType.to_string(background_type_image) == 'image'
    assert BackgroundType.to_string(background_type_transparent) == 'transparent'
    assert BackgroundType.to_string(background_type_video) == 'video'
    assert BackgroundType.to_string(background_type_stream) == 'stream'


def test_background_type_from_string():
    """
    Test the from_string method of :class:`BackgroundType`
    """
    # GIVEN: The BackgroundType strings
    background_type_solid = 'solid'
    background_type_gradient = 'gradient'
    background_type_image = 'image'
    background_type_transparent = 'transparent'
    background_type_video = 'video'
    background_type_stream = 'stream'

    # WHEN: Calling BackgroundType.from_string
    # THEN: The enum equivalents should be returned
    assert BackgroundType.from_string(background_type_solid) == BackgroundType.Solid
    assert BackgroundType.from_string(background_type_gradient) == BackgroundType.Gradient
    assert BackgroundType.from_string(background_type_image) == BackgroundType.Image
    assert BackgroundType.from_string(background_type_transparent) == BackgroundType.Transparent
    assert BackgroundType.from_string(background_type_video) == BackgroundType.Video
    assert BackgroundType.from_string(background_type_stream) == BackgroundType.Stream


def test_background_gradient_type_to_string():
    """
    Test the to_string method of :class:`BackgroundGradientType`
    """
    # GIVEN: The BackgroundGradientType member
    background_gradient_horizontal = BackgroundGradientType.Horizontal
    background_gradient_vertical = BackgroundGradientType.Vertical
    background_gradient_circular = BackgroundGradientType.Circular
    background_gradient_left_top = BackgroundGradientType.LeftTop
    background_gradient_left_bottom = BackgroundGradientType.LeftBottom

    # WHEN: Calling BackgroundGradientType.to_string
    # THEN: The string equivalents should be returned
    assert BackgroundGradientType.to_string(background_gradient_horizontal) == 'horizontal'
    assert BackgroundGradientType.to_string(background_gradient_vertical) == 'vertical'
    assert BackgroundGradientType.to_string(background_gradient_circular) == 'circular'
    assert BackgroundGradientType.to_string(background_gradient_left_top) == 'leftTop'
    assert BackgroundGradientType.to_string(background_gradient_left_bottom) == 'leftBottom'


def test_background_gradient_type_from_string():
    """
    Test the from_string method of :class:`BackgroundGradientType`
    """
    # GIVEN: The BackgroundGradientType strings
    background_gradient_horizontal = 'horizontal'
    background_gradient_vertical = 'vertical'
    background_gradient_circular = 'circular'
    background_gradient_left_top = 'leftTop'
    background_gradient_left_bottom = 'leftBottom'

    # WHEN: Calling BackgroundGradientType.from_string
    # THEN: The enum equivalents should be returned
    assert BackgroundGradientType.from_string(background_gradient_horizontal) == BackgroundGradientType.Horizontal
    assert BackgroundGradientType.from_string(background_gradient_vertical) == BackgroundGradientType.Vertical
    assert BackgroundGradientType.from_string(background_gradient_circular) == BackgroundGradientType.Circular
    assert BackgroundGradientType.from_string(background_gradient_left_top) == BackgroundGradientType.LeftTop
    assert BackgroundGradientType.from_string(background_gradient_left_bottom) == BackgroundGradientType.LeftBottom


def test_transition_type_to_string():
    """
    Test the to_string method of :class:`TransitionType`
    """
    # GIVEN: The TransitionType member
    transition_type_fade = TransitionType.Fade
    transition_type_slide = TransitionType.Slide
    transition_type_convex = TransitionType.Convex
    transition_type_concave = TransitionType.Concave
    transition_type_zoom = TransitionType.Zoom

    # WHEN: Calling TransitionType.to_string
    # THEN: The string equivalents should be returned
    assert TransitionType.to_string(transition_type_fade) == 'fade'
    assert TransitionType.to_string(transition_type_slide) == 'slide'
    assert TransitionType.to_string(transition_type_convex) == 'convex'
    assert TransitionType.to_string(transition_type_concave) == 'concave'
    assert TransitionType.to_string(transition_type_zoom) == 'zoom'


def test_transition_type_from_string():
    """
    Test the from_string method of :class:`TransitionType`
    """
    # GIVEN: The TransitionType strings
    transition_type_fade = 'fade'
    transition_type_slide = 'slide'
    transition_type_convex = 'convex'
    transition_type_concave = 'concave'
    transition_type_zoom = 'zoom'

    # WHEN: Calling TransitionType.from_string
    # THEN: The enum equivalents should be returned
    assert TransitionType.from_string(transition_type_fade) == TransitionType.Fade
    assert TransitionType.from_string(transition_type_slide) == TransitionType.Slide
    assert TransitionType.from_string(transition_type_convex) == TransitionType.Convex
    assert TransitionType.from_string(transition_type_concave) == TransitionType.Concave
    assert TransitionType.from_string(transition_type_zoom) == TransitionType.Zoom


def test_transition_speed_to_string():
    """
    Test the to_string method of :class:`TransitionSpeed`
    """
    # GIVEN: The TransitionSpeed member
    transition_speed_normal = TransitionSpeed.Normal
    transition_speed_fast = TransitionSpeed.Fast
    transition_speed_slow = TransitionSpeed.Slow

    # WHEN: Calling TransitionSpeed.to_string
    # THEN: The string equivalents should be returned
    assert TransitionSpeed.to_string(transition_speed_normal) == 'normal'
    assert TransitionSpeed.to_string(transition_speed_fast) == 'fast'
    assert TransitionSpeed.to_string(transition_speed_slow) == 'slow'


def test_transition_speed_from_string():
    """
    Test the from_string method of :class:`TransitionSpeed`
    """
    # GIVEN: The TransitionSpeed strings
    transition_speed_normal = 'normal'
    transition_speed_fast = 'fast'
    transition_speed_slow = 'slow'

    # WHEN: Calling TransitionSpeed.from_string
    # THEN: The enum equivalents should be returned
    assert TransitionSpeed.from_string(transition_speed_normal) == TransitionSpeed.Normal
    assert TransitionSpeed.from_string(transition_speed_fast) == TransitionSpeed.Fast
    assert TransitionSpeed.from_string(transition_speed_slow) == TransitionSpeed.Slow


def test_new_theme(mock_geometry):
    """
    Test the Theme constructor
    """
    # GIVEN: The Theme class
    # WHEN: A theme object is created
    default_theme = Theme()

    # THEN: The default values should be correct
    check_theme(default_theme)


def test_expand_json(mock_geometry):
    """
    Test the expand_json method
    """
    # GIVEN: A Theme object and some JSON to "expand"
    theme = Theme()
    theme_json = {
        'background': {
            'border_color': '#000000',
            'type': 'solid'
        },
        'display': {
            'vertical_align': 0
        },
        'font': {
            'footer': {
                'bold': False
            },
            'main': {
                'name': 'Arial'
            }
        }
    }

    # WHEN: Theme.expand_json() is run
    theme.expand_json(theme_json)

    # THEN: The attributes should be set on the object
    check_theme(theme)


def test_extend_image_filename(mock_geometry):
    """
    Test the extend_image_filename method
    """
    # GIVEN: A theme object
    theme = Theme()
    theme.theme_name = 'MyBeautifulTheme'
    theme.background_filename = Path('video.mp4')
    theme.background_type = 'video'
    path = Path.home()

    # WHEN: Theme.extend_image_filename is run
    theme.extend_image_filename(path)

    # THEN: The filename of the background should be correct
    expected_filename = path / 'MyBeautifulTheme' / 'video.mp4'
    assert expected_filename == theme.background_filename
    assert 'MyBeautifulTheme' == theme.theme_name


def test_save_retrieve(mock_geometry):
    """
    Load a dummy theme, save it and reload it
    """
    # GIVEN: The default Theme class
    # WHEN: A theme object is created
    default_theme = Theme()
    # THEN: The default values should be correct
    save_theme_json = default_theme.export_theme()
    lt = Theme()
    lt.load_theme(save_theme_json)
    check_theme(lt)


def test_set_default_header_footer_overridden(mock_geometry):
    """
    Check that when the theme header and footer locations are overridden, the defaults are not set
    """
    # GIVEN: A theme with the overrides on
    theme = Theme()
    theme.set_default_header = MagicMock()
    theme.set_default_footer = MagicMock()
    theme.font_main_override = True
    theme.font_footer_override = True

    # WHEN: set_default_header_footer is called
    theme.set_default_header_footer()

    # THEN: Neither header or footer default fns should have been called
    assert theme.set_default_header.call_count == 0
    assert theme.set_default_footer.call_count == 0


def test_set_default_footer(mock_geometry):
    """
    Test the set_default_footer function sets the footer back to default
    (reletive to the screen)
    """
    # GIVEN: A screen geometry object and a Theme footer with a strange area
    theme = Theme()
    theme.font_main_x = 20
    theme.font_footer_x = 207
    theme.font_footer_y = 25
    theme.font_footer_width = 4253
    theme.font_footer_height = 5423

    # WHEN: set_default_footer is called
    theme.set_default_footer()

    # THEN: footer should be set, header should not have changed
    assert theme.font_main_x == 20, 'header should not have been changed'
    assert theme.font_footer_x == 10, 'x pos should be reset to default of 10'
    assert theme.font_footer_y == 540, 'y pos should be reset to (screen_size_height * 9 / 10)'
    assert theme.font_footer_width == 380, 'width should have been reset to (screen_size_width - 20)'
    assert theme.font_footer_height == 60, 'height should have been reset to (screen_size_height / 10)'


def test_set_default_header(mock_geometry):
    """
    Test the set_default_header function sets the header back to default
    (reletive to the screen)
    """
    # GIVEN: A screen geometry object and a Theme header with a strange area
    theme = Theme()
    theme.font_footer_x = 200
    theme.font_main_x = 687
    theme.font_main_y = 546
    theme.font_main_width = 345
    theme.font_main_height = 653

    # WHEN: set_default_header is called
    theme.set_default_header()

    # THEN: footer should be set, header should not have changed
    assert theme.font_footer_x == 200, 'footer should not have been changed'
    assert theme.font_main_x == 10, 'x pos should be reset to default of 10'
    assert theme.font_main_y == 0, 'y pos should be reset to 0'
    assert theme.font_main_width == 380, 'width should have been reset to (screen_size_width - 20)'
    assert theme.font_main_height == 540, 'height should have been reset to (screen_size_height * 9 / 10)'


def test_set_default_header_footer(mock_geometry):
    """
    Test the set_default_header_footer function sets the header and footer back to default
    (reletive to the screen)
    """
    # GIVEN: A screen geometry object and a Theme header with a strange area
    theme = Theme()
    theme.font_footer_x = 200
    theme.font_main_x = 687

    # WHEN: set_default_header is called
    theme.set_default_header_footer()

    # THEN: footer should be set, header should not have changed
    assert theme.font_footer_x == 10, 'footer x pos should be reset to default of 10'
    assert theme.font_main_x == 10, 'header x pos should be reset to default of 10'


def check_theme(theme):
    assert '#000000' == theme.background_border_color, 'background_border_color should be "#000000"'
    assert 'solid' == theme.background_type, 'background_type should be "solid"'
    assert 0 == theme.display_vertical_align, 'display_vertical_align should be 0'
    assert theme.font_footer_bold is False, 'font_footer_bold should be False'
    assert 'Arial' == theme.font_main_name, 'font_main_name should be "Arial"'
    assert 58 == len(theme.__dict__), 'The theme should have 58 attributes'
