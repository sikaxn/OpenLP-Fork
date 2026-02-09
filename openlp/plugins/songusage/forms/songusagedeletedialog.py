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


class Ui_SongUsageDeleteDialog(object):
    """
    The Song Usage delete dialog
    """
    def setup_ui(self, song_usage_delete_dialog):
        """
        Setup the UI

        :param song_usage_delete_dialog:
        """
        song_usage_delete_dialog.setObjectName('song_usage_delete_dialog')
        song_usage_delete_dialog.setWindowIcon(UiIcons().main_icon)
        song_usage_delete_dialog.resize(291, 243)
        self.vertical_layout = QtWidgets.QVBoxLayout(song_usage_delete_dialog)
        self.vertical_layout.setSpacing(8)
        self.vertical_layout.setContentsMargins(8, 8, 8, 8)
        self.vertical_layout.setObjectName('vertical_layout')
        self.delete_label = QtWidgets.QLabel(song_usage_delete_dialog)
        self.delete_label.setObjectName('delete_label')
        self.vertical_layout.addWidget(self.delete_label)
        self.delete_calendar = QtWidgets.QCalendarWidget(song_usage_delete_dialog)
        self.delete_calendar.setFirstDayOfWeek(QtCore.Qt.DayOfWeek.Sunday)
        self.delete_calendar.setGridVisible(True)
        self.delete_calendar.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.delete_calendar.setObjectName('delete_calendar')
        self.vertical_layout.addWidget(self.delete_calendar)
        self.button_box = create_button_box(song_usage_delete_dialog, 'button_box', ['cancel', 'ok', 'help'])
        self.vertical_layout.addWidget(self.button_box)
        self.retranslate_ui(song_usage_delete_dialog)

    def retranslate_ui(self, song_usage_delete_dialog):
        """
        Retranslate the strings
        :param song_usage_delete_dialog:
        """
        song_usage_delete_dialog.setWindowTitle(
            translate('SongUsagePlugin.SongUsageDeleteForm', 'Delete Song Usage Data'))
        self.delete_label.setText(
            translate('SongUsagePlugin.SongUsageDeleteForm', 'Select the date up to which the song usage data '
                      'should be deleted. \nAll data recorded before this date will be permanently deleted.'))
