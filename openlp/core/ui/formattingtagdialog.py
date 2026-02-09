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
The UI widgets for the formatting tags window.
"""
from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.lib.ui import create_button_box
from openlp.core.ui.icons import UiIcons


class Ui_FormattingTagDialog(object):
    """
    The UI widgets for the formatting tags window.
    """
    def setup_ui(self, formatting_tag_dialog):
        """
        Set up the UI
        """
        formatting_tag_dialog.setObjectName('formatting_tag_dialog')
        formatting_tag_dialog.setWindowIcon(UiIcons().main_icon)
        formatting_tag_dialog.resize(835, 548)
        self.list_data_grid_layout = QtWidgets.QVBoxLayout(formatting_tag_dialog)
        self.list_data_grid_layout.setContentsMargins(8, 8, 8, 8)
        self.list_data_grid_layout.setObjectName('list_data_grid_layout')
        self.tag_table_widget_read_label = QtWidgets.QLabel()
        self.list_data_grid_layout.addWidget(self.tag_table_widget_read_label)
        self.tag_table_widget_read = QtWidgets.QTableWidget(formatting_tag_dialog)
        self.tag_table_widget_read.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tag_table_widget_read.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tag_table_widget_read.setAlternatingRowColors(True)
        self.tag_table_widget_read.setCornerButtonEnabled(False)
        self.tag_table_widget_read.setObjectName('tag_table_widget_read')
        self.tag_table_widget_read.setColumnCount(4)
        self.tag_table_widget_read.setRowCount(0)
        self.tag_table_widget_read.horizontalHeader().setStretchLastSection(True)
        item = QtWidgets.QTableWidgetItem()
        self.tag_table_widget_read.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tag_table_widget_read.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tag_table_widget_read.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tag_table_widget_read.setHorizontalHeaderItem(3, item)
        self.list_data_grid_layout.addWidget(self.tag_table_widget_read)
        self.tag_table_widget_label = QtWidgets.QLabel()
        self.list_data_grid_layout.addWidget(self.tag_table_widget_label)
        self.tag_table_widget = QtWidgets.QTableWidget(formatting_tag_dialog)
        self.tag_table_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tag_table_widget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.AllEditTriggers)
        self.tag_table_widget.setAlternatingRowColors(True)
        self.tag_table_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tag_table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tag_table_widget.setCornerButtonEnabled(False)
        self.tag_table_widget.setObjectName('tag_table_widget')
        self.tag_table_widget.setColumnCount(5)
        self.tag_table_widget.setRowCount(0)
        self.tag_table_widget.horizontalHeader().setStretchLastSection(True)
        item = QtWidgets.QTableWidgetItem()
        self.tag_table_widget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tag_table_widget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tag_table_widget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tag_table_widget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tag_table_widget.setHorizontalHeaderItem(4, item)
        self.list_data_grid_layout.addWidget(self.tag_table_widget)
        self.edit_button_layout = QtWidgets.QHBoxLayout()
        self.new_button = QtWidgets.QPushButton(formatting_tag_dialog)
        self.new_button.setIcon(UiIcons().new)
        self.new_button.setObjectName('new_button')
        self.edit_button_layout.addWidget(self.new_button)
        self.delete_button = QtWidgets.QPushButton(formatting_tag_dialog)
        self.delete_button.setIcon(UiIcons().delete)
        self.delete_button.setObjectName('delete_button')
        self.edit_button_layout.addWidget(self.delete_button)
        self.edit_button_layout.addStretch()
        self.list_data_grid_layout.addLayout(self.edit_button_layout)
        self.button_box = create_button_box(formatting_tag_dialog, 'button_box', ['cancel', 'save', 'defaults'])
        self.save_button = self.button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Save)
        self.save_button.setObjectName('save_button')
        self.restore_button = self.button_box.button(QtWidgets.QDialogButtonBox.StandardButton.RestoreDefaults)
        self.restore_button.setIcon(UiIcons().undo)
        self.restore_button.setObjectName('restore_button')
        self.list_data_grid_layout.addWidget(self.button_box)
        self.retranslate_ui(formatting_tag_dialog)

    def retranslate_ui(self, formatting_tag_dialog):
        """
        Translate the UI on the fly
        """
        formatting_tag_dialog.setWindowTitle(translate('OpenLP.FormattingTagDialog', 'Configure Formatting Tags'))
        self.delete_button.setText(UiStrings().Delete)
        self.new_button.setText(UiStrings().New)
        self.tag_table_widget_read_label.setText(translate('OpenLP.FormattingTagDialog', 'Default Formatting'))
        self.tag_table_widget_read.horizontalHeaderItem(0).\
            setText(translate('OpenLP.FormattingTagDialog', 'Description'))
        self.tag_table_widget_read.horizontalHeaderItem(1).setText(translate('OpenLP.FormattingTagDialog', 'Tag'))
        self.tag_table_widget_read.horizontalHeaderItem(2).\
            setText(translate('OpenLP.FormattingTagDialog', 'Start HTML'))
        self.tag_table_widget_read.horizontalHeaderItem(3).setText(translate('OpenLP.FormattingTagDialog', 'End HTML'))
        self.tag_table_widget_read.setColumnWidth(0, 120)
        self.tag_table_widget_read.setColumnWidth(1, 80)
        self.tag_table_widget_read.setColumnWidth(2, 330)
        self.tag_table_widget_label.setText(translate('OpenLP.FormattingTagDialog', 'Custom Formatting'))
        self.tag_table_widget.horizontalHeaderItem(0).setText(translate('OpenLP.FormattingTagDialog', 'Description'))
        self.tag_table_widget.horizontalHeaderItem(1).setText(translate('OpenLP.FormattingTagDialog', 'Tag'))
        self.tag_table_widget.horizontalHeaderItem(2).setText(translate('OpenLP.FormattingTagDialog', 'Start HTML'))
        self.tag_table_widget.horizontalHeaderItem(3).setText(translate('OpenLP.FormattingTagDialog', 'End HTML'))
        self.tag_table_widget.horizontalHeaderItem(4).setText(translate('OpenLP.FormattingTagDialog',
                                                                        'Hide content from Live/Preview'))
        self.tag_table_widget.setColumnWidth(0, 80)
        self.tag_table_widget.setColumnWidth(1, 40)
        self.tag_table_widget.setColumnWidth(2, 320)
        self.tag_table_widget.setColumnWidth(3, 150)
