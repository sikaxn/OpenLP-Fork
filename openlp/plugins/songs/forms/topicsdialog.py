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
from openlp.core.lib.ui import create_button_box
from openlp.core.ui.icons import UiIcons


class Ui_TopicsDialog(object):
    """
    The user interface for the topics dialog.
    """
    def setup_ui(self, topics_dialog):
        """
        Set up the user interface for the topics dialog.
        """
        topics_dialog.setObjectName('topics_dialog')
        topics_dialog.setWindowIcon(UiIcons().main_icon)
        topics_dialog.resize(300, 10)
        self.dialog_layout = QtWidgets.QVBoxLayout(topics_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.name_layout = QtWidgets.QFormLayout()
        self.name_layout.setObjectName('name_layout')
        self.name_label = QtWidgets.QLabel(topics_dialog)
        self.name_label.setObjectName('name_label')
        self.name_edit = QtWidgets.QLineEdit(topics_dialog)
        self.name_edit.setObjectName('name_edit')
        self.name_label.setBuddy(self.name_edit)
        self.name_layout.addRow(self.name_label, self.name_edit)
        self.dialog_layout.addLayout(self.name_layout)
        self.button_box = create_button_box(topics_dialog, 'button_box', ['cancel', 'save'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslate_ui(topics_dialog)
        topics_dialog.setMaximumHeight(topics_dialog.sizeHint().height())

    def retranslate_ui(self, topics_dialog):
        """
        Translate the UI on the fly.
        """
        topics_dialog.setWindowTitle(translate('SongsPlugin.TopicsForm', 'Topic Maintenance'))
        self.name_label.setText(translate('SongsPlugin.TopicsForm', 'Topic name:'))
