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
This module contains the topic edit form.
"""

from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.songs.forms.topicsdialog import Ui_TopicsDialog


class TopicsForm(QtWidgets.QDialog, Ui_TopicsDialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(TopicsForm, self).__init__(parent,
                                         QtCore.Qt.WindowType.WindowSystemMenuHint |
                                         QtCore.Qt.WindowType.WindowTitleHint |
                                         QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui(self)

    def exec(self, clear=True):
        """
        Execute the dialog.
        """
        if clear:
            self.name_edit.clear()
        self.name_edit.setFocus()
        return QtWidgets.QDialog.exec(self)

    def accept(self):
        """
        Override the inherited method to check before we close.
        """
        if not self.name_edit.text():
            critical_error_message_box(
                message=translate('SongsPlugin.TopicsForm', 'You need to type in a topic name.'))
            self.name_edit.setFocus()
            return False
        else:
            return QtWidgets.QDialog.accept(self)

    def _get_name(self):
        """
        Return the name of the topic.
        """
        return self.name_edit.text()

    def _set_name(self, value):
        """
        Set the topic name.
        """
        self.name_edit.setText(value)

    name = property(_get_name, _set_name)
