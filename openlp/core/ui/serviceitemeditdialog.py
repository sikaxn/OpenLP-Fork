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
The UI widgets for the service item edit dialog
"""
from PySide6 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import create_button, create_button_box
from openlp.core.ui.icons import UiIcons


class Ui_ServiceItemEditDialog(object):
    """
    The UI widgets for the service item edit dialog
    """
    def setup_ui(self, serviceItemEditDialog):
        """
        Set up the UI
        """
        serviceItemEditDialog.setObjectName('serviceItemEditDialog')
        serviceItemEditDialog.setWindowIcon(UiIcons().main_icon)
        self.dialog_layout = QtWidgets.QGridLayout(serviceItemEditDialog)
        self.dialog_layout.setContentsMargins(8, 8, 8, 8)
        self.dialog_layout.setSpacing(8)
        self.dialog_layout.setObjectName('dialog_layout')
        self.list_widget = QtWidgets.QListWidget(serviceItemEditDialog)
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setObjectName('list_widget')
        self.dialog_layout.addWidget(self.list_widget, 0, 0)
        self.button_layout = QtWidgets.QVBoxLayout()
        self.button_layout.setObjectName('button_layout')
        self.delete_button = create_button(serviceItemEditDialog, 'deleteButton', role='delete',
                                           click=serviceItemEditDialog.on_delete_button_clicked)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addStretch()
        self.up_button = create_button(serviceItemEditDialog, 'up_button', role='up',
                                       click=serviceItemEditDialog.on_up_button_clicked)
        self.down_button = create_button(serviceItemEditDialog, 'down_button', role='down',
                                         click=serviceItemEditDialog.on_down_button_clicked)
        self.button_layout.addWidget(self.up_button)
        self.button_layout.addWidget(self.down_button)
        self.dialog_layout.addLayout(self.button_layout, 0, 1)
        self.button_box = create_button_box(serviceItemEditDialog, 'button_box', ['cancel', 'save'])
        self.dialog_layout.addWidget(self.button_box, 1, 0, 1, 2)
        self.retranslate_ui(serviceItemEditDialog)

    def retranslate_ui(self, serviceItemEditDialog):
        """
        Translate the UI on the fly
        """
        serviceItemEditDialog.setWindowTitle(translate('OpenLP.ServiceItemEditForm', 'Reorder Service Item'))
