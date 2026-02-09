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
Package to test the openlp.core.pages package.
"""
from unittest.mock import MagicMock, call, patch

import pytest

from openlp.core.pages import GridLayoutPage


@patch('openlp.core.pages.GridLayoutPage.setup_ui')
@patch('openlp.core.pages.GridLayoutPage.retranslate_ui')
def test_resize_event(mocked_retranslate_ui, mocked_setup_ui, settings):
    """
    Test that the `resizeEvent()` method called the `resize_columns()` method.
    """
    # GIVEN: An instance of GridLayoutPage with a mocked out "resize_columns" method
    instance = GridLayoutPage()
    instance.resize_columns = MagicMock()

    # WHEN: resizeEvent is called
    instance.resizeEvent(None)

    # THEN: resize_widgets should have been called
    instance.resize_columns.assert_called_once()


def test_unimplemented_setup_ui(settings):
    """
    Test that setup_ui() throws a NotImplementedError
    """
    with pytest.raises(NotImplementedError, match='Descendant pages need to implement setup_ui'):
        GridLayoutPage()


@patch('openlp.core.pages.GridLayoutPage.setup_ui')
def test_unimplemented_retranslate_ui(mocked_setup_ui, settings):
    """
    Test that retranslate_ui() throws a NotImplementedError
    """
    with pytest.raises(NotImplementedError, match='Descendant pages need to implement retranslate_ui'):
        GridLayoutPage()


@patch('openlp.core.pages.GridLayoutPage.setup_ui')
@patch('openlp.core.pages.GridLayoutPage.retranslate_ui')
def test_resize_columns(mocked_retranslate_ui, mocked_setup_ui, settings):
    """
    Test the `resize_columns()` method with an implemented page
    """
    # GIVEN: An instance of GridLayoutPage and various mocked out methods
    instance = GridLayoutPage()
    instance.layout.contentsRect = MagicMock(return_value=MagicMock(**{'width.return_value': 100}))
    instance.layout.horizontalSpacing = MagicMock(return_value=6)
    instance.layout.columnCount = MagicMock(return_value=4)
    instance.layout.setColumnMinimumWidth = MagicMock()

    # WHEN: `resize_columns()` is called
    instance.resize_columns()

    # THEN: The column widths should be set to 16
    instance.layout.contentsRect.assert_called_once()
    instance.layout.horizontalSpacing.assert_called_once()
    instance.layout.columnCount.assert_called_once()
    assert instance._column_width == 20
    assert instance.layout.setColumnMinimumWidth.call_args_list == [call(0, 20), call(1, 20),
                                                                    call(2, 20), call(3, 20)]
