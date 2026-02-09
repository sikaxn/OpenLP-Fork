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

import logging
import re

from PySide6 import QtCore, QtWidgets, QtGui

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.bibles.lib import BibleStrings
from openlp.plugins.bibles.lib.db import BiblesResourcesDB

from .editbibledialog import Ui_EditBibleDialog


log = logging.getLogger(__name__)


class EditBibleForm(QtWidgets.QDialog, Ui_EditBibleDialog, RegistryProperties):
    """
    Class to manage the editing of a bible
    """
    log.info('{name} EditBibleForm loaded'.format(name=__name__))

    def __init__(self, media_item, parent, manager):
        """
        Constructor
        """
        super(EditBibleForm, self).__init__(parent,
                                            QtCore.Qt.WindowType.WindowSystemMenuHint |
                                            QtCore.Qt.WindowType.WindowTitleHint |
                                            QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.media_item = media_item
        self.book_names = BibleStrings().BookNames
        self.setup_ui(self)
        self.manager = manager

    def load_bible(self, bible):
        """
        Loads a bible.

        ``bible``

        :param bible: The name of the bible.
        """
        log.debug('Load Bible')
        self.bible = bible
        book_name_language = self.manager.get_meta_data(self.bible, 'book_name_language')
        """
        Try loading the metadata, if the field does not exist in the metadata, continue executing the code,
        missing fields will be created on "self.accept" (save).
        """
        meta = self.manager.get_meta_data(self.bible, 'name')
        copyright = self.manager.get_meta_data(self.bible, 'copyright')
        permission = self.manager.get_meta_data(self.bible, 'permissions')
        full_license = self.manager.get_meta_data(self.bible, 'full_license')
        if meta:
            self.version_name_edit.setText(meta.value)
        if copyright:
            self.copyright_edit.setText(copyright.value)
        if permission:
            self.permissions_edit.setText(permission.value)
        if full_license:
            self.full_license_edit.setPlainText(full_license.value)
        # Set placeholder texts for the fields.
        self.version_name_edit.setPlaceholderText(UiStrings().RequiredShowInFooter)
        self.copyright_edit.setPlaceholderText(UiStrings().RequiredShowInFooter)
        self.permissions_edit.setPlaceholderText(UiStrings().OptionalShowInFooter)
        self.full_license_edit.setPlaceholderText(UiStrings().OptionalHideInFooter)
        if book_name_language and book_name_language.value != 'None':
            self.language_selection_combo_box.setCurrentIndex(int(book_name_language.value) + 1)
        self.books = {}
        self.web_bible = self.manager.get_meta_data(self.bible, 'download_source')
        if self.web_bible:
            self.book_name_notice.setText(
                translate('BiblesPlugin.EditBibleForm',
                          'This is a Web Download Bible.\nIt is not possible to customize the Book Names.'))
            self.scroll_area.hide()
        else:
            self.book_name_notice.setText(
                translate('BiblesPlugin.EditBibleForm',
                          'To use the customized book names, "Bible language" must be selected on the Meta Data tab '
                          'or, if "Global settings" is selected, on the Bible page in Configure OpenLP.'))
            for book in BiblesResourcesDB.get_books():
                self.books[book['abbreviation']] = self.manager.get_book_by_id(self.bible, book['id'])
                if self.books[book['abbreviation']] and not self.web_bible:
                    self.book_name_edit[book['abbreviation']].setText(self.books[book['abbreviation']].name)
                else:
                    # It is necessary to remove the Widget otherwise there still
                    # exists the vertical spacing in QFormLayout
                    self.book_name_widget_layout.removeWidget(self.book_name_label[book['abbreviation']])
                    self.book_name_label[book['abbreviation']].hide()
                    self.book_name_widget_layout.removeWidget(self.book_name_edit[book['abbreviation']])
                    self.book_name_edit[book['abbreviation']].hide()

    def reject(self):
        """
        Exit Dialog and do not save
        """
        log.debug('BibleEditForm.reject')
        self.bible = None
        QtWidgets.QDialog.reject(self)

    def accept(self):
        """
        Exit Dialog and save data
        """
        log.debug('BibleEditForm.accept')
        version = self.version_name_edit.text()
        copyright = self.copyright_edit.text()
        permissions = self.permissions_edit.text()
        full_license = self.full_license_edit.toPlainText()
        book_name_language = self.language_selection_combo_box.currentIndex() - 1
        if book_name_language == -1:
            book_name_language = None
        if not self.validate_meta(version, copyright):
            return
        if not self.web_bible:
            custom_names = {}
            for abbr, book in self.books.items():
                if book:
                    custom_names[abbr] = self.book_name_edit[abbr].text()
                    if book.name != custom_names[abbr]:
                        if not self.validate_book(custom_names[abbr], abbr):
                            return
        self.application.set_busy_cursor()
        self.manager.save_meta_data(self.bible, version, copyright, permissions, full_license, book_name_language)
        if not self.web_bible:
            for abbr, book in self.books.items():
                if book:
                    if book.name != custom_names[abbr]:
                        book.name = custom_names[abbr]
                        self.manager.update_book(self.bible, book)
        self.bible = None
        self.application.set_normal_cursor()
        QtWidgets.QDialog.accept(self)

    def validate_meta(self, name, copyright):
        """
        Validate the Meta before saving.
        """
        if not name:
            self.version_name_edit.setFocus()
            critical_error_message_box(
                UiStrings().EmptyField,
                translate('BiblesPlugin.BibleEditForm', 'You need to specify a version name for your Bible.'))
            return False
        elif not copyright:
            self.copyright_edit.setFocus()
            critical_error_message_box(
                UiStrings().EmptyField,
                translate('BiblesPlugin.BibleEditForm',
                          'You need to set a copyright for your Bible. Bibles in the Public Domain need to be marked '
                          'as such.'))
            return False
        elif self.manager.exists(name) and self.manager.get_meta_data(self.bible, 'name').value != name:
            self.version_name_edit.setFocus()
            critical_error_message_box(
                translate('BiblesPlugin.BibleEditForm', 'Bible Exists'),
                translate('BiblesPlugin.BibleEditForm', 'This Bible already exists. Please import '
                          'a different Bible or first delete the existing one.'))
            return False
        return True

    def validate_book(self, new_book_name, abbreviation):
        """
        Validate a book.
        """
        book_regex = re.compile(r'[\d]*[^\d]+$')
        if not new_book_name:
            self.book_name_edit[abbreviation].setFocus()
            critical_error_message_box(
                UiStrings().EmptyField,
                translate('BiblesPlugin.BibleEditForm',
                          'You need to specify a book name for "{text}".').format(text=self.book_names[abbreviation]))
            return False
        elif not book_regex.match(new_book_name):
            self.book_name_edit[abbreviation].setFocus()
            critical_error_message_box(
                UiStrings().EmptyField,
                translate('BiblesPlugin.BibleEditForm',
                          'The book name "{name}" is not correct.\n'
                          'Numbers can only be used at the beginning and must\nbe '
                          'followed by one or more non-numeric characters.').format(name=new_book_name))
            return False
        for abbr, book in self.books.items():
            if book:
                if abbr == abbreviation:
                    continue
                if self.book_name_edit[abbr].text() == new_book_name:
                    self.book_name_edit[abbreviation].setFocus()
                    critical_error_message_box(
                        translate('BiblesPlugin.BibleEditForm', 'Duplicate Book Name'),
                        translate('BiblesPlugin.BibleEditForm',
                                  'The Book Name "{name}" has been entered more than once.').format(name=new_book_name))
                    return False
        return True

    def provide_help(self):
        """
        Provide help within the form by opening the appropriate page of the openlp manual in the user's browser
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://manual.openlp.org/bibles.html#edit-bible-data"))
