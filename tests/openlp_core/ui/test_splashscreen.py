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
Package to test the openlp.core.ui package.
"""
from unittest.mock import MagicMock
from PySide6 import QtCore

from openlp.core.ui.splashscreen import SplashScreen


def test_splashscreen(mock_settings: MagicMock):
    """
    Test that the SpashScreen is created correctly
    """
    # GIVEN: the SplashScreen class
    # WHEN: An object is created

    ss = SplashScreen()
    # THEN: Nothing should go wrong and the instance should have the correct values
    assert ss.objectName() == 'splashScreen', 'The ObjectName should have be ' \
        'splashScreen'
    assert ss.frameSize() == QtCore.QSize(370, 370), 'The frameSize should be (370, 370)'
    assert ss.contextMenuPolicy() == QtCore.Qt.ContextMenuPolicy.PreventContextMenu, 'The ContextMenuPolicy ' \
        'should have been QtCore.Qt.ContextMenuPolicy.PreventContextMenu or 4'
