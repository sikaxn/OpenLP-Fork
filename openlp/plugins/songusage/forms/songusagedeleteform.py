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

from PySide6 import QtCore, QtWidgets, QtGui

from openlp.core.common.i18n import translate
from openlp.core.common.mixins import RegistryProperties
from openlp.plugins.songusage.forms.songusagedeletedialog import Ui_SongUsageDeleteDialog
from openlp.plugins.songusage.lib.db import SongUsageItem


class SongUsageDeleteForm(QtWidgets.QDialog, Ui_SongUsageDeleteDialog, RegistryProperties):
    """
    Class documentation goes here.
    """
    def __init__(self, manager, parent):
        """
        Constructor
        """
        self.manager = manager
        super(SongUsageDeleteForm, self).__init__(parent,
                                                  QtCore.Qt.WindowType.WindowSystemMenuHint |
                                                  QtCore.Qt.WindowType.WindowTitleHint |
                                                  QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui(self)
        self.button_box.clicked.connect(self.on_button_box_clicked)

    def on_button_box_clicked(self, button):
        """
        The button event has been triggered

        :param button: The button pressed
        """
        if self.button_box.standardButton(button) == QtWidgets.QDialogButtonBox.StandardButton.Ok:
            ret = QtWidgets.QMessageBox.question(self,
                                                 translate('SongUsagePlugin.SongUsageDeleteForm',
                                                           'Delete Selected Song Usage Events?'),
                                                 translate('SongUsagePlugin.SongUsageDeleteForm',
                                                           'Are you sure you want to delete selected Song Usage data?'),
                                                 defaultButton=QtWidgets.QMessageBox.StandardButton.No)
            if ret == QtWidgets.QMessageBox.StandardButton.Yes:
                delete_date = self.delete_calendar.selectedDate().toPyDate()
                self.manager.delete_all_objects(SongUsageItem, SongUsageItem.usagedate <= delete_date)
                self.main_window.information_message(
                    translate('SongUsagePlugin.SongUsageDeleteForm', 'Deletion Successful'),
                    translate('SongUsagePlugin.SongUsageDeleteForm',
                              'All requested data has been deleted successfully.')
                )
                self.accept()
        else:
            self.reject()

    def provide_help(self):
        """
        Provide help within the form by opening the appropriate page of the openlp manual in the user's browser
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://manual.openlp.org/song_usage.html"))
