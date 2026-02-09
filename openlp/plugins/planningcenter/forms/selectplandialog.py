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
The :mod:`~openlp.plugins.planningcenter.forms.selectplandialog` module contains the user interface code for the dialog
"""
from PySide6 import QtWidgets

from openlp.core.common.i18n import translate


class Ui_SelectPlanDialog(object):
    """
    The actual Qt components that make up the dialog.
    """
    def setup_ui(self, planningcenter_dialog):
        planningcenter_dialog.setObjectName('planningcenter_dialog')
        planningcenter_dialog.resize(400, 280)
        self.planningcenter_layout = QtWidgets.QFormLayout(planningcenter_dialog)
        self.planningcenter_layout.setContentsMargins(50, 50, 50, 50)
        self.planningcenter_layout.setSpacing(8)
        self.planningcenter_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        # Service Type GUI Elements -- service_type combo_box
        self.service_type_label = QtWidgets.QLabel(planningcenter_dialog)
        self.service_type_combo_box = QtWidgets.QComboBox(planningcenter_dialog)
        self.planningcenter_layout.addRow(self.service_type_label, self.service_type_combo_box)
        # Plan Selection GUI Elements
        self.plan_selection_label = QtWidgets.QLabel(planningcenter_dialog)
        self.plan_selection_combo_box = QtWidgets.QComboBox(planningcenter_dialog)
        self.planningcenter_layout.addRow(self.plan_selection_label, self.plan_selection_combo_box)
        # Theme List for Songs and Custom Slides
        self.song_theme_selection_label = QtWidgets.QLabel(planningcenter_dialog)
        self.song_theme_selection_combo_box = QtWidgets.QComboBox(planningcenter_dialog)
        self.planningcenter_layout.addRow(self.song_theme_selection_label, self.song_theme_selection_combo_box)
        self.slide_theme_selection_label = QtWidgets.QLabel(planningcenter_dialog)
        self.slide_theme_selection_combo_box = QtWidgets.QComboBox(planningcenter_dialog)
        self.planningcenter_layout.addRow(self.slide_theme_selection_label, self.slide_theme_selection_combo_box)
        # Import Button
        self.button_layout = QtWidgets.QDialogButtonBox(planningcenter_dialog)
        self.import_as_new_button = QtWidgets.QPushButton(planningcenter_dialog)
        self.button_layout.addButton(self.import_as_new_button, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.update_existing_button = QtWidgets.QPushButton(planningcenter_dialog)
        self.button_layout.addButton(self.update_existing_button, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.edit_auth_button = QtWidgets.QPushButton(planningcenter_dialog)
        self.button_layout.addButton(self.edit_auth_button, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.planningcenter_layout.addRow(self.button_layout)
        self.retranslate_ui(planningcenter_dialog)

    def retranslate_ui(self, planningcenter_dialog):
        """
        Translate the GUI.
        """
        planningcenter_dialog.setWindowTitle(translate('PlanningCenterPlugin.PlanningCenterForm',
                                                       'Planning Center Online Service Importer'))
        self.service_type_label.setText(translate('PlanningCenterPlugin.PlanningCenterForm', 'Service Type'))
        self.plan_selection_label.setText(translate('PlanningCenterPlugin.PlanningCenterForm', 'Select Plan'))
        self.import_as_new_button.setText(translate('PlanningCenterPlugin.PlanningCenterForm', 'Import New'))
        self.import_as_new_button.setToolTip(translate('PlanningCenterPlugin.PlanningCenterForm',
                                                       'Import As New Service'))
        self.update_existing_button.setText(translate('PlanningCenterPlugin.PlanningCenterForm', 'Refresh Service'))
        self.update_existing_button.setToolTip(translate('PlanningCenterPlugin.PlanningCenterForm',
                                                         'Refresh Existing Service from Planning Center. '
                                                         'This will update song lyrics or item orders that '
                                                         'have changed'))
        self.edit_auth_button.setText(translate('PlanningCenterPlugin.PlanningCenterForm', 'Edit Authentication'))
        self.edit_auth_button.setToolTip(translate('PlanningCenterPlugin.PlanningCenterForm', 'Edit the Application '
                                                   'ID and Secret Code to login to Planning Center Online'))
        self.song_theme_selection_label.setText(translate('PlanningCenterPlugin.PlanningCenterForm', 'Song Theme'))
        self.slide_theme_selection_label.setText(translate('PlanningCenterPlugin.PlanningCenterForm', 'Slide Theme'))
