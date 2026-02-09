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
The :mod:`~openlp.plugins.custom.customplugin` module contains the Plugin class
for the Custom Slides plugin.
"""

import logging

from openlp.core.state import State
from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.lib import build_icon
from openlp.core.db.manager import DBManager
from openlp.core.lib.plugin import Plugin, StringContent
from openlp.core.ui.icons import UiIcons
from openlp.plugins.custom.lib.db import CustomSlide, init_schema
from openlp.plugins.custom.lib.mediaitem import CustomMediaItem
from openlp.plugins.custom.lib.customtab import CustomTab


log = logging.getLogger(__name__)


class CustomPlugin(Plugin):
    """
    This plugin enables the user to create, edit and display custom slide shows. Custom shows are divided into slides.
    Each show is able to have it's own theme.
    Custom shows are designed to replace the use of songs where the songs plugin has become restrictive.
    Examples could be Welcome slides, Bible Reading information, Orders of service.
    """
    log.info('Custom Plugin loaded')

    def __init__(self):
        super(CustomPlugin, self).__init__('custom', CustomMediaItem, CustomTab)
        self.weight = -5
        self.db_manager = DBManager('custom', init_schema)
        self.icon_path = UiIcons().custom
        Registry().register('custom_manager', self.db_manager)
        self.icon = build_icon(self.icon_path)
        State().add_service(self.name, self.weight, is_plugin=True)
        State().update_pre_conditions(self.name, self.check_pre_conditions())

    @staticmethod
    def about():
        about_text = translate('CustomPlugin', '<strong>Custom Slide Plugin</strong><br />The custom slide plugin '
                               'provides the ability to set up custom text slides that can be displayed on the screen '
                               'the same way songs are. This plugin provides greater freedom over the songs plugin.')
        return about_text

    def check_pre_conditions(self):
        """
        Check the plugin can run.
        """
        return self.db_manager.session is not None

    def uses_theme(self, theme):
        """
        Called to find out if the custom plugin is currently using a theme.

        Returns count of the times the theme is used.
        :param theme: Theme to be queried
        """
        return len(self.db_manager.get_all_objects(CustomSlide, CustomSlide.theme_name == theme))

    def rename_theme(self, old_theme, new_theme):
        """
        Renames a theme the custom plugin is using making the plugin use the new name.

        :param old_theme: The name of the theme the plugin should stop using.
        :param new_theme: The new name the plugin should now use.
        """
        customs_using_theme = self.db_manager.get_all_objects(CustomSlide, CustomSlide.theme_name == old_theme)
        for custom in customs_using_theme:
            custom.theme_name = new_theme
            self.db_manager.save_object(custom)

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('CustomPlugin', 'Custom Slide', 'name singular'),
            'plural': translate('CustomPlugin', 'Custom Slides', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('CustomPlugin', 'Custom Slides', 'container title')
        }
        # Middle Header Bar
        tooltips = {
            'load': translate('CustomPlugin', 'Load a new custom slide.'),
            'import': translate('CustomPlugin', 'Import a custom slide.'),
            'new': translate('CustomPlugin', 'Add a new custom slide.'),
            'edit': translate('CustomPlugin', 'Edit the selected custom slide.'),
            'delete': translate('CustomPlugin', 'Delete the selected custom slide.'),
            'preview': translate('CustomPlugin', 'Preview the selected custom slide.'),
            'live': translate('CustomPlugin', 'Send the selected custom slide live.'),
            'service': translate('CustomPlugin', 'Add the selected custom slide to the service.')
        }
        self.set_plugin_ui_text_strings(tooltips)

    def finalise(self):
        """
        Time to tidy up on exit
        """
        log.info('Custom Finalising')
        # call custom manager to delete pco slides
        pco_slides = self.db_manager.get_all_objects(CustomSlide, CustomSlide.credits == 'pco')
        for slide in pco_slides:
            self.db_manager.delete_object(CustomSlide, slide.id)
        self.db_manager.finalise()
        Plugin.finalise(self)
