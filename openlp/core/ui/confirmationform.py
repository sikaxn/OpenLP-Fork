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
A general-purpose confirmation form. This can be used to obtain confirmation
that the user wants to delete a list of items, for example.
It is implemented as a QDialog containing:
- a QListView to display the list of items (eg the items to be deleted)
- a message which asks the user for confirmation
- Yes and No buttons, with Yes being the default
After instantiating a ConfirmationForm object the calling code must call exec() on the instance.
This runs the Qt dialog, which returns the usual 0 (for No) or 1 (for Yes)
"""
from PySide6 import QtCore, QtWidgets

from openlp.core.ui.confirmationdialog import Ui_ConfirmationDialog


class ConfirmationForm(QtWidgets.QDialog, Ui_ConfirmationDialog):
    """
    The Confirmation form
    """

    def __init__(self, parent, title, items, message, width=400, height=600):
        """
        :param parent:   The parent QWidget
        :param title:    The title to be applied to the QDialog window
        :param items:    A list (or other iterable) of Strings for the items
        :param message:  The confirmation message to display
        :param width:    Width of the dialog window
        :param height:   Height of the dialog window
        """
        super(ConfirmationForm, self).__init__(parent,
                                               QtCore.Qt.WindowType.WindowSystemMenuHint |
                                               QtCore.Qt.WindowType.WindowTitleHint |
                                               QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui(self, title, items, message, width, height)
