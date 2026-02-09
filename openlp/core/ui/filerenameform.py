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
The file rename dialog.
"""
from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.registry import Registry
from openlp.core.ui.filerenamedialog import Ui_FileRenameDialog


class FileRenameForm(QtWidgets.QDialog, Ui_FileRenameDialog, RegistryProperties):
    """
    The file rename dialog
    """
    def __init__(self):
        """
        Constructor
        """
        super(FileRenameForm, self).__init__(Registry().get('main_window'),
                                             QtCore.Qt.WindowType.WindowSystemMenuHint |
                                             QtCore.Qt.WindowType.WindowTitleHint |
                                             QtCore.Qt.WindowType.WindowCloseButtonHint)
        self._setup()

    def _setup(self):
        """
        Set up the class. This method is mocked out by the tests.
        """
        self.setup_ui(self)

    def exec(self, copy=False):
        """
        Run the Dialog with correct heading.
        """
        if copy:
            self.setWindowTitle(translate('OpenLP.FileRenameForm', 'File Copy'))
        else:
            self.setWindowTitle(translate('OpenLP.FileRenameForm', 'File Rename'))
        self.file_name_edit.setFocus()
        return QtWidgets.QDialog.exec(self)
