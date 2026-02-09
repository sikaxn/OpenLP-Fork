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
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.edits import PathEdit
from openlp.core.widgets.enums import PathEditType


class Ui_SongUsageDetailDialog(object):
    """
    The Song Usage report details
    """
    def setup_ui(self, song_usage_detail_dialog):
        """
        Set up the UI

        :param song_usage_detail_dialog:
        """
        song_usage_detail_dialog.setObjectName('song_usage_detail_dialog')
        song_usage_detail_dialog.setWindowIcon(UiIcons().main_icon)
        song_usage_detail_dialog.resize(609, 413)
        self.vertical_layout = QtWidgets.QVBoxLayout(song_usage_detail_dialog)
        self.vertical_layout.setSpacing(8)
        self.vertical_layout.setContentsMargins(8, 8, 8, 8)
        self.vertical_layout.setObjectName('vertical_layout')
        self.date_range_group_box = QtWidgets.QGroupBox(song_usage_detail_dialog)
        self.date_range_group_box.setObjectName('date_range_group_box')
        self.date_horizontal_layout = QtWidgets.QHBoxLayout(self.date_range_group_box)
        self.date_horizontal_layout.setSpacing(8)
        self.date_horizontal_layout.setContentsMargins(8, 8, 8, 8)
        self.date_horizontal_layout.setObjectName('date_horizontal_layout')
        self.from_date_calendar = QtWidgets.QCalendarWidget(self.date_range_group_box)
        self.from_date_calendar.setObjectName('from_date_calendar')
        self.date_horizontal_layout.addWidget(self.from_date_calendar)
        self.to_label = QtWidgets.QLabel(self.date_range_group_box)
        self.to_label.setScaledContents(False)
        self.to_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.to_label.setObjectName('to_label')
        self.date_horizontal_layout.addWidget(self.to_label)
        self.to_date_calendar = QtWidgets.QCalendarWidget(self.date_range_group_box)
        self.to_date_calendar.setObjectName('to_date_calendar')
        self.date_horizontal_layout.addWidget(self.to_date_calendar)
        self.vertical_layout.addWidget(self.date_range_group_box)
        self.file_group_box = QtWidgets.QGroupBox(self.date_range_group_box)
        self.file_group_box.setObjectName('file_group_box')
        self.file_horizontal_layout = QtWidgets.QHBoxLayout(self.file_group_box)
        self.file_horizontal_layout.setSpacing(8)
        self.file_horizontal_layout.setContentsMargins(8, 8, 8, 8)
        self.file_horizontal_layout.setObjectName('file_horizontal_layout')
        self.report_path_edit = PathEdit(self.file_group_box, path_type=PathEditType.Directories, show_revert=False)
        self.file_horizontal_layout.addWidget(self.report_path_edit)
        self.vertical_layout.addWidget(self.file_group_box)
        self.button_box = create_button_box(song_usage_detail_dialog, 'button_box', ['cancel', 'ok', 'help'])
        self.vertical_layout.addWidget(self.button_box)
        self.retranslate_ui(song_usage_detail_dialog)
        self.report_path_edit.pathChanged.connect(song_usage_detail_dialog.on_report_path_edit_path_changed)

    def retranslate_ui(self, song_usage_detail_dialog):
        """
        Retranslate the UI

        :param song_usage_detail_dialog:
        """
        song_usage_detail_dialog.setWindowTitle(
            translate('SongUsagePlugin.SongUsageDetailForm', 'Song Usage Extraction'))
        self.date_range_group_box.setTitle(translate('SongUsagePlugin.SongUsageDetailForm', 'Select Date Range'))
        self.to_label.setText(translate('SongUsagePlugin.SongUsageDetailForm', 'to'))
        self.file_group_box.setTitle(translate('SongUsagePlugin.SongUsageDetailForm', 'Report Location'))
