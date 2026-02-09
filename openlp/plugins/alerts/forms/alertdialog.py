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

from PySide6 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import create_button, create_button_box
from openlp.core.ui.icons import UiIcons


class AlertDialog(object):
    """
    Alert UI Class
    """
    def setup_ui(self, alert_dialog):
        """
        Setup the Alert UI dialog

        :param alert_dialog: The dialog
        """
        alert_dialog.setObjectName('alert_dialog')
        alert_dialog.resize(400, 300)
        alert_dialog.setWindowIcon(UiIcons().main_icon)
        self.alert_dialog_layout = QtWidgets.QGridLayout(alert_dialog)
        self.alert_dialog_layout.setObjectName('alert_dialog_layout')
        self.alert_text_layout = QtWidgets.QFormLayout()
        self.alert_text_layout.setObjectName('alert_text_layout')
        self.alert_entry_label = QtWidgets.QLabel(alert_dialog)
        self.alert_entry_label.setObjectName('alert_entry_label')
        self.alert_text_edit = QtWidgets.QLineEdit(alert_dialog)
        self.alert_text_edit.setObjectName('alert_text_edit')
        self.alert_entry_label.setBuddy(self.alert_text_edit)
        self.alert_text_layout.addRow(self.alert_entry_label, self.alert_text_edit)
        self.alert_parameter = QtWidgets.QLabel(alert_dialog)
        self.alert_parameter.setObjectName('alert_parameter')
        self.parameter_edit = QtWidgets.QLineEdit(alert_dialog)
        self.parameter_edit.setObjectName('parameter_edit')
        self.alert_parameter.setBuddy(self.parameter_edit)
        self.alert_text_layout.addRow(self.alert_parameter, self.parameter_edit)
        self.alert_dialog_layout.addLayout(self.alert_text_layout, 0, 0, 1, 2)
        self.alert_list_widget = QtWidgets.QListWidget(alert_dialog)
        self.alert_list_widget.setAlternatingRowColors(True)
        self.alert_list_widget.setObjectName('alert_list_widget')
        self.alert_dialog_layout.addWidget(self.alert_list_widget, 1, 0)
        self.manage_button_layout = QtWidgets.QVBoxLayout()
        self.manage_button_layout.setObjectName('manage_button_layout')
        self.new_button = QtWidgets.QPushButton(alert_dialog)
        self.new_button.setIcon(UiIcons().new)
        self.new_button.setObjectName('new_button')
        self.manage_button_layout.addWidget(self.new_button)
        self.save_button = QtWidgets.QPushButton(alert_dialog)
        self.save_button.setEnabled(False)
        self.save_button.setIcon(UiIcons().save)
        self.save_button.setObjectName('save_button')
        self.manage_button_layout.addWidget(self.save_button)
        self.delete_button = create_button(alert_dialog, 'delete_button', role='delete', enabled=False,
                                           click=alert_dialog.on_delete_button_clicked)
        self.manage_button_layout.addWidget(self.delete_button)
        self.manage_button_layout.addStretch()
        self.alert_dialog_layout.addLayout(self.manage_button_layout, 1, 1)
        self.display_button = create_button(alert_dialog, 'display_button', icon=UiIcons().live, enabled=False)
        self.display_close_button = create_button(alert_dialog, 'display_close_button', icon=UiIcons().live,
                                                  enabled=False)
        self.button_box = create_button_box(alert_dialog, 'button_box', ['close', 'help'],
                                            [self.display_button, self.display_close_button])
        self.alert_dialog_layout.addWidget(self.button_box, 2, 0, 1, 2)
        self.retranslate_ui(alert_dialog)

    def retranslate_ui(self, alert_dialog):
        """
        Retranslate the UI strings

        :param alert_dialog: The dialog
        """
        alert_dialog.setWindowTitle(translate('AlertsPlugin.AlertForm', 'Alert Message'))
        self.alert_entry_label.setText(translate('AlertsPlugin.AlertForm', 'Alert &text:'))
        self.alert_parameter.setText(translate('AlertsPlugin.AlertForm', '&Parameter:'))
        self.new_button.setText(translate('AlertsPlugin.AlertForm', '&New'))
        self.save_button.setText(translate('AlertsPlugin.AlertForm', '&Save'))
        self.display_button.setText(translate('AlertsPlugin.AlertForm', 'Displ&ay'))
        self.display_close_button.setText(translate('AlertsPlugin.AlertForm', 'Display && Cl&ose'))
