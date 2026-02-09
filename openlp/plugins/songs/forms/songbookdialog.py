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


class Ui_SongBookDialog(object):
    """
    The user interface for the Songbook dialog.
    """
    def setup_ui(self, song_book_dialog):
        """
        Set up the user interface.
        """
        song_book_dialog.setObjectName('song_book_dialog')
        song_book_dialog.setWindowIcon(UiIcons().main_icon)
        song_book_dialog.resize(300, 10)
        self.dialog_layout = QtWidgets.QVBoxLayout(song_book_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.book_layout = QtWidgets.QFormLayout()
        self.book_layout.setObjectName('book_layout')
        self.name_label = QtWidgets.QLabel(song_book_dialog)
        self.name_label.setObjectName('name_label')
        self.name_edit = QtWidgets.QLineEdit(song_book_dialog)
        self.name_edit.setObjectName('name_edit')
        self.name_label.setBuddy(self.name_edit)
        self.book_layout.addRow(self.name_label, self.name_edit)
        self.publisher_label = QtWidgets.QLabel(song_book_dialog)
        self.publisher_label.setObjectName('publisher_label')
        self.publisher_edit = QtWidgets.QLineEdit(song_book_dialog)
        self.publisher_edit.setObjectName('publisher_edit')
        self.publisher_label.setBuddy(self.publisher_edit)
        self.book_layout.addRow(self.publisher_label, self.publisher_edit)
        self.dialog_layout.addLayout(self.book_layout)
        self.button_box = create_button_box(song_book_dialog, 'button_box', ['cancel', 'save'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslate_ui(song_book_dialog)
        song_book_dialog.setMaximumHeight(song_book_dialog.sizeHint().height())

    def retranslate_ui(self, song_book_dialog):
        """
        Translate the UI on the fly.
        """
        song_book_dialog.setWindowTitle(translate('SongsPlugin.SongBookForm', 'Songbook Maintenance'))
        self.name_label.setText(translate('SongsPlugin.SongBookForm', '&Name:'))
        self.publisher_label.setText(translate('SongsPlugin.SongBookForm', '&Publisher:'))
