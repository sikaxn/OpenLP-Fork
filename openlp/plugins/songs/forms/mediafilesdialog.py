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


class Ui_MediaFilesDialog(object):
    """
    The user interface for the media files dialog.
    """
    def setup_ui(self, media_files_dialog):
        """
        Set up the user interface.
        """
        media_files_dialog.setObjectName('media_files_dialog')
        media_files_dialog.setWindowIcon(UiIcons().main_icon)
        media_files_dialog.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        media_files_dialog.resize(400, 300)
        media_files_dialog.setModal(True)
        self.files_vertical_layout = QtWidgets.QVBoxLayout(media_files_dialog)
        self.files_vertical_layout.setSpacing(8)
        self.files_vertical_layout.setContentsMargins(8, 8, 8, 8)
        self.files_vertical_layout.setObjectName('files_vertical_layout')
        self.select_label = QtWidgets.QLabel(media_files_dialog)
        self.select_label.setWordWrap(True)
        self.select_label.setObjectName('select_label')
        self.files_vertical_layout.addWidget(self.select_label)
        self.file_list_widget = QtWidgets.QListWidget(media_files_dialog)
        self.file_list_widget.setAlternatingRowColors(True)
        self.file_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list_widget.setObjectName('file_list_widget')
        self.files_vertical_layout.addWidget(self.file_list_widget)
        self.button_box = create_button_box(media_files_dialog, 'button_box', ['cancel', 'ok'])
        self.files_vertical_layout.addWidget(self.button_box)
        self.retranslate_ui(media_files_dialog)

    def retranslate_ui(self, media_files_dialog):
        """
        Translate the UI on the fly.

        :param media_files_dialog:
        """
        media_files_dialog.setWindowTitle(translate('SongsPlugin.MediaFilesForm', 'Select Media File(s)'))
        self.select_label.setText(translate('SongsPlugin.MediaFilesForm', 'Select one or more audio files from the '
                                                                          'list below, and click OK to import them '
                                                                          'into this song.'))
