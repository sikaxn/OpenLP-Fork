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

from PySide6 import QtGui, QtWidgets

from openlp.core.ui.icons import UiIcons


class Ui_ConfirmationDialog():
    """
    The UI for the Confirmation dialog.
    """

    def setup_ui(self, confirmation_dialog, title, items, message, width=400, height=600):
        """
        Set up the UI for the confirmation dialog.

        :param confirmation_dialog: The QDialog object to set up.
        :param items:               A list (or other iterable) containing the items
        :param message:             The confirmation message to display
        :param width:               Width of the dialog window
        :param height:              Height of the dialog window

        :return:                    None
        """
        # overall aspects for confirmation dialog
        confirmation_dialog.setObjectName('confirmation_dialog')
        confirmation_dialog.setWindowIcon(UiIcons().main_icon)
        confirmation_dialog.resize(width, height)
        confirmation_dialog.setWindowTitle(title)

        self.confirmation_layout = QtWidgets.QVBoxLayout(confirmation_dialog)
        self.confirmation_layout.setObjectName('confirmation_layout')

        # listview to display the items
        self.listview = QtWidgets.QListView(self)
        self.listview.setObjectName("confirmation listview")
        # make the entries read-only
        self.listview.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.confirmation_layout.addWidget(self.listview)

        # add the items to the listview model
        model = QtGui.QStandardItemModel()
        self.listview.setModel(model)
        for item in items:
            model.appendRow(QtGui.QStandardItem(item))

        # confirmation message and Yes/No buttons
        self.message_and_buttons = QtWidgets.QWidget(confirmation_dialog)
        self.message_and_buttons.setObjectName('message and buttons')
        self.message_and_buttons_layout = QtWidgets.QHBoxLayout(self.message_and_buttons)
        self.message_and_buttons_layout.setObjectName('message and buttons layout')

        self.message_label = QtWidgets.QLabel(message)
        self.message_label.setObjectName('message')
        self.message_label.setWordWrap(True)
        self.message_and_buttons_layout.addWidget(self.message_label)

        button_types = QtWidgets.QDialogButtonBox.StandardButton.Yes | QtWidgets.QDialogButtonBox.StandardButton.No
        self.buttonBox = QtWidgets.QDialogButtonBox(button_types)
        self.buttonBox.setObjectName('buttons')
        self.message_and_buttons_layout.addWidget(self.buttonBox)

        self.confirmation_layout.addWidget(self.message_and_buttons)

        # slot connections
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
