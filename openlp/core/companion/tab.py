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
The :mod:`openlp.core.companion.tab` module provides Companion settings in Configure OpenLP.
"""

from PySide6 import QtCore, QtWidgets

from openlp.core.common import get_network_interfaces
from openlp.core.common.i18n import translate
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.ui.icons import UiIcons


class CompanionTab(SettingsTab):
    """
    OpenLP Settings -> Companion settings.
    """
    def __init__(self, parent):
        self.icon_path = UiIcons().remote
        companion_translated = translate('OpenLP.CompanionTab', 'Companion')
        super(CompanionTab, self).__init__(parent, 'Companion', companion_translated)

    def setup_ui(self):
        self.setObjectName('CompanionTab')
        super(CompanionTab, self).setup_ui()
        self.info_group_box = QtWidgets.QGroupBox(self.left_column)
        self.info_group_box.setObjectName('info_group_box')
        self.info_layout = QtWidgets.QVBoxLayout(self.info_group_box)
        self.info_layout.setObjectName('info_layout')
        self.info_label = QtWidgets.QLabel(self.info_group_box)
        self.info_label.setWordWrap(True)
        self.info_label.setObjectName('info_label')
        self.info_layout.addWidget(self.info_label)
        self.info_link_label = QtWidgets.QLabel(self.info_group_box)
        self.info_link_label.setOpenExternalLinks(True)
        self.info_link_label.setTextInteractionFlags(
            self.info_link_label.textInteractionFlags() | QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.info_link_label.setObjectName('info_link_label')
        self.info_layout.addWidget(self.info_link_label)
        self.api_link_label = QtWidgets.QLabel(self.info_group_box)
        self.api_link_label.setObjectName('api_link_label')
        self.info_layout.addWidget(self.api_link_label)
        self.api_link_value = QtWidgets.QLabel(self.info_group_box)
        self.api_link_value.setObjectName('api_link_value')
        self.api_link_value.setOpenExternalLinks(True)
        self.info_layout.addWidget(self.api_link_value)
        self.left_layout.addWidget(self.info_group_box)
        self.connection_group_box = QtWidgets.QGroupBox(self.left_column)
        self.connection_group_box.setObjectName('connection_group_box')
        self.connection_layout = QtWidgets.QFormLayout(self.connection_group_box)
        self.connection_layout.setObjectName('connection_layout')
        self.auto_connect_default_checkbox = QtWidgets.QCheckBox(self.connection_group_box)
        self.auto_connect_default_checkbox.setObjectName('auto_connect_default_checkbox')
        self.connection_layout.addRow(self.auto_connect_default_checkbox)
        self.first_slide_safety_checkbox = QtWidgets.QCheckBox(self.connection_group_box)
        self.first_slide_safety_checkbox.setObjectName('first_slide_safety_checkbox')
        self.connection_layout.addRow(self.first_slide_safety_checkbox)
        self.allow_autodelete_checkbox = QtWidgets.QCheckBox(self.connection_group_box)
        self.allow_autodelete_checkbox.setObjectName('allow_autodelete_checkbox')
        self.connection_layout.addRow(self.allow_autodelete_checkbox)
        self.autotrigger_open_mode_label = QtWidgets.QLabel(self.connection_group_box)
        self.autotrigger_open_mode_label.setObjectName('autotrigger_open_mode_label')
        self.autotrigger_open_mode_combo = QtWidgets.QComboBox(self.connection_group_box)
        self.autotrigger_open_mode_combo.setObjectName('autotrigger_open_mode_combo')
        self.autotrigger_open_mode_combo.addItem('', 'last')
        self.autotrigger_open_mode_combo.addItem('', 'on')
        self.autotrigger_open_mode_combo.addItem('', 'off')
        self.connection_layout.addRow(self.autotrigger_open_mode_label, self.autotrigger_open_mode_combo)
        self.left_layout.addWidget(self.connection_group_box)
        self.left_layout.addStretch()

    def retranslate_ui(self):
        self.tab_title_visible = translate('OpenLP.CompanionTab', 'Companion')
        self.info_group_box.setTitle(translate('OpenLP.CompanionTab', 'About Bitfocus Companion'))
        self.info_label.setText(
            translate('OpenLP.CompanionTab',
                      'Use Bitfocus Companion to automate external devices and actions from OpenLP triggers.'))
        self.info_link_label.setText(
            translate('OpenLP.CompanionTab',
                      '<a href="https://bitfocus.io/companion">Download Bitfocus Companion</a>'))
        self.api_link_label.setText(translate('OpenLP.CompanionTab', 'OpenLP Companion API endpoint:'))
        self.connection_group_box.setTitle(translate('OpenLP.CompanionTab', 'Connection Options'))
        self.auto_connect_default_checkbox.setText(
            translate('OpenLP.CompanionTab', 'Auto connect default companion on file open'))
        self.first_slide_safety_checkbox.setText(
            translate('OpenLP.CompanionTab',
                      'First slide safety (do not auto-trigger first slide when selecting a new service item)'))
        self.allow_autodelete_checkbox.setText(
            translate('OpenLP.CompanionTab',
                      'Allow auto-delete of triggers when linked service items are deleted'))
        self.autotrigger_open_mode_label.setText(
            translate('OpenLP.CompanionTab', 'Auto trigger on file open:'))
        self.autotrigger_open_mode_combo.setItemText(
            0, translate('OpenLP.CompanionTab', 'Use last setting'))
        self.autotrigger_open_mode_combo.setItemText(
            1, translate('OpenLP.CompanionTab', 'Always ON'))
        self.autotrigger_open_mode_combo.setItemText(
            2, translate('OpenLP.CompanionTab', 'Always OFF'))

    def load(self):
        auto_connect = self.settings.value('companion/auto connect default on file open')
        self.auto_connect_default_checkbox.setChecked(
            self._to_bool(auto_connect, default=True))
        self.first_slide_safety_checkbox.setChecked(
            self._to_bool(self.settings.value('companion/first slide safety'), default=False))
        self.allow_autodelete_checkbox.setChecked(
            self._to_bool(self.settings.value('companion/allow autotrigger auto delete'), default=False))
        mode = str(self.settings.value('companion/autotrigger on file open mode') or 'last').lower()
        index = self.autotrigger_open_mode_combo.findData(mode)
        if index < 0:
            index = self.autotrigger_open_mode_combo.findData('last')
        if index >= 0:
            self.autotrigger_open_mode_combo.setCurrentIndex(index)
        self.set_companion_api_url()

    def save(self):
        self.settings.setValue('companion/auto connect default on file open',
                               self.auto_connect_default_checkbox.isChecked())
        self.settings.setValue('companion/first slide safety',
                               self.first_slide_safety_checkbox.isChecked())
        self.settings.setValue('companion/allow autotrigger auto delete',
                               self.allow_autodelete_checkbox.isChecked())
        self.settings.setValue('companion/autotrigger on file open mode',
                               self.autotrigger_open_mode_combo.currentData())

    @staticmethod
    def _get_ip_address(ip_address):
        if ip_address == '0.0.0.0':
            for _, interface in get_network_interfaces().items():
                ip_address = interface['ip']
                break
        return ip_address

    def set_companion_api_url(self):
        ip_address = self._get_ip_address(self.settings.value('api/ip address'))
        port = self.settings.value('api/port')
        if not ip_address:
            ip_address = '127.0.0.1'
        url = f'http://{ip_address}:{port}/api/v2/controller/companion'
        self.api_link_value.setText(f'<a href="{url}">{url}</a>')
    @staticmethod
    def _to_bool(value, default=False):
        if value is None:
            return default
        if isinstance(value, str):
            return value.strip().lower() in ('1', 'true', 'yes', 'on')
        return bool(value)
