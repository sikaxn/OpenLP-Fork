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
Module implementing BookNameForm.
"""
import logging
import re

from PySide6 import QtCore
from PySide6.QtWidgets import QDialog

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.bibles.forms.booknamedialog import Ui_BookNameDialog
from openlp.plugins.bibles.lib import BibleStrings
from openlp.plugins.bibles.lib.db import BiblesResourcesDB


log = logging.getLogger(__name__)


class BookNameForm(QDialog, Ui_BookNameDialog):
    """
    Class to manage a dialog which help the user to refer a book name a
    to a english book name
    """
    log.info('BookNameForm loaded')

    def __init__(self, parent=None):
        """
        Constructor
        """
        super(BookNameForm, self).__init__(parent,
                                           QtCore.Qt.WindowType.WindowSystemMenuHint |
                                           QtCore.Qt.WindowType.WindowTitleHint |
                                           QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui(self)
        self.custom_signals()
        self.book_names = BibleStrings().BookNames
        self.book_id = False

    def custom_signals(self):
        """
        Set up the signals used in the booknameform.
        """
        self.old_testament_check_box.stateChanged.connect(self.on_check_box_index_changed)
        self.new_testament_check_box.stateChanged.connect(self.on_check_box_index_changed)
        self.apocrypha_check_box.stateChanged.connect(self.on_check_box_index_changed)

    def on_check_box_index_changed(self, index):
        """
        Reload Combobox if CheckBox state has changed
        """
        self.reload_combo_box()

    def reload_combo_box(self):
        """
        Reload the Combobox items
        """
        self.corresponding_combo_box.clear()
        items = BiblesResourcesDB.get_books()
        for item in items:
            add_book = True
            for book in self.books:
                if book.book_reference_id == item['id']:
                    add_book = False
                    break
            if (self.old_testament_check_box.checkState() == QtCore.Qt.CheckState.Unchecked
                    and item['testament_id'] == 1):
                add_book = False
            elif (self.new_testament_check_box.checkState() == QtCore.Qt.CheckState.Unchecked
                    and item['testament_id'] == 2):
                add_book = False
            elif self.apocrypha_check_box.checkState() == QtCore.Qt.CheckState.Unchecked and item['testament_id'] == 3:
                add_book = False
            if add_book:
                self.corresponding_combo_box.addItem(self.book_names[item['abbreviation']])

    def exec(self, name, books, max_books):
        self.books = books
        log.debug(max_books)
        if max_books <= 27:
            self.old_testament_check_box.setCheckState(QtCore.Qt.CheckState.Unchecked)
            self.apocrypha_check_box.setCheckState(QtCore.Qt.CheckState.Unchecked)
        elif max_books <= 66:
            self.apocrypha_check_box.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.reload_combo_box()
        self.current_book_label.setText(str(name))
        self.corresponding_combo_box.setFocus()
        return QDialog.exec(self)

    def accept(self):
        if not self.corresponding_combo_box.currentText():
            critical_error_message_box(message=translate('BiblesPlugin.BookNameForm', 'You need to select a book.'))
            self.corresponding_combo_box.setFocus()
            return False
        else:
            cor_book = self.corresponding_combo_box.currentText()
            for character in '\\.^$*+?{}[]()':
                cor_book = cor_book.replace(character, '\\' + character)
            books = [key for key in list(self.book_names.keys()) if re.match(cor_book, str(self.book_names[key]))]
            books = [_f for _f in map(BiblesResourcesDB.get_book, books) if _f]
            if books:
                self.book_id = books[0]['id']
            return QDialog.accept(self)
