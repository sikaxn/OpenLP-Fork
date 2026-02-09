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
from datetime import datetime

from PySide6 import QtCore, QtWidgets

from openlp.core.state import State
from openlp.core.common.actions import ActionList
from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.db.manager import DBManager
from openlp.core.lib.plugin import Plugin, StringContent
from openlp.core.lib.ui import create_action
from openlp.core.ui.icons import UiIcons
from openlp.plugins.songusage.forms.songusagedetailform import SongUsageDetailForm
from openlp.plugins.songusage.forms.songusagedeleteform import SongUsageDeleteForm
from openlp.plugins.songusage.lib import upgrade
from openlp.plugins.songusage.lib.db import SongUsageItem, init_schema


log = logging.getLogger(__name__)

TODAY = QtCore.QDate.currentDate()


class SongUsagePlugin(Plugin):
    """
    Song Usage Plugin class
    """
    log.info('SongUsage Plugin loaded')

    def __init__(self):
        super(SongUsagePlugin, self).__init__('songusage')
        self.manager = DBManager('songusage', init_schema, upgrade_mod=upgrade)
        self.weight = -4
        self.icon = UiIcons().song_usage
        self.song_usage_active = False
        State().add_service('song_usage', self.weight, is_plugin=True)
        State().update_pre_conditions('song_usage', self.check_pre_conditions())

    def check_pre_conditions(self):
        """
        Check the plugin can run.
        """
        return self.manager.session is not None

    def add_tools_menu_item(self, tools_menu):
        """
        Give the SongUsage plugin the opportunity to add items to the **Tools** menu.

        :param tools_menu: The actual **Tools** menu item, so that your actions can use it as their parent.
        """
        log.info('add tools menu')
        self.tools_menu = tools_menu
        self.song_usage_menu = QtWidgets.QMenu(tools_menu)
        self.song_usage_menu.setObjectName('song_usage_menu')
        self.song_usage_menu.setTitle(translate('SongUsagePlugin', '&Song Usage Tracking'))
        # SongUsage Delete
        self.song_usage_delete = create_action(
            tools_menu, 'songUsageDelete',
            text=translate('SongUsagePlugin', '&Delete Tracking Data'),
            statustip=translate('SongUsagePlugin', 'Delete song usage data up to a specified date.'),
            triggers=self.on_song_usage_delete)
        # SongUsage Report
        self.song_usage_report = create_action(
            tools_menu, 'songUsageReport',
            text=translate('SongUsagePlugin', '&Extract Tracking Data'),
            statustip=translate('SongUsagePlugin', 'Generate a report on song usage.'),
            triggers=self.on_song_usage_report)
        # SongUsage activation
        self.song_usage_status = create_action(
            tools_menu, 'songUsageStatus',
            text=translate('SongUsagePlugin', 'Toggle Tracking'),
            statustip=translate('SongUsagePlugin', 'Toggle the tracking of song usage.'), checked=False,
            can_shortcuts=True, triggers=self.toggle_song_usage_state)
        # Add Menus together
        self.tools_menu.addAction(self.song_usage_menu.menuAction())
        self.song_usage_menu.addAction(self.song_usage_status)
        self.song_usage_menu.addSeparator()
        self.song_usage_menu.addAction(self.song_usage_report)
        self.song_usage_menu.addAction(self.song_usage_delete)
        self.song_usage_active_button = QtWidgets.QToolButton(self.main_window.status_bar)
        self.song_usage_active_button.setCheckable(True)
        self.song_usage_active_button.setAutoRaise(True)
        self.song_usage_active_button.setStatusTip(translate('SongUsagePlugin', 'Toggle the tracking of song usage.'))
        self.song_usage_active_button.setObjectName('song_usage_active_button')
        self.main_window.status_bar.insertPermanentWidget(1, self.song_usage_active_button)
        self.song_usage_active_button.hide()
        # Signals and slots
        self.song_usage_active_button.toggled.connect(self.toggle_song_usage_state)
        self.song_usage_menu.menuAction().setVisible(False)

    def initialise(self):
        log.info('SongUsage Initialising')
        super(SongUsagePlugin, self).initialise()
        Registry().register_function('slidecontroller_live_started', self.display_song_usage)
        Registry().register_function('print_service_started', self.print_song_usage)
        self.song_usage_active = self.settings.value('songusage/active')
        # Set the button and checkbox state
        self.set_button_state()
        action_list = ActionList.get_instance()
        action_list.add_action(self.song_usage_status, translate('SongUsagePlugin', 'Song Usage'))
        action_list.add_action(self.song_usage_delete, translate('SongUsagePlugin', 'Song Usage'))
        action_list.add_action(self.song_usage_report, translate('SongUsagePlugin', 'Song Usage'))
        self.song_usage_delete_form = SongUsageDeleteForm(self.manager, self.main_window)
        self.song_usage_detail_form = SongUsageDetailForm(self, self.main_window)
        self.song_usage_menu.menuAction().setVisible(True)
        self.song_usage_active_button.show()

    def finalise(self):
        """
        Tidy up on exit
        """
        log.info('Plugin Finalise')
        self.manager.finalise()
        super(SongUsagePlugin, self).finalise()
        self.song_usage_menu.menuAction().setVisible(False)
        action_list = ActionList.get_instance()
        action_list.remove_action(self.song_usage_status, translate('SongUsagePlugin', 'Song Usage'))
        action_list.remove_action(self.song_usage_delete, translate('SongUsagePlugin', 'Song Usage'))
        action_list.remove_action(self.song_usage_report, translate('SongUsagePlugin', 'Song Usage'))
        self.song_usage_active_button.hide()
        # stop any events being processed
        self.song_usage_active = False

    def toggle_song_usage_state(self):
        """
        Manage the state of the audit collection and amend
        the UI when necessary,
        """
        self.song_usage_active = not self.song_usage_active
        self.settings.setValue('songusage/active', self.song_usage_active)
        self.set_button_state()

    def set_button_state(self):
        """
        Keep buttons inline.  Turn of signals to stop dead loop but we need the button and check box set correctly.
        """
        self.song_usage_active_button.blockSignals(True)
        self.song_usage_status.blockSignals(True)
        if self.song_usage_active:
            self.song_usage_active_button.setIcon(UiIcons().song_usage_active)
            self.song_usage_status.setChecked(True)
            self.song_usage_active_button.setChecked(True)
            self.song_usage_active_button.setToolTip(translate('SongUsagePlugin', 'Song usage tracking is active.'))
        else:
            self.song_usage_active_button.setIcon(UiIcons().song_usage_inactive)
            self.song_usage_status.setChecked(False)
            self.song_usage_active_button.setChecked(False)
            self.song_usage_active_button.setToolTip(translate('SongUsagePlugin', 'Song usage tracking is inactive.'))
        self.song_usage_active_button.blockSignals(False)
        self.song_usage_status.blockSignals(False)

    def display_song_usage(self, item):
        """
        Song Usage for which has been displayed

        :param item: Item displayed
        """
        self._add_song_usage(translate('SongUsagePlugin', 'display'), item)

    def print_song_usage(self, item):
        """
        Song Usage for which has been printed

        :param item: Item printed
        """
        self._add_song_usage(translate('SongUsagePlugin', 'printed'), item)

    def _add_song_usage(self, source, item):
        audit = item[0].audit
        if self.song_usage_active and audit:
            song_usage_item = SongUsageItem(
                usagedate=datetime.today(),
                usagetime=datetime.now().time(),
                title=audit[0],
                copyright=audit[2],
                ccl_number=audit[3],
                authors=' '.join(audit[1]),
                plugin_name=item[0].name,
                source=source
            )
            self.manager.save_object(song_usage_item)

    def on_song_usage_delete(self):
        """
        Request the delete form to be displayed
        """
        self.song_usage_delete_form.exec()

    def on_song_usage_report(self):
        """
        Display the song usage report generator screen

        """
        self.song_usage_detail_form.initialise()
        self.song_usage_detail_form.exec()

    @staticmethod
    def about():
        """
        The plugin about text

        :return: the text to be displayed
        """
        about_text = translate('SongUsagePlugin',
                               '<strong>SongUsage Plugin</strong><br />'
                               'This plugin tracks the usage of songs in services.')
        return about_text

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('SongUsagePlugin', 'SongUsage', 'name singular'),
            'plural': translate('SongUsagePlugin', 'SongUsage', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('SongUsagePlugin', 'SongUsage', 'container title')
        }
