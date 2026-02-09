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
The :mod:`~openlp.core.pages` module contains wizard pages used in OpenLP
"""
from PySide6 import QtWidgets


class GridLayoutPage(QtWidgets.QWizardPage):
    """
    A class that has a QGridLayout for its layout which automatically ensure all columns are equal width
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._column_width = 0
        self.layout = QtWidgets.QGridLayout(self)
        self.setup_ui()
        self.retranslate_ui()
        self.resize_columns()

    def resizeEvent(self, event):
        """
        Override inherited resize method
        """
        super().resizeEvent(event)
        self.resize_columns()

    def resize_columns(self):
        """
        Resize all the column widths
        """
        width = self.layout.contentsRect().width()
        spacing = self.layout.horizontalSpacing()
        column_count = self.layout.columnCount()
        self._column_width = (width - (spacing * (column_count - 1))) // column_count
        for column_number in range(column_count):
            self.layout.setColumnMinimumWidth(column_number, self._column_width)

    def setup_ui(self):
        raise NotImplementedError('Descendant pages need to implement setup_ui')

    def retranslate_ui(self):
        raise NotImplementedError('Descendant pages need to implement retranslate_ui')
