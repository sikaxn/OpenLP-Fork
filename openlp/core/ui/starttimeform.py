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
The actual start time form.
"""
from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.registry import Registry
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.starttimedialog import Ui_StartTimeDialog


class StartTimeForm(QtWidgets.QDialog, Ui_StartTimeDialog, RegistryProperties):
    """
    The start time dialog
    """
    def __init__(self):
        """
        Constructor
        """
        super(StartTimeForm, self).__init__(Registry().get('main_window'),
                                            QtCore.Qt.WindowType.WindowSystemMenuHint |
                                            QtCore.Qt.WindowType.WindowTitleHint |
                                            QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui(self)

    def exec(self):
        """
        Run the Dialog with correct heading.
        """
        hour, minutes, seconds = self._time_split(self.item['service_item'].start_time)
        self.hour_spin_box.setValue(hour)
        self.minute_spin_box.setValue(minutes)
        self.second_spin_box.setValue(seconds)
        hours, minutes, seconds = self._time_split(self.item['service_item'].end_time)
        if hours == 0 and minutes == 0 and seconds == 0:
            hours, minutes, seconds = self._time_split(self.item['service_item'].media_length)
        self.hour_finish_spin_box.setValue(hours)
        self.minute_finish_spin_box.setValue(minutes)
        self.second_finish_spin_box.setValue(seconds)
        self.hour_finish_label.setText('{val:d}{text}'.format(val=hour, text=UiStrings().Hours))
        self.minute_finish_label.setText('{val:d}{text}'.format(val=minutes, text=UiStrings().Minutes))
        self.second_finish_label.setText('{val:d}{text}'.format(val=seconds, text=UiStrings().Seconds))
        return QtWidgets.QDialog.exec(self)

    def accept(self):
        """
        When the dialog succeeds, this is run
        """
        start = self.hour_spin_box.value() * 3600 + self.minute_spin_box.value() * 60 + self.second_spin_box.value()
        end = self.hour_finish_spin_box.value() * 3600 + \
            self.minute_finish_spin_box.value() * 60 + self.second_finish_spin_box.value()
        if end > self.item['service_item'].media_length // 1000:
            critical_error_message_box(title=translate('OpenLP.StartTime_form', 'Time Validation Error'),
                                       message=translate('OpenLP.StartTime_form',
                                                         'Finish time is set after the end of the media item'))
            return
        elif start > end:
            critical_error_message_box(title=translate('OpenLP.StartTime_form', 'Time Validation Error'),
                                       message=translate('OpenLP.StartTime_form',
                                                         'Start time is after the finish time of the media item'))
            return
        self.item['service_item'].start_time = start * 1000
        self.item['service_item'].end_time = end * 1000
        return QtWidgets.QDialog.accept(self)

    def _time_split(self, milliseconds):
        """
        Split time up into hours minutes and seconds from milliseconds
        """
        seconds = milliseconds // 1000
        hours = seconds // 3600
        seconds -= 3600 * hours
        minutes = seconds // 60
        seconds -= 60 * minutes
        return hours, minutes, seconds
