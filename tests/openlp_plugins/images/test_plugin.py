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
This module contains tests for the plugin class Images plugin.
"""
from openlp.plugins.images.imageplugin import ImagePlugin


def test_image_plugin_about():
    result = ImagePlugin.about()

    assert result == (
        '<strong>Image Plugin</strong>'
        '<br />The image plugin provides displaying of images.<br />One '
        'of the distinguishing features of this plugin is the ability to '
        'group a number of images together in the service manager, making '
        'the displaying of multiple images easier. This plugin can also '
        'make use of OpenLP\'s "timed looping" feature to create a slide '
        'show that runs automatically. In addition to this, images from '
        'the plugin can be used to override the current theme\'s '
        'background, which renders text-based items like songs with the '
        'selected image as a background instead of the background '
        'provided by the theme.'
    )
