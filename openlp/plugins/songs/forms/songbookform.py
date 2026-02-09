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
This module contains the song book form
"""

from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.songs.forms.songbookdialog import Ui_SongBookDialog


class SongBookForm(QtWidgets.QDialog, Ui_SongBookDialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(SongBookForm, self).__init__(parent,
                                           QtCore.Qt.WindowType.WindowSystemMenuHint |
                                           QtCore.Qt.WindowType.WindowTitleHint |
                                           QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui(self)

    def exec(self, clear=True):
        """
        Execute the song book form.

        :param clear: Clear the fields on the form before displaying it.
        """
        if clear:
            self.name_edit.clear()
            self.publisher_edit.clear()
        self.name_edit.setFocus()
        return QtWidgets.QDialog.exec(self)

    def accept(self):
        """
        Override the inherited method to check that the name of the book has been typed in.
        """
        if not self.name_edit.text():
            critical_error_message_box(
                message=translate('SongsPlugin.SongBookForm', 'You need to type in a name for the book.'))
            self.name_edit.setFocus()
            return False
        else:
            return QtWidgets.QDialog.accept(self)
