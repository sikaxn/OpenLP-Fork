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
The UI widgets of the settings dialog.
"""
from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import create_button_box
from openlp.core.ui.icons import UiIcons


class Ui_SettingsDialog(object):
    """
    The UI widgets of the settings dialog.
    """
    def setup_ui(self, settings_dialog):
        """
        Set up the UI
        """
        settings_dialog.setObjectName('settings_dialog')
        settings_dialog.setWindowIcon(UiIcons().main_icon)
        settings_dialog.resize(900, 500)
        self.dialog_layout = QtWidgets.QGridLayout(settings_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.dialog_layout.setContentsMargins(8, 8, 8, 8)
        self.setting_list_widget = QtWidgets.QListWidget(settings_dialog)
        self.setting_list_widget.setUniformItemSizes(True)
        self.setting_list_widget.setMinimumSize(QtCore.QSize(150, 0))
        self.setting_list_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setting_list_widget.setObjectName('setting_list_widget')
        self.dialog_layout.addWidget(self.setting_list_widget, 0, 0, 1, 1)
        self.stacked_layout = QtWidgets.QStackedLayout()
        self.stacked_layout.setObjectName('stacked_layout')
        self.dialog_layout.addLayout(self.stacked_layout, 0, 1, 1, 1)
        self.button_box = create_button_box(settings_dialog, 'button_box', ['cancel', 'ok', 'help'])
        self.dialog_layout.addWidget(self.button_box, 1, 1, 1, 1)
        self.retranslate_ui(settings_dialog)

    def retranslate_ui(self, settings_dialog):
        """
        Translate the UI on the fly
        """
        settings_dialog.setWindowTitle(translate('OpenLP.SettingsForm', 'Configure OpenLP'))
