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

from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import create_button_box


class Ui_ChooseGroupDialog(object):
    """
    The UI for the "Choose Image Group" form.
    """
    def setup_ui(self, choose_group_dialog):
        """
        Set up the UI.

        :param choose_group_dialog: The form object (not the class).
        """
        choose_group_dialog.setObjectName('choose_group_dialog')
        choose_group_dialog.resize(399, 119)
        self.choose_group_layout = QtWidgets.QFormLayout(choose_group_dialog)
        self.choose_group_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.choose_group_layout.setContentsMargins(8, 8, 8, 8)
        self.choose_group_layout.setSpacing(8)
        self.choose_group_layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft |
                                                   QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.choose_group_layout.setObjectName('choose_group_layout')
        self.group_question_label = QtWidgets.QLabel(choose_group_dialog)
        self.group_question_label.setWordWrap(True)
        self.group_question_label.setObjectName('group_question_label')
        self.choose_group_layout.setWidget(1, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.group_question_label)
        self.nogroup_radio_button = QtWidgets.QRadioButton(choose_group_dialog)
        self.nogroup_radio_button.setChecked(True)
        self.nogroup_radio_button.setObjectName('nogroup_radio_button')
        self.choose_group_layout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.nogroup_radio_button)
        self.existing_radio_button = QtWidgets.QRadioButton(choose_group_dialog)
        self.existing_radio_button.setChecked(False)
        self.existing_radio_button.setObjectName('existing_radio_button')
        self.choose_group_layout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.existing_radio_button)
        self.group_combobox = QtWidgets.QComboBox(choose_group_dialog)
        self.group_combobox.setObjectName('group_combobox')
        self.group_combobox.activated.connect(self.on_group_combobox_selected)
        self.choose_group_layout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.group_combobox)
        self.new_radio_button = QtWidgets.QRadioButton(choose_group_dialog)
        self.new_radio_button.setChecked(False)
        self.new_radio_button.setObjectName('new_radio_button')
        self.choose_group_layout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.new_radio_button)
        self.new_group_edit = QtWidgets.QLineEdit(choose_group_dialog)
        self.new_group_edit.setObjectName('new_group_edit')
        self.new_group_edit.textEdited.connect(self.on_new_group_edit_changed)
        self.choose_group_layout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.new_group_edit)
        self.group_button_box = create_button_box(choose_group_dialog, 'buttonBox', ['ok'])
        self.choose_group_layout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.group_button_box)

        self.retranslate_ui(choose_group_dialog)
        QtCore.QMetaObject.connectSlotsByName(choose_group_dialog)

    def retranslate_ui(self, choose_group_dialog):
        """
        Translate the UI on the fly.

        :param choose_group_dialog: The form object (not the class).
        """
        choose_group_dialog.setWindowTitle(translate('ImagePlugin.ChooseGroupForm', 'Select Image Group'))
        self.group_question_label.setText(translate('ImagePlugin.ChooseGroupForm', 'Add images to group:'))
        self.nogroup_radio_button.setText(translate('ImagePlugin.ChooseGroupForm', 'No group'))
        self.existing_radio_button.setText(translate('ImagePlugin.ChooseGroupForm', 'Existing group'))
        self.new_radio_button.setText(translate('ImagePlugin.ChooseGroupForm', 'New group'))

    def on_group_combobox_selected(self, index):
        """
        Handles the activated signal from the existing group combobox when the
        user makes a selection

        :param index: position of the selected item in the combobox
        """
        self.existing_radio_button.setChecked(True)
        self.group_combobox.setFocus()

    def on_new_group_edit_changed(self, new_group):
        """
        Handles the textEdited signal from the new group text input field
        when the user enters a new group name

        :param new_group: new text entered by the user
        """
        self.new_radio_button.setChecked(True)
