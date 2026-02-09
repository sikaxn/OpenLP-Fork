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
from unittest.mock import MagicMock

from openlp.core.widgets.comboboxes import LazyComboBox


def test_lazy_loading(mock_settings: MagicMock):
    # GIVEN: an instance of LazyComboBox, and a callable loader
    loader_mock = MagicMock()
    loader_mock.side_effect = [False, False, True]

    comboxbox = LazyComboBox(None, loader_mock)

    # WHEN: the showPopup is called multiple times
    comboxbox.showPopup()
    comboxbox.showPopup()
    comboxbox.showPopup()
    comboxbox.showPopup()

    # THEN: loader should be called only three times, since loader returned True
    assert loader_mock.call_count == 3
