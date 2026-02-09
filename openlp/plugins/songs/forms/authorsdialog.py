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

from PySide6 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import create_button_box
from openlp.core.ui.icons import UiIcons


class Ui_AuthorsDialog(object):
    """
    The :class:`~openlp.plugins.songs.forms.authorsdialog.Ui_AuthorsDialog` class defines the user interface for the
    AuthorsForm dialog.
    """
    def setup_ui(self, authors_dialog):
        """
        Set up the UI for the dialog.
        """
        authors_dialog.setObjectName('authors_dialog')
        authors_dialog.setWindowIcon(UiIcons().main_icon)
        authors_dialog.resize(300, 10)
        authors_dialog.setModal(True)
        self.dialog_layout = QtWidgets.QVBoxLayout(authors_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.author_layout = QtWidgets.QFormLayout()
        self.author_layout.setObjectName('author_layout')
        self.first_name_label = QtWidgets.QLabel(authors_dialog)
        self.first_name_label.setObjectName('first_name_label')
        self.first_name_edit = QtWidgets.QLineEdit(authors_dialog)
        self.first_name_edit.setObjectName('first_name_edit')
        self.first_name_label.setBuddy(self.first_name_edit)
        self.author_layout.addRow(self.first_name_label, self.first_name_edit)
        self.last_name_label = QtWidgets.QLabel(authors_dialog)
        self.last_name_label.setObjectName('last_name_label')
        self.last_name_edit = QtWidgets.QLineEdit(authors_dialog)
        self.last_name_edit.setObjectName('last_name_edit')
        self.last_name_label.setBuddy(self.last_name_edit)
        self.author_layout.addRow(self.last_name_label, self.last_name_edit)
        self.display_label = QtWidgets.QLabel(authors_dialog)
        self.display_label.setObjectName('display_label')
        self.display_edit = QtWidgets.QLineEdit(authors_dialog)
        self.display_edit.setObjectName('display_edit')
        self.display_label.setBuddy(self.display_edit)
        self.author_layout.addRow(self.display_label, self.display_edit)
        self.dialog_layout.addLayout(self.author_layout)
        self.button_box = create_button_box(authors_dialog, 'button_box', ['cancel', 'save'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslate_ui(authors_dialog)
        authors_dialog.setMaximumHeight(authors_dialog.sizeHint().height())

    def retranslate_ui(self, authors_dialog):
        """
        Translate the UI on the fly.
        """
        authors_dialog.setWindowTitle(translate('SongsPlugin.AuthorsForm', 'Author Maintenance'))
        self.display_label.setText(translate('SongsPlugin.AuthorsForm', 'Display name:'))
        self.first_name_label.setText(translate('SongsPlugin.AuthorsForm', 'First name:'))
        self.last_name_label.setText(translate('SongsPlugin.AuthorsForm', 'Last name:'))
