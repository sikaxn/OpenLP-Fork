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

import logging

from openlp.core.common.i18n import translate
from openlp.core.lib import build_icon
from openlp.core.db.manager import DBManager
from openlp.core.lib.plugin import Plugin, StringContent
from openlp.core.state import State
from openlp.core.ui.icons import UiIcons

from openlp.plugins.images.lib import upgrade
from openlp.plugins.images.lib.db import init_schema
from openlp.plugins.images.lib.imagetab import ImageTab
from openlp.plugins.images.lib.mediaitem import ImageMediaItem


log = logging.getLogger(__name__)


class ImagePlugin(Plugin):
    log.info('Image Plugin loaded')

    def __init__(self):
        super(ImagePlugin, self).__init__('images', ImageMediaItem, ImageTab)
        self.manager = DBManager('images', init_schema, upgrade_mod=upgrade)
        self.weight = -7
        self.icon_path = UiIcons().picture
        self.icon = build_icon(self.icon_path)
        State().add_service('image', self.weight, is_plugin=True)
        State().update_pre_conditions('image', self.check_pre_conditions())

    @staticmethod
    def about():
        about_text = translate('ImagePlugin', '<strong>Image Plugin</strong>'
                               '<br />The image plugin provides displaying of images.<br />One '
                               'of the distinguishing features of this plugin is the ability to '
                               'group a number of images together in the service manager, making '
                               'the displaying of multiple images easier. This plugin can also '
                               'make use of OpenLP\'s "timed looping" feature to create a slide '
                               'show that runs automatically. In addition to this, images from '
                               'the plugin can be used to override the current theme\'s '
                               'background, which renders text-based items like songs with the '
                               'selected image as a background instead of the background '
                               'provided by the theme.')
        return about_text

    def check_pre_conditions(self):
        """
        Check the plugin can run.
        """
        return self.manager.session is not None

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin.
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('ImagePlugin', 'Image', 'name singular'),
            'plural': translate('ImagePlugin', 'Images', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {'title': translate('ImagePlugin', 'Images', 'container title')}
        # Middle Header Bar
        tooltips = {
            'load': translate('ImagePlugin', 'Add new image(s).'),
            'import': '',
            'new': translate('ImagePlugin', 'Add a new image.'),
            'edit': translate('ImagePlugin', 'Edit the selected image.'),
            'delete': translate('ImagePlugin', 'Delete the selected image.'),
            'preview': translate('ImagePlugin', 'Preview the selected image.'),
            'live': translate('ImagePlugin', 'Send the selected image live.'),
            'service': translate('ImagePlugin', 'Add the selected image to the service.')
        }
        self.set_plugin_ui_text_strings(tooltips)
