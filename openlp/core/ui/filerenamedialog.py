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
The UI widgets for the rename dialog
"""
from PySide6 import QtCore, QtGui, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import create_button_box
from openlp.core.ui.icons import UiIcons


class Ui_FileRenameDialog(object):
    """
    The UI widgets for the rename dialog
    """
    def setup_ui(self, file_rename_dialog):
        """
        Set up the UI
        """
        file_rename_dialog.setObjectName('file_rename_dialog')
        file_rename_dialog.setWindowIcon(UiIcons().main_icon)
        file_rename_dialog.resize(300, 10)
        self.dialog_layout = QtWidgets.QGridLayout(file_rename_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.file_name_label = QtWidgets.QLabel(file_rename_dialog)
        self.file_name_label.setObjectName('file_name_label')
        self.dialog_layout.addWidget(self.file_name_label, 0, 0)
        self.file_name_edit = QtWidgets.QLineEdit(file_rename_dialog)
        self.file_name_edit.setValidator(
            QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r'[^/\\?*|<>\[\]":+%]+'), self))
        self.file_name_edit.setObjectName('file_name_edit')
        self.dialog_layout.addWidget(self.file_name_edit, 0, 1)
        self.button_box = create_button_box(file_rename_dialog, 'button_box', ['cancel', 'ok'])
        self.dialog_layout.addWidget(self.button_box, 1, 0, 1, 2)
        self.retranslate_ui(file_rename_dialog)
        self.setMaximumHeight(self.sizeHint().height())

    def retranslate_ui(self, file_rename_dialog):
        """
        Translate the UI on the fly.
        """
        self.file_name_label.setText(translate('OpenLP.FileRenameForm', 'New File Name:'))
