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
The screen settings tab in the configuration dialog
"""
from PySide6 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.display.screens import ScreenList
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.common.registry import Registry
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.widgets import ScreenSelectionWidget


class ScreensTab(SettingsTab):
    """
    ScreensTab is the screen settings tab in the configuration dialog
    """
    def __init__(self, parent):
        """
        Initialise the screen settings tab
        """
        self.icon_path = UiIcons().desktop
        screens_translated = translate('OpenLP.ScreensTab', 'Screens')
        super(ScreensTab, self).__init__(parent, 'Screens', screens_translated)
        self.settings_section = 'core'

    def setup_ui(self):
        """
        Set up the user interface elements
        """
        self.setObjectName('self')
        self.tab_layout = QtWidgets.QVBoxLayout(self)
        self.tab_layout.setObjectName('tab_layout')
        self.screen_selection_widget = ScreenSelectionWidget(self, ScreenList())
        self.tab_layout.addWidget(self.screen_selection_widget)
        self.generic_group_box = QtWidgets.QGroupBox(self)
        self.generic_group_box.setObjectName('generic_group_box')
        self.generic_group_layout = QtWidgets.QVBoxLayout(self.generic_group_box)
        self.display_on_monitor_check = QtWidgets.QCheckBox(self.generic_group_box)
        self.display_on_monitor_check.setObjectName('monitor_combo_box')
        self.generic_group_layout.addWidget(self.display_on_monitor_check)
        self.tab_layout.addWidget(self.generic_group_box)
        Registry().register_function('config_screen_changed', self.screen_selection_widget.load)

        self.retranslate_ui()

    def retranslate_ui(self):
        self.generic_group_box.setTitle(translate('OpenLP.ScreensTab', 'Generic screen settings'))
        self.display_on_monitor_check.setText(translate('OpenLP.ScreensTab', 'Display if a single screen'))

    def resizeEvent(self, event=None):
        """
        Override resizeEvent() to adjust the position of the identify_button.

        NB: Don't call SettingsTab's resizeEvent() because we're not using its widgets.
        """
        QtWidgets.QWidget.resizeEvent(self, event)

    def load(self):
        """
        Load the settings to populate the tab
        """
        self.screen_selection_widget.load()
        # Load generic settings
        self.display_on_monitor_check.setChecked(self.settings.value('core/display on monitor'))

    def save(self):
        self.screen_selection_widget.save()
        self.settings.setValue('core/display on monitor', self.display_on_monitor_check.isChecked())
        # On save update the screens as well
        if self.tab_visited:
            self.settings_form.register_post_process('config_screen_changed')
        self.tab_visited = False
