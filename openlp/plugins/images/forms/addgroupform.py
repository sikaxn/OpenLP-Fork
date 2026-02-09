# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2022 OpenLP Developers                              #
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
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.images.forms.addgroupdialog import Ui_AddGroupDialog


class AddGroupForm(QtWidgets.QDialog, Ui_AddGroupDialog):
    """
    This class implements the 'Add group' form for the Images plugin.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(AddGroupForm, self).__init__(parent,
                                           QtCore.Qt.WindowType.WindowSystemMenuHint |
                                           QtCore.Qt.WindowType.WindowTitleHint |
                                           QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui(self)

    def exec(self, clear=True, show_top_level_group=False, selected_group=None):
        """
        Show the form.

        :param clear:  Set to False if the text input box should not be cleared when showing the dialog (default: True).
        :param show_top_level_group:  Set to True when "-- Top level group --" should be showed as first item
            (default: False).
        :param selected_group: The ID of the group that should be selected by default when showing the dialog.
        """
        if clear:
            self.name_edit.clear()
        self.name_edit.setFocus()
        if show_top_level_group and not self.parent_group_combobox.top_level_group_added:
            self.parent_group_combobox.insertItem(0, translate('ImagePlugin.MediaItem', '-- Top-level group --'), 0)
            self.parent_group_combobox.top_level_group_added = True
        if selected_group is not None:
            for i in range(self.parent_group_combobox.count()):
                if self.parent_group_combobox.itemData(i) == selected_group:
                    self.parent_group_combobox.setCurrentIndex(i)
        return QtWidgets.QDialog.exec(self)

    def accept(self):
        """
        Override the accept() method from QDialog to make sure something is entered in the text input box.
        """
        if not self.name_edit.text():
            critical_error_message_box(message=translate('ImagePlugin.AddGroupForm',
                                                         'You need to type in a group name.'))
            self.name_edit.setFocus()
            return False
        else:
            return QtWidgets.QDialog.accept(self)
