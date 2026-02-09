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
For the Presentation tests
"""
import pytest
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.plugins.presentations.lib.mediaitem import PresentationMediaItem


@pytest.fixture
def media_item(settings, mock_plugin):
    """Local test setup"""
    Registry().register('service_manager', MagicMock())
    Registry().register('main_window', MagicMock())
    with patch('openlp.plugins.presentations.lib.mediaitem.FolderLibraryItem._setup'), \
            patch('openlp.plugins.presentations.lib.mediaitem.PresentationMediaItem.setup_item'):
        m_item = PresentationMediaItem(None, mock_plugin, MagicMock())
        m_item.settings_section = 'media'
    return m_item


@pytest.fixture()
def mock_plugin(temp_folder):
    m_plugin = MagicMock()
    m_plugin.settings_section = temp_folder
    m_plugin.manager = MagicMock()
    yield m_plugin
