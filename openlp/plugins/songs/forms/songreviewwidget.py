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
A widget representing a song in the duplicate song removal wizard review page.
"""
from PySide6 import QtCore, QtWidgets

from openlp.core.ui.icons import UiIcons
from openlp.plugins.songs.lib import VerseType
from openlp.plugins.songs.lib.openlyricsxml import SongXML


class SongReviewWidget(QtWidgets.QWidget):
    """
    A widget representing a song on the duplicate song review page.
    It displays most of the information a song contains and
    provides a "remove" button to remove the song from the database.
    The remove logic is not implemented here, but a signal is provided
    when the remove button is clicked.
    """

    # Signals have to be class variables and not instance variables. Otherwise
    # they are not registered by Qt (missing emit and connect methods are artifacts of this).
    # To use SongReviewWidget as a signal parameter one would have to assigning the class
    # variable after the class is declared. While this is possible, it also messes Qts meta
    # object system up. The result is an
    # "Object::connect: Use the SIGNAL macro to bind SongReviewWidget::(QWidget*)" error on
    # connect calls.
    # That's why we cheat a little and use QWidget instead of SongReviewWidget as parameter.
    # While not being entirely correct, it does work.
    song_remove_button_clicked = QtCore.Signal(QtWidgets.QWidget)

    def __init__(self, parent, song):
        """
        :param parent: The QWidget-derived parent of the wizard.
        :param song: The Song which this SongReviewWidget should represent.
        """
        super(SongReviewWidget, self).__init__(parent)
        self.song = song
        self.setup_ui()
        self.retranslate_ui()
        self.song_remove_button.clicked.connect(self.on_remove_button_clicked)

    def setup_ui(self):
        self.song_vertical_layout = QtWidgets.QVBoxLayout(self)
        self.song_vertical_layout.setObjectName('song_vertical_layout')
        self.song_group_box = QtWidgets.QGroupBox(self)
        self.song_group_box.setObjectName('song_group_box')
        self.song_group_box.setFixedWidth(300)
        self.song_group_box_layout = QtWidgets.QVBoxLayout(self.song_group_box)
        self.song_group_box_layout.setObjectName('song_group_box_layout')
        self.song_info_form_layout = QtWidgets.QFormLayout()
        self.song_info_form_layout.setObjectName('song_info_form_layout')
        # Add title widget.
        self.song_title_label = QtWidgets.QLabel(self)
        self.song_title_label.setObjectName('song_title_label')
        self.song_info_form_layout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.song_title_label)
        self.song_title_content = QtWidgets.QLabel(self)
        self.song_title_content.setObjectName('song_title_content')
        self.song_title_content.setText(self.song.title)
        self.song_title_content.setWordWrap(True)
        self.song_info_form_layout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.song_title_content)
        # Add alternate title widget.
        self.song_alternate_title_label = QtWidgets.QLabel(self)
        self.song_alternate_title_label.setObjectName('song_alternate_title_label')
        self.song_info_form_layout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole,
                                             self.song_alternate_title_label)
        self.song_alternate_title_content = QtWidgets.QLabel(self)
        self.song_alternate_title_content.setObjectName('song_alternate_title_content')
        self.song_alternate_title_content.setText(self.song.alternate_title)
        self.song_alternate_title_content.setWordWrap(True)
        self.song_info_form_layout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole,
                                             self.song_alternate_title_content)
        # Add last modified date.
        self.song_last_modified_label = QtWidgets.QLabel(self)
        self.song_last_modified_label.setObjectName('last_modified_label')
        self.song_last_modified_label.setText('Last Modified:')
        self.song_info_form_layout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.song_last_modified_label)
        self.song_last_modified_content = QtWidgets.QLabel(self)
        self.song_last_modified_content.setObjectName('last_modified_content')
        self.song_last_modified_content.setText(self.song.last_modified.strftime("%Y-%m-%d %H:%M:%S"))
        self.song_last_modified_content.setWordWrap(True)
        self.song_info_form_layout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole,
                                             self.song_last_modified_content)
        # Add Theme widget.
        self.song_theme_label = QtWidgets.QLabel(self)
        self.song_theme_label.setObjectName('song_theme_label')
        self.song_theme_label.setText('Theme:')
        self.song_info_form_layout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.song_theme_label)
        self.song_theme_content = QtWidgets.QLabel(self)
        self.song_theme_content.setObjectName('song_theme_content')
        self.song_theme_content.setText(self.song.theme_name)
        self.song_theme_content.setWordWrap(True)
        self.song_info_form_layout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.song_theme_content)
        # Add CCLI number widget.
        self.song_ccli_number_label = QtWidgets.QLabel(self)
        self.song_ccli_number_label.setObjectName('song_ccli_number_label')
        self.song_info_form_layout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.song_ccli_number_label)
        self.song_ccli_number_content = QtWidgets.QLabel(self)
        self.song_ccli_number_content.setObjectName('song_ccli_number_content')
        self.song_ccli_number_content.setText(self.song.ccli_number)
        self.song_ccli_number_content.setWordWrap(True)
        self.song_info_form_layout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.song_ccli_number_content)
        # Add copyright widget.
        self.song_copyright_label = QtWidgets.QLabel(self)
        self.song_copyright_label.setObjectName('song_copyright_label')
        self.song_info_form_layout.setWidget(5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.song_copyright_label)
        self.song_copyright_content = QtWidgets.QLabel(self)
        self.song_copyright_content.setObjectName('song_copyright_content')
        self.song_copyright_content.setWordWrap(True)
        self.song_copyright_content.setText(self.song.copyright)
        self.song_info_form_layout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.song_copyright_content)
        # Add comments widget.
        self.song_comments_label = QtWidgets.QLabel(self)
        self.song_comments_label.setObjectName('song_comments_label')
        self.song_info_form_layout.setWidget(6, QtWidgets.QFormLayout.ItemRole.LabelRole, self.song_comments_label)
        self.song_comments_content = QtWidgets.QLabel(self)
        self.song_comments_content.setObjectName('song_comments_content')
        self.song_comments_content.setText(self.song.comments)
        self.song_comments_content.setWordWrap(True)
        self.song_info_form_layout.setWidget(6, QtWidgets.QFormLayout.ItemRole.FieldRole, self.song_comments_content)
        # Add authors widget.
        self.song_authors_label = QtWidgets.QLabel(self)
        self.song_authors_label.setObjectName('song_authors_label')
        self.song_info_form_layout.setWidget(7, QtWidgets.QFormLayout.ItemRole.LabelRole, self.song_authors_label)
        self.song_authors_content = QtWidgets.QLabel(self)
        self.song_authors_content.setObjectName('song_authors_content')
        self.song_authors_content.setWordWrap(True)
        authors_text = ', '.join([author.display_name for author in self.song.authors])
        self.song_authors_content.setText(authors_text)
        self.song_info_form_layout.setWidget(7, QtWidgets.QFormLayout.ItemRole.FieldRole, self.song_authors_content)
        # Add verse order widget.
        self.song_verse_order_label = QtWidgets.QLabel(self)
        self.song_verse_order_label.setObjectName('song_verse_order_label')
        self.song_info_form_layout.setWidget(8, QtWidgets.QFormLayout.ItemRole.LabelRole, self.song_verse_order_label)
        self.song_verse_order_content = QtWidgets.QLabel(self)
        self.song_verse_order_content.setObjectName('song_verse_order_content')
        self.song_verse_order_content.setText(self.song.verse_order)
        self.song_verse_order_content.setWordWrap(True)
        self.song_info_form_layout.setWidget(8, QtWidgets.QFormLayout.ItemRole.FieldRole, self.song_verse_order_content)
        self.song_group_box_layout.addLayout(self.song_info_form_layout)
        # Add verses widget.
        self.song_info_verse_list_widget = QtWidgets.QTableWidget(self.song_group_box)
        self.song_info_verse_list_widget.setColumnCount(1)
        self.song_info_verse_list_widget.horizontalHeader().setVisible(False)
        self.song_info_verse_list_widget.setObjectName('song_info_verse_list_widget')
        self.song_info_verse_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.song_info_verse_list_widget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.song_info_verse_list_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.song_info_verse_list_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.song_info_verse_list_widget.setAlternatingRowColors(True)
        song_xml = SongXML()
        verses = song_xml.get_verses(self.song.lyrics)
        self.song_info_verse_list_widget.setRowCount(len(verses))
        song_tags = []
        for verse_number, verse in enumerate(verses):
            item = QtWidgets.QTableWidgetItem()
            item.setText(verse[1])
            self.song_info_verse_list_widget.setItem(verse_number, 0, item)

            # We cannot use from_loose_input() here, because database
            # is supposed to contain English lowercase singlechar tags.
            verse_tag = verse[0]['type']
            verse_index = None
            if len(verse_tag) > 1:
                verse_index = VerseType.from_translated_string(verse_tag)
                if verse_index is None:
                    verse_index = VerseType.from_string(verse_tag, None)
            if verse_index is None:
                verse_index = VerseType.from_tag(verse_tag)
            verse_tag = VerseType.translated_tags[verse_index].upper()
            song_tags.append(str(verse_tag + verse[0]['label']))
        self.song_info_verse_list_widget.setVerticalHeaderLabels(song_tags)
        # Resize table fields to content and table to columns
        self.song_info_verse_list_widget.setColumnWidth(0, self.song_group_box.width())
        self.song_info_verse_list_widget.resizeRowsToContents()
        # The 6 is a trial and error value since verticalHeader().length() + offset() is a little bit to small.
        # It seems there is no clean way to determine the real height of the table contents.
        # The "correct" value slightly fluctuates depending on the theme used, in the worst case
        # Some pixels are missing at the bottom of the table, but all themes I tried still allowed
        # to read the last verse line, so I'll just leave it at that.
        self.song_info_verse_list_widget.setFixedHeight(self.song_info_verse_list_widget.verticalHeader().length() +
                                                        self.song_info_verse_list_widget.verticalHeader().offset() + 6)
        self.song_group_box_layout.addWidget(self.song_info_verse_list_widget)
        self.song_group_box_layout.addStretch()
        self.song_vertical_layout.addWidget(self.song_group_box)
        self.song_remove_button = QtWidgets.QPushButton(self)
        self.song_remove_button.setObjectName('song_remove_button')
        self.song_remove_button.setIcon(UiIcons().delete)
        self.song_remove_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.song_vertical_layout.addWidget(self.song_remove_button, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

    def retranslate_ui(self):
        self.song_remove_button.setText('Remove')
        self.song_title_label.setText('Title:')
        self.song_alternate_title_label.setText('Alternate Title:')
        self.song_ccli_number_label.setText('CCLI Number:')
        self.song_verse_order_label.setText('Verse Order:')
        self.song_copyright_label.setText('Copyright:')
        self.song_comments_label.setText('Comments:')
        self.song_authors_label.setText('Authors:')

    def on_remove_button_clicked(self):
        """
        Signal emitted when the "remove" button is clicked.
        """
        self.song_remove_button_clicked.emit(self)
