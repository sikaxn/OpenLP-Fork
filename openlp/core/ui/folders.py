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

from openlp.core.common.i18n import get_natural_key, translate
from openlp.core.lib.ui import create_button_box, critical_error_message_box


class FolderPopulateMixin(object):
    """
    A mixin for common code between the two folder dialogs
    """
    def populate_folders(self, parent_id=None, prefix=''):
        """
        Recursively add folders to the combobox

        :param folders: A dictionary object of the folders, in a tree.
        :param parent_id: The ID of the parent folder.
        :param prefix: A string containing the prefix that will be added in front of the folder name for each
            level of the tree.
        """
        if parent_id is None:
            self.folder_combobox.clear()
            # I'm not sure what this is here for, I'm just leaving it in for now.
            self.folder_combobox.top_level_folder_added = False
        folders = self.db_manager.get_all_objects(self.folder_class, self.folder_class.parent_id == parent_id)
        folders.sort(key=lambda folder: get_natural_key(folder.name))
        for folder in folders:
            self.folder_combobox.addItem(prefix + folder.name, folder)
            self.populate_folders(folder.id, prefix + '   ')


class AddFolderForm(QtWidgets.QDialog, FolderPopulateMixin):
    """
    This class implements the 'Add folder' form for the plugins.
    """
    def __init__(self, parent=None, db_manager=None, folder_class=None):
        """
        Constructor
        """
        super().__init__(parent, QtCore.Qt.WindowType.WindowSystemMenuHint | QtCore.Qt.WindowType.WindowTitleHint |
                         QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui()
        self.db_manager = db_manager
        self.folder_class = folder_class

    def setup_ui(self):
        self.setObjectName('AddFolderDialog')
        self.resize(300, 10)
        self.dialog_layout = QtWidgets.QVBoxLayout(self)
        self.dialog_layout.setObjectName('dialog_layout')
        self.name_layout = QtWidgets.QFormLayout()
        self.name_layout.setObjectName('name_layout')
        self.parent_folder_label = QtWidgets.QLabel(self)
        self.parent_folder_label.setObjectName('parent_folder_label')
        self.folder_combobox = QtWidgets.QComboBox(self)
        self.folder_combobox.setObjectName('folder_combobox')
        self.name_layout.addRow(self.parent_folder_label, self.folder_combobox)
        self.name_label = QtWidgets.QLabel(self)
        self.name_label.setObjectName('name_label')
        self.name_edit = QtWidgets.QLineEdit(self)
        self.name_edit.setObjectName('name_edit')
        self.name_label.setBuddy(self.name_edit)
        self.name_layout.addRow(self.name_label, self.name_edit)
        self.dialog_layout.addLayout(self.name_layout)
        self.button_box = create_button_box(self, 'button_box', ['cancel', 'save'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslate_ui()
        self.setMaximumHeight(self.sizeHint().height())

    def retranslate_ui(self):
        self.setWindowTitle(translate('OpenLP.AddFolderForm', 'Add folder'))
        self.parent_folder_label.setText(translate('OpenLP.AddFolderForm', 'Parent folder:'))
        self.name_label.setText(translate('OpenLP.AddFolderForm', 'Folder name:'))

    def exec(self, clear=True, show_top_level_folder=False, selected_folder=None):
        """
        Show the form.

        :param clear:  Set to False if the text input box should not be cleared when showing the dialog (default: True).
        :param show_top_level_folder:  Set to True when "-- Top level folder --" should be showed as first item
            (default: False).
        :param selected_folder: The ID of the folder that should be selected by default when showing the dialog.
        """
        self.populate_folders()
        if clear:
            self.name_edit.clear()
        self.name_edit.setFocus()
        if show_top_level_folder and not self.folder_combobox.top_level_folder_added:
            self.folder_combobox.insertItem(0, translate('OpenLP.AddFolderForm', '-- Top-level folder --'), 0)
            self.folder_combobox.top_level_folder_added = True
        if selected_folder is not None:
            for i in range(self.folder_combobox.count()):
                if self.folder_combobox.itemData(i) == selected_folder:
                    self.folder_combobox.setCurrentIndex(i)
        return QtWidgets.QDialog.exec(self)

    def accept(self):
        """
        Override the accept() method from QDialog to make sure something is entered in the text input box.
        """
        if not self.name_edit.text():
            critical_error_message_box(message=translate('OpenLP.AddFolderForm',
                                                         'You need to type in a folder name.'))
            self.name_edit.setFocus()
            return False
        elif self.is_existing_folder():
            critical_error_message_box(message=translate('OpenLP.AddFolderForm',
                                                         'This folder already exists, please use a different name.'))
            return False
        else:
            return QtWidgets.QDialog.accept(self)

    @property
    def parent_id(self):
        """
        A property to get the parent folder id
        """
        if self.folder_combobox.currentIndex() == 0:
            return None
        return self.folder_combobox.itemData(self.folder_combobox.currentIndex(), QtCore.Qt.ItemDataRole.UserRole).id

    @property
    def folder_name(self):
        """
        A property to return the folder name
        """
        return self.name_edit.text()

    @property
    def new_folder(self):
        """
        A Folder object property
        """
        return self.folder_class(parent_id=self.parent_id, name=self.folder_name)

    def is_existing_folder(self):
        """
        Check if this folder already exists
        """
        return self.db_manager.get_object_filtered(self.folder_class,
                                                   self.folder_class.parent_id == self.parent_id,
                                                   self.folder_class.name == self.folder_name) is not None


class ChooseFolderForm(QtWidgets.QDialog, FolderPopulateMixin):
    """
    This class implements the 'Choose folder' form for the plugins.
    """
    def __init__(self, parent=None, db_manager=None, folder_class=None):
        """
        Constructor
        """
        super().__init__(parent, QtCore.Qt.WindowType.WindowSystemMenuHint | QtCore.Qt.WindowType.WindowTitleHint |
                         QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui()
        self.db_manager = db_manager
        self.folder_class = folder_class

    def setup_ui(self):
        """
        Set up the UI.
        """
        self.setObjectName('ChooseFolderForm')
        self.resize(399, 119)
        self.choose_folder_layout = QtWidgets.QFormLayout(self)
        self.choose_folder_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.choose_folder_layout.setContentsMargins(8, 8, 8, 8)
        self.choose_folder_layout.setSpacing(8)
        self.choose_folder_layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft |
                                                    QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.choose_folder_layout.setObjectName('choose_folder_layout')
        self.folder_question_label = QtWidgets.QLabel(self)
        self.folder_question_label.setWordWrap(True)
        self.folder_question_label.setObjectName('folder_question_label')
        self.choose_folder_layout.setWidget(1, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.folder_question_label)
        self.nofolder_radio_button = QtWidgets.QRadioButton(self)
        self.nofolder_radio_button.setChecked(True)
        self.nofolder_radio_button.setObjectName('nofolder_radio_button')
        self.choose_folder_layout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.nofolder_radio_button)
        self.existing_radio_button = QtWidgets.QRadioButton(self)
        self.existing_radio_button.setChecked(False)
        self.existing_radio_button.setObjectName('existing_radio_button')
        self.choose_folder_layout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.existing_radio_button)
        self.folder_combobox = QtWidgets.QComboBox(self)
        self.folder_combobox.setObjectName('folder_combobox')
        self.folder_combobox.activated.connect(self.on_folder_combobox_selected)
        self.choose_folder_layout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.folder_combobox)
        self.new_radio_button = QtWidgets.QRadioButton(self)
        self.new_radio_button.setChecked(False)
        self.new_radio_button.setObjectName('new_radio_button')
        self.choose_folder_layout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.new_radio_button)
        self.new_folder_edit = QtWidgets.QLineEdit(self)
        self.new_folder_edit.setObjectName('new_folder_edit')
        self.new_folder_edit.textEdited.connect(self.on_new_folder_edit_changed)
        self.choose_folder_layout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.new_folder_edit)
        self.folder_button_box = create_button_box(self, 'buttonBox', ['ok'])
        self.choose_folder_layout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.folder_button_box)

        self.retranslate_ui()

    def retranslate_ui(self):
        """
        Translate the UI on the fly.

        :param self: The form object (not the class).
        """
        self.setWindowTitle(translate('OpenLP.ChooseFolderForm', 'Select Folder'))
        self.folder_question_label.setText(translate('OpenLP.ChooseFolderForm', 'Add items to folder:'))
        self.nofolder_radio_button.setText(translate('OpenLP.ChooseFolderForm', 'No folder'))
        self.existing_radio_button.setText(translate('OpenLP.ChooseFolderForm', 'Existing folder'))
        self.new_radio_button.setText(translate('OpenLP.ChooseFolderForm', 'New folder'))

    def exec(self, selected_folder=None):
        """
        Show the form

        :param selected_folder: The ID of the folder that should be selected by default when showing the dialog.
        """
        is_disabled = self.db_manager.get_object_count(self.folder_class) == 0
        self.existing_radio_button.setDisabled(is_disabled)
        self.folder_combobox.setDisabled(is_disabled)
        self.new_folder_edit.clear()
        self.populate_folders()
        if selected_folder is not None:
            for index in range(self.folder_combobox.count()):
                if self.folder_combobox.itemData(index) == selected_folder:
                    self.folder_combobox.setCurrentIndex(index)
                    self.existing_radio_button.setChecked(True)
        return QtWidgets.QDialog.exec(self)

    def accept(self):
        """
        Override the accept() method from QDialog to make sure something is entered in the text input box.
        """
        if self.new_radio_button.isChecked() and not self.new_folder_edit.text():
            critical_error_message_box(message=translate('OpenLP.ChooseFolderForm',
                                                         'You need to type in a folder name.'))
            self.new_folder_edit.setFocus()
            return False
        else:
            return QtWidgets.QDialog.accept(self)

    def on_folder_combobox_selected(self, index: int):
        """
        Handles the activated signal from the existing folder combobox when the
        user makes a selection

        :param index: position of the selected item in the combobox
        """
        self.existing_radio_button.setChecked(True)
        self.folder_combobox.setFocus()

    def on_new_folder_edit_changed(self, new_folder: str):
        """
        Handles the textEdited signal from the new folder text input field
        when the user enters a new folder name

        :param new_folder: new text entered by the user
        """
        self.new_radio_button.setChecked(True)

    @property
    def folder_name(self):
        """
        A property to return the folder name
        """
        return self.new_folder_edit.text()

    @property
    def folder(self):
        if self.existing_radio_button.isChecked() and self.folder_combobox.currentIndex() != -1:
            return self.folder_combobox.currentData(QtCore.Qt.ItemDataRole.UserRole)
        elif self.new_radio_button.isChecked() and self.new_folder_edit.text():
            return self.folder_class(name=self.new_folder_edit.text())
        return None

    @property
    def is_new_folder(self):
        """
        A property to indicate if the folder from the ``folder`` property is a new folder or an existing one
        """
        return self.new_radio_button.isChecked()
