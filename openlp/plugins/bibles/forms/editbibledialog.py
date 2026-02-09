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

from openlp.core.common.enum import LanguageSelection
from openlp.core.common.i18n import translate
from openlp.core.lib.ui import create_button_box
from openlp.core.ui.icons import UiIcons
from openlp.plugins.bibles.lib import BibleStrings
from openlp.plugins.bibles.lib.db import BiblesResourcesDB


class Ui_EditBibleDialog(object):
    def setup_ui(self, edit_bible_dialog):
        edit_bible_dialog.setObjectName('edit_bible_dialog')
        edit_bible_dialog.setWindowIcon(UiIcons().main_icon)
        edit_bible_dialog.resize(520, 400)
        edit_bible_dialog.setModal(True)
        self.dialog_layout = QtWidgets.QVBoxLayout(edit_bible_dialog)
        self.dialog_layout.setSpacing(8)
        self.dialog_layout.setContentsMargins(8, 8, 8, 8)
        self.dialog_layout.setObjectName('dialog_layout')
        self.bible_tab_widget = QtWidgets.QTabWidget(edit_bible_dialog)
        self.bible_tab_widget.setObjectName('BibleTabWidget')
        # Meta tab
        self.meta_tab = QtWidgets.QWidget()
        self.meta_tab.setObjectName('meta_tab')
        self.meta_tab_layout = QtWidgets.QVBoxLayout(self.meta_tab)
        self.meta_tab_layout.setObjectName('meta_tab_layout')
        self.license_details_group_box = QtWidgets.QGroupBox(self.meta_tab)
        self.license_details_group_box.setObjectName('license_details_group_box')
        self.license_details_layout = QtWidgets.QFormLayout(self.license_details_group_box)
        self.license_details_layout.setObjectName('license_details_layout')
        self.version_name_label = QtWidgets.QLabel(self.license_details_group_box)
        self.version_name_label.setObjectName('version_name_label')
        self.version_name_edit = QtWidgets.QLineEdit(self.license_details_group_box)
        self.version_name_edit.setObjectName('version_name_edit')
        self.version_name_label.setBuddy(self.version_name_edit)
        self.license_details_layout.addRow(self.version_name_label, self.version_name_edit)
        self.copyright_label = QtWidgets.QLabel(self.license_details_group_box)
        self.copyright_label.setObjectName('copyright_label')
        self.copyright_edit = QtWidgets.QLineEdit(self.license_details_group_box)
        self.copyright_edit.setObjectName('copyright_edit')
        self.copyright_label.setBuddy(self.copyright_edit)
        self.license_details_layout.addRow(self.copyright_label, self.copyright_edit)
        self.permissions_label = QtWidgets.QLabel(self.license_details_group_box)
        self.permissions_label.setObjectName('permissions_label')
        self.permissions_edit = QtWidgets.QLineEdit(self.license_details_group_box)
        self.permissions_edit.setObjectName('permissions_edit')
        self.permissions_label.setBuddy(self.permissions_edit)
        self.license_details_layout.addRow(self.permissions_label, self.permissions_edit)
        self.full_license_label = QtWidgets.QLabel(self.license_details_group_box)
        self.full_license_label.setObjectName('full_license_label')
        self.full_license_edit = QtWidgets.QPlainTextEdit(self.license_details_group_box)
        self.full_license_edit.setObjectName('full_license_edit')
        self.full_license_label.setBuddy(self.full_license_edit)
        self.license_details_layout.addRow(self.full_license_label, self.full_license_edit)
        self.meta_tab_layout.addWidget(self.license_details_group_box)
        self.language_selection_group_box = QtWidgets.QGroupBox(self.meta_tab)
        self.language_selection_group_box.setObjectName('language_selection_group_box')
        self.language_selection_layout = QtWidgets.QVBoxLayout(self.language_selection_group_box)
        self.language_selection_label = QtWidgets.QLabel(self.language_selection_group_box)
        self.language_selection_label.setObjectName('language_selection_label')
        self.language_selection_combo_box = QtWidgets.QComboBox(self.language_selection_group_box)
        self.language_selection_combo_box.setObjectName('language_selection_combo_box')
        self.language_selection_combo_box.addItems(['', '', '', ''])
        self.language_selection_layout.addWidget(self.language_selection_label)
        self.language_selection_layout.addWidget(self.language_selection_combo_box)
        self.meta_tab_layout.addWidget(self.language_selection_group_box)
        self.meta_tab_layout.addStretch()
        self.bible_tab_widget.addTab(self.meta_tab, '')
        # Book name tab
        self.book_name_tab = QtWidgets.QWidget()
        self.book_name_tab.setObjectName('book_name_tab')
        self.book_name_tab_layout = QtWidgets.QVBoxLayout(self.book_name_tab)
        self.book_name_tab_layout.setObjectName('book_name_tab_layout')
        self.book_name_notice = QtWidgets.QLabel(self.book_name_tab)
        self.book_name_notice.setObjectName('book_name_notice')
        self.book_name_notice.setWordWrap(True)
        self.book_name_tab_layout.addWidget(self.book_name_notice)
        self.scroll_area = QtWidgets.QScrollArea(self.book_name_tab)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName('scroll_area')
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.book_name_widget = QtWidgets.QWidget(self.scroll_area)
        self.book_name_widget.setObjectName('book_name_widget')
        self.book_name_widget_layout = QtWidgets.QFormLayout(self.book_name_widget)
        self.book_name_widget_layout.setObjectName('book_name_widget_layout')
        self.book_name_label = {}
        self.book_name_edit = {}
        for book in BiblesResourcesDB.get_books():
            self.book_name_label[book['abbreviation']] = QtWidgets.QLabel(self.book_name_widget)
            self.book_name_label[book['abbreviation']].setObjectName(
                'book_name_label[{book}]'.format(book=book['abbreviation']))
            self.book_name_edit[book['abbreviation']] = QtWidgets.QLineEdit(self.book_name_widget)
            self.book_name_edit[book['abbreviation']].setObjectName(
                'book_name_edit[{name}]'.format(name=book['abbreviation']))
            self.book_name_widget_layout.addRow(
                self.book_name_label[book['abbreviation']],
                self.book_name_edit[book['abbreviation']])
        self.scroll_area.setWidget(self.book_name_widget)
        self.book_name_tab_layout.addWidget(self.scroll_area)
        self.book_name_tab_layout.addStretch()
        self.bible_tab_widget.addTab(self.book_name_tab, '')
        # Last few bits
        self.dialog_layout.addWidget(self.bible_tab_widget)
        self.button_box = create_button_box(edit_bible_dialog, 'button_box', ['cancel', 'save', 'help'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslate_ui(edit_bible_dialog)
        QtCore.QMetaObject.connectSlotsByName(edit_bible_dialog)

    def retranslate_ui(self, edit_bible_dialog):
        self.book_names = BibleStrings().BookNames
        edit_bible_dialog.setWindowTitle(translate('BiblesPlugin.EditBibleForm', 'Bible Editor'))
        # Meta tab
        self.bible_tab_widget.setTabText(
            self.bible_tab_widget.indexOf(self.meta_tab), translate('SongsPlugin.EditBibleForm', 'Meta Data'))
        self.license_details_group_box.setTitle(translate('BiblesPlugin.EditBibleForm', 'License Details'))
        self.version_name_label.setText(translate('BiblesPlugin.EditBibleForm', 'Version name:'))
        self.copyright_label.setText(translate('BiblesPlugin.EditBibleForm', 'Copyright:'))
        self.permissions_label.setText(translate('BiblesPlugin.EditBibleForm', 'Permissions:'))
        self.full_license_label.setText(translate('BiblesPlugin.EditBibleForm', 'Full license:'))
        self.language_selection_group_box.setTitle(translate('BiblesPlugin.EditBibleForm', 'Default Bible Language'))
        self.language_selection_label.setText(
            translate('BiblesPlugin.EditBibleForm', 'Book name language in search field, search results and '
                                                    'on display:'))
        self.language_selection_combo_box.setItemText(0, translate('BiblesPlugin.EditBibleForm', 'Global Settings'))
        self.language_selection_combo_box.setItemText(
            LanguageSelection.Bible + 1,
            translate('BiblesPlugin.EditBibleForm', 'Bible Language'))
        self.language_selection_combo_box.setItemText(
            LanguageSelection.Application + 1, translate('BiblesPlugin.EditBibleForm', 'Application Language'))
        self.language_selection_combo_box.setItemText(
            LanguageSelection.English + 1,
            translate('BiblesPlugin.EditBibleForm', 'English'))
        # Book name tab
        self.bible_tab_widget.setTabText(
            self.bible_tab_widget.indexOf(self.book_name_tab),
            translate('SongsPlugin.EditBibleForm', 'Custom Book Names'))
        for book in BiblesResourcesDB.get_books():
            self.book_name_label[book['abbreviation']].setText(
                '{text}:'.format(text=self.book_names[book['abbreviation']]))
