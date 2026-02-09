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
The :mod:`~openlp.plugins.planningcenter.PlanningCenterPlugin` module contains
the Plugin class for the PlanningCenter plugin.
"""
import logging
from typing import Optional

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.lib.plugin import Plugin, StringContent
from openlp.core.lib.ui import create_action
from openlp.core.state import State
from openlp.core.ui.icons import UiIcons
from openlp.plugins.planningcenter.forms.selectplanform import SelectPlanForm
from openlp.plugins.planningcenter.lib.planningcentertab import PlanningCenterTab

log = logging.getLogger(__name__)


class PlanningCenterPlugin(Plugin):
    """
    This plugin enables the user to import services from Planning Center Online.
    """
    log.info('PlanningCenter Plugin loaded')

    def __init__(self):
        """
        Create and set up the PlanningCenter plugin.
        """
        super(PlanningCenterPlugin, self).__init__('planningcenter', settings_tab_class=PlanningCenterTab)
        self.planningcenter_form = None
        self.icon = UiIcons().planning_center
        self.icon_path = self.icon
        self.weight = -1
        self.application_id: Optional[str] = None
        self.secret: Optional[str] = None
        State().add_service('planning_center', self.weight, is_plugin=True)
        State().update_pre_conditions('planning_center', self.check_pre_conditions())

    def initialise(self):
        """
        Initialise the plugin
        """
        log.info('PlanningCenter Initialising')
        super(PlanningCenterPlugin, self).initialise()
        self.import_planning_center.setVisible(True)

    def add_import_menu_item(self, import_menu):
        """
        Add "PlanningCenter Service" to the **Import** menu.

        :param import_menu: The actual **Import** menu item, so that your
        actions can use it as their parent.
        """
        self.import_planning_center = create_action(import_menu, 'import_planning_center',
                                                    text=translate('PlanningCenterPlugin', 'Planning Center Service'),
                                                    visible=False,
                                                    statustip=translate('PlanningCenterPlugin',
                                                                        'Import Planning Center Service Plan '
                                                                        'from Planning Center Online.'),
                                                    triggers=self.on_import_planning_center_triggered
                                                    )
        import_menu.addAction(self.import_planning_center)

    def on_import_planning_center_triggered(self):
        """
        Run the PlanningCenter importer.
        """
        # Determine which dialog to show based on whether the auth values are set yet
        self.application_id = self.settings.value("planningcenter/application_id")
        self.secret = self.settings.value("planningcenter/secret")
        if not self.application_id or not self.secret:
            self.planningcenter_form = Registry().get('settings_form')
            self.planningcenter_form.exec(translate('PlanningCenterPlugin', 'PlanningCenter'))
        else:
            self.planningcenter_form = SelectPlanForm(Registry().get('main_window'), self)
            self.planningcenter_form.exec()

    @staticmethod
    def about():
        """
        Provides information for the plugin manager to display.

        :return: A translatable string with some basic information about the
        PlanningCenter plugin
        """
        return translate('PlanningCenterPlugin', '<strong>PlanningCenter Plugin</strong>'
                         '<br />The planningcenter plugin provides an interface to import '
                         'service plans from the Planning Center Online v2 API.')

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('PlanningCenterPlugin', 'PlanningCenter',
                                  'name singular'),
            'plural': translate('PlanningCenterPlugin', 'PlanningCenter',
                                'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('PlanningCenterPlugin', 'PlanningCenter',
                               'container title')
        }
        # Middle Header Bar
        tooltips = {
            'load': '',
            'import': translate('PlanningCenterPlugin', 'Import All Plan Items '
                                'into Current Service'),
            'new': '',
            'edit': '',
            'delete': '',
            'preview': '',
            'live': '',
            'service': '',
        }
        self.set_plugin_ui_text_strings(tooltips)

    def finalise(self):
        """
        Tidy up on exit
        """
        log.info('PlanningCenter Finalising')
        self.import_planning_center.setVisible(False)
        super(PlanningCenterPlugin, self).finalise()
