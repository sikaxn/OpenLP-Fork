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
The UI widgets for the time dialog
"""
from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.lib.ui import create_button_box
from openlp.core.ui.icons import UiIcons


class Ui_StartTimeDialog(object):
    """
    The UI widgets for the time dialog
    """
    def setup_ui(self, StartTimeDialog):
        """
        Set up the UI
        """
        StartTimeDialog.setObjectName('StartTimeDialog')
        StartTimeDialog.setWindowIcon(UiIcons().main_icon)
        StartTimeDialog.resize(350, 10)
        self.dialog_layout = QtWidgets.QGridLayout(StartTimeDialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.start_label = QtWidgets.QLabel(StartTimeDialog)
        self.start_label.setObjectName('start_label')
        self.start_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.dialog_layout.addWidget(self.start_label, 0, 1, 1, 1)
        self.finish_label = QtWidgets.QLabel(StartTimeDialog)
        self.finish_label.setObjectName('finish_label')
        self.finish_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.dialog_layout.addWidget(self.finish_label, 0, 2, 1, 1)
        self.length_label = QtWidgets.QLabel(StartTimeDialog)
        self.length_label.setObjectName('start_label')
        self.length_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.dialog_layout.addWidget(self.length_label, 0, 3, 1, 1)
        self.hour_label = QtWidgets.QLabel(StartTimeDialog)
        self.hour_label.setObjectName('hour_label')
        self.dialog_layout.addWidget(self.hour_label, 1, 0, 1, 1)
        self.hour_spin_box = QtWidgets.QSpinBox(StartTimeDialog)
        self.hour_spin_box.setObjectName('hour_spin_box')
        self.hour_spin_box.setMinimum(0)
        self.hour_spin_box.setMaximum(4)
        self.dialog_layout.addWidget(self.hour_spin_box, 1, 1, 1, 1)
        self.hour_finish_spin_box = QtWidgets.QSpinBox(StartTimeDialog)
        self.hour_finish_spin_box.setObjectName('hour_finish_spin_box')
        self.hour_finish_spin_box.setMinimum(0)
        self.hour_finish_spin_box.setMaximum(4)
        self.dialog_layout.addWidget(self.hour_finish_spin_box, 1, 2, 1, 1)
        self.hour_finish_label = QtWidgets.QLabel(StartTimeDialog)
        self.hour_finish_label.setObjectName('hour_label')
        self.hour_finish_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.dialog_layout.addWidget(self.hour_finish_label, 1, 3, 1, 1)
        self.minute_label = QtWidgets.QLabel(StartTimeDialog)
        self.minute_label.setObjectName('minute_label')
        self.dialog_layout.addWidget(self.minute_label, 2, 0, 1, 1)
        self.minute_spin_box = QtWidgets.QSpinBox(StartTimeDialog)
        self.minute_spin_box.setObjectName('minute_spin_box')
        self.minute_spin_box.setMinimum(0)
        self.minute_spin_box.setMaximum(59)
        self.dialog_layout.addWidget(self.minute_spin_box, 2, 1, 1, 1)
        self.minute_finish_spin_box = QtWidgets.QSpinBox(StartTimeDialog)
        self.minute_finish_spin_box.setObjectName('minute_finish_spin_box')
        self.minute_finish_spin_box.setMinimum(0)
        self.minute_finish_spin_box.setMaximum(59)
        self.dialog_layout.addWidget(self.minute_finish_spin_box, 2, 2, 1, 1)
        self.minute_finish_label = QtWidgets.QLabel(StartTimeDialog)
        self.minute_finish_label.setObjectName('minute_label')
        self.minute_finish_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.dialog_layout.addWidget(self.minute_finish_label, 2, 3, 1, 1)
        self.second_label = QtWidgets.QLabel(StartTimeDialog)
        self.second_label.setObjectName('second_label')
        self.dialog_layout.addWidget(self.second_label, 3, 0, 1, 1)
        self.second_spin_box = QtWidgets.QSpinBox(StartTimeDialog)
        self.second_spin_box.setObjectName('second_spin_box')
        self.second_spin_box.setMinimum(0)
        self.second_spin_box.setMaximum(59)
        self.second_finish_spin_box = QtWidgets.QSpinBox(StartTimeDialog)
        self.second_finish_spin_box.setObjectName('second_finish_spin_box')
        self.second_finish_spin_box.setMinimum(0)
        self.second_finish_spin_box.setMaximum(59)
        self.dialog_layout.addWidget(self.second_finish_spin_box, 3, 2, 1, 1)
        self.second_finish_label = QtWidgets.QLabel(StartTimeDialog)
        self.second_finish_label.setObjectName('second_label')
        self.second_finish_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.dialog_layout.addWidget(self.second_finish_label, 3, 3, 1, 1)
        self.dialog_layout.addWidget(self.second_spin_box, 3, 1, 1, 1)
        self.button_box = create_button_box(StartTimeDialog, 'button_box', ['cancel', 'ok'])
        self.dialog_layout.addWidget(self.button_box, 5, 2, 1, 2)
        self.retranslate_ui(StartTimeDialog)
        self.setMaximumHeight(self.sizeHint().height())

    def retranslate_ui(self, StartTimeDialog):
        """
        Update the translations on the fly
        """
        self.setWindowTitle(translate('OpenLP.StartTime_form', 'Item Start and Finish Time'))
        self.hour_spin_box.setSuffix(UiStrings().Hours)
        self.minute_spin_box.setSuffix(UiStrings().Minutes)
        self.second_spin_box.setSuffix(UiStrings().Seconds)
        self.hour_finish_spin_box.setSuffix(UiStrings().Hours)
        self.minute_finish_spin_box.setSuffix(UiStrings().Minutes)
        self.second_finish_spin_box.setSuffix(UiStrings().Seconds)
        self.hour_label.setText(translate('OpenLP.StartTime_form', 'Hours:'))
        self.minute_label.setText(translate('OpenLP.StartTime_form', 'Minutes:'))
        self.second_label.setText(translate('OpenLP.StartTime_form', 'Seconds:'))
        self.start_label.setText(translate('OpenLP.StartTime_form', 'Start'))
        self.finish_label.setText(translate('OpenLP.StartTime_form', 'Finish'))
        self.length_label.setText(translate('OpenLP.StartTime_form', 'Length'))
