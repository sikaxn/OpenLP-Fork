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
import logging

from PySide6 import QtCore, QtWidgets, QtGui
from sqlalchemy.sql import and_

from openlp.core.common.i18n import translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.path import create_paths
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.songusage.lib.db import SongUsageItem

from .songusagedetaildialog import Ui_SongUsageDetailDialog


log = logging.getLogger(__name__)


class SongUsageDetailForm(QtWidgets.QDialog, Ui_SongUsageDetailDialog, RegistryProperties):
    """
    Class documentation goes here.
    """
    log.info('SongUsage Detail Form Loaded')

    def __init__(self, plugin, parent):
        """
        Initialise the form
        """
        super(SongUsageDetailForm, self).__init__(parent,
                                                  QtCore.Qt.WindowType.WindowSystemMenuHint |
                                                  QtCore.Qt.WindowType.WindowTitleHint |
                                                  QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.plugin = plugin
        self.setup_ui(self)

    def initialise(self):
        """
        We need to set up the screen
        """
        to_date = self.settings.value('songusage/to date')
        if not (isinstance(to_date, QtCore.QDate) and to_date.isValid()):
            to_date = QtCore.QDate.currentDate()
        from_date = self.settings.value('songusage/from date')
        if not (isinstance(from_date, QtCore.QDate) and from_date.isValid()):
            from_date = to_date.addYears(-1)
        self.from_date_calendar.setSelectedDate(from_date)
        self.to_date_calendar.setSelectedDate(to_date)
        self.report_path_edit.path = self.settings.value('songusage/last directory export')

    def on_report_path_edit_path_changed(self, file_path):
        """
        Handle the `pathEditChanged` signal from report_path_edit

        :param pathlib.Path file_path: The new path.
        :rtype: None
        """
        self.settings.setValue('songusage/last directory export', file_path)

    def accept(self):
        """
        Ok was triggered so lets save the data and run the report
        """
        log.debug('accept')
        path = self.report_path_edit.path
        if not path:
            self.main_window.error_message(
                translate('SongUsagePlugin.SongUsageDetailForm', 'Output Path Not Selected'),
                translate('SongUsagePlugin.SongUsageDetailForm', 'You have not set a valid output location for your'
                          ' song usage report.\nPlease select an existing path on your computer.')
            )
            return
        create_paths(path)
        file_name = translate('SongUsagePlugin.SongUsageDetailForm',
                              'usage_detail_{old}_{new}.txt'
                              ).format(old=self.from_date_calendar.selectedDate().toString('ddMMyyyy'),
                                       new=self.to_date_calendar.selectedDate().toString('ddMMyyyy'))
        self.settings.setValue('songusage/from date', self.from_date_calendar.selectedDate())
        self.settings.setValue('songusage/to date', self.to_date_calendar.selectedDate())
        usage = self.plugin.manager.get_all_objects(
            SongUsageItem, and_(SongUsageItem.usagedate >= self.from_date_calendar.selectedDate().toPyDate(),
                                SongUsageItem.usagedate < self.to_date_calendar.selectedDate().toPyDate()),
            [SongUsageItem.usagedate, SongUsageItem.usagetime])
        report_file_name = path / file_name
        try:
            with report_file_name.open('wb') as file_handle:
                for instance in usage:
                    record = ('\"{date}\",\"{time}\",\"{title}\",\"{copyright}\",\"{ccli}\",\"{authors}\",'
                              '\"{name}\",\"{source}\"\n').format(date=instance.usagedate, time=instance.usagetime,
                                                                  title=instance.title, copyright=instance.copyright,
                                                                  ccli=instance.ccl_number, authors=instance.authors,
                                                                  name=instance.plugin_name, source=instance.source)
                    file_handle.write(record.encode('utf-8'))
                self.main_window.information_message(
                    translate('SongUsagePlugin.SongUsageDetailForm', 'Report Creation'),
                    translate('SongUsagePlugin.SongUsageDetailForm',
                              'Report\n{name}\nhas been successfully created.').format(name=report_file_name)
                )
        except OSError as ose:
            log.exception('Failed to write out song usage records')
            critical_error_message_box(translate('SongUsagePlugin.SongUsageDetailForm', 'Report Creation Failed'),
                                       translate('SongUsagePlugin.SongUsageDetailForm',
                                                 'An error occurred while creating the report: {error}'
                                                 ).format(error=ose.strerror))
        self.close()

    def provide_help(self):
        """
        Provide help within the form by opening the appropriate page of the openlp manual in the user's browser
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://manual.openlp.org/song_usage.html"))
