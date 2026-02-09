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
The :mod:`~openlp.core.ui.servicenoteform` module contains the `ServiceNoteForm` class.
"""
from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.registry import Registry
from openlp.core.lib.ui import create_button_box
from openlp.core.widgets.edits import SpellTextEdit


class ServiceNoteForm(QtWidgets.QDialog, RegistryProperties):
    """
    This is the form that is used to edit the verses of the song.
    """
    def __init__(self):
        """
        Constructor
        """
        super(ServiceNoteForm, self).__init__(Registry().get('main_window'),
                                              QtCore.Qt.WindowType.WindowSystemMenuHint |
                                              QtCore.Qt.WindowType.WindowTitleHint |
                                              QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui()
        self.retranslate_ui()

    def exec(self):
        """
        Execute the form and return the result.
        """
        self.text_edit.setFocus()
        return QtWidgets.QDialog.exec(self)

    def setup_ui(self):
        """
        Set up the UI of the dialog
        """
        self.setObjectName('serviceNoteEdit')
        self.dialog_layout = QtWidgets.QVBoxLayout(self)
        self.dialog_layout.setContentsMargins(8, 8, 8, 8)
        self.dialog_layout.setSpacing(8)
        self.dialog_layout.setObjectName('vertical_layout')
        self.text_edit = SpellTextEdit(self, False)
        self.text_edit.setObjectName('textEdit')
        self.dialog_layout.addWidget(self.text_edit)
        self.button_box = create_button_box(self, 'button_box', ['cancel', 'save'])
        self.dialog_layout.addWidget(self.button_box)

    def retranslate_ui(self):
        """
        Translate the UI on the fly
        """
        self.setWindowTitle(translate('OpenLP.ServiceNoteForm', 'Service Item Notes'))
