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
The language selection dialog.
"""
from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import LanguageManager
from openlp.core.lib.ui import create_action

from .firsttimelanguagedialog import Ui_FirstTimeLanguageDialog


class FirstTimeLanguageForm(QtWidgets.QDialog, Ui_FirstTimeLanguageDialog):
    """
    The language selection dialog.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(FirstTimeLanguageForm, self).__init__(parent,
                                                    QtCore.Qt.WindowType.WindowSystemMenuHint |
                                                    QtCore.Qt.WindowType.WindowTitleHint |
                                                    QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui(self)
        self.qm_list = LanguageManager.get_qm_list()
        self.language_combo_box.addItem('Autodetect')
        self.language_combo_box.addItems(sorted(self.qm_list.keys()))

    def exec(self):
        """
        Run the Dialog with correct heading.
        """
        return QtWidgets.QDialog.exec(self)

    def accept(self):
        """
        Run when the dialog is OKed.
        """
        # It's the first row so must be Automatic
        if self.language_combo_box.currentIndex() == 0:
            LanguageManager.auto_language = True
            LanguageManager.set_language(False, False)
        else:
            LanguageManager.auto_language = False
            action = create_action(None, self.language_combo_box.currentText())
            LanguageManager.set_language(action, False)
        return QtWidgets.QDialog.accept(self)

    def reject(self):
        """
        Run when the dialog is canceled.
        """
        LanguageManager.auto_language = True
        LanguageManager.set_language(False, False)
        return QtWidgets.QDialog.reject(self)
