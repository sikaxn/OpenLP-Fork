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
The :mod:`~openlp.plugins.songs.forms.songselectdialog` module contains the user interface code for the dialog
"""

from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.ui import SingleColumnTableWidget
from openlp.core.ui.icons import UiIcons
from openlp.plugins.songs.forms.webengine import WebEngineView


class Ui_SongSelectDialog(object):
    """
    The actual Qt components that make up the dialog.
    """
    def setup_ui(self, songselect_dialog):
        songselect_dialog.setObjectName('songselect_dialog')
        songselect_dialog.resize(800, 600)
        self.songselect_layout = QtWidgets.QVBoxLayout(songselect_dialog)
        self.songselect_layout.setSpacing(8)
        self.songselect_layout.setContentsMargins(8, 8, 8, 8)
        self.songselect_layout.setObjectName('songselect_layout')
        self.stacked_widget = QtWidgets.QStackedWidget(songselect_dialog)
        self.stacked_widget.setObjectName('stacked_widget')
        # Webview page
        self.webview_page = QtWidgets.QWidget()
        self.webview_page.setObjectName('webview_page')
        self.webview_layout = QtWidgets.QGridLayout(self.webview_page)
        self.webview_layout.setObjectName('webview_layout')
        self.webview_layout.setContentsMargins(0, 0, 0, 0)
        self.webview = WebEngineView(self)
        self.webview_layout.addWidget(self.webview, 1, 0, 3, 1)
        self.stacked_widget.addWidget(self.webview_page)
        # Song page
        self.song_page = QtWidgets.QWidget()
        self.song_page.setObjectName('song_page')
        self.song_layout = QtWidgets.QGridLayout(self.song_page)
        self.song_layout.setContentsMargins(8, 8, 8, 8)
        self.song_layout.setSpacing(8)
        self.song_layout.setObjectName('song_layout')
        self.title_label = QtWidgets.QLabel(self.song_page)
        self.title_label.setObjectName('title_label')
        self.song_layout.addWidget(self.title_label, 0, 0, 1, 1)
        self.title_edit = QtWidgets.QLineEdit(self.song_page)
        self.title_edit.setReadOnly(True)
        self.title_edit.setObjectName('title_edit')
        self.song_layout.addWidget(self.title_edit, 0, 1, 1, 1)
        self.authors_label = QtWidgets.QLabel(self.song_page)
        self.authors_label.setObjectName('authors_label')
        self.song_layout.addWidget(self.authors_label, 0, 2, 1, 1)
        self.author_list_widget = QtWidgets.QListWidget(self.song_page)
        self.author_list_widget.setObjectName('author_list_widget')
        self.song_layout.addWidget(self.author_list_widget, 0, 3, 3, 1)
        self.copyright_label = QtWidgets.QLabel(self.song_page)
        self.copyright_label.setObjectName('copyright_label')
        self.song_layout.addWidget(self.copyright_label, 1, 0, 1, 1)
        self.copyright_edit = QtWidgets.QLineEdit(self.song_page)
        self.copyright_edit.setReadOnly(True)
        self.copyright_edit.setObjectName('copyright_edit')
        self.song_layout.addWidget(self.copyright_edit, 1, 1, 1, 1)
        self.ccli_label = QtWidgets.QLabel(self.song_page)
        self.ccli_label.setObjectName('ccli_label')
        self.song_layout.addWidget(self.ccli_label, 2, 0, 1, 1)
        self.ccli_edit = QtWidgets.QLineEdit(self.song_page)
        self.ccli_edit.setReadOnly(True)
        self.ccli_edit.setObjectName('ccli_edit')
        self.song_layout.addWidget(self.ccli_edit, 2, 1, 1, 1)
        self.lyrics_label = QtWidgets.QLabel(self.song_page)
        self.lyrics_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading |
                                       QtCore.Qt.AlignmentFlag.AlignLeft |
                                       QtCore.Qt.AlignmentFlag.AlignTop)
        self.lyrics_label.setObjectName('lyrics_label')
        self.song_layout.addWidget(self.lyrics_label, 3, 0, 1, 1)
        self.lyrics_table_widget = SingleColumnTableWidget(self.song_page)
        self.lyrics_table_widget.setObjectName('lyrics_table_widget')
        self.lyrics_table_widget.setRowCount(0)
        self.song_layout.addWidget(self.lyrics_table_widget, 3, 1, 1, 3)
        self.title_label.setBuddy(self.title_edit)
        self.authors_label.setBuddy(self.author_list_widget)
        self.copyright_label.setBuddy(self.copyright_edit)
        self.ccli_label.setBuddy(self.ccli_edit)
        self.lyrics_label.setBuddy(self.lyrics_table_widget)
        self.stacked_widget.addWidget(self.song_page)
        # The top panel
        self.top_button_layout = QtWidgets.QGridLayout()
        self.top_button_layout.setContentsMargins(0, 0, 0, 0)
        self.top_button_layout.setSpacing(8)
        self.top_button_layout.setObjectName('top_button_layout')
        self.back_button = QtWidgets.QPushButton(songselect_dialog)
        self.back_button.setIcon(UiIcons().back)
        self.back_button.setObjectName('back_button')
        self.top_button_layout.addWidget(self.back_button, 0, 0, 1, 1)
        self.url_bar = QtWidgets.QLineEdit(songselect_dialog)
        self.url_bar.setObjectName('ccli_edit')
        self.top_button_layout.addWidget(self.url_bar, 0, 1, 1, 8)
        self.song_progress_bar = QtWidgets.QProgressBar(songselect_dialog)
        self.song_progress_bar.setMinimum(0)
        self.song_progress_bar.setMaximum(3)
        self.song_progress_bar.setValue(0)
        self.song_progress_bar.setVisible(False)
        self.top_button_layout.addWidget(self.song_progress_bar, 0, 1, 1, 8)
        # The bottom panel
        self.bottom_button_layout = QtWidgets.QGridLayout()
        self.bottom_button_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_button_layout.setSpacing(8)
        self.bottom_button_layout.setObjectName('bottom_button_layout')
        self.close_button = QtWidgets.QPushButton(songselect_dialog)
        self.close_button.setIcon(UiIcons().close)
        self.close_button.setObjectName('close_button')
        self.bottom_button_layout.addWidget(self.close_button, 0, 0, 1, 1)
        self.message_area = QtWidgets.QLabel()
        self.message_area.setWordWrap(True)
        self.message_area.setObjectName('message_area')
        self.bottom_button_layout.addWidget(self.message_area, 0, 1, 1, 7)
        # Add everything to the interface layout
        self.songselect_layout.addLayout(self.top_button_layout)
        self.songselect_layout.addWidget(self.stacked_widget)
        self.songselect_layout.addLayout(self.bottom_button_layout)
        self.retranslate_ui(songselect_dialog)
        self.stacked_widget.setCurrentIndex(0)

    def retranslate_ui(self, songselect_dialog):
        """
        Translate the GUI.
        """
        songselect_dialog.setWindowTitle(translate('SongsPlugin.SongSelectForm', 'CCLI SongSelect Importer'))
        self.title_label.setText(translate('SongsPlugin.SongSelectForm', 'Title:'))
        self.authors_label.setText(translate('SongsPlugin.SongSelectForm', 'Author(s):'))
        self.copyright_label.setText(translate('SongsPlugin.SongSelectForm', 'Copyright:'))
        self.ccli_label.setText(translate('SongsPlugin.SongSelectForm', 'CCLI Number:'))
        self.lyrics_label.setText(translate('SongsPlugin.SongSelectForm', 'Lyrics:'))
        self.back_button.setText(translate('SongsPlugin.SongSelectForm', 'Back',
                                           'When pressed takes user to the CCLI home page'))
        self.close_button.setText(translate('SongsPlugin.SongSelectForm', 'Close'))
