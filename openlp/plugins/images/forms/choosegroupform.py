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

from openlp.plugins.images.forms.choosegroupdialog import Ui_ChooseGroupDialog


class ChooseGroupForm(QtWidgets.QDialog, Ui_ChooseGroupDialog):
    """
    This class implements the 'Choose group' form for the Images plugin.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(ChooseGroupForm, self).__init__(parent,
                                              QtCore.Qt.WindowType.WindowSystemMenuHint |
                                              QtCore.Qt.WindowType.WindowTitleHint |
                                              QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui(self)

    def exec(self, selected_group=None):
        """
        Show the form

        :param selected_group: The ID of the group that should be selected by default when showing the dialog.
        """
        self.new_group_edit.clear()
        if selected_group is not None:
            for index in range(self.group_combobox.count()):
                if self.group_combobox.itemData(index) == selected_group:
                    self.group_combobox.setCurrentIndex(index)
                    self.existing_radio_button.setChecked(True)
        return QtWidgets.QDialog.exec(self)
