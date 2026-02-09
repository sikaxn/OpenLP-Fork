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
The :mod:`~openlp.core.loader` module provides a bootstrap for the singleton classes
"""

from openlp.core.display.render import Renderer
from openlp.core.lib.pluginmanager import PluginManager
from openlp.core.state import State
from openlp.core.ui.media.mediacontroller import MediaController

from openlp.core.ui.slidecontroller import LiveController, PreviewController


def loader():
    """
    God method to load all the components which are registered with the Registry

    :return: None
    """
    State().load_settings()
    MediaController()
    PluginManager()
    # Set up the path with plugins
    Renderer(window_title='Renderer')
    # Create slide controllers
    PreviewController()
    LiveController()
